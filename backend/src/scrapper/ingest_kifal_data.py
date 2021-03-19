import requests
from src.db.enum_classes import Transmission, Fuel, Origin
from src.scrapper.utils import save_new_data
from datetime import datetime
import pandas as pd
import urllib3
import traceback


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print('Start ingesting Kifal data')


def get_kifal_page_url(page):
    return f'https://operations-kifal.com/api/website/listed-cars/?p={page}&sort=newest'


headers = {
    "Content-Type": "application/json"
}

r = requests.get(get_kifal_page_url(1), headers=headers, verify=False)

data = r.json()['data']
page_count = r.json()['nbPages']

for i in range(2, page_count):
    r = requests.get(get_kifal_page_url(i), headers=headers, verify=False)
    data = data + r.json()['data']

source = 'kifal'
output = {source: []}


def format_transmission(transmission):
    if transmission == 'Automatique':
        return Transmission.automatic.name
    return Transmission.manual.name


def format_origin(origin):
    if origin == 'WW maroc':
        return Origin.morocco.name
    return Origin.abroad.name


def format_fuel(fuel):
    if fuel == 'Diesel':
        return Fuel.diesel.name
    return Fuel.essence.name


for e in data:
    try:
        ref = e['ref']
        print(ref)
        url = f'https://operations-kifal.com/api/website/car-details/?id={ref}'
        r = requests.get(url, headers=headers, verify=False, timeout=5)
        car_data = r.json()
        output['kifal'].append({
            'id': ref,
            'price': car_data['prix'],
            'brand': car_data['marque'],
            'model': car_data['modele'],
            'transmission': format_transmission(car_data['transmission']),
            'fuel': format_fuel(car_data['carburant']),
            'carrosserie': car_data['carrosserie'],
            'finish': car_data['finition'],
            'mileage': car_data['kilometrage'],
            'tax_rating': car_data['puissanceFiscale'],
            'horse_power': car_data['chevaux'],
            'city': car_data['ville'],
            'origin': format_origin(car_data['origine']),
            'date_on_the_road': car_data['dateMiseEnCirculation'],
            'year': car_data['annee'],
            'vignette_price': car_data['prixVignette'],
            'url': f'https://annonces.kifal-auto.ma/annonce/{ref}',
            'source': source,
            'scrapping_date': datetime.now()
        })
    except requests.exceptions.RequestException:
        traceback.print_exc()
        continue
    except:
        continue

if __name__ == '__main__':
    new_data = pd.DataFrame.from_records(output['kifal'])
    save_new_data(new_data, 'kifal')
    print('Successfully ingested Kifal data')
