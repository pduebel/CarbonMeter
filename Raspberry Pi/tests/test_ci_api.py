import datetime as dt
import requests

headers = {'Accept': 'application/json'}

postcode = 'RH2'
date_from = dt.datetime(2021, 7, 1, 0, 0).isoformat()
date_to = dt.datetime(2021, 7, 1, 18, 30).isoformat()

r = requests.get(f'https://api.carbonintensity.org.uk/regional/intensity/{date_from}/{date_to}/postcode/{postcode}',
                 headers=headers)

print(r.json())