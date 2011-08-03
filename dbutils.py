#!/usr/bin/python
''' Keep database code that would be shared between projects here '''

import config,psycopg2

def get_fieldid_for_field(fieldname):
  conn = opendb()
  cur = conn.cursor()
  cur.execute("SELECT fieldid FROM geofield WHERE fieldname=%s;", (fieldname,))
  returner = cur.fetchone()[0] # TODO Handle if we don't get one! Make a new one?
  return returner

def opendb():
	''' Give us a database connection. Configured by data from the config module. '''
	conn = psycopg2.connect(get_dbconn_string())
	return conn

def get_dbconn_string():
	''' Based on the data defined in the config module, return us a psycopg2 connection string '''
	returner = ""
	if(('config.DBUSER' in globals() ) and (config.DBUSER != None)):
		returner = "dbname=%s user=%s password=%s" % (config.DBNAME, config.DBUSER, config.DBPASS)
	else:
		returner = "dbname=%s" % (config.DBNAME)
	return returner
