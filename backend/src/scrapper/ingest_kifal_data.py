import requests
from backend.src.db.enum_classes import Transmission, Fuel, Origin
from backend.src.db.table import car_data as car_table
from backend.src.db import engine
from datetime import datetime


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
        return Transmission.automatic
    return Transmission.manual


def format_origin(origin):
    if origin == 'WW maroc':
        return Origin.morocco
    return Origin.abroad


def format_fuel(fuel):
    if fuel == 'Diesel':
        return Fuel.diesel
    return Fuel.essence


for e in data:
    ref = e['ref']
    url = f'https://operations-kifal.com/api/website/car-details/?id={ref}'
    r = requests.get(url, headers=headers, verify=False)
    car_data = r.json()
    output['kifal'].append({
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

if __name__ == '__main__':
    print(output['kifal'])

    # Delete previous Kifal data
    engine.execute(car_table.delete().where(car_table.c.source == 'kifal'))

    # Update Kifal Data
    engine.execute(car_table.insert(), output['kifal'])
