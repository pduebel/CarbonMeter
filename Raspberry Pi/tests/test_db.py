import datetime
import sqlite3

conn = sqlite3.connect('test.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS energy (
                         timestamp TEXT PRIMARY KEY,
                         battery INTEGER,
                         total_kWh,
                         kWh FLOAT,
                         kW FLOAT,
                         carbon_intensity INTEGER,
                         carbon INTEGER
                      );''')

timestamp = datetime.datetime.now()
timestamp = timestamp.replace(second=0, microsecond=0)
battery = 20
total_kWh = 51
kW = 21

data = (timestamp, battery, total_kWh, total_kWh, kW)

c.execute('''REPLACE INTO energy (timestamp, battery, total_kWh, kWh, kW)
                 VALUES (?, ?, ?, (? - (SELECT total_kWh
                                        FROM energy
                                        WHERE timestamp = (SELECT MAX(timestamp)
                                                           FROM energy))), ?)''', data)
conn.commit()
conn.close()