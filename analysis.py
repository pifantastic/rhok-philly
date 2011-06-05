"""
Analysis of weather data from satellite and ground sources.
Goal: Generate contoured maps of the data plotted by geographical location.
"""

import config, psycopg2
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
import numpy as np

PGSQL_CONN_STRING = "dbname=%s user=%s password=%s" % (config.DBNAME, config.DBUSER, config.DBPASS)

def get_monthly_tempmax_averages():
  dbconn = psycopg2.connect(PGSQL_CONN_STRING)
  curs = dbconn.cursor()
  # Get average maximum temperature (from 2 years of data) for every month. 
  # Tuples will be lat, long, location id, month number, and average (maximum) temperature 
  curs.execute("SELECT lat,lng,myquery.locid,monthtime,avgtmpmax FROM "+\
    "(SELECT locid,EXTRACT(month FROM geodata.date) "+\
    "AS monthtime,AVG(tempmax) AS avgtmpmax FROM geodata "+\
    "WHERE locid IN (SELECT locid FROM location WHERE sourceid='ground') "+\
    "GROUP BY EXTRACT(month FROM geodata.date),locid ORDER BY locid,monthtime) "+\
    "AS myquery JOIN location ON location.locid=myquery.locid;")
  return curs.fetchall()
 

def graph_monthly_temp(tuple_list):
 # Tuples will be lat, long, location id, month number, and average (maximum) temperature 
 
 # define grid.
  xi = np.linspace(-2.1,2.1,100)
  yi = np.linspace(-2.1,2.1,200)
  
  # grid the data.
  zi = griddata(x,y,z,xi,yi,interp='linear')
  # contour the gridded data, plotting dots at the nonuniform data points.
  CS = plt.contour(xi,yi,zi,15,linewidths=0.5,colors='k')
  CS = plt.contourf(xi,yi,zi,15,cmap=plt.cm.jet)
  plt.colorbar() # draw colorbar
  # plot data points.
  plt.scatter(x,y,marker='o',c='b',s=5,zorder=10)
  plt.xlim(-2,2)
  plt.ylim(-2,2)
  plt.title('griddata test')
  plt.show()

get_monthly_tempmax_averages()