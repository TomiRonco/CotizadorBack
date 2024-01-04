from bs4 import BeautifulSoup
from .models import UvaValue, DollarValue
from django.http import HttpResponse
from django.http import JsonResponse
import requests
import json
import datetime
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal

@csrf_exempt
def process_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            amount = float(data.get('amount'))  # Convierte a float
            date_str = data.get('date')

            # Convierte la fecha a un objeto de tipo datetime.date
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Busca el valor de UVA y dólar en la base de datos para la fecha dada
            dollar_value = DollarValue.objects.filter(date=date).first()
            uva_value = UvaValue.objects.filter(date=date).first()

            result = {}

            if uva_value:
                # Multiplica el monto por el valor de UVA y redondea a dos cifras
                result['uva'] = round(amount * uva_value.value, 2)
            else:
                print(f"No se encontraron valores de uva para la fecha {date}")

            if dollar_value:
                result['dollarPurchase'] = round(amount * float(dollar_value.buy_value), 2)
                result['dollarSale'] = round(amount * float(dollar_value.sell_value), 2)
            else:
                print(f"No se encontraron valores de dólar para la fecha {date}")

            if not result:
                return JsonResponse({'error': 'No hay valores para la fecha proporcionada'}, status=404)

            # Devuelve el resultado como JSON
            return JsonResponse(result)

        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Error al procesar los datos JSON o en la conversión de tipos'}, status=400)

    else:
        return JsonResponse({'error': 'Esta vista solo acepta solicitudes POST'}, status=405)

def update_uva_value(request):
    website = 'https://prestamos.ikiwi.net.ar/api/v1/engine/uva/valores/'
    result = requests.get(website)
    content = result.text

    soup = BeautifulSoup(content, 'lxml')
    box = soup.find('body')
    data_json = json.loads(box.find('p').text)

    response_data = []

    for entry in data_json:
        date_str = entry['fecha']
        value = entry['valor']
        date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
        
        uva_value, created = UvaValue.objects.get_or_create(date=date, defaults={'value': value})
        response_data.append(f"Fecha: {date_str}, Valor UVA: {value}")

    response_text = "\n".join(response_data)
    return HttpResponse(response_text)

def update_dollar_value(request):
    website = 'https://mercados.ambito.com//dolar/informal/historico-general/2000-01-01/2024-12-31'
    result = requests.get(website)
    content = result.text

    soup = BeautifulSoup(content, 'lxml')
    box = soup.find('body')
    data_json = json.loads(box.find('p').text)

    response_data = []

    for entry in data_json[1:]:
        date_str = entry[0].replace('/','-')
        buy_value_str = entry[1]
        sell_value_str = entry[2]

        date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
        buy_value = Decimal(buy_value_str.replace(",", "."))
        sell_value = Decimal(sell_value_str.replace(",", "."))

        dollar_value, created = DollarValue.objects.get_or_create(
            date=date,
            defaults={'buy_value': buy_value, 'sell_value': sell_value}
        )
        response_data.append(f"Fecha: {date_str}, Compra: {buy_value}, Venta: {sell_value}")

    response_text = "\n".join(response_data)
    return HttpResponse(response_text)