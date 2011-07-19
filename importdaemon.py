#!/usr/bin/python
#
# Invoked from cron, reads config file, retrieves new data from various sources.
# Saves files if they are files. Drops HTTP or POP3 data into files, otherwise.
# Invokes importbackend.py appropriately.

import os, sys, urllib, urllib2, getopt, csv, datetime, config, glob, subprocess

if sys.version < '2.7':
	print "Requires Python 2.7, you have", sys.version
	sys.exit(8)

######################
# TODO:
#	Rework to avoid underscores, as per python convention

#################################################
# Source/Policy management

def get_source_list():

def get_stale_sources():
# A stale source is one that we should retrieve now
#	We define this as:
#	LAST_RETRIEVED + UPDATE_INTERVAL < NOW
#
#	When we successfully check a source, and if it either:
#	A) Does not have new data for us, or
#	B) We integrate any new data
#	We update LAST_RETRIEVED to NOW (CACHE that!)

def define_source(source, sourcetype, site=None, path=None, user=None, pass=None):
# 	"source" is a short name of a source
#	sourcetype is one of (ftp, http, https, pop3, scp, file)
#		Not all of these will initially be implemented
#	site is a hostname of where to retrieve files. Blank for "file" sourcetype
#	path is URL components after the hostname, or FTP components, or ...
#		leave blank for pop3
#	user is the login name for the resource (if applicable)
#	pass is the password for the resource (if applicable)
#
#	We may need to figure out a way to work geo and time information in here? Maybe?

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

def source_retrieve(source):
# Needed for some sourcetypes, like pop3 and *maybe* file?
#	For these sources, if there is data, it is imported.

#################################################
# Data retrieval functions

def get_ftplist(site, path, user=None, pass=None):

def get_ftpfile(site, filename, user=None, pass=None):

def get_httpfile(url):

#################################################
# Local cache management functions

def build_cache_filename(source, filename):
# Use a predefined cachedir, sourcename, and sourcetype to attempt to integrate data into a source-specific
# subdirectory so that:
#	1) We can identify when we already have a certain file, for protocols (like FTP) where these might stick around
#	2) Filenames won't overwrite each other for protocols where there are no filenames

