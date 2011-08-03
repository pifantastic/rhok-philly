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
	curs.execute("")

def latestCompleteData(datatype):
	"""Returns the latest date for which all sources have entries 
	for given datatype."""
	conn = opendb()
	curs = conn.cursor()
	curs.execute("")

