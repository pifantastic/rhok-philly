#!/usr/bin/python
# For now, this hardcodes the sat data in fetch_nasa_data(). We should
# parameterise this.

"""
Data Importer v%(VERSION)s
 
Synopsis: import.py

	-h  This help message
	-s  Import satellite data
	
	Requires Python 2.7
"""

from geodb import *
import os, sys, urllib, urllib2, getopt, psycopg2, csv, datetime, config, glob, subprocess
from dbutils import *
if sys.version < '2.7':
  print "Requires Python 2.7! You have ", sys.version
  sys.exit(8)

VERSION = '0.9'
IMPORT_SAT = True

def usage(exit_code=0): 
  print __doc__ % globals()
  sys.exit(exit_code)

def fetch_nasa_data_for_daterange(lat, lng, yearstart=1989, yearend=1990, monthstart=1, monthend=12, daystart=1, dayend=31):  
  NASA_URL = 'http://earth-www.larc.nasa.gov/cgi-bin/cgiwrap/solar/agro.cgi?email=agroclim@larc.nasa.gov'

  # Original: 1983-2011
  # Now: 1989-1990
  params = {
    'email': 'agroclim@larc.nasa.gov',
    'step': 1,
    'lat': lat,
    'lon': lng,
    'ms': monthstart,
    'ds': daystart,
    'ys': yearstart,
    'me': monthend,
    'de': dayend,
    'ye': yearend,
    'submit': 'Yes'
  }
# Is a bulk-fetch the best way to do this?
# Also: This should be modified so if there already is data, it will not try to import it again.
#	That same code probably will handle incremental imports.

  request = urllib2.Request(NASA_URL, urllib.urlencode(params))
  response = urllib2.urlopen(request)
  lines = response.read().strip().split("\n")
  conn = opendb() 
  cur = conn.cursor()

  locid = sat_getlocid(lat,lng)
  solarradiation_fieldid 	= get_fieldid_for_field("solarradiation")
  tempmax_fieldid 		= get_fieldid_for_field("tempmax")
  tempmin_fieldid		= get_fieldid_for_field("tempmin")
  tempmedian_fieldid		= get_fieldid_for_field("tempmedian")
  rain_fieldid			= get_fieldid_for_field("rain")
  wind_fieldid			= get_fieldid_for_field("wind")
  dewpoint_fieldid		= get_fieldid_for_field("dewpoint")
  humidity_fieldid		= get_fieldid_for_field("humidity")

  for data in lines:
    data = data.split(None)
    print "[" + str(data) + "]"
    if((len(data) == 0) or (data[0].startswith("!") ) or (data[0].startswith("@") ) or (data[0].startswith("*")) or (data[0] == "NASA") ):
	continue
    # print("Fetching for " + data[0] + " plus " + str(int(data[1]) - 1) + "\n")
    date = datetime.date(int(data[0]), 1, 1) + datetime.timedelta(days=int(data[1]) - 1)
    geots = get_geotsid(date, locid)

    set_geodata_by_fieldid(geots, solarradiation_fieldid, 	data[2])
    set_geodata_by_fieldid(geots, tempmax_fieldid, 		data[3])
    set_geodata_by_fieldid(geots, tempmin_fieldid, 		data[4])
    set_geodata_by_fieldid(geots, tempmedian_fieldid, 		data[8])
    set_geodata_by_fieldid(geots, rain_fieldid,			data[5])
    set_geodata_by_fieldid(geots, wind_fieldid,			data[6])
    set_geodata_by_fieldid(geots, dewpoint_fieldid, 		data[7])
    set_geodata_by_fieldid(geots, humidity_fieldid, 		data[9])

###################################################
# main()
#
# Not used when this is used as a library
###################################################


if __name__ == "__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:], "h", ['daystart=', 'dayend=', 'monthstart=', 'monthend=', 'yearstart=', 'yearend='])
  except getopt.GetoptError, err:
    print str(err)
    usage(1)

  daystart = 1
  dayend = 31
  monthstart = 1
  monthend = 12
  yearstart = 1989
  yearend = 1990

  for o, a in opts:
    if o == "-h": usage()
    elif o == "--daystart":
	daystart = a
    elif o == "--dayend":
	dayend = a
    elif o == "--monthstart":
	monthstart = a
    elif o == "--monthend":
	monthend = a
    elif o == "--yearstart":
	yearstart = a
    elif o == "--yearend":
	yearend = a
    else: assert False, "unhandled option"

  if IMPORT_SAT:
    reader = csv.reader(open('data/grid-sample-unique.csv', 'rU'), delimiter=',')
    reader.next()

    for row in reader:
      print("Fetching weather data for lat=%s, lng=%s, ys=%s ye=%s" %(row[0], row[1], yearstart, yearend))
      fetch_nasa_data_for_daterange(row[0], row[1], yearstart, yearend, monthstart, monthend, daystart, dayend)

