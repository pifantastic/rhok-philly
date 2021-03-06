#!/usr/bin/python


''' importworker.py - A component that takes a source and a file and
figures out the right way to shove it into the database. '''

from importdaemonlib import *
from string import *
from importer import *
from geodb import *

def db_import_file(source, thisfile):
	''' The main entry point into this software component. For a named source,
	parse it and put it into the database. '''

	print "db_import_file: " + thisfile
	extension = split(thisfile, '.')[-1]
	loctype = get_source_loctype(source)
	realpath = get_cache_filedir(source) + '/' + thisfile
	handle_db_import(loctype, extension, realpath) # Do we really need source? Maybe we don't!

def handle_db_import(loctype, extension, thisfile):
	''' Based on file extension, actually call the appropriate import routines '''
	if(extension == "csv"):		# csv, with header
		handle_delimited_input(',', thisfile, loctype)
	elif(extension == "txt"):	# Assume this is csv too
		handle_delimited_input(',', thisfile, loctype)
	elif(extension == "cgi"):	# The text/http output from NASA cgis? We need to make sure the caches actually have this extension!
		handle_delimited_input(' ', thisfile, loctype) # We'll actually accept any whitespace
	elif(extension == "dbf"):	# DBase. Sigh.
		handle_dbase_input(thisfile, loctype)
	elif(extension == "xls"):	# Older versions of excel. We maybe can handle these
		handle_excel_input(thisfile, loctype)
	elif(extension == "xlsx"):	# Excel 97+. We can't handle this yet.
		die("Excel 97+ files are not supported")
	elif(extension == "mark"):	# A "mark" file is full of random data, used for debugging. No import.
		print "Got mark file " + thisfile
	else:				# Something else we're not going to even try
		die("Unrecognised extension " + extension + " for " + thisfile)

######################################
# This should maybe be moved somewhere better so it can be shared
def die(message, returncode=1):
	'''
	Spits out a message to the user, and exits (optionally with a specified return code)
	'''
	print message
	exit(returncode)

######################################
# Import handlers - loctype is "sat" or "ground"

def handle_delimited_input(sep, fname, loctype):
	'''
	Input handler for delimited input. Takes three arguments, a separator, a filename, and
	a loctype
	Assumes the first row has fieldnames.
	If the separator is ' ', split on any whitespace.
	'''
	if(loctype == "ground"):
		import_csv_data_two_underscores(sep, fname, loctype)
	else:
		die("Sky data in CSV format is not yet supported.")

def handle_dbase_input(fname, loctype):
	'''
	Input handler for dbase files.
	'''
	if(loctype == "ground"):
		import_ground_dbf(fname)
	else:
		die("Sky data in DBF format is not yet supported.")

def handle_excel_input(fname, loctype): # This is best-effort
	'''
	Input handler for excel files. Will not work with the new "open" "XML" files.
	'''
	if(loctype == "ground"):
		import_ground_xls(fname)
	else:
		die("Sky data in XLS format is not yet supported.")
