from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
import requests
import json
import datetime
from project_cotizador.models import UvaValue

class Command(BaseCommand):
    help = 'Actualiza los valores de UVA desde la fuente externa'

    def handle(self, *args, **kwargs):
        website = 'https://prestamos.ikiwi.net.ar/api/v1/engine/uva/valores/'
        result = requests.get(website)
        content = result.text

        soup = BeautifulSoup(content, 'lxml')
        box = soup.find('body')
        data_json = json.loads(box.find('p').text)

        for entry in data_json:
            date_str = entry['fecha']
            value = entry['valor']
            date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
            uva_value, created = UvaValue.objects.get_or_create(date=date, defaults={'value': value})

        self.stdout.write(self.style.SUCCESS('Valores UVA actualizados exitosamente'))
