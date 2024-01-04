from django.core.management.base import BaseCommand
import requests
import json
import datetime
from decimal import Decimal
from project_cotizador.models import DollarValue

class Command(BaseCommand):
    help = 'Actualiza los valores del dólar desde la fuente externa'

    def handle(self, *args, **kwargs):
        website = 'https://mercados.ambito.com//dolar/informal/historico-general/2000-01-01/2024-01-03'
        result = requests.get(website)
        content = result.text

        data_json = json.loads(content)

        for entry in data_json[1:]:
            date_str = entry[0].replace('/','-')
            buy_value_str = entry[1]
            sell_value_str = entry[2]

            date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
            buy_value = Decimal(buy_value_str.replace(",", "."))
            sell_value = Decimal(sell_value_str.replace(",", "."))

            dollar_value, created = DollarValue.objects.get_or_create(
                date=date, 
                defaults={
                    'buy_value': buy_value,
                    'sell_value': sell_value
                }
            )

        self.stdout.write(self.style.SUCCESS('Valores del dólar actualizados exitosamente'))
