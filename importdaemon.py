#!/usr/bin/python

''' Invoked from cron, reads config file, retrieves new data from various sources.
Saves files if they are files. Drops HTTP or POP3 data into files, otherwise.
Invokes worker script appropriately.

#########################################
Design issues:
	1) Should this be configured primarily from a dotfile or from the
		database?
	2) Should this be invokable by the CGI or just by cron/manual invoke?
	3) Which account will this script run under?
'''

import os, sys, urllib, urllib2, getopt, csv, datetime, glob, subprocess
from dbutils import *
from importdaemonlib import *
from importworker import *
from config import *
from sat_ranged_import import *
import psycopg2
import config	# If this fails, move the template to an actual file
from ftplib import FTP
from datetime import date

if sys.version < '2.7':
	print "Requires Python 2.7, you have", sys.version
	sys.exit(8)

######################################

def main():
	''' Do stuff. '''
	print "Importdaemon starting up"
	stales = get_stale_sources()
	for sourceid in stales:
		print "\tHandling source %s" % sourceid
		handle_source_update(sourceid)
	print "Importdaemon done"



#################################################
# Source update functions
# 	Do we already have this chunk of data?

def handle_source_update(source):
	'''
	Fetch all stale files from the given source
	'''
	sourcename, updinterval, lastupdate, protocol, site, path, ftplogin, ftppass = get_source_info(source)
	if(protocol == "ftp"):
		cachedir = get_cache_filedir(source)
		cachefiles = set(os.listdir(cachedir))
		remfiles = set(get_filelist(source))
		to_cache = remfiles - cachefiles # Yay set objects!
		for thisfile in to_cache:
			get_file(source, thisfile)
			db_import_file(source, thisfile)
		mark_source_current(source)
	elif(protocol == "http"):
		lastday, lastmonth, lastyear = time.strptime(lastupdate, "%Y-%m-%d")
		today_dt = date.today()
		reader = csv.reader(open('data/grid-sample-unique.csv', 'rU'), delimiter=',') # FIXME Might be good to rely on database instead of files
		reader.next()

		for row in reader:
			fetch_nasa_data_for_daterange(row[0], row[1], lastyear, today.year, lastmonth, today.month, lastday, today.day)
		mark_source_current(source)

	else:
		print "Unsupported protocol %s" % protocol
		exit(1)
		
#def getNeededSources(source, cachedir):
	# Is this better, or..
#def source_do_ihave(source, filename):
	# Is this better?

main()
