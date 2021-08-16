config = {
    'DEVICE': 'h7:04:7a:c2:27:10', # ip address of puck
    'DB_PATH': '/home/pi/energy.db', # filepath to database
    'IMP/KWH': 1000, # can find this next to led on meter, usually 800 or 1000
    'POST_URL_KW': 'https://pimeter.herokuapp.com/kW-upload', # (optional) url to post kW value to
    'POST_URL_DB': 'https://pimeter.herokuapp.com/data-upload', # (optional) url to post db to
    'POSTCODE': 'RH13' # outward part of postcode (first part, UK only)
}