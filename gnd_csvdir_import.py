#!/usr/bin/python

"""
Data Importer v%(VERSION)s
 
Synopsis: gnd_csvdir_import.py DIR

	Requires Python 2.7
"""

from geodb import *
import os, sys, urllib, urllib2, getopt, psycopg2, csv, datetime, config, glob, subprocess
from dbutils import *
if sys.version < '2.7':
  print "Requires Python 2.7! You have ", sys.version
  sys.exit(8)

VERSION = '0.9'

def usage(exit_code=0): 
  print __doc__ % globals()
  sys.exit(exit_code)

def insert_ground_loc_csv(csv_path):
  data = []
  for row in csv.reader(open(csv_path)):
    data.append(row)

  header = data.pop(0)    

  station_ids, station_names, lats, longs = zip(*data)

  dbconn = opendb()
  curs = dbconn.cursor()

  for i in range(len(station_ids)):
    station_ensure_locid(lats[i], longs[i], station_ids[i].split(".")[0], station_names[i]) 
    #    curs.execute(
    #      "INSERT INTO location(sourceid,lat,lng,stationid,locname)"\
    #      "VALUES (%s,%s,%s,%s,%s);",\
    #      ("ground",lats[i],longs[i],station_ids[i].split(".")[0],station_names[i]))
      # Had to split station_ids at the decimal because string float needs to be an int.
      # Left it as a string int because the %s insertion expects a string anyway.
  dbconn.commit()

def import_csv_data(sep, fname):
	print "CSV parser parsing file " + fname
	tempmax_fieldid = get_fieldid_for_field("tempmax")
	tempmin_fieldid = get_fieldid_for_field("tempmin")
	rain_fieldid    = get_fieldid_for_field("rain")
	stationid = int(fname.split("_")[-1].split(".")[0]) + 100
	locid = get_locid_from_stationid(str(stationid))
	fname_short = fname.split("/")[-1]
	if(locid == None):
		print "No station location with station id " + stationid
	else:
		if(fname_short.startswith("TMP_")): # Temperature data
			csvhandle = open(fname, "rb")
			csvdialect = csv.Sniffer().sniff(csvhandle.read(1024))
			csvhandle.seek(0)
			reader = csv.DictReader(csvhandle) # We require fields (and header): date,tempmax,tempmin
			for row in reader:
				tsid = get_geotsid(date_csvtosql(row["DATE"]), locid)
				set_geodata_by_fieldid(tsid, tempmax_fieldid, row["MAX"])
				set_geodata_by_fieldid(tsid, tempmin_fieldid, row["MIN"])
		elif(fname_short.startswith("PCP_")): # Precipitation data
			csvhandle = open(fname, "rb")
			csvdialect = csv.Sniffer().sniff(csvhandle.read(1024))
			csvhandle.seek(0)
			reader = csv.DictReader(csvhandle) # We require fields (and header): date,tempmax,tempmin
			for row in reader:
				tsid = get_geotsid(date_csvtosql(row["DATE"]), locid)
				set_geodata_by_fieldid(tsid, rain_fieldid, row["RAIN"])
		else:
			print "Ignoring file " + fname

def insert_ground_data(datadir):
	print "Looking in " + datadir + "/*.csv"
	temperature_files = glob.glob(datadir + "/TMP_*.csv")
	temperature_files.sort()
	for filename in temperature_files:
		print "Parse: " + filename
		import_csv_data(",", filename)
	precip_files = glob.glob(datadir + "/PCP_*.csv")
	precip_files.sort()
	for filename in precip_files:
		import_csv_data(",", filename)
	

def date_csvtosql(slashdate):
	''' D/M/Y to Y-M-D '''
	month, day, year = slashdate.split("/")
	return year + "-" + month + "-" + day

###################################################
# main()
#
# Not used when this is used as a library
###################################################


if __name__ == "__main__":

  datadir = sys.argv[1]
  insert_ground_loc_csv('data/local_weather.csv')
  insert_ground_data(datadir)
