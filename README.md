## Real Time Climate Data Comparison Platform
  For more information on project goals, see the http://www.rhok.org website at:
    http://www.rhok.org/problems/real-time-climate-data-comparison-platform

## Database

Create the database and define tables: `python import.py -c`

## Importing data

Import ground station data: `python import.py -g`
Import satellite data: `python import.py -s`

## Future Work
   [ ] Change source of ground data to use ftp source
   [ ] Create functions to update database with new weather data and automate checking ftp / online sources
   [ ] When graphing, handle -99 values from data sources that were not available in certain years.  
	 >> Current solution requires deleting those values from the database. 
         >> Proposed solution: a "cleanResults" function to remove stations & data from the query results
   [ ] Create an online CGI interface for specifying data to display.
   [ ] Overlay .png graphs on map image.  
	 >> Proposal: Use Image Magick.