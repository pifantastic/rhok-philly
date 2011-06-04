#!/usr/bin/python

"""
NASA Data Importer v%(VERSION)s
 
Synopsis: nasa.py

	-h  This help message
	-l  CSV file containing station data
	
"""

import sys, urllib, urllib2, getopt, psycopg2

VERSION = '0.1'
LOAD_DATA = False
PGSQL_CONN_STRING = "dbname=%s user=%s password=%s" % ('', '', '')

def usage(exit_code=0): 
  print __doc__ % globals()
  sys.exit(exit_code)

def fetch_nasa_data(lat=10, lon=10):
  NASA_URL = 'http://earth-www.larc.nasa.gov/cgi-bin/cgiwrap/solar/agro.cgi?email=agroclim@larc.nasa.gov'

  params = {
    'email': 'agroclim@larc.nasa.gov',
    'step': 1,
    'lat': lat,
    'lon': lon,
    'ms': 1,
    'ds': 1,
    'ys': 2011,
    'me': 12,
    'de': 31,
    'ye': 2011,
    'submit': 'Yes'
  }

  request = urllib2.Request(NASA_URL, urllib.urlencode(params))
  response = urllib2.urlopen(request)
  lines = response.read().strip().split("\n")
  headers = lines[5].split(None)
  
  conn = psycopg2.connect(PGSQL_CONN_STRING)
  cur = conn.cursor()
  
  for data in lines[6:1]:
    cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))
  
  return lines[6:]


if __name__ == "__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hl")
  except getopt.GetoptError, err:
    print str(err)
    usage(1)

  for o, a in opts:
    if o == "-h":
      usage()
    elif o == '-l':
      LOAD_DATA = True
    else:
      assert False, "unhandled option"
  
  fetch_nasa_data()
