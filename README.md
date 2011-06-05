# Real Time Climate Data Comparison Platform

http://www.rhok.org/problems/real-time-climate-data-comparison-platform

## Database

Create a database using schema.sql.  Enter database creds in `config.py`.

## Importing data

Import ground station data: `python import.py -g`

Import satellite data: `python import.py -s`

## Future Work

   [ ] Change source of ground data to use ftp source 
   [ ] Handle -99 values from data sources that were not available in certain years