#!/usr/bin/python
#
# Invoked from cron, reads config file, retrieves new data from various sources.
# Saves files if they are files. Drops HTTP or POP3 data into files, otherwise.
# Invokes importbackend.py appropriately.
#
#########################################
# Design issues:
#	1) Should this be configured primarily from a dotfile or from the
#		database?
#	2) Should this be invokable by the CGI or just by cron/manual invoke?
#	3) Which account will this script run under?


import os, sys, urllib, urllib2, getopt, csv, datetime, config, glob, subprocess
import config	# If this fails, move the template to an actual file
from ftplib import FTP

if sys.version < '2.7':
	print "Requires Python 2.7, you have", sys.version
	sys.exit(8)

######################
# TODO:
#	Rework to avoid underscores, as per python convention

#################################################
# Source/Policy management

def get_source_list():
	''' Returns datsourceid for each defined datasource
	'''
	dbconn = psycopg2.connect(PSQL_CONN_STRING)
	curs = dbconn.cursor()
	curs.execute("SELECT datsourceid FROM datasource;")
	return curs.fetchall()

def get_stale_sources():
	''' A stale source is one that we should retrieve now
	We define this as:
	LAST_RETRIEVED + UPDATE_INTERVAL < NOW

	When we successfully check a source, and if it either:
	A) Does not have new data for us, or
	B) We integrate any new data
	We update LAST_RETRIEVED to NOW (CACHE that!) '''
	dbconn = psycopg2.connect(PSQL_CONN_STRING)
	stalesources = []
	for i in get_source_list():
		curs = dbconn.cursor()
		curs.execute("SELECT source_is_current(%s)", (i,))
		res = curs.fetchone()[0]
		if(res):
			stalesources.append(i)
	return stalesources
	

def define_source(sourcename, sourcetype, updinterval=None, site=None, path=None, login=None, pass=None):
	''' "source" is a short name of a source
	sourcetype is one of (ftp, http, https, pop3, scp, file)
		Not all of these will initially be implemented
	site is a hostname of where to retrieve files. Blank for "file" sourcetype
	path is URL components after the hostname, or FTP components, or ...
		leave blank for pop3
	login is the login name for the resource (if applicable)
	pass is the password for the resource (if applicable)

	We may need to figure out a way to work geo and time information in here? Maybe? '''
	dbconn = psycopg2.connect(PSQL_CONN_STRING)
	curs = dbconn.cursor()
	curs.execute("INSERT INTO datasource(sourcename, sourcetype, updinterval, site, path, login, pass) VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING datsourceid;", (sourcename, sourcetype, updinterval, site, path, login, pass) )
	return curs.fetchone()[0]

#################################################
# Source retrieval functions

def get_filelist(source):

def get_file(source, filename):

#################################################
# Source identity functions
# 	Do we already have this chunk of data?


def getNeededSources(source, cachedir):
# Is this better, or..
def source_do_ihave(source, filename):
# Is this better?

#################################################
# Misc

def get_source_info(source):
# Returns info from define_source

def source_retrieveall(source):
# Needed for some sourcetypes, like pop3 and *maybe* file?
#	For these sources, if there is data, it is imported.

#################################################
# Data retrieval functions

def get_ftplist(site, path, user=None, pass=None):
	try:
		ftphandle = FTP(site)
	except Exception:
		print "Failed to connect to site"

	if(user != None):
		try:
			ftphandle.login(user,pass)
		except Exception:
			print "Failed to login to site"
	else:
		ftphandle.login()
	files = ftphandle.nlst(path)
	return files

def get_ftpfile(targfile, site, filename, user=None, pass=None):
	try:
		ftphandle = FTP(site)
	except Exception:
		print "Failed to connect to site"

	if(user != None):
		try:
			ftphandle.login(user,pass)
		except Exception:
			print "Failed to login to site"
	else:
		ftphandle.login()
	try:
		targ = open(targfile, "wb")
	except Exception:
		print "Cound not open target filename"
	try:
		ftphandle.retrbinary("RETR " + path, targ.write)
	except Exception:
		print "Download error"
	return


def get_httpfile(url):
	try:
		datahandle = urllib2.urlopen(url)
		return (1, datahandle.read() )
	except URLError:
		return (0, None)

#################################################
# Local cache management functions

def build_cache_filename(source, filename):
# Use a predefined cachedir, sourcename, and sourcetype to attempt to integrate data into a source-specific
# subdirectory so that:
#	1) We can identify when we already have a certain file, for protocols (like FTP) where these might stick around
#	2) Filenames won't overwrite each other for protocols where there are no filenames

