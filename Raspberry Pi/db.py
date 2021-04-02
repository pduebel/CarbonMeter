import sqlite3

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
                         id int PRIMARY KEY,
                         date date,
                         hour int,
                         minute int,
                         battery int,
                         kWh float,
                         kW float
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
                id: int
                    unique id number, if this already exists in the table then existing data
                    will be replaced
                date: date
                hour: int
                minute: int
                battery: int
                kWh: float
                kW: float
        
        Returns
        -------
        None
        '''
        
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''REPLACE INTO energy (id, date, hour, minute, battery, kWh, kW)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
        conn.close()