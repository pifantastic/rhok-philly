#!/usr/bin/python
#
#
# importworker.py - A component that takes a source and a file and
#	figures out the right way to shove it into the database.

def db_import_file(source, thisfile):
''' The main entry point into this software component. For a named source,
	parse it and put it into the database. '''

	print "db_import_file: " + thisfile
	extension = split(thisfile, '.')[-1]
	handle_db_import(extension, thisfile) # Do we really need source? Maybe we don't!

def handle_db_import(extension, thisfile):
''' Based on file extension, actually call the appropriate import routines '''
	if(extension == "csv"):		# csv, with header
		handle_delimited_input(',', thisfile)
	elif(extension == "txt"):	# Assume this is csv too
		handle_delimited_input(',', thisfile)
	elif(extension == "cgi"):	# The text/http output from NASA cgis? We need to make sure the caches actually have this extension!
		handle_delimited_input(' ', thisfile) # We'll actually accept any whitespace
	elif(extension == "dbf"):	# DBase. Sigh.
		handle_dbase_input(thisfile)
	elif(extension == "xls"):	# Older versions of excel. We maybe can handle these
		handle_excel_input(thisfile)
	elif(extension == "xlsx"):	# Excel 97+. We can't handle this yet.
		die("Excel 97+ files are not supported")
	else:				# Something else we're not going to even try
		die("Unrecognised extension " + extension + " for " + thisfile)

######################################
# This should maybe be moved somewhere better so it can be shared
def die(message, returncode=1):
	print message
	exit(returncode)

######################################
# Import handlers

def handle_delimited_input(sep, file):
'''
Input handler for delimited input. Takes two arguments, a separator and a filename.
Assumes the first row has fieldnames.
If the separator is ' ', split on any whitespace.
'''

def handle_dbase_input(file): # This is best-effort
'''
Input handler for dbase files.
'''

def handle_excel_input(file): # This is best-effort
'''
Input handler for excel files. Will not work with the new "open" "XML" files.
'''

