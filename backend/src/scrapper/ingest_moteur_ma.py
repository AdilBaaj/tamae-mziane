import requests
from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urlparse
import re
from datetime import datetime
import pandas as pd
from backend.src.db import engine, car_data as car_table
import traceback


print("Ingesting moteur.ma")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
URL = 'https://www.moteur.ma/fr/voiture/achat-voiture-occasion/recherche/?prix_min=10000'
page = requests.get(URL, verify=False)

soup = BeautifulSoup(page.content, 'html.parser')

number_pages = soup.find('span', class_='pull-right').contents[3].contents[0]

mapper = {
    'Kilométrage': 'mileage',
    'Année': 'year',
    'Boite de vitesses': 'transmission',
    'Carburant': 'fuel',
    'Puissance fiscale': 'tax_rating',
}


def process_car_element(car_element):
    href = car_element['href']
    print(href)
    page = requests.get(href, verify=False)
    car_soup = BeautifulSoup(page.content, 'html.parser')
    car_details_elements = car_soup.find_all('div', class_='detail_line')
    car_details = {}
    keys = mapper.keys()
    ref = urlparse(href).path.split('/')[5]
    for e in car_details_elements:
        for key in keys:
            if key in e.contents[1].contents[0]:
                value = e.contents[3].contents[0]
                value = re.sub(r"[\n\t\r\s]*", "", value)
                car_details[mapper[key]] = value
    price = int(re.sub(r"[\n\t\r]*", "", car_soup.find('div', class_=['color_primary', 'text_bold', 'price-block']).contents[0])[:-4].replace(' ', ''))
    brand_model = re.sub(r"[\n\t\r]*", "", car_soup.find('span', class_='text_bold').contents[0]).split(' ')
    brand = brand_model[0]
    model = ' '.join(brand_model[1:])
    car_data = {
        'id': ref, # A récupérer directement
        'price': price, # A récupérer directement
        'brand': brand, # A récupérer directement
        'model': model, # A récupérer directement
        'carrosserie': None,
        'finish': None,
        'horse_power': None,
        'city': None,
        'origin': None,
        'date_on_the_road': None,
        'vignette_price': None,
        'url': href,
        'source': 'moteur.ma',
        'scrapping_date': datetime.now(),
        'mileage': int(car_details.get('mileage', 0)),
        'year': int(car_details.get('year', 0)),
        'tax_rating': int(car_details.get('tax_rating', 0)),
        'fuel': car_details.get('fuel').lower(),
        'transmission': 'automatic' if car_details.get('transmission') == 'Automatique' else 'manual',
    }
    return car_data


if __name__ == '__main__':
    car_pictures_soup = soup.find_all(attrs={'class': 'picture_show', 'style': 'height:100% !important;line-height:0!important;'})
    car_elements = [e.contents[1] for e in car_pictures_soup]
    new_data = []
    for e in car_elements:
        try:
            new_data.append(process_car_element(e))
        except:
            traceback.print_exc()
            print(f'Error with element %{e.href}')
            continue
    new_data_df = pd.DataFrame.from_records(new_data)
    old_data_df = pd.read_sql(car_table.select().where(car_table.c.source == 'moteur.ma'), engine)
    old_data_df['transmission'] = old_data_df['transmission'].apply(lambda x: x.name)
    old_data_df['fuel'] = old_data_df['fuel'].apply(lambda x: x.name)
    old_data_df['origin'] = old_data_df['origin'].apply(lambda x: (None if x is None else True) and x.name)

    all_data = pd.concat([old_data_df, new_data_df])
    all_data = all_data.drop_duplicates(subset=['id'])

    all_data.to_sql('car_data', engine, if_exists='append', index=False)

