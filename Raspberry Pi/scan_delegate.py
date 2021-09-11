import datetime

import requests
from bluepy.btle import DefaultDelegate

from config import config


class ScanDelegate(DefaultDelegate):
    '''
    Class that gets the actual scanning data from ble scan. Processes data
    received from puck.js and inserts into database.
     
    Attributes
    ----------
    devices: list
        list of ip addresses (str) to search for
        
    imp_kwh: int
        imp/kWh setting of energy meter, usually dsiplayed on meter next to
        flashing LED, commonly 1000 or 800
    
    db: object
        database object for inserting scan data
        
    post_url_kw: str
        url to post kW data to if using web app to display data (feel free to remove
        if viewing data a different way)
        
    Methods
    -------
    handleDiscovery():
        Upon discovery of ble advertisement from device in list of devices processes
        advertised energy data and inserts into database. Also post current usage in
        kW to url for display in web app (optional).
    '''
    
    def __init__(self, devices, imp_kwh, db, web_app, post_url_kw, auth):
        '''
        Constructs attributes of ScanDelegate object.       
        '''
        DefaultDelegate.__init__(self)
        self.devices = devices
        self.imp_kwh = imp_kwh
        self.db = db
        self.web_app = web_app
        # --- optional ---
        # for use with web app
        self.post_url_kw = post_url_kw
        self.auth = auth
    
    def handleDiscovery(self, dev, isNewDev, isNewData):
        '''
        Upon discovery of ble advertisement from device in list of devices processes
        advertised energy data and inserts into database. Also post current usage in
        kW to url for display in web app (optional).
        
        Parameters
        ----------
        dev: object
           data received from ble scanning
        '''
        if not dev.addr in self.devices: return
        for (adtype, desc, value) in dev.getScanData():
            if adtype==255 and value[:4]=="9005": # Manufacturer Data
                # Get raw data
                data = value[4:]
                battery = int(data[:2], 16)
                counter = int(data[2:10], 16)
                rate = int(data[10:], 16)
        
                # Derive power metrics
                total_kWh = counter / self.imp_kwh
                kW = rate / self.imp_kwh
        
                # Get time info
                timestamp = datetime.datetime.now()
                timestamp = timestamp.replace(second=0, microsecond=0)
        
                # Input to database
                print (f'Timestamp: {timestamp}, Battery: {battery}, total_kWh {total_kWh}, kW: {kW}')
                data = (timestamp, battery, total_kWh, total_kWh, kW)
                self.db.insert(data)
                self.db.tries = 0
                # --- optional ---
                # post current usage to web app
                if self.web_app:
                    try:
                        r = requests.post(self.post_url_kw, data={'kW': kW}, auth=self.auth)
                        print(r.content)
                        r.raise_for_status()
                        print('kW uploaded')
                    except Exception as e:
                        print(e)
                        print('kW upload failed')