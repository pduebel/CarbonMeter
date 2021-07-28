import sqlite3
import requests
import math
import datetime as dt


conn = sqlite3.connect('test.db')
cur = conn.cursor()

cur.execute('''SELECT
                 MIN(timestamp),
                 MAX(timestamp)
               FROM energy
               WHERE carbon_intensity IS NULL''')

min_date_str, max_date_str = cur.fetchall()[0]

if min_date_str and max_date_str:
    headers = {'Accept': 'application/json'}
    postcode = 'RH2'
    date_format = '%Y-%m-%d %H:%M:%S'
    min_date = dt.datetime.strptime(min_date_str, date_format)
    max_date = dt.datetime.strptime(max_date_str, date_format) + dt.timedelta(minutes=30)
    
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

# need to use update rather than insert into
    for intensity_dict in intensity_data:
        timestamp = dt.datetime.strptime(intensity_dict['timestamp'], '%Y-%m-%dT%H:%MZ')
        from_timestamp = str(timestamp)
        to_timestamp = str(timestamp + dt.timedelta(minutes=30))
        cur.execute('''UPDATE energy
                       SET
                         carbon_intensity = ?,
                         intensity_index = ?,
                         carbon = (? * kWh)
                       WHERE timestamp >= ?
                         AND timestamp < ?
                         AND carbon_intensity IS NULL''',
                    (intensity_dict['carbon intensity'],
                     intensity_dict['intensity index'],
                     intensity_dict['carbon intensity'],
                     from_timestamp, to_timestamp))

    conn.commit()
    conn.close()
