import requests
from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urlparse
import re
from datetime import datetime
import pandas as pd
import traceback
from src.scrapper.moteur_ma_utils import save_data
from src.db.enum_classes import Origin
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

mapper = {
    'Kilométrage': 'mileage',
    'Année-Modèle': 'year',
    'Boite de vitesses': 'transmission',
    'Carburant': 'fuel',
    'Puissance fiscale': 'tax_rating',
    'Marque': 'brand',
    'Modèle': 'model',
    'Origine': 'origin',
}

fuel_mapper = {
    'diesel': 'diesel',
    'hybride': 'hybrid',
    'essence': 'essence'
}


def find_value_by_key(key, params):
    matches_key = lambda d: d.get('key') == key
    d = next(filter(matches_key, params), {})
    return d.get('value')


def process_car_element(href):
    print(href)
    page = requests.get(href, verify=False, timeout=5)
    car_soup = BeautifulSoup(page.content, 'html.parser')
    car_details = {}
    other_details = json.loads(car_soup.find_all(text=re.compile(r'Type'))[1])['props']['pageProps']['apolloState']
    params_key = [value for value in other_details.keys() if 'Ad' in value][0]
    params = other_details[params_key]['params']
    details = params['primary'] + params['secondary']

    price = other_details[params_key]['price']['value']
    mileage = find_value_by_key('mileage', details)
    year = find_value_by_key('regdate', details)
    brand = find_value_by_key('brand', details)
    model = find_value_by_key('model', details)
    origin = find_value_by_key('v_origin', details)
    fuel = find_value_by_key('fuel', details)
    tax_rating = find_value_by_key('pfiscale', details)
    transmission = find_value_by_key('bv', details)

    car_data = {
        'id': 'TOTO',
        'price': price,
        'brand': brand,
        'model': model,
        'carrosserie': None,
        'finish': None,
        'horse_power': None,
        'city': None,
        'origin': origin,
        'date_on_the_road': None,
        'vignette_price': None,
        'url': href,
        'source': 'avito.ma',
        'scrapping_date': datetime.now(),
        'mileage': mileage,
        'year': year,
        'tax_rating': tax_rating,
        'fuel': fuel,
        'transmission': transmission,
    }
    return car_data


def get_soup_page(page):
    URL = 'https://www.avito.ma/fr/maroc/voitures-%C3%A0_vendre?spr=50000&rs=26&re=41&o=${page}'.format(page=page)
    page = requests.get(URL, verify=False, timeout=10)
    return BeautifulSoup(page.content, 'html.parser')


if __name__ == '__main__':
    print("Ingesting avito.ma")

    for page in range(1500):
        print(f'Getting avito.ma page {page}')
        car_elements = []
        new_data = []
        try:
            soup = get_soup_page(page)
            car_elements = soup.select('div[data-testid^=adListCard]')
            hrefs = [e.contents[0]['href'] for e in car_elements]
            print(f'Processing moteur.ma data')
            for href in hrefs:
                try:
                    car_data = process_car_element(href)
                    new_data.append(car_data)
                except:
                    traceback.print_exc()
                    print(f'Error with element %{e.href}')
                    continue

            new_data_df = pd.DataFrame.from_records(new_data)
            save_data(new_data_df)
        except requests.exceptions.RequestException:
            traceback.print_exc()
            continue
        except:
            traceback.print_exc()
            continue

    print('Successfully ingested moteur.ma')
