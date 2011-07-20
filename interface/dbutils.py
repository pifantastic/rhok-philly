""" Requires project-specific config file.
    Future improvement needed: Handle different authentication types."""

import psycopg2, config

"""def opendb(connectString):
    try:
        db = psycopg2.connect(connectString)
        return db
    except:
        print("Could not connect to the database")"""

def connStr(dbname, dbuser, dbpasswd):
    return "dbname=%s user=%s password=%s" %(dbname,dbuser,dbpasswd)

def opendb(authType="ident"):
    if authType == "password":
        return psycopg2.connect(connStr(config.DBNAME,
                                      config.DBUSER,
                                      config.DBPASS))

    elif authType == "ident":
        return psycopg2.connect("dbname=%s" %config.DBNAME)

    
