import requests
from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urlparse
import re
from datetime import datetime
import pandas as pd
import traceback
from backend.src.scrapper.utils import save_new_data
from backend.src.db.enum_classes import Origin


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


mapper = {
    'Kilométrage': 'mileage',
    'Année': 'year',
    'Boite de vitesses': 'transmission',
    'Carburant': 'fuel',
    'Puissance fiscale': 'tax_rating',
}

fuel_mapper = {
    'diesel': 'diesel',
    'hybride': 'hybrid',
    'essence': 'essence'
}


def process_car_element(car_element):
    href = car_element['href']
    print(href)
    page = requests.get(href, verify=False, timeout=5)
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
    price = int(re.sub(r"[\n\t\r]*", "",
                       car_soup.find('div', class_=['color_primary', 'text_bold', 'price-block']).contents[0])[
                :-4].replace(' ', ''))
    brand_model = re.sub(r"[\n\t\r]*", "", car_soup.find('span', class_='text_bold').contents[0]).split(' ')
    brand = brand_model[0]
    model = ' '.join(brand_model[1:])
    car_data = {
        'id': ref,
        'price': price,
        'brand': brand,
        'model': model,
        'carrosserie': None,
        'finish': None,
        'horse_power': None,
        'city': None,
        'origin': Origin.morocco.name,
        'date_on_the_road': None,
        'vignette_price': None,
        'url': href,
        'source': 'moteur.ma',
        'scrapping_date': datetime.now(),
        'mileage': int(car_details.get('mileage', 0)),
        'year': int(car_details.get('year', 0)),
        'tax_rating': int(car_details.get('tax_rating', 0)),
        'fuel': fuel_mapper.get(car_details.get('fuel').lower()),
        'transmission': 'automatic' if car_details.get('transmission') == 'Automatique' else 'manual',
    }
    return car_data


if __name__ == '__main__':
    print("Ingesting moteur.ma")
    URL = 'https://www.moteur.ma/fr/voiture/achat-voiture-occasion/recherche/?prix_min=10000'
    page = requests.get(URL, verify=False, timeout=5)
    soup = BeautifulSoup(page.content, 'html.parser')

    # TODO: scrap all pages
    number_pages = soup.find('span', class_='pull-right').contents[3].contents[0]
    car_pictures_soup = soup.find_all(
        attrs={'class': 'picture_show', 'style': 'height:100% !important;line-height:0!important;'})
    car_elements = [e.contents[1] for e in car_pictures_soup]
    new_data = []
    for e in car_elements:
        try:
            car_data = process_car_element(e)
            new_data.append(car_data)
            new_data_df = pd.DataFrame.from_records(new_data)
            save_new_data(new_data_df, 'moteur.ma')
            print('Successfully ingested moteur.ma')
        except requests.exceptions.RequestException:
            traceback.print_exc()
            continue
        except:
            traceback.print_exc()
            print(f'Error with element %{e.href}')
            continue
