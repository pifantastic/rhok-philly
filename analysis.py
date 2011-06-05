"""
Analysis of weather data from satellite and ground sources.
Goal: Generate contoured maps of the data plotted by geographical location.
"""

import config, psycopg2
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
import numpy as np

PGSQL_CONN_STRING = "dbname=%s user=%s password=%s" % (config.DBNAME, config.DBUSER, config.DBPASS)

def get_data_by_date(querydate):
  dbconn = psycopg2.connect(PGSQL_CONN_STRING)
  curs = dbconn.cursor()
  curs.execute("SELECT (locid,tempmax) FROM geodata WHERE date = %s AND locid IN (SELECT locid FROM location WHERE sourceid='ground') ORDER BY locid;", (querydate,))
  curs.fetchall()
  print curs
  
get_data_by_date("89-01-01")