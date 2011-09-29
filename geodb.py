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
	curs.execute("SELECT locid FROM location WHERE stationid = %s;", (stationid,))
	return curs.fetchone()[0]

def set_geodata_by_fieldid(geotsid, fieldid, value):
	"""Arguments: geotsid, fieldid, value of data to insert or update."""
	conn = opendb()
	curs = conn.cursor()
	curs.execute("SELECT geovalueid FROM geovalue WHERE geotsid=%s AND geofieldid=%s;", (geotsid, fieldid)) # Does this data exist?
	exists = curs.rowcount
	if(exists == 0):
		curs.execute("INSERT INTO geovalue (geotsid, geofieldid, geoval) VALUES (%s, %s, %s);", (geotsid,fieldid,value))
	else:
		curs.execute("UPDATE geovalue SET geoval=%s WHERE geotsid=%s AND geofieldid=%s;", (value, geotsid, fieldid))
	conn.commit()

def get_geotsid(date, locid):
	""" Arguments: date, locid
	Returns: geotsid, an integer which is the unique identifier for a 
	location in time and space.
	If there is not yet a geotsid for the given information, this function
	generates a new one."""
	conn = opendb()
	curs = conn.cursor()
	curs.execute("SELECT geotsid FROM geotimespace WHERE date=%s AND locid=%s;", (date, locid))
	shouldbeone = curs.rowcount
	if(shouldbeone == 1):
		return curs.fetchone()[0]
	else: # We didn't get a geotsid, so let's make one
		curs.execute("INSERT INTO geotimespace(date,locid) VALUES (%s, %s) RETURNING geotsid;", (date, locid))
		conn.commit()
		return curs.fetchone()[0]

def sat_getlocid(lat, lng):
	"""Returns locid (an integer) for the given latitude and longitude."""
	conn = opendb()
	curs = conn.cursor()
	curs.execute("SELECT locid FROM location WHERE lat = %s AND lng = %s AND sourceid = 'sat';", (lat, lng))
	shouldbeone = curs.rowcount
	if(shouldbeone > 0):
		return curs.fetchone()[0]
	else:
		curs.execute("INSERT INTO location (sourceid, lat, lng) VALUES ('sat', %s, %s) RETURNING locid;", (lat, lng))
		conn.commit()
		return curs.fetchone()[0]

def station_ensure_locid(lat, lng, stationid, locname):
	"""Arguments: latitude, logitude, stationid, location name
	Returns the locid for the given station information, creating a new
	locid if one does not already exist."""
	conn = opendb()
	curs = conn.cursor()
	curs.execute("SELECT locid FROM location WHERE lat = %s AND lng = %s AND sourceid = 'ground';", (lat, lng))
	shouldbeone = curs.rowcount
	if(shouldbeone > 0):
		return curs.fetchone()[0]
	else:
		curs.execute("INSERT INTO location(sourceid, lat, lng, stationid, locname) VALUES (%s, %s, %s, %s, %s) RETURNING locid;", ("ground", lat, lng, stationid, locname))
		conn.commit()
		return curs.fetchone()[0]

