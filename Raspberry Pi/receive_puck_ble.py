'''Receive advertising data from named device (i.e. puck.js) and input this info, along with
   date and time data, into an sqlite database. Linux only, must be run as root.'''
import datetime

from bluepy.btle import Scanner, DefaultDelegate

from db import DB

# The devices we're searching for
devices = [
  'f8:04:7f:c2:35:10'
];

# Initialise database
db = DB('test.db')
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
        kWh = counter / 800
        kW = rate / 800
        
        # Get time info
        date = datetime.date.today()
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        
        id_number = int(str(now.year)
                        + str(now.month)
                        + str(now.day)
                        + str(now.hour)
                        + str(now.minute))
        
        # Input to database
        print (f'ID: {id_number}, Date: {date}, Hour: {hour}, Minute: {minute}, Battery: {battery}, kWh {kWh}, kW: {kW}')
        data = (id_number, date, hour, minute, battery, kWh, kW)
        db.insert(data)

# Start scanning
scanner = Scanner().withDelegate(ScanDelegate())
scanner.clear()
scanner.start()
# Keep scanning in  10 second chunks
while True:
    print('Scanning...')
    scanner.process(10)
# in case were wanted to finish, we should call 'stop'
scanner.stop()