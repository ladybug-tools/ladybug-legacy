# True north
# By Djordje Spasic
# djordjedspasic@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to calculate Earth's true north from magnetic north.
Based on World Magnetic Model of the NOAA:
http://www.ngdc.noaa.gov/geomag/WMM/DoDWMM.shtml
-
All credit goes to Christopher Weiss (cmweiss@gmail.com), the author of the World Magnetic Model python code.
source: https://pypi.python.org/pypi/geomag
-
Provided by Ladybug 0.0.59
    
    input:
        _location: Input data from Ladybug's "Import epw" "location" output, or create your own location data with Ladybug's "Construct Location" component.
        magneticNorth_: Input a vector to be used as a magnetic North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
                        Magnetic north direction is direction a compass-needle points to.
                        -
                        If not supplied, default North direction will be set to the Y-axis (0 degrees).
        date_: Date for which magnetic north should be calculated. Input a date in the following order: month, day, year.
               Example "5,24,2016" (24nd May 2016).
               -
               If not supplied, present date will be used.
        COFfile_: By default "Magnetic north" component already has 2015-2020 integrated WMM coefficients data.
                  In case you would like to analysis periods of time before the year 2015, input an appropriate WMM.COF file path in here.
                  -
                  If not supplied, integrated WMM.COF 2015-2020 coefficients data will be used.
        
    output:
        readMe!: ...
        trueNorth: Geographic north (direction towards the North Pole) - magnetic north corrected for the value of magnetic declination. Ranges from 0-360.
                       In decimal degrees (°).
        trueNorthVec: Vector representation of the upper "trueNorth".
        magneticDeclination: An angle between magnetic north and true north. It is positive east of true north and negative west of true north.
                             In decimal degrees (°).
        magneticFieldVec: Earth's magnetic field vector at chosen location.
                          Vector's intensity represents the strength in nanoTeslas (nT).
"""

ghenv.Component.Name = "Ladybug_True North"
ghenv.Component.NickName = "TrueNorth"
ghenv.Component.Message = "VER 0.0.59\nAPR_26_2015"
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.59\nMAY_26_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc
import datetime
import Rhino
import math
import os


def getLocationData(location):
    
    if location:
        try:
            locationName, latitude, longitude, timeZone, elevation = lb_preparation.decomposeLocation(location)
            validLocationData = True
            printMsg = "ok"
        
        except Exception, e:
            # something is wrong with "_location" input (the input is not from Ladybug 'Import epw' component 'location' ouput)
            latitude = longitude = timeZone = elevation = locationName = None
            validLocationData = False
            printMsg = "Something is wrong with \"_location\" input."
    
    return latitude, longitude, timeZone, elevation, locationName, validLocationData, printMsg


def angle2northClockwise(north):
    # temporary function, until "Sunpath" class from Labybug_ladbybug.py starts calculating sun positions counterclockwise
    try:
        northVec =Rhino.Geometry.Vector3d.YAxis
        northVec.Rotate(-math.radians(float(north)),Rhino.Geometry.Vector3d.ZAxis)
        northVec.Unitize()
        return 2*math.pi-math.radians(float(north)), northVec
    except Exception, e:
        try:
            northVec =Rhino.Geometry.Vector3d(north)
            northVec.Unitize()
            return Rhino.Geometry.Vector3d.VectorAngle(Rhino.Geometry.Vector3d.YAxis, northVec, Rhino.Geometry.Plane.WorldXY), northVec
        except Exception, e:
            return 0, Rhino.Geometry.Vector3d.YAxis


def checkInputData(magneticNorth, date, COFfile):
    
    if (magneticNorth == None):
        magneticNorthDeg = 0  # default
        magneticNorthVec = Rhino.Geometry.Vector3d(0,1,0)  # default
    else:
        try:  # check if it's a number
            magneticNorth = float(magneticNorth)
            if (magneticNorth < 0) or (magneticNorth > 360):
                magneticNorthDeg = magneticNorthVec = date = coefficients = COFfileName = False
                validInputData = False
                printMsg = "Please input magnetic north angle value from 0 to 360."
                return magneticNorthDeg, magneticNorthVec, date, coefficients, COFfileName, validInputData, printMsg
        except Exception, e:  # check if it's a vector
            magneticNorth.Unitize()
        
        magneticNorthRad, magneticNorthVec = angle2northClockwise(magneticNorth)
        magneticNorthDeg = 360-math.degrees(magneticNorthRad)
    
    if (date == None):
        date = datetime.date.today()  # year, month, day
    else:
        try:
            dateSplitted = date.split(",")
            date = datetime.date(int(dateSplitted[2]),int(dateSplitted[0]),int(dateSplitted[1]))
        except Exception, e:
            magneticNorthDeg = magneticNorthVec = date = coefficients = COFfileName = False
            validInputData = False
            printMsg = "Something is wrong with your date format. Please input a date in the following order: month, day, year\nExample: \"5,24,2016\" (24nd May 2016)."
            return magneticNorthDeg, magneticNorthVec, date, coefficients, COFfileName, validInputData, printMsg
    
    if COFfile == None:
        coefficients = lb_photovoltaics.WMMcoefficients()  # use WMM 2015-2020 coefficients
        COFfileName = "WMM2015-2020.COF"
    else:
        try:
            coefficients = lb_photovoltaics.WMMcoefficients(COFfile)
            COFfileName = os.path.basename(COFfile)
        except Exception, e:
            magneticNorthDeg = magneticNorthVec = date = coefficients = COFfileName = False
            validInputData = False
            printMsg = "Something is wrong with your \"COFfile\" file path input data. Please input a valid file path and a valid WMM.COF file."
            return magneticNorthDeg, magneticNorthVec, date, coefficients, COFfileName, validInputData, printMsg
    
    validInputData = True
    printMsg = "ok"
    
    return magneticNorthDeg, magneticNorthVec, date, coefficients, COFfileName, validInputData, printMsg


def main(latitude, longitude, elevation, magneticNorthDeg, magneticNorthVec, date, coefficients):
    
    magneticDeclination, magneticInclination, totalIntensity, magneticVectorX, magneticVectorY, magneticVectorZ, time = lb_photovoltaics.GeoMag(latitude, longitude, elevation, date, coefficients)     #(self, dlat, dlon, h=0, time=datetime.date.today()): # latitude (decimal degrees), longitude (decimal degrees), altitude (feet), datetime.date
    trueNorthDeg = magneticNorthDeg + magneticDeclination
    if trueNorthDeg > 360:
        trueNorthDeg = trueNorthDeg - 360
    elif trueNorthDeg < 0:
        trueNorthDeg = 360 + trueNorthDeg
    trueNorthRad, trueNorthVec = angle2northClockwise(trueNorthDeg)
    
    magneticFieldVec = Rhino.Geometry.Vector3d(magneticVectorX, magneticVectorY, magneticVectorZ)
    
    return round(trueNorthDeg,2), trueNorthVec, magneticDeclination, magneticFieldVec


def printOutput(locationName, latitude, longitude, timeZone, elevation, magneticNorthDeg, date, COFfileName):
    dateString = "%s,%s,%s" % (date.month, date.day, date.year)
    resultsCompletedMsg = "PVsurface component results successfully completed!"
    printOutputMsg = \
    """
Input data:

Location: %s
Latitude: %s
Longitude: %s
Time zone: %s
Elevation: %s

North: %s
Date: %s
COF file: %s
    """ % (locationName, latitude, longitude, timeZone, elevation, magneticNorthDeg, dateString, COFfileName)
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        if _location:
            latitude, longitude, timeZone, elevation, locationName, validLocationData, printMsg = getLocationData(_location)
            if validLocationData:
                magneticNorthDeg, magneticNorthVec, date, coefficients, COFfileName, validInputData, printMsg = checkInputData(magneticNorth_, date_, COFfile_)
                if validInputData:
                    trueNorth, trueNorthVec, magneticDeclination, magneticFieldVec = main(latitude, longitude, elevation, magneticNorthDeg, magneticNorthVec, date, coefficients)
                    printOutput(locationName, latitude, longitude, timeZone, elevation, magneticNorthDeg, date, COFfileName)
                else:
                    print printMsg
                    ghenv.Component.AddRuntimeMessage(level, printMsg)
            else:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
        else:
            printMsg = "Please input \"location\" output from Ladybug's \"Import epw\" component.\nOr create your own location with Ladybug's \"Construct Location\" component."
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        printMsg = "You need a newer version of Ladybug to use this component." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag the Ladybug_Ladybug component " + \
            "into the canvas and try again."
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
else:
    printMsg = "First please let the Ladybug fly..."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)
    