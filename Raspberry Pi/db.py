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
                         kWh FLOAT,
                         kW FLOAT
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
        
    def post(self, post_url):
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