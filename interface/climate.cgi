#! /usr/bin/python

import cgi
import cgitb
from os import path
from cgiutils import *
import htmlGen as h

cgitb.enable()  # Enabling traceback to display in the browser.
#cgitb.enable(display=0, logdir="/tmp")   # Use this for more privacy.

monthDict = dict({1:"January",
		 2:"February",
		 3:"March",
		 4:"April",
		 5:"May",
		 6:"June",
		 7:"July",
		 8:"August",
		 9:"September",
		 10:"October",
		 11:"November",
		 12:"December"})

datatypeDict = dict({#"solarradiation":"solar radiation",
		     "tempmax":"maximum temperature",
		     "tempmin":"minimum temperature",
		     "tempmedian":"median temperature",
		     "rain":"rainfall" # Add comma when uncommenting!
		     #"wind":"wind speed",
		     #"dewpoint":"dew point",
		     #"humidity":"humidity"
		     })

def graphCached(graphPath):
	"""	This returns a boolean value after we figure out 
	whether we already have a graph of the requested data."""
	if path.isfile(graphPath): return True
	else: return False

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
	print '<h1>Bolivian Climate Data</h1>'

def printYearOptions():
	for yr in range(1989,2012,1):
		print '<option value="%s">%s</option>' %(yr,yr)

def printMonthOptions():
	print h.inputSelectFromDict("month",monthDict)

def printDataOptions():
	for key,val in datatypeDict.items():
		print h.inputRadioButton("querytype",key) + val + '<br/>'

def monthAvgForm():
	print '<form class="formblock" id="formid" name="climateform" action="climate.cgi" method="post" enctype="multipart/form-data">'
	print '<h3>Monthly Averages</h3>'
	print '<p id="col_1"><em>Month:</em>',
	printMonthOptions()
	print '<br/><em>Start Year:</em>'
	print '<select name="startyear">'
	printYearOptions()
	print '</select>\n'
	print '<br/><em>End Year:</em>'
	print '<select name="endyear">'
	printYearOptions()
	print '</select></p>'
	print '<p id="col_2"><br/><em>Data Type</em><br/>'
	printDataOptions()
	print '<br/><input type=submit name="submission" value="monthavg"></p>'
	print '</form>'

def singleDayForm():
	print '<form class="formblock" id="formid" name="climateform" action="climate.cgi" method="post" enctype="multipart/form-data">'
	print '<h3>Single Day Data</h3>'
	print '<p id="col_1"><em>Month:</em>',
	print h.inputSelectFromDict("month",monthDict)
	print '<br/><em>Year:</em>'
	print '<select name="year">'
	printYearOptions()
	print '</select>\n'
	print '</p>'
	print '<p id="col_2"><em>Data Type:</em><br/>'
	printDataOptions()
	print '<br/><input type=submit name="submission" value="singleday" ></p>'
	print '</form>'

def insertQueryMenu():
	print '<div id="querybar">'
	monthAvgForm()
	singleDayForm()
	print '\n</div> '
	print 'End of bar'

#------------------------------------------------------------------------
# Dealing with content
#------------------------------------------------------------------------

form = cgi.FieldStorage()


insertHeader()
insertQueryMenu()


soughtGraph = "images/" + form["month"].value + "_" + form["startyear"].value + ".png"
if graphCached(soughtGraph):
	print "     <p><img src='" + soughtGraph + "'/></p>"
else:
    print "    <p>We'll need to generate the", soughtGraph,"graph.</p>"
        

print "</body></html>"
