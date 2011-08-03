#!/usr/bin/python

from analysis import *
import cgi
import cgitb
from os import path
from cgiutils import * # Comes with dbutils
import htmlGen as h
from geodb import *
import config

#os.environ['HOME'] = '/tmp/' # To allow Matplotlib to run under cgi
#os.environ['MPLCONFIGDIR'] = '/tmp/' 

cgitb.enable()  # Enabling traceback to display in the browser.
#cgitb.enable(display=0, logdir="/tmp")   # Use this for more privacy.

datatypeDict = dict({#"solarradiation":"solar radiation",
		     "tempmax":"maximum temperature",
		     "tempmin":"minimum temperature",
		     #"tempmedian":"median temperature",
		     "rain":"precipitation" # Add comma when uncommenting!
		     #"wind":"wind speed",
		     #"dewpoint":"dew point",
		     #"humidity":"humidity"
		     })

#def dataRecorded():
#	"""	This returns a boolean value after we figure out whether requested data is in the database."""
#	return True

#------------------------------------------------------------------------
# Functions for generating page elements
#------------------------------------------------------------------------

def insertHeader():
	print 'Content-Type: text/html\n\n'
	print '<html><head><title>Climate Data Result</title>'
	print '  <link rel="stylesheet" type="text/css" href="stylesheet.css" />'
	print '</head>\n<body>'
	print '<h2>Satellite and Local Climate Data Monitoring Platform</h2>'

def printMonthOptions():
	print '<option value="01">January</option>'
	print '<option value="02">February</option>'
	print '<option value="03">March</option>'
	print '<option value="04">April</option>'
	print '<option value="05">May</option>'
	print '<option value="06">June</option>'
	print '<option value="07">July</option>'
	print '<option value="08">August</option>'
	print '<option value="09">September</option>'
	print '<option value="10">October</option>'
	print '<option value="11">November</option>'
	print '<option value="12">December</option>'

def printDayOptions():
	for day in range(1,32):
		print '<option value="%s">%s</option>' %(day,day)

def printYearOptions():
	"""This prints <options> for years of data available. 
	Changes based on data availability in database."""
	startyear = earliestData()
	endyear = latestData()

	for yr in range(int(startyear),int(endyear)+1,1):
		print '<option value="%s">%s</option>' %(yr,yr)

def printYearRanges():
	"""This prints <options> for number of years of data available. 
	Changes based on data availability in database."""
	for yr in range(1,yearsOfData()+1):
		print '<option value="%s">%s</option>' %(yr,yr)

def printDataOptions():
	"""Prints radio buttons for data types given in a global dictionary."""
	for key,val in datatypeDict.items():
		print h.inputRadioButton("querytype",key) + val + '<br/>'

def monthAvgForm():
	""" This is form would select a month to investigate and the  """
	print '<form class="formblock" id="formid" name="climateform" action="index.cgi" method="post" enctype="multipart/form-data">'
	print '<h3>Monthly Averages</h3>'
	print '<p id="col_1"><em>Month:</em>',
	printMonthOptions()
	print '<br/><em>Start Year:</em>'
	print '<select name="startyear">'
	printYearOptions()
	print '</select>  '
	print '<br/><em>End Year:</em>'
	print '<select name="endyear">'
	printYearOptions()
	print '</select></p>'
	print '<p id="col_2"><br/><em>Data Type</em><br/>'
	printDataOptions()
	h.inputSubmit("submission","get data")
	print '</p>\n</form>'

def singleDayForm():
	print '<form class="formblock" id="formid" name="climateform" action="index.cgi" method="post" enctype="multipart/form-data">'
	print '<h3>Single Day Data</h3>'
	print '<p id="col_1">'
	singleDayFormContents()
	print '</p>'
	print '<p id="col_2"><em>Data Type:</em><br/>'
	printDataOptions()
	h.inputSubmit("submission","get data")
	print '</form>'

def singleDayFormContents():
	print 'Get data from a single day: '
	#print '<em>Day:</em>'
	print '<select name="day">'
	printDayOptions()
	print '</select>'
	#print '<em>Month:</em>',
	print '<select name="month">'
	printMonthOptions()
	print '</select>'
	#print '<em>Year:</em>'
	print '<select name="year">'
	printYearOptions()
	print '</select>'

def dataForm():
	print '<form id="formid" name="climateform" action="index.cgi" method="post" enctype="multipart/form-data">'
	printDataOptions()

	# Date range
	print '<p>Get data from'
	print '<select name="startday">'
	printDayOptions()
	print '</select>'
	print '<select name="startmonth">'
	printMonthOptions()
	print '</select>'
	print '<select name="startyear">'
	printYearOptions()
	print '</select>'
	print 'through' 	
	print '<select name="endday">'
	printDayOptions()
	print '</select>'
	print '<select name="endmonth">'
	printMonthOptions()
	print '</select>'
	print '<select name="endyear">'
	printYearOptions()
	print '</select>'
	print h.inputSubmit("daterange","get data")
	print '</p>'
	
	# Single date
	print '<p>'
	singleDayFormContents()
	print h.inputSubmit("singleday","get data")

	# Last N years
	print '<p>'
	print 'Get data from the last ',
	print '<select name="years">'
	printYearRanges() # This should change based on database availability
	print '</select>'
	print 'years.'
	print h.inputSubmit("pastyears","get data")
	print '</p>'
	print '</form>'

def insertQueryMenu():
	print '<div class="formblock">'
	dataForm()
	print '</div> '

def insertAvailabilityNote():
	startdate = earliestData()
	enddate = latestData()
	print '<p>Information is available from %s to %s.</p>' % (startdate, enddate)

#------------------------------------------------------------------------
# Functions for storing, finding, refreshing, converting graph output
#------------------------------------------------------------------------

def graphCached(graphPath):
	"""	This returns a boolean value after we figure out 
	whether we already have a graph of the requested data."""
	if path.isfile(graphPath): return True
	else: return False

def makeFilename(myForm):
	""" File names are determined the time scope requested (singleday,daterange,pastyears) and the querytype."""
	ext = ".svg"

	if "singleday" in myForm:
		return "singleday-"+myForm["querytype"].value+"_"+myForm["year"].value+"-"+myForm["month"].value+"-"+myForm["day"].value+ext 
	elif "daterange" in myForm:
		return "daterange-"+myForm["querytype"].value+"_"+myForm["startyear"].value+"-"+myForm["startmonth"].value+"-"+myForm["startday"]+"-through-"+myForm["endyear"].value+"-"+myForm["endmonth"].value+"-"+myForm["endday"].value+ext 
	elif "pastyears" in myForm:
		return "pastyears-"+myForm["querytype"].value+"_"+myForm["years"]+ext 


#------------------------------------------------------------------------
# Dealing with page content
#------------------------------------------------------------------------

form = cgi.FieldStorage()

insertHeader()
insertAvailabilityNote()
insertQueryMenu()

if form == None:
	print "</body></html>"
elif "singleday" in form:
	
	soughtGraph = makeFilename(form) 
	if graphCached(soughtGraph):
		print "<p><img src='"+config.IMAGERESULTPATH+soughtGraph+"'/></p>"
	else:
		tuples = get_daily_field_values(form["day"].value,
			       form["month"].value,
			       form["year"].value,
			       form["querytype"].value)
		graph_result(tuples, config.IMAGERESULTPATH + soughtGraph)
		print "<p><img src='"+config.IMAGERESULTPATH+soughtGraph+"'/></p>"
        print "</body></html>"
else:
	print "</body></html>"
