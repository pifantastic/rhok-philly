#!/usr/bin/python

import psycopg2
import csv

psql_connection_string = "dbname=%s user=%s password=%s" %('','','')

location_csv = "data/local_weather.csv"

def insert_csv(csv_path):
    data = []
    for row in csv.reader(open(csv_path)):
        data.append(row)
    
    header = data.pop(0)    
    
    ids, names, lats, longs = zip(*data)
    
    dbconn = psycopg2.connect(psql_connection_string)
    curs = dbconn.cursor()
    
    for i in range(len(ids)):
        curs.execute(
            "INSERT INTO location(sourceid,lat,lng,locname)"\
            "VALUES (%s,%s,%s,%s);",\
            ("ground",lats[i],longs[i],names[i]))
    dbconn.commit()

insert_csv(location_csv)
