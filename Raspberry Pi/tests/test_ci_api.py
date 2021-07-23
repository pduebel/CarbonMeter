import datetime as dt
import requests
import math

headers = {'Accept': 'application/json'}

postcode = 'RH2'
min_date = dt.datetime(2021, 5, 1, 0, 0)
max_date = dt.datetime(2021, 5, 1, 0, 30)
diff = max_date - min_date
steps = math.floor(diff / dt.timedelta(days=13))
dates = [min_date.isoformat(), max_date.isoformat()]
prev_date = min_date
for i in range(steps):
    prev_date = prev_date + dt.timedelta(days=13)
    dates.insert(-1, prev_date.isoformat())

intensity_data = []
for i in range(len(dates) - 1):
    date_from = dates[i]
    date_to = dates[i + 1]

    r = requests.get(f'https://api.carbonintensity.org.uk/regional/intensity/{date_from}/{date_to}/postcode/{postcode}',
                     headers=headers)

    for data_dict in r.json()['data']['data']:
        intensity_dict = {'timestamp': data_dict['from'],
                          'carbon intensity': data_dict['intensity']['forecast'],
                          'intensity index': data_dict['intensity']['index']}
        intensity_data.append(intensity_dict)

for intensity_dict in intensity_data:
    print(intensity_dict['timestamp'])
    print(dt.datetime.strptime(intensity_dict['timestamp'], '%Y-%m-%dT%H:%MZ') + dt.timedelta(minutes=30))
    
