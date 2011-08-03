#!/usr/bin/python
#
# Library code to handle software imports

import os, sys, urllib, urllib2, getopt, csv, datetime, config, glob, subprocess, errno
from config import *
from dbutils import *
import psycopg2
import importworker	# If this fails, move the template to an actual file
from ftplib import FTP


######################################

# Source/Policy management

def get_source_list():
	''' Returns datsourceid for each defined datasource
	'''
	dbconn = opendb()
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
	dbconn = opendb()
	stalesources = []
	for sourceid in get_source_list():
		curs = dbconn.cursor()
		curs.execute("SELECT source_is_current(%s)", (sourceid,))
		res = curs.fetchone()[0]
		if(res == False):
			stalesources.append(sourceid)
	return stalesources

def mark_source_current(source):
	''' Mark a source as having been updated '''
	dbconn = opendb()
	curs = dbconn.cursor()
	curs.execute("UPDATE datasource SET lastupdate=now() WHERE datsourceid=%s", (source,))
	dbconn.commit()

def define_source(sourcename, protocol, updinterval=None, site=None, path=None, login=None, lpass=None):
	''' "sourcename" is a human-readable name of a source
	protocol is one of (ftp, http, https, pop3, scp, file)
		Not all of these will initially be implemented
	site is a hostname of where to retrieve files. Blank for "file" protocol 
	path is URL components after the hostname, or FTP components, or ...
		leave blank for pop3
	login is the login name for the resource (if applicable)
	lpass is the password for the resource (if applicable)

	We may need to figure out a way to work geo and time information in here? Maybe? '''
	dbconn = opendb()
	curs = dbconn.cursor()
	curs.execute("INSERT INTO datasource(sourcename, protocol, updinterval, site, path, login, pass) VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING datsourceid;", (sourcename, protocol, updinterval, site, path, login, lpass) )
	dbconn.commit()
	return curs.fetchone()[0]

#################################################
# Source retrieval functions

def get_filelist(source):
	protocol = get_protocol(source)
	if(protocol == "ftp"):
		sourcename, updinterval, lastupdate, protocol, site, path, ftplogin, ftppass = get_source_info(source)
		files = get_ftplist(site, path, ftplogin, ftppass)
	else:
		print "Unsupported protocol %s" % protocol 
		exit(1)
	return files

def get_file(source, filename):
	'''
	Retrieve the named file from the given site. The actual remote path is the source's path concatenated with the
	file path

	'''
	protocol = get_protocol(source)
	if(protocol == "ftp"):
		sourcename, updinterval, lastupdate, protocol, site, path, ftplogin, ftppass = get_source_info(source)
		targfile = build_cache_filename(source, filename)
		get_ftpfile(targfile, site, path + "/" + filename, ftplogin, ftppass)
	else:
		print "Unsupported protocol %s" % protocol
		exit(1)

		


#################################################
# Misc

def get_source_info(source):
	# Returns info from define_source
	dbconn = opendb()
	curs = dbconn.cursor()
	curs.execute("SELECT sourcename, updinterval, lastupdate, protocol, site, path, login, pass FROM datasource WHERE datsourceid=%s", (source,))
	res = curs.fetchone()
	return res

#def source_retrieveall(source):
	# Needed for some protocols, like pop3 and *maybe* file?
	#	For these sources, if there is data, it is imported.

def get_protocol(source):
	dbconn = opendb()
	curs = dbconn.cursor()
	curs.execute("SELECT protocol FROM datasource WHERE datsourceid=%s", (source,))
	res = curs.fetchone()[0]
	return res

def get_source_loctype(source):
	'''
	sat or ground
	'''
	dbconn = opendb()
	curs = dbconn.cursor()
	curs.execute("SELECT loctype FROM datasource WHERE datsourceid=%s", (source,))
	res = curs.fetchone()[0]
	return res

def get_source_with_name(sourcename):
	dbconn = opendb()
	curs = dbconn.cursor()
	curs.execute("SELECT datsourceid FROM datasource WHERE sourcename=%s", (sourcename,))
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
	ftphandle.cwd(path)
	files = ftphandle.nlst()
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
		print "Cound not open target filename %s" % targfile
	try:
		ftphandle.retrbinary("RETR " + filename, targ.write)
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
	sourcetype = get_protocol(source)
	if(protocol == "ftp"):
		mkdir_p((DATCACHE + "%s") % source)
		return DATCACHE + "%s" % source 
	else:
		print "Unsupported protocol %s" % protocol
		exit(1)

def build_cache_filename(source, filename):
	''' Use a predefined cachedir, sourcename, and protocol to attempt to integrate data into a source-specific
	subdirectory so that:
	1) We can identify when we already have a certain file, for protocols (like FTP) where these might stick around
	2) Filenames won't overwrite each other for protocols where there are no filenames
	'''
	protocol = get_protocol(source)
	if(protocol == "ftp"):
		mkdir_p(DATCACHE + ("%s" % source))
		return DATCACHE + ("%s" % source) + "/" + filename # I know source is numeric. I hope that's fine.
	elif(protocol == "http"):
		mkdir_p(DATCACHE + ("%s" % source))
		return DATCACHE + ("%s" % source) + "/" + filename # Ugh. I really don't know how well this will work.
	else:
		print "Unsupported protocol %s" % protocol
		exit(1)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as myerr: 
        if myerr.errno == errno.EEXIST:
            pass
        else: raise
