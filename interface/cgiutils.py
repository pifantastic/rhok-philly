
import cgi, crypt
import os
from dbutils import * # This includes psycopg2
from random import randrange
from Cookie import SimpleCookie

def makeCookie(key,val):
    cook = SimpleCookie()
    cook.load("%s=%s" %(key,val))
    return cook

def retrieveCookies():
    # Returns a dictionary with keys and values determined by the
    if 'HTTP_COOKIE' in os.environ:
        cookies = os.environ['HTTP_COOKIE']
        cookies = cookies.split('; ')
        handler = {}

        for cookie in cookies:
            cook = cookie.split('=')
            handler[cook[0]] = cook[1]
        return handler
    else: 
        return {} # Empty dictionary
    

def makeSessionID():
    return randrange(999999999999)

def makeSession(userid):
    """ Get a new session id, then store session id and user id in database."""
    sessID = makeSessionID()

    tempdb = opendb()
    curs = tempdb.cursor()
    curs.execute("DELETE FROM websessions WHERE userid=%s;",(userid,))
    curs.execute("INSERT INTO websessions(userid,sessionid,startdate)"+\
                     "VALUES (%s,%s,current_date);",(userid,sessID))
    tempdb.commit()
    tempdb.close()
    return sessID

def getSessionUser(sessid):
    """ Get the userid associated with the specified session ID. """
    tempdb = opendb()
    curs = tempdb.cursor()
    curs.execute("SELECT userid FROM websessions WHERE sessionid=%s;",(sessid,))
    # Can't index tuple if there are no results.
    result = curs.fetchone()  
    if result==None: return None # Oops! Error! Oh no! WTF! Session was purged.
    else: return result[0]

def purgeOldSessions():
    """ Purge all old sessionid values, anything over a week."""
    tempdb = opendb()
    curs = tempdb.cursor()
    curs.execute("DELETE FROM websessions WHERE (current_date - startdate) >7;")
    tempdb.commit()
    tempdb.close()


