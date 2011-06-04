#!/usr/bin/python

"""
NASA Data Importer v%(VERSION)s
 
Synopsis: nasa.py

	-h  This help message
	-l  CSV file containing station data
	
"""

import sys, urllib, urllib2, getopt, psycopg2, csv, datetime, config

VERSION = '0.1'
PGSQL_CONN_STRING = "dbname=%s user=%s password=%s" % (config.DBNAME, config.DBUSER, config.DBPASS)

conn = psycopg2.connect(PGSQL_CONN_STRING)

def usage(exit_code=0): 
  print __doc__ % globals()
  sys.exit(exit_code)

def fetch_nasa_data(lat=10, lng=10):  
  NASA_URL = 'http://earth-www.larc.nasa.gov/cgi-bin/cgiwrap/solar/agro.cgi?email=agroclim@larc.nasa.gov'

  params = {
    'email': 'agroclim@larc.nasa.gov',
    'step': 1,
    'lat': lat,
    'lon': lng,
    'ms': 1,
    'ds': 1,
    'ys': 1983,
    'me': 12,
    'de': 31,
    'ye': 2011,
    'submit': 'Yes'
  }

  request = urllib2.Request(NASA_URL, urllib.urlencode(params))
  response = urllib2.urlopen(request)
  lines = response.read().strip().split("\n")
  
  cur = conn.cursor()

  # Does this sattelite have a location?
  cur.execute("SELECT locid from location WHERE lat = %s AND lng = %s AND sourceid = 'sat';", (lat, lng))
  location = cur.fetchone()
  
  if location is None:
    cur.execute("INSERT INTO location (sourceid, lat, lng) VALUES ('sat', %s, %s) RETURNING locid;", (lat, lng))
    conn.commit()
    location = cur.fetchone()
  
  locid = location[0]      
  
  for data in lines[6:]:
    data = data.split(None)
    date = datetime.date(int(data[0]), 1, 1) + datetime.timedelta(int(row[1]) - 1)
    
    cur.execute("INSERT INTO geodata (locid, date, solarradiation, tempmax, tempmin, tempmedian, rain, wind, dewpoint, humidity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
      (locid, date, data[2], data[3], data[4], data[8], data[5], data[6], data[7], data[9]))
    conn.commit()
  
  conn.close()
  
if __name__ == "__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:], "h")
  except getopt.GetoptError, err:
    print str(err)
    usage(1)

  for o, a in opts:
    if o == "-h": usage()
    else: assert False, "unhandled option"

  reader = csv.reader(open('grid-sample-unique.csv', 'rU'), delimiter=',')
  reader.next()
  
  for row in reader:
    print("Fetching weather data for lat=%s, lng=%s" %(row[0], row[1]))
    fetch_nasa_data(row[0], row[1])
