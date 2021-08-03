from bluepy.btle import DefaultDelegate
from config import config

# Gets the actual scanning data  
class ScanDelegate(DefaultDelegate):
  def __init__(self, devices, ):
    DefaultDelegate.__init__(self)
    self.devices = devices
    
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
        total_kWh = counter / config['IMP/KWH']
        kW = rate / config['IMP/KWH']
        
        # Get time info
        timestamp = datetime.datetime.now()
        timestamp = timestamp.replace(second=0, microsecond=0)
        
        # Input to database
        print (f'Timestamp: {timestamp}, Battery: {battery}, total_kWh {total_kWh}, kW: {kW}')
        data = (timestamp, battery, total_kWh, total_kWh, kW)
        db.insert(data)
        db.tries = 0
        # --- optional ---
        # post current usage to web app
        try:
            r = requests.post(config['POST_URL_KW'], data={'kW': kW})
            r.raise_for_status()
            print('kW uploaded')
        except:
            print('kW upload failed')