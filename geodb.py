#!/usr/bin/python

# Keep shared database code here

import config,psycopg2
PGSQL_CONN_STRING = "dbname=%s user=%s password=%s" % (config.DBNAME, config.DBUSER, config.DBPASS)

def get_fieldid_for_field(fieldname):
  conn = psycopg2.connect(PGSQL_CONN_STRING)
  cur = conn.cursor()
  cur.execute("SELECT fieldid FROM geofield WHERE fieldname=%s;", (fieldname,))
  returner = cur.fetchone()[0] # TODO Handle if we don't get one! Make a new one?
  return returner 
