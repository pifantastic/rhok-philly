#!/usr/bin/python
"""  geodb.py contains database functions related to the climate data project, 
but not involved in the analysis.py process. 
dbutils.py is for generic database functions not specific to this project."""

from dbutils import *

def yearsOfData():
	"""Returns an integer number of years of data available in the database."""
	conn = opendb()
	curs = conn.cursor()
	curs.execute("SELECT COUNT(DISTINCT date_part('year', date)) FROM geotimespace;")
	return curs.fetchone()[0]

def earliestData():
	"""Returns the earliest date for which data is available. 
	Not sensitive to source type or data type."""
	conn = opendb()
	curs = conn.cursor()
	curs.execute("SELECT date_part('year', date) AS geoyear FROM geotimespace ORDER BY geoyear LIMIT 1;")
	return curs.fetchone()[0]

def latestData():
	"""Returns the most recent date for which data is available.
	Not sensitive to source type or data type."""
	conn = opendb()
	curs = conn.cursor()
	curs.execute("SELECT date_part('year', date) AS geoyear FROM geotimespace ORDER BY geoyear DESC LIMIT 1;")
	return curs.fetchone()[0]

def earliestSourceData(source,datatype):
	"""Returns the date of the earliest data entry available for 
	given source and data type."""
	conn = opendb()
	curs = conn.cursor()
	curs.execute("SELECT date_part('year', date) AS geoyear FROM geotimespace WHERE locid IN (SELECT locid FROM location WHERE sourceid='%s') ORDER BY geoyear LIMIT 1;", (datatype,))
	return curs.fetchone()[0]

def latestSourceData(source,datatype):
	"""Returns the date of the most recent data entry available 
	for given source and data type."""
	conn = opendb()
	curs = conn.cursor()
	curs.execute("SELECT date_part('year', date) AS geoyear FROM geotimespace WHERE locid IN (SELECT locid FROM location WHERE sourceid='%s') ORDER BY geoyear DESC LIMIT 1;", (datatype,))
	return curs.fetchone()[0]

def earliestCompleteData(datatype):
	"""Returns the earliest date for which all sources have entries 
	for given datatype."""
	conn = opendb()
	curs = conn.cursor()
	curs.execute("SELECT satdates FROM (SELECT DISTINCT date_part('year',date) FROM geotimespace NATURAL JOIN location WHERE location.sourceid='sat') AS satdates JOIN (SELECT DISTINCT date_part('year',date)  FROM geotimespace NATURAL JOIN location WHERE location.sourceid='ground') AS gnddates ON satdates = gnddates ORDER BY satdates LIMIT 1;")
	return curs.fetchone()[0]

def latestCompleteData(datatype):
	"""Returns the latest date for which all sources have entries 
	for given datatype."""
	conn = opendb()
	curs = conn.cursor()
	curs.execute("SELECT satdates FROM (SELECT DISTINCT date_part('year',date) FROM geotimespace NATURAL JOIN location WHERE location.sourceid='sat') AS satdates JOIN (SELECT DISTINCT date_part('year',date)  FROM geotimespace NATURAL JOIN location WHERE location.sourceid='ground') AS gnddates ON satdates = gnddates ORDER BY satdates DESC LIMIT 1;")
	return curs.fetchone()[0]

##########################
# From import.py, with love

def get_locid_from_stationid(stationid):
	''' Given a string stationid, return the locationid '''
	conn = opendb()
	curs = conn.cursor()
	cur.execute("SELECT locid FROM location WHERE stationid = %s;", (str(source_num),))
	return curs.fetchone()[0]

def set_geodata_by_fieldid(geotsid, fieldid, value):
	conn = opendb()
	cur = conn.cursor()
	cur.execute("SELECT geovalueid FROM geovalue WHERE geotsid=%s AND geofieldid=%s;", (geotsid, fieldid)) # Does this data exist?
	exists = cur.rowcount
	if(exists == 0):
		cur.execute("INSERT INTO geovalue (geotsid, geofieldid, geoval) VALUES (%s, %s, %s);", (geotsid,fieldid,value))
	else:
		cur.execute("UPDATE geovalue SET geoval=%s WHERE geotsid=%s AND geofieldid=%s;", (value, geotsid, fieldid))
	conn.commit()

def get_geotsid(date, locid):
	conn = opendb()
	cur = conn.cursor()
	cur.execute("SELECT geotsid FROM geotimespace WHERE date=%s AND locid=%s;", (date, locid))
	shouldbeone = cur.rowcount
	if(shouldbeone == 1):
		return cur.fetchone()[0]
	else: # We didn't get a geotsid, so let's make one
		cur.execute("INSERT INTO geotimespace(date,locid) VALUES (%s, %s) RETURNING geotsid;", (date, locid))
		conn.commit()
		return cur.fetchone()[0]

def sat_getlocid(lat, lng):
	conn = opendb()
	cur = conn.cursor()
	cur.execute("SELECT locid FROM location WHERE lat = %s AND lng = %s AND sourceid = 'sat';", (lat, lng))
	shouldbeone = cur.fetchone()
	if(shouldbeone > 0):
		return cur.fetchone()[0]
	else:
		cur.execute("INSERT INTO location (sourceid, lat, lng) VALUES ('sat', %s, %s) RETURNING locid;", (lat, lng))
		conn.commit()
		return cur.fetchone()[0]

def station_ensure_locid(lat, lng, stationid, locname):
	conn = opendb()
	cur = conn.cursor()
	cur.execute("SELECT locid FROM location WHERE lat = %s AND lng = %s AND sourceid = 'ground';", (lat, lng))
	shouldbeone = cur.fetchone()
	if(shouldbeone > 0):
		returner = cur.fetchone()[0]
		return returner
	else:
		cur.execute("INSERT INTO location(sourceid, lat, lng, stationid, locname) VALUES (%s, %s, %s, %s, %s) RETURNING locid;", ("ground", lat, lng, stationid, locname))
		conn.commit()
		return cur.fetchone()[0]

