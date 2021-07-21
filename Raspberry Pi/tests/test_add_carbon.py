import sqlite3
import requests

conn = sqlite3.connect('test.db')
cur = conn.cursor()

no_carbon = '''SELECT *
               FROM energy
               WHERE carbon_intensity IS NULL'''
cur.execute('''SELECT
                 MIN(timestamp),
                 MAX(timestamp)
               FROM energy
               WHERE carbon_intensity IS NULL''')
for row in cur.fetchall():
    print(row)