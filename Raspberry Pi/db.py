import datetime as dt
import math
import requests
import sqlite3
import pandas as pd

class DB:
    '''
    A class for creating and storing energy data in an sqlite database.
    
    Attributes
    ----------
    name: str
        filename of database
        
    Methods
    -------
    create_db():
        Creates sqlite database with energy table.
    insert(data):
        Accepts tuple of data and inserts or replaces into energy table of database.
    '''
    
    def __init__(self, db_name):
        '''
        Constructs attributes of database object.
        
        Parameters
        ----------
        name: str
            filename of database            
        '''
            
        self.db_name = db_name
        
    def create_db(self):
        '''
        Creates connection to database (creating it if it doesn't already exist) and
        creates a table for energy data (if this also does not already exist).
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS energy (
                         timestamp TEXT PRIMARY KEY,
                         battery INTEGER,
                         total_kWh FLOAT,
                         kWh FLOAT,
                         kW FLOAT,
                         carbon_intensity INTEGER,
                         intensity_index TEXT,
                         carbon INTEGER
                      );''')
        conn.commit()
        conn.close()
    
    def insert(self, data):
        '''
        Creates connection to database and inserts or replaces tuple of data into energy
        table.
        
        Parameters
        ----------
        data: tuple
            A tuple containing the energy data to insert/replace into database.
            Expected to contain (in this order):
                timestamp: str
                    unique timestamp, if this already exists in the table then existing data
                    will be replaced
                battery: int
                kWh: float
                kW: float
        
        Returns
        -------
        None
        '''
        
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''REPLACE INTO energy (timestamp, battery, kWh, kW)
                         VALUES (?, ?, ?, ?)''', data)
        conn.commit()
        conn.close()
        
    def post_data(self, post_url):
        '''
        Converts entire energy table to json, creates post request to input url,
        and prints contents of response.
        
        Parameters
        ----------
        post_url: string
            Url to submit post request to
            
        Returns
        -------
        None
        '''
        
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql('SELECT * FROM energy', con=conn)
        json = df.to_json()
        r = requests.post(post_url, json=json)
        print(r.content)
        
    def get_carbon_intensity(self):
        
        conn = sqlite3.connect(self)
        cur = conn.cursor()

        cur.execute('''SELECT
                         MIN(timestamp),
                         MAX(timestamp)
                       FROM energy
                       WHERE carbon_intensity IS NULL''')

        min_date_str, max_date_str = cur.fetchall()[0]

        if min_date_str and max_date_str:
            headers = {'Accept': 'application/json'}
            postcode = 'RH2'
            date_format = '%Y-%m-%d %H:%M:%S'
            min_date = dt.datetime.strptime(min_date_str, date_format)
            max_date = dt.datetime.strptime(max_date_str, date_format) + dt.timedelta(minutes=30)
    
            diff = max_date - min_date
            steps = math.floor(diff / dt.timedelta(days=13))
            dates = [min_date.isoformat(), max_date.isoformat()]
            prev_date = min_date
            for i in range(steps):
                prev_date = prev_date + dt.timedelta(days=13)
                dates.insert(-1, prev_date.isoformat())

            intensity_data = []
            for i in range(len(dates) - 1):
                date_from = dates[i]
                date_to = dates[i + 1]
                r = requests.get(f'https://api.carbonintensity.org.uk/regional/intensity/{date_from}/{date_to}/postcode/{postcode}',
                                 headers=headers)
            for data_dict in r.json()['data']['data']:
                intensity_dict = {'timestamp': data_dict['from'],
                                  'carbon intensity': data_dict['intensity']['forecast'],
                                  'intensity index': data_dict['intensity']['index']}
                intensity_data.append(intensity_dict)

            # need to use update rather than insert into
            for intensity_dict in intensity_data:
                timestamp = dt.datetime.strptime(intensity_dict['timestamp'],
                                                 '%Y-%m-%dT%H:%MZ')
                from_timestamp = str(timestamp)
                to_timestamp = str(timestamp + dt.timedelta(minutes=30))
                cur.execute('''UPDATE energy
                               SET
                                 carbon_intensity = ?,
                                 intensity_index = ?,
                                 carbon = (? * kWh)
                               WHERE timestamp >= ?
                                 AND timestamp < ?
                                 AND carbon_intensity IS NULL''',
                            (intensity_dict['carbon intensity'],
                             intensity_dict['intensity index'],
                             intensity_dict['carbon intensity'],
                             from_timestamp,
                             to_timestamp))

        conn.commit()
        conn.close()