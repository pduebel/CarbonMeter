'''Receive advertising data from named device (i.e. puck.js) and input this info, along with
   date and time data, into an sqlite database. Linux only, must be run as root.'''
import sys
import os
import datetime

import requests
from bluepy.btle import Scanner

from db import DB
from config import config
from scan_delegate import ScanDelegate

# The devices we're searching for
devices = [config['DEVICE']]

# Initialise database
db = DB(config['DB_PATH'])
db.create_db()

# --- optional ---
# username and password if using web app
auth = (config['USERNAME'], config['PASSWORD'])

# Start scanning
scanner = Scanner().withDelegate(ScanDelegate(devices,
                                              config['IMP/KWH'],
                                              db,
                                              config['POST_URL_KW'],
                                              auth))
scanner.clear()
scanner.start()

uploaded = False

# Keep scanning in  10 second chunks
while True:
    # every 15 mins add carbon intensity data and upload data to web app (optional)
    if (datetime.datetime.now().minute in [0, 15, 30, 45]) and not uploaded:
        # get carbon intensity data
        try:
            db.get_carbon_intensity(config['POSTCODE'])
            print('Carbon intensity added')
        except Exception as e:
            print(e)
            print('Could not get carbon intensity.')
        # --- optional ---
        # post database to web app as json
        try:
            db.post_data(config['POST_URL_DB'], auth=auth)
            uploaded = True
            print('Data uploaded')
        except Exception as e:
            print(e)
            print('Data upload failed.')
            
    elif datetime.datetime.now().minute not in [0, 15, 30, 45]:
        uploaded = False
    
    # get & process scan data
    print('Scanning...')
    scanner.process(10)
    db.tries += 1
    
    # restart script if no data received after 5 loops
    if db.tries >= 5:
        print('Restarting')
        try:
            scanner.stop()
        except:
            pass
        sys.stdout.flush()
        os.execv(sys.executable, ['python3'] + sys.argv)
        
# in case were wanted to finish, we should call 'stop'
scanner.stop()