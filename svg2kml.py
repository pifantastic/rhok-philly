"""
This script takes an svg's paths and generates a kml file with polygons based on the svg paths.

To do:
    Set this up to run with arguments.
    Convert this to operate as a generator object, perhaps?
    Account for SVG paths that contain curve elements (q and c control points).
"""

import xml.dom.minidom as mdom

#######################################################################
# I/O convenience functions.

def domFromFile(filename):
    file = open(filename, 'r')
    dom = mdom.parseString(file.read())
    return dom

def saveKML(filename):
    kmlFile = open(filename,'w')
    kmlFile.write(outputDom.toprettyxml('  ', newl='\n', encoding = 'utf-8'))

#######################################################################
# relatively generic KML generation functions

def kmlRing(coordsStr):
    """ Returns <LinearRing> node with <coordinates> child that has a 
    text node child based on passed coords."""
    ring = outputDom.createElement("LinearRing")
    coo = outputDom.createElement("coordinates")
    ring.appendChild(coo)
    data = outputDom.createTextNode(coordsStr)
    coo.appendChild(data)
    return ring

def kmlPolygon(ringNode, innerRing=None):
    """ Creates a new polygon node associated with the outputDom, given a
    kml node detailing the perimiter.
    Allows optional inner boundary, which is also a linear ring kml node.
    """
    poly = outputDom.createElement("Polygon")
    ex = outputDom.createElement("extrude")
    poly.appendChild(ex)
    ex.appendChild(outputDom.createTextNode("1"))
    alti = outputDom.createElement("altitudeMode")
    poly.appendChild(alti)
    alti.appendChild(outputDom.createTextNode("relativeToGround"))
    outerBound = outputDom.createElement("outerBoundaryIs")
    poly.appendChild(outerBound)
    outerBound.appendChild(ringNode)
    if innerRing != None:
        innerBound = outputDom.createElement("innerBoundaryIs")
        poly.appendChild(innerBound)
        innerBound.appendChild(innerRing)
    return poly

def kmlPlace(placename,placeNode):
    """ The place node will be added to the kml root.
    Returns nothing."""
    place = outputDom.createElement("Placemark")
    kmlRoot.appendChild(place)
    name = outputDom.createElement("name")
    place.appendChild(name)
    name.appendChild(outputDom.createTextNode(placename))
    place.appendChild(placeNode)
    
    
#######################################################################
# SVG handling functions

def svgPath_to_Polygon(svgPathNode):
    dataString = svgPathNode.getAttribute("d")[1:-1] # remove leading M, final z
    pointList = dataString.split("L")
    print pointList
    data = ""
    for point in pointList:
        if point != "":
            l = point.split()
            data = data + l[0] + "," + l[1] + ",0\n"  # build coordinate data
    perimeter = kmlRing(data)
    polygon = kmlPolygon(perimeter)
    if polygon == None:
        print "Seriously, wtf?"
    return polygon
    

def handlePaths(dom):
    """ Identify all paths in the given svg dom and generate kml polygons.
    TODO: Figure out which belong in the same polygon as inner/outer bounds."""
    pathNodes = dom.getElementsByTagName("path")
    for node in pathNodes:
        poly = svgPath_to_Polygon(node)
        if poly == None:
            print "oh noes, poly didn't work"
        kmlPlace("Something", poly) # TODO: Figure out proper names.


#######################################################################
# Global setup 

# These shouldn't be global, ultimately, but this is for convenience now.
outputDom = mdom.Document() # Empty document
kmlRoot = outputDom.createElementNS('http://earth.google.com/kml/2.2', 'kml')
outputDom.appendChild(kmlRoot)

#######################################################################
# Action part!   ...should not be hard coded like this. Testing purposes!

sourceDom = domFromFile("/home/kepod/code/rhok-examples/sat_temperature.svg")
handlePaths(sourceDom)
saveKML("/home/kepod/code/rhok-examples/kml-test.kml")







