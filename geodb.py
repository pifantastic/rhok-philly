#!/usr/bin/python

# Keep shared database code here

import config,psycopg2

def get_fieldid_for_field(fieldname):
  conn = psycopg2.connect(get_dbconn_string())
  cur = conn.cursor()
  cur.execute("SELECT fieldid FROM geofield WHERE fieldname=%s;", (fieldname,))
  returner = cur.fetchone()[0] # TODO Handle if we don't get one! Make a new one?
  return returner

def get_dbconn_string():
	returner = ""
	if(('config.DBUSER' in globals() ) and (config.DBUSER != None)):
		returner = "dbname=%s user=%s password=%s" % (config.DBNAME, config.DBUSER, config.DBPASS)
	else:
		returner = "dbname=%s" % (config.DBNAME)
	return returner
