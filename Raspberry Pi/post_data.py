import sqlite3

import requests
import pandas as pd

conn = sqlite3.connect('processed_test.db')

df = pd.read_sql('SELECT * FROM energy', con=conn)
df = df.drop_duplicates(subset='timestamp', keep='last')
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H%M')
df['timestamp'] = df['timestamp'].astype(str)
json = df.to_json()

r = requests.post('https://carbon-meter.herokuapp.com/data-upload', json=json)
print(r.content)