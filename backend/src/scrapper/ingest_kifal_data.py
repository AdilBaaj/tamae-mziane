import requests
from backend.src.db.enum_classes import Transmission, Fuel, Origin
from backend.src.db import engine, car_data as car_table
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

    try:
        old_data = pd.read_sql(car_table.select().where(car_table.c.source == 'kifal'), engine)
        old_data['transmission'] = old_data['transmission'].apply(lambda x: x.name)
        old_data['fuel'] = old_data['fuel'].apply(lambda x: x.name)
        old_data['origin'] = old_data['origin'].apply(lambda x: x.name)
        all_data = pd.concat([old_data, new_data])
    # TODO: narrow exception -> In case table does not exist
    except:
        traceback.print_exc()
        all_data = new_data

    all_data = all_data.drop_duplicates(subset=['id'])
    all_data.to_sql('car_data', engine, if_exists='append', index=False)

    print('Successfully ingested Kifal data')
