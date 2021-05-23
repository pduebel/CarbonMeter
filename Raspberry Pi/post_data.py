import sqlite3

import requests
import pandas as pd

conn = sqlite3.connect('/home/pi/Documents/Energy Meter/Raspberry Pi/energy.db')

df = pd.read_sql('SELECT * FROM energy', con=conn)
json = df.to_json()

r = requests.post('https://carbon-meter.herokuapp.com/data-upload', json=json)
print(r.content)