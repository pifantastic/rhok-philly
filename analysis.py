#!/usr/bin/python

"""
Analysis of weather data from satellite and ground sources.
Goal: Generate contoured maps of the data plotted by geographical location.
"""

import os
os.environ['HOME'] = '/tmp/' # To allow Matplotlib to run under cgi
os.environ['MPLCONFIGDIR'] = '/tmp/' 

import config, psycopg2, sys, getopt
from dbutils import *
from scipy.interpolate import griddata
import matplotlib 
matplotlib.use('Agg')  # This & second matplotlib import enable backend for SVG support
import matplotlib.pyplot as plt
import numpy as np

def usage(exit_code=0): 
  print __doc__ % globals()
  sys.exit(exit_code)

def get_daily_field_values(day,month,year,fieldname):
  ''' Get data for a specified field for a specific day. 
      Returned tuples will be lat, long, and value for that field.'''
  dbconn = opendb()
  curs = dbconn.cursor()

  fieldid = get_fieldid_for_field(fieldname)
  datefield = psycopg2.Date(year,month,day)
  curs.execute("SELECT lat,lng,geoval FROM geotimespace JOIN location ON geotimespace.locid=location.locid JOIN geovalue ON geotimespace.geotsid = geovalue.geotsid WHERE date=%s AND geofieldid=%s", (datefield,fieldid)) 
  # Could return geotimespace.locid if need be, but not right now.
  return curs.fetchall()

def get_monthly_field_averages(fieldname):
  dbconn = opendb()
  curs = dbconn.cursor()
  # Get average named field value (from 2 years of data) for every month. 
  # Tuples will be lat, long, location id, month number, and average for that field
  fieldid = get_fieldid_for_field(fieldname)

  curs.execute("SELECT lat,lng,myquery.locid,monthtime,avggeoval FROM " +\
    "(SELECT locid,EXTRACT(month FROM geotimespace.date) "+\
    "AS monthtime,AVG(geoval) AS avggeoval FROM geotimespace "+\
    "JOIN geovalue ON geovalue.geotsid = geotimespace.geotsid "+\
    "WHERE geofieldid=%s AND locid IN "+\
    "(SELECT locid FROM location WHERE sourceid = 'ground') "+\
    "GROUP BY EXTRACT(month FROM geotimespace.date),locid ORDER BY locid,monthtime) "+\
    "AS myquery JOIN location ON location.locid=myquery.locid;", (fieldid,))
  return curs.fetchall()

def get_month_field_averages(month,qtype,fieldname):
  """
  Inputs:
      month = numeric (1-12), what month you want
      qtype = 'sat' or 'ground'
      fieldname
  """

  dbconn = opendb()
  curs = dbconn.cursor()
  fieldid = get_fieldid_for_field(fieldname)
  # Get average named field value(from 2 years of data) for given month. 
  # Tuples will be lat, long, location id, month number, and average value for that field
  curs.execute("SELECT lat,lng,avggeoval FROM "+\
    "(SELECT locid,EXTRACT(month FROM geotimespace.date) "+\
    "AS monthtime,AVG(geoval) AS avggeoval FROM geotimespace "+\
    "JOIN geovalue ON geovalue.geotsid = geotimespace.geotsid "+\
    "WHERE geofieldid=%s AND locid IN (SELECT locid FROM location WHERE sourceid=%s) "+\
    "GROUP BY EXTRACT(month FROM geotimespace.date),locid ORDER BY locid,monthtime) "+\
    "AS myquery JOIN location ON location.locid=myquery.locid AND monthtime=%s", (fieldid,qtype,month))
  return curs.fetchall()

def get_monthly_tempmax_averages():
  return get_monthly_field_averages("tempmax")
  #dbconn = opendb()
  #curs = dbconn.cursor()
  # Get average maximum temperature (from 2 years of data) for every month. 
  # Tuples will be lat, long, location id, month number, and average (maximum) temperature 
  #curs.execute("SELECT lat,lng,myquery.locid,monthtime,avgtmpmax FROM "+\
  #  "(SELECT locid,EXTRACT(month FROM geodata.date) "+\
  #  "AS monthtime,AVG(tempmax) AS avgtmpmax FROM geodata "+\
  #  "WHERE locid IN (SELECT locid FROM location WHERE sourceid='ground') "+\
  #  "GROUP BY EXTRACT(month FROM geodata.date),locid ORDER BY locid,monthtime) "+\
  #  "AS myquery JOIN location ON location.locid=myquery.locid;")
  #return curs.fetchall()

def get_month_tempmax_averages(month,qtype):
  return get_month_field_averages(month,qtype,"tempmax")
  #"""
  #Inputs:
  #month = numeric (1-12), what month you want
  #qtype = 'sat' or 'ground'

  #"""
  #dbconn = opendb()
  #curs = dbconn.cursor()
  # Get average maximum temperature (from 2 years of data) for given month. 
  # Tuples will be lat, long, location id, month number, and average (maximum) temperature 
  #curs.execute("SELECT lat,lng,avgtmpmax FROM "+\
  #  "(SELECT locid,EXTRACT(month FROM geodata.date) "+\
  #  "AS monthtime,AVG(tempmax) AS avgtmpmax FROM geodata "+\
  #  "WHERE locid IN (SELECT locid FROM location WHERE sourceid=%s) "+\
  #  "GROUP BY EXTRACT(month FROM geodata.date),locid ORDER BY locid,monthtime) "+\
  #  "AS myquery JOIN location ON location.locid=myquery.locid AND monthtime=%s", (qtype,month))
  #return curs.fetchall()
    

def graph_result(result_tuples,filename):
  """ Tuples will be lat, long, and the desired data. 
  We need the filename to save the figure in. """
  lats, longs, temps = zip(*result_tuples)
  
  f_lats = [float(item) for item in lats]
  f_longs = [float(item) for item in longs]
  f_temps = [float(item) for item in temps]
  #print f_temps
  
  # define grid.
  yi = np.linspace(-22.0,-10.0,100) # Based on range of latitudes for the country data
  xi = np.linspace(-70.0,-57.0,100) # Based on longitudes (East/West)
	#  yi = np.linspace(-30.0,0.0,100) # Based on range of latitudes for the country data
	#  xi = np.linspace(-70.0,-40.0,100) # Based on longitudes (East/West)  

  # grid the data.
  zi = griddata((f_longs,f_lats),f_temps,(xi[None,:],yi[:,None]),method='linear')
  # contour the gridded data, plotting dots at the nonuniform data points.
  CS = plt.contour(xi,yi,zi,15,linewidths=0.5,colors='k')
  CS = plt.contourf(xi,yi,zi,15,cmap=plt.cm.jet)
  plt.colorbar() # draw colorbar
  
  # plot data points.
  plt.scatter(f_longs,f_lats,marker='+',c='b',s=len(f_lats))
  #plt.xlim(-22,-10)
  #plt.ylim(-70,-57)
  #plt.title('Maximum Temperatures For Month')
  plt.xlabel("Longitude")
  plt.ylabel("Latitude")
  plt.savefig(filename+'.svg',dpi=150)

if __name__ == "__main__":
  
  source = ""
  month = -1
  
  try:
    opts, args = getopt.getopt(sys.argv[1:], "m:s:")
  except getopt.GetoptError, err:
    print str(err)
    usage(1)

  for o, a in opts:
    if o == "-m":
      if 1 <= int(a) <= 12:
	month = int(a)
      else:
	assert False, "Not a valid month number."
    elif o == "-s": 
      if a in ["sat", "ground"]:  # Only allowing very strictly correct input for now.
	source = a
      else: assert False, "Not a valid source option. Acceptable input: sat or ground"
    else: assert False, "unhandled option"
  
  if source == "": assert False, "Need to specify a source!"
  elif month < 0: assert False, "Need to specify a month!"
  else:
    result = get_month_tempmax_averages(month,source) 
    graph_monthly_temp(result,source+"_output")
    #plt.show()

  
