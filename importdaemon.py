#!/usr/bin/python
#
# Invoked from cron, reads config file, retrieves new data from various source,
# drops it into a file, invokes importbackend.py appropriately.

import os, sys, urllib, urllib2, getopt, csv, datetime, config, glob, subprocess

if sys.version < '2.7':
	print "Requires Python 2.7, you have", sys.version
	sys.exit(8)


#################################################
# Source/Policy management

def get_source_list():

def get_eligible_sources():
# An eligible source is one that we should retrieve now
#	We define this as:
#	LAST_RETRIEVED + RETRIEVAL_FREQUENCY < NOW
#
#	When we successfully check a source, and if it either:
#	A) Does not have new data for us, or
#	B) We integrate any new data
#	We update LAST_RETRIEVED to NOW (CACHE that!)

def define_source(source, sourcetype, site, path=None, user=None, pass=None):
# 	"source" is a short name of a source
#	sourcetype is one of (ftp, http, pop3, scp, file)
#		Not all of these will initially be implemented
#	site is a hostname of where to retrieve files. Blank for "file" sourcetype
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

def get_source_info(source):

def source_what_do_i_lack(source, cachedir):
# Is this better, or..
def source_do_ihave(source, filename):
# Is this better?
def source_retrieve(source):
# Needed for some sourcetypes, like pop3 and *maybe* file?

#################################################
# Data retrieval functions

def get_ftplist(site, path, user=None, pass=None):

def get_ftpfile(site, filename, user=None, pass=None):

def get_httpfile(url):

#################################################
# Local cache management functions

def build_cache_filename(source, origfn):
# Use a predefined cachedir, sourcename, and sourcetype to attempt to integrate data into a source-specific
# subdirectory so that:
#	1) We can identify when we already have a certain file, for protocols (like FTP) where these might stick around
#	2) Filenames won't overwrite each other for protocols where there are no filenames

