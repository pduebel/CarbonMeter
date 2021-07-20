import sqlite3
import requests

conn = sqlite3.connect('test.db')
cur = conn.cursor()

cur.execute('''SELECT *
               FROM energy
               WHERE carbon_intensity IS NULL''')
for row in cur.fetchall():
    print(row)