import requests
import json

url = "https://operations-kifal.com/api/website/listed-cars/?p=1&sort=newest"

headers = {
    "Content-Type": "application/json"
}

r = requests.get(url, headers=headers, verify=False)
data = r.json()['data']

output = {'kifal': []}

for e in data:
    ref = e['ref']
    url = f'https://operations-kifal.com/api/website/car-details/?id=${ref}'
    r = requests.get(url, headers=headers, verify=False)
    car_data = r.json()
    output['kifal'].append({
        'price': car_data['prix'],
        'brand': car_data['marque'],
        'model': car_data['modele'],
        'transmission': car_data['transmission'],
        'fuel': car_data['carburant'],
        'carrosserie': car_data['carrosserie'],
        'finish': car_data['finition'],
        'mileage': car_data['kilometrage'],
        'tax_rating': car_data['puissanceFiscale'],
        'horse_power': car_data['chevaux'],
        'city': car_data['ville'],
        'origin': car_data['origine'],
        'date_on_the_road': car_data['dateMiseEnCirculation'],
        'year': car_data['annee'],
        'vignette_price': car_data['prixVignette'],
    })

with open('output.json', 'w', encoding="utf-8") as outfile:
    json.dump(output, outfile, ensure_ascii=False)