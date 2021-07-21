import datetime as dt
import requests

headers = {'Accept': 'application/json'}

postcode = 'RH2'
date_from = dt.datetime(2021, 7, 1, 0, 0).isoformat()
date_to = dt.datetime(2021, 7, 20, 18, 30).isoformat()
intensity_data = []

check = True

while check:
    print(date_from)

    r = requests.get(f'https://api.carbonintensity.org.uk/regional/intensity/{date_from}/{date_to}/postcode/{postcode}',
                     headers=headers)

    for data_dict in r.json()['data']['data']:
        intensity_dict = {'timestamp': data_dict['from'],
                          'carbon intensity': data_dict['intensity']['forecast'],
                          'intensity index': data_dict['intensity']['index']}
        intensity_data.append(intensity_dict)

    if r.json()['data']['data'][-1]['to'][:-1] != date_to[:-3]:
        date_from = intensity_data[-1]['timestamp']
    else:
        check = False

print(intensity_data)
