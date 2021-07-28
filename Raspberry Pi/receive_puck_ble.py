'''Receive advertising data from named device (i.e. puck.js) and input this info, along with
   date and time data, into an sqlite database. Linux only, must be run as root.'''
import sys
import os
import datetime

import requests
from bluepy.btle import Scanner, DefaultDelegate

from db import DB

# The devices we're searching for
devices = [
  'f8:04:7f:c2:35:10'
];

# Initialise database
db = DB('/home/pi/Documents/Energy Meter/Raspberry Pi/energy.db')
db.create_db()

# Gets the actual scanning data  
class ScanDelegate(DefaultDelegate):
  def __init__(self):
    DefaultDelegate.__init__(self)
  def handleDiscovery(self, dev, isNewDev, isNewData):
    if not dev.addr in devices: return
    for (adtype, desc, value) in dev.getScanData():
      if adtype==255 and value[:4]=="9005": # Manufacturer Data
        # Get raw data
        data = value[4:]
        battery = int(data[:2], 16)
        counter = int(data[2:10], 16)
        rate = int(data[10:], 16)
        
        # Derive power metrics
        kWh = counter / 1000
        kW = rate / 1000
        
        # Get time info
        timestamp = datetime.datetime.now()
        timestamp = timestamp.replace(second=0, microsecond=0)
        
        # Input to database
        print (f'Timestamp: {timestamp}, Battery: {battery}, kWh {kWh}, kW: {kW}')
        data = (timestamp, battery, kWh, kW)
        db.insert(data)
        try:
            r = requests.post('https://carbon-meter.herokuapp.com/kW-upload', data={'kW': kW})
            print(r.content)
        except:
            print('kW upload failed')
        global tries
        tries = 0

# Start scanning

scanner = Scanner().withDelegate(ScanDelegate())
scanner.clear()
scanner.start()

tries = 0
uploaded = False

# Keep scanning in  10 second chunks
while True:
    if (datetime.datetime.now().minute in [0, 15, 30, 45]) and not uploaded:
        try:
            db.get_carbon_intensity()
        except Exception as e:
            print(e)
            print('Could not get carbon intensity.')
        try:
            db.post_data('https://carbon-meter.herokuapp.com/data-upload')
            uploaded = True
        except Exception as e:
            print(e)
            print('JSON upload failed.')
            
    elif datetime.datetime.now().minute not in [0, 15, 30, 45]:
        uploaded = False
        
    print('Scanning...')
    scanner.process(10)
    tries += 1
    # restart script if no data received after 5 loops
    if tries >= 5:
        print('Restarting')
        sys.stdout.flush()
        os.execv(sys.executable, ['python3'] + sys.argv)
# in case were wanted to finish, we should call 'stop'
scanner.stop()