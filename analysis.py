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

def get_month_tempmax_averages(month):
  dbconn = psycopg2.connect(PGSQL_CONN_STRING)
  curs = dbconn.cursor()
  # Get average maximum temperature (from 2 years of data) for given month. 
  # Tuples will be lat, long, location id, month number, and average (maximum) temperature 
  curs.execute("SELECT lat,lng,avgtmpmax FROM "+\
    "(SELECT locid,EXTRACT(month FROM geodata.date) "+\
    "AS monthtime,AVG(tempmax) AS avgtmpmax FROM geodata "+\
    "WHERE locid IN (SELECT locid FROM location WHERE sourceid='ground') "+\
    "GROUP BY EXTRACT(month FROM geodata.date),locid ORDER BY locid,monthtime) "+\
    "AS myquery JOIN location ON location.locid=myquery.locid AND monthtime=%s", (month,))
  return curs.fetchall()
    

def graph_monthly_temp(month_num):
  # Tuples will be lat, long, location id, month number, and average (maximum) temperature 
  result_tuples = get_month_tempmax_averages(month_num) 
  lats, longs, temps = zip(*result_tuples)
  
  f_lats = [float(item) for item in lats]
  f_longs = [float(item) for item in longs]
  f_temps = [float(item) for item in temps]
  print f_temps
  
  # define grid.
  #yi = np.linspace(-22.0,-10.0,100) # Based on range of latitudes for the country data
  #xi = np.linspace(-70.0,-57.0,100) # Based on longitudes (East/West)
  yi = np.linspace(-30.0,0.0,100) # Based on range of latitudes for the country data
  xi = np.linspace(-70.0,-40.0,100) # Based on longitudes (East/West)  


  # grid the data.
  zi = griddata(f_longs,f_lats,f_temps,xi,yi,interp='linear')
  # contour the gridded data, plotting dots at the nonuniform data points.
  CS = plt.contour(xi,yi,zi,15,linewidths=0.5,colors='k')
  CS = plt.contourf(xi,yi,zi,15,cmap=plt.cm.jet)
  plt.colorbar() # draw colorbar
  
  # plot data points.
  plt.scatter(f_longs,f_lats,marker='o',c='b',s=len(f_lats))
  plt.xlim(-22,-10)
  plt.ylim(-70,-57)
  plt.title('griddata test')
  plt.show()

graph_monthly_temp(4)