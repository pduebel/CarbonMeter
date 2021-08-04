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
        self.tries = 0
        
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
        try:
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
        
        except Exception as e:
            print(e)
            print('Error creating table')
    
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
        
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('''REPLACE INTO energy (
                           timestamp,
                           battery,
                           total_kWh,
                           kWh,
                           kW
                         )
                         VALUES (
                           ?,
                           ?,
                           ?,
                           (? - (
                               SELECT total_kWh
                               FROM energy
                               WHERE timestamp = (
                                   SELECT MAX(timestamp)
                                   FROM energy
                               )
                           )),
                           ?)''',
                      data)
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(e)
            print('Error inserting data into db')
        
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
        
        try:
            conn = sqlite3.connect(self.db_name)
            df = pd.read_sql('SELECT * FROM energy', con=conn)
            json = df.to_json()
            r = requests.post(post_url, json=json)
            r.raise_for_status()
            print('Database uploaded')
            
        except Exception as e:
            print(e)
            print('Error uploading db')
        
    def get_carbon_intensity(self, postcode):
        '''
        Finds min and max times of records that are missing carbon intensity
        data and gets regional carbon intensity data (in gCO2/kWh) across this
        range by querying the National Grid API. Then updates records with this
        data where missing. Also multiplies kWh by carbon intensity to give gCO2
        produced.
        
        Carbon intensity data is for the UK only, with regional data currently in
        beta so only able to use forecasted values.
        
        Parameters
        ----------
        postcode: string
            Outward part (the first part) of user postcode (UK only) for providing
            regional carbon intensity data.
        
        Returns
        -------
        None
        '''
        
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            # find min and max datetimes that are missing data
            cur.execute('''SELECT
                             MIN(timestamp),
                             MAX(timestamp)
                           FROM energy
                           WHERE carbon_intensity IS NULL''')

            min_date_str, max_date_str = cur.fetchall()[0]

            if min_date_str and max_date_str:
                headers = {'Accept': 'application/json'}
                postcode = postcode
                date_format = '%Y-%m-%d %H:%M:%S'
                min_date = dt.datetime.strptime(min_date_str, date_format)
                max_date = dt.datetime.strptime(max_date_str, date_format) + dt.timedelta(minutes=30)
            
                # API can only work in date ranges <14 days - so break the date
                # range into 13 day chunks
                diff = max_date - min_date
                steps = math.floor(diff / dt.timedelta(days=13))
                dates = [min_date.isoformat(), max_date.isoformat()]
                prev_date = min_date
                for i in range(steps):
                    prev_date = prev_date + dt.timedelta(days=13)
                    dates.insert(-1, prev_date.isoformat())
            
                # loop through 13 day chunks to call API
                intensity_data = []
                for i in range(len(dates) - 1):
                    date_from = dates[i]
                    date_to = dates[i + 1]
                    r = requests.get(f'https://api.carbonintensity.org.uk/regional/intensity/{date_from}/{date_to}/postcode/{postcode}',
                                     headers=headers)
                # extract relevant data from response
                for data_dict in r.json()['data']['data']:
                    intensity_dict = {'timestamp': data_dict['from'],
                                      'carbon intensity': data_dict['intensity']['forecast'],
                                      'intensity index': data_dict['intensity']['index']}
                    intensity_data.append(intensity_dict)

                # add data to db
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
            
        except Exception as e:
            print(e)
            print('Error getting carbon intensity data')