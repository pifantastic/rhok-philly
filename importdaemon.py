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
import psycopg2
import config,importworker	# If this fails, move the template to an actual file
from ftplib import FTP

if sys.version < '2.7':
	print "Requires Python 2.7, you have", sys.version
	sys.exit(8)

######################################

def main():
	''' Do stuff. '''
	print "Importdaemon starting up"
	stales = get_stale_sources()
	for sourceid in stales:
		print "\tHandling source " + sourceid
		handle_source_update(sourceid)
	print "Importdaemon done"


######################
# TODO:
#	Rework to avoid underscores, as per python convention

#################################################
# Source/Policy management

def get_source_list():
	''' Returns datsourceid for each defined datasource
	'''
	dbconn = psycopg2.connect(get_dbconn_string())
	curs = dbconn.cursor()
	curs.execute("SELECT datsourceid FROM datasource;")
	return curs.fetchall()

def get_stale_sources():
	''' A stale source is one that we should retrieve now
	We define this as:
	LAST_RETRIEVED + UPDATE_INTERVAL < NOW

	LAST_RETRIEVED is updated if we're either current or
	just got some new data.
	'''
	dbconn = psycopg2.connect(get_dbconn_string())
	stalesources = []
	for sourceid in get_source_list():
		curs = dbconn.cursor()
		curs.execute("SELECT source_is_current(%s)", (sourceid,))
		res = curs.fetchone()[0]
		if(res):
			stalesources.append(sourceid)
	return stalesources

def mark_source_current(source):
	''' Mark a source as having been updated '''
	dbconn = psycopg2.connect(get_dbconn_string())
	curs = dbconn.cursor()
	curs.execute("UPDATE datasource SET lastupdate=now() WHERE datsourceid=%s", (source,))

def define_source(sourcename, sourcetype, updinterval=None, site=None, path=None, login=None, lpass=None):
	''' "sourcename" is a human-readable name of a source
	sourcetype is one of (ftp, http, https, pop3, scp, file)
		Not all of these will initially be implemented
	site is a hostname of where to retrieve files. Blank for "file" sourcetype
	path is URL components after the hostname, or FTP components, or ...
		leave blank for pop3
	login is the login name for the resource (if applicable)
	lpass is the password for the resource (if applicable)

	We may need to figure out a way to work geo and time information in here? Maybe? '''
	dbconn = psycopg2.connect(get_dbconn_string())
	curs = dbconn.cursor()
	curs.execute("INSERT INTO datasource(sourcename, sourcetype, updinterval, site, path, login, pass) VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING datsourceid;", (sourcename, sourcetype, updinterval, site, path, login, lpass) )
	return curs.fetchone()[0]

#################################################
# Source retrieval functions

def get_filelist(source):
	sourcetype = get_source_type(source)
	if(sourcetype == "ftp"):
		sourcename, updinterval, lastupdate, sourcetype, site, path, ftplogin, ftppass = get_source_info(source)
		files = get_ftplist(site, path, ftplogin, ftppass)
	else:
		print "Unsupported protocol %s" % sourcetype
		exit(1)
	return files

def get_file(source, filename):
	'''
	Retrieve the named file from the given site. The actual remote path is the source's path concatenated with the
	file path

	'''
	sourcetype = get_source_type(source)
	if(sourcetype == "ftp"):
		sourcename, updinterval, lastupdate, sourcetype, site, path, ftplogin, ftppass = get_source_info(source)
		targfile = build_cache_filename(source, filename)
		get_ftpfile(targfile, site, path + "/" + filename, ftplogin, ftppass)
	else:
		print "Unsupported protocol %s" % sourcetype
		exit(1)

#################################################
# Source update functions
# 	Do we already have this chunk of data?

def handle_source_update(source):
	'''
	Fetch all stale files from the given source
	'''
	sourcename, updinterval, lastupdate, sourcetype, site, path, ftplogin, ftppass = get_source_info(source)
	if(sourcetype == "ftp"):
		cachedir = get_cache_filedir(source)
		cachefiles = set(os.listdir(cachedir))
		remfiles = set(get_filelist(source))
		to_cache = remfiles - cachefiles # Yay set objects!
		for thisfile in to_cache:
			get_file(source, thisfile)
			db_import_file(source, thisfile)
		mark_source_current(source)
	else:
		print "Unsupported protocol %s" % sourcetype
		exit(1)
		

#def getNeededSources(source, cachedir):
	# Is this better, or..
#def source_do_ihave(source, filename):
	# Is this better?

#################################################
# Misc

def get_source_info(source):
	# Returns info from define_source
	dbconn = psycopg2.connect(get_dbconn_string())
	curs = dbconn.cursor()
	curs.execute("SELECT sourcename, updinterval, lastupdate, sourcetype, site, path, login, pass FROM datasource WHERE datsourceid=?", (source,))
	res = curs.fetchone()
	return res

#def source_retrieveall(source):
	# Needed for some sourcetypes, like pop3 and *maybe* file?
	#	For these sources, if there is data, it is imported.

def get_source_type(source):
	dbconn = psycopg2.connect(get_dbconn_string())
	curs = dbconn.cursor()
	curs.execute("SELECT sourcetype FROM datasource WHERE datsourceid=?", (source,))
	res = curs.fetchone()[0]
	return res

#################################################
# Data retrieval functions

def get_ftplist(site, path, user=None, lpass=None):
	try:
		ftphandle = FTP(site)
	except Exception:
		print "Failed to connect to site"

	if(user != None):
		try:
			ftphandle.login(user,lpass)
		except Exception:
			print "Failed to login to site"
	else:
		ftphandle.login()
	files = ftphandle.nlst(path)
	return files

def get_ftpfile(targfile, site, filename, user=None, lpass=None):
	try:
		ftphandle = FTP(site)
	except Exception:
		print "Failed to connect to site"

	if(user != None):
		try:
			ftphandle.login(user,lpass)
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

def get_cache_filedir(source):
	''' Where are our cachefiles stored? Use this to sync '''
	sourcetype = get_source_type(source)
	if(sourcetype == "ftp"):
		return GROUNDDATAPATH + source 
	else:
		print "Unsupported protocol %s" % sourcetype
		exit(1)

def build_cache_filename(source, filename):
	''' Use a predefined cachedir, sourcename, and sourcetype to attempt to integrate data into a source-specific
	subdirectory so that:
	1) We can identify when we already have a certain file, for protocols (like FTP) where these might stick around
	2) Filenames won't overwrite each other for protocols where there are no filenames
	'''
	sourcetype = get_source_type(source)
	if(sourcetype == "ftp"):
		os.mkdir(GROUNDDATAPATH + source)
		return GROUNDDATAPATH + source + "/" + filename # I know source is numeric. I hope that's fine.
	elif(sourcetype == "http"):
		os.mkdir(GROUNDDATAPATH + source)
		return GROUNDDATAPATH + source + "/" + filename # Ugh. I really don't know how well this will work.
	else:
		print "Unsupported protocol %s" % sourcetype
		exit(1)

main()
