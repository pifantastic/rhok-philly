#!/usr/bin/python
# For now, this hardcodes the sat data in fetch_nasa_data(). We should
# parameterise this.

"""
Data Importer v%(VERSION)s
 
Synopsis: import.py

	-h  This help message
	-s  Import satellite data
	-g  Import ground data
	-a  Register areas only
	-c  Create database
	
	Requires Python 2.7
"""

from geodb import *
import os, sys, urllib, urllib2, getopt, psycopg2, csv, datetime, config, glob, subprocess
from dbutils import *
if sys.version < '2.7':
  print "Requires Python 2.7! You have ", sys.version
  sys.exit(8)

VERSION = '0.9'
IMPORT_SAT = False
IMPORT_GROUND = False
AREAS_ONLY = False
CREATE_DB = False
DAYS_IMPORT = 365 * 2 # Temporarily limiting to the first two years of data because there's so much

def usage(exit_code=0): 
  print __doc__ % globals()
  sys.exit(exit_code)

def fetch_nasa_data(lat=10, lng=10):  
  NASA_URL = 'http://earth-www.larc.nasa.gov/cgi-bin/cgiwrap/solar/agro.cgi?email=agroclim@larc.nasa.gov'

  # Original: 1983-2011
  # Now: 1989-1990
  params = {
    'email': 'agroclim@larc.nasa.gov',
    'step': 1,
    'lat': lat,
    'lon': lng,
    'ms': 1,
    'ds': 1,
    'ys': 1989,
    'me': 12,
    'de': 31,
    'ye': 1990,
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

  for data in lines[6:]:
    data = data.split(None)
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

    #cur.execute("INSERT INTO geodata (locid, date, solarradiation, tempmax, tempmin, tempmedian, rain, wind, dewpoint, humidity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
    #  (locid, date, data[2], data[3], data[4], data[8], data[5], data[6], data[7], data[9]))
    #conn.commit()

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

def parse_ground_dbf(dbf_path):
  return subprocess.check_output(["dbfxtrct", "-i%s" %(dbf_path)]).split()

def import_ground_dbf(dbfile):
	print "DBF Parser Parsing file " + dbfile
	tempmax_fieldid = get_fieldid_for_field("tempmax")
	tempmin_fieldid = get_fieldid_for_field("tempmin")
	rain_fieldid    = get_fieldid_for_field("rain")
	# First we must correct for a numbering oddity (probably)
	stationid = int(dbfile.split("_")[-1].split(".")[0]) + 100
	locid = get_locid_from_stationid(str(stationid))
	if(locid == None):
		print "No station location with station id " + stationid
	else:
		if(dbfile.startswith("TMP_")): # Temperature data
			dbf_string_lines = parse_ground_dbf(dbfile)
			for j in range (len(dbf_string_lines)):
				datalist = dbf_string_lines[j].split(",")
				tsid = get_geotsid(datalist[0], locid)
				set_geodata_by_fieldid(tsid, tempmax_fieldid, datalist[1])
				set_geodata_by_fieldid(tsid, tempmin_fieldid, datalist[2])

		elif(dbfile.startswith("PCP_")): # Precipitation data
			dbf_string_lines = parse_ground_dbf(dbfile)
			for j in range (len(dbf_string_lines)):
				datalist = dbf_string_lines[j].split(",")
				tsid = get_geotsid(datalist[0], locid)
				set_geodata_by_fieldid(tsid, rain_fieldid, datalist[1])
		else:
			print "Ignoring file " + dbfile

def import_csv_data(sep, fname, loctype):
	print "CSV parser parsing file " + fname
	tempmax_fieldid = get_fieldid_for_field("tempmax")
	tempmin_fieldid = get_fieldid_for_field("tempmin")
	rain_fieldid    = get_fieldid_for_field("rain")
	stationid = int(fname.split("_")[-1].split(".")[0]) + 100
	locid = get_locid_from_stationid(str(stationid))
	if(locid == None):
		print "No station location with station id " + stationid
	else:
		if(fname.startswith("TMP_")): # Temperature data
			reader = csv.DictReader(open(fname,'rb')) # We require fields (and header): date,tempmax,tempmin
			for row in reader:
				tsid = get_geotsid(row["date"], locid)
				set_geodata_by_fieldid(tsid, tempmax_fieldid, row["tempmax"])
				set_geodata_by_fieldid(tsid, tempmin_fieldid, row["tempmin"])
		elif(fname.startswith("PCP_")): # Precipitation data
			reader = csv.DictReader(open(fname,'rb')) # We require fields (and header): date, rain
			for row in reader:
				tsid = get_geotsid(row["date"], locid)
				set_geodata_by_fieldid(tsid, rain_fieldid, row["rain"])
		else:
			print "Ignoring file " + fname

def import_csv_data_two_underscores(sep, fname, loctype):
	''' Just like the above but handles files with TYPE_AREA_FILEID form. Also handles paths better '''
	print "CSV parser parsing file " + fname + " loctype=" + loctype + " sep=[" + sep + "]"
	fname_lastpart  = fname.split("/")[-1]
	tempmax_fieldid = get_fieldid_for_field("tempmax")
	tempmin_fieldid = get_fieldid_for_field("tempmin")
	rain_fieldid    = get_fieldid_for_field("rain")
	stationid = int(fname.split("_")[-2].split(".")[0]) + 100
	locid = get_locid_from_stationid(str(stationid))
	if(locid == None):
		print "No station location with station id " + stationid
	else:
		if(fname_lastpart.startswith("TMP_")): # Temperature data
			reader = csv.DictReader(open(fname, 'rb')) # We require fields (and header): date,max,min
			for row in reader:
				tsid = get_geotsid(row["DATE"], locid)
				set_geodata_by_fieldid(tsid, tempmax_fieldid, row["MAX"])
				set_geodata_by_fieldid(tsid, tempmin_fieldid, row["MIN"])
		elif(fname_lastpart.startswith("PCP_")): # Precipitation data
			reader = csv.DictReader(open(fname,'rb')) # We require fields (and header): date, rain
			for row in reader:
				tsid = get_geotsid(row["date"], locid)
				set_geodata_by_fieldid(tsid, rain_fieldid, row["rain"])
		else:
			print "Ignoring file " + fname



# import xlrd
# Note that this is CC-BY-NC, and may have license implications!

def import_ground_xls(fname):
	print "XLS parser parsing file " + fname
	tempmax_fieldid = get_fieldid_for_field("tempmax")
	tempmin_fieldid = get_fieldid_for_field("tempmin")
	rain_fieldid    = get_fieldid_for_field("rain")
	stationid = int(fname.split("_")[-1].split(".")[0]) + 100
	locid = get_locid_from_stationid(str(stationid))
	if(locid == None):
		print "No station location with station id " + stationid
	else:
		if(fname.startswith("TMP_")): # Temperature data
			xlrd.open_workbook(fname)
		elif(fname.startswith("PCP_")): # Precipitation data
			wb = xlrd.open_workbook(fname)
			sheet = wb.sheets()[0]
			# FIXME - NOT Done. How will these things be formatted?
		else:
			print "Ignoring file " + fname


def insert_ground_data():
	temperature_files = glob.glob(config.GROUNDDATAPATH + "TMP_*.dbf")
	temperature_files.sort()
	for filename in temperature_files:
		import_ground_dbf(dbfile)
	precip_files = glob.glob(config.GROUNDDATAPATH + "PCP_*.dbf")
	precip_files.sort()
	for filename in precip_files:
		import_ground_dbf(dbfile)
	

'''
def OLD_insert_ground_data():
  # Split the file-specific code off into import_ground_dbf() so other code
  # can call that.

  temperature_files = glob.glob(config.GROUNDDATAPATH + "TMP_*.dbf")
  temperature_files.sort()
  dbconn = opendb()

  tempmax_fieldid = get_fieldid_for_field("tempmax")
  tempmin_fieldid = get_fieldid_for_field("tempmin")

  for filename in temperature_files:
    print filename, "-->" 
    source_num = int(filename.split("_")[-1].split(".")[0]) + 100
    # The files are named with numbers that don't line up with weather station
    # id numbers. We have to add 100 to the numbers in the file names so we
    # can match the station id numbers specified in the ground location csv.
    cur = dbconn.cursor()
    cur.execute("SELECT locid FROM location WHERE stationid = %s;", (str(source_num),))
    result = cur.fetchone()
    if result==None:
      print "No station location with station id", source_num
    else:
      file_locid = result[0]

      dbf_string_lines = parse_ground_dbf(filename)
      #for line in dbf_string_lines:
	#datalist = line.split(",")
      for j in range(DAYS_IMPORT): # Temporarily limiting to the first two years of data because there's so much
	datalist = dbf_string_lines[j].split(",")
	tsid = get_geotsid(datalist[0], file_locid)

	set_geodata_by_fieldid(tsid, tempmax_fieldid, datalist[1])
	set_geodata_by_fieldid(tsid, tempmin_fieldid, datalist[2])
	#curs = dbconn.cursor()
	#curs.execute(
        #    "INSERT INTO geodata(locid,date,tempmax,tempmin) VALUES (%s,%s,%s,%s);",\
        #    (file_locid,datalist[0],datalist[1],datalist[2]))
	#dbconn.commit()
        
  precip_files = glob.glob(config.GROUNDDATAPATH + "PCP_*.dbf")
  precip_files.sort()
  dbconn = opendb()

  rain_fieldid= get_fieldid_for_field("rain")

  for filename in precip_files:
    print filename, "-->"
    source_num = int(filename.split("_")[-1].split(".")[0]) + 100
    # The files are named with numbers that don't line up with weather station
    # id numbers. We have to add 100 to the numbers in the file names so we
    # can match the station id numbers specified in the ground location csv.
    cur = dbconn.cursor()
    cur.execute("SELECT locid FROM location WHERE stationid = %s;", (str(source_num),))
    result = cur.fetchone()
    if result==None:
      print "No station location with station id", source_num
    else:
      file_locid = result[0]

      dbf_string_lines = parse_ground_dbf(filename)
      #for line in dbf_string_lines:
	#datalist = line.split(",")
      for j in range(DAYS_IMPORT): 
	datalist = dbf_string_lines[j].split(",") # We should gracefully handle if the dbf is malformed
	tsid = get_geotsid(datalist[0], file_locid)
	set_geodata_by_fieldid(tsid, rain_fieldid, datalist[1])

	#curs = dbconn.cursor()
	#curs.execute(
        #    "INSERT INTO geodata(locid,date,rain) VALUES (%s,%s,%s);",\
        #    (file_locid,datalist[0],datalist[1]))
	#dbconn.commit()    
'''

###################################################
# main()
#
# Not used when this is used as a library
###################################################


if __name__ == "__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hgsca")
  except getopt.GetoptError, err:
    print str(err)
    usage(1)

  for o, a in opts:
    if o == "-h": usage()
    elif o == "-g": IMPORT_GROUND = True
    elif o == "-s": IMPORT_SAT = True
    elif o == "-c": CREATE_DB = True
    elif o == "-a": AREAS_ONLY = True
    else: assert False, "unhandled option"

  if CREATE_DB:
    os.system("createdb %s" % (config.DBNAME))
    os.system("psql -d %s -f %s" % (config.DBNAME, 'schema.sql')) # Must be in the current dir :(

  if IMPORT_SAT:
    reader = csv.reader(open('data/grid-sample-unique.csv', 'rU'), delimiter=',')
    reader.next()

    if(AREAS_ONLY):
      for row in reader:
        locid = sat_getlocid(row[0],row[1])

    if(not(AREAS_ONLY)):  
      for row in reader:
        print("Fetching weather data for lat=%s, lng=%s" %(row[0], row[1]))
        fetch_nasa_data(row[0], row[1])
  
  if IMPORT_GROUND:
    insert_ground_loc_csv('data/local_weather.csv')
    if(not(AREAS_ONLY)):
      insert_ground_data()
