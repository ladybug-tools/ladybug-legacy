# This is the heart of the Ladybug
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component carries all of Ladybug's main classes. Other components refer to these
classes to run the studies. Therefore, you need to let her fly before running the studies so the
classes will be copied to Rhino’s shared space. So let her fly!
-
Ladybug started by Mostapha Sadeghipour Roudsari is licensed
under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
Based on a work at https://github.com/mostaphaRoudsari/ladybug.
-
Check this link for more information about the license:
http://creativecommons.org/licenses/by-sa/3.0/deed.en_US
-
Source code is available at:
https://github.com/mostaphaRoudsari/ladybug
-
Provided by Ladybug 0.0.35
    
    Args:
        letItFly: Set Boolean to True to let the Ladybug fly!
    Returns:
        report: Current Ladybug mood!!!
"""

ghenv.Component.Name = "Ladybug_Ladybug"
ghenv.Component.NickName = 'Ladybug'
ghenv.Component.Message = 'VER 0.0.35\nJAN_15_2013'


import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import math
import shutil
import sys
import os
import System.Threading.Tasks as tasks
import System
import time
from itertools import chain
import datetime
PI = math.pi


class Preparation(object):
    """ Set of functions to prepare the environment for running the studies"""
    def __init__(self):
        self.monthList = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        self.numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
        self.numOfHours = [24 * numOfDay for numOfDay in self.numOfDays]
        
    def checkUnits(self):
        units = sc.doc.ModelUnitSystem
        if `units` == 'Rhino.UnitSystem.Meters': conversionFactor = 1.00
        elif `units` == 'Rhino.UnitSystem.Centimeters': conversionFactor = 0.01
        elif `units` == 'Rhino.UnitSystem.Millimeters': conversionFactor = 0.001
        elif `units` == 'Rhino.UnitSystem.Feet': conversionFactor = 0.305
        elif `units` == 'Rhino.UnitSystem.Inches': conversionFactor = 0.0254
        else:
            print 'Kidding me! Which units are you using?'+ `units`+'?'
            print 'Please use Meters, Centimeters, Millimeters, Inches or Feet'
            return
        print 'Current document units is in', sc.doc.ModelUnitSystem
        print 'Conversion to Meters will be applied = ' + "%.3f"%conversionFactor
        return conversionFactor
    
    def angle2north(self, north):
        try:
            # print north
            northVector = rc.Geometry.Vector3d.YAxis
            northVector.Rotate(math.radians(float(north)), rc.Geometry.Vector3d.ZAxis)
            northVector.Unitize()
            return math.radians(float(north)), northVector
        except Exception, e:
            # print `e`
            try:
                northVector = rc.Geometry.Vector3d(north)
                northVector.Unitize()
                return rc.Geometry.Vector3d.VectorAngle(rc.Geometry.Vector3d.YAxis, northVector, rc.Geometry.Plane.WorldXY), northVector
            except:
                    #w = gh.GH_RuntimeMessageLevel.Warning
                    #ghenv.Component.AddRuntimeMessage(w, "North should be a number or a vector!")
                    return 0, rc.Geometry.Vector3d.YAxis
    
    def setScale(self, scale, conversionFac = 1):
        try:
            if float(scale)!=0:
                try:scale = float(scale)/conversionFac
                except: scale = 1/conversionFac
            else: scale = 1/conversionFac
        except: scale = 1/conversionFac
        return scale
    
    
    def readRunPeriod(self, runningPeriod, p = True, full = True):
        if not runningPeriod or runningPeriod[0]==None:
            runningPeriod = ((1, 1, 1),(12, 31, 24))
            
        stMonth = runningPeriod [0][0]; stDay = runningPeriod [0][1]; stHour = runningPeriod [0][2];
        endMonth = runningPeriod [1][0]; endDay = runningPeriod [1][1]; endHour = runningPeriod [1][2];
        
        if p:
            if full: print 'Simulation period is:', self.hour2Date(self.date2Hour(stMonth, stDay, stHour)), ' to ', self.hour2Date(self.date2Hour(endMonth, endDay, endHour))
            else: print self.hour2Date(self.date2Hour(stMonth, stDay, stHour)), ' - ', self.hour2Date(self.date2Hour(endMonth, endDay, endHour))
             
        return stMonth, stDay, stHour, endMonth, endDay, endHour
    
    
    def checkHour(self, hour):
        if hour<1: hour = 1
        elif hour%24==0: hour = 24
        else: hour = hour%24
        return hour

    def checkMonth(self, month):
        if month<1: month = 1
        elif month%12==0: month = 12
        else: month = month%12
        return month

    def checkDay(self, day, month):
        if day<1: day = 1
        if month == 2 and day > 28: day = 28
        elif (month == 4 or month == 6 or month == 9 or month == 11) and day > 30: day = 30
        elif day > 31: day = 31
        return day
    
    def hour2Date(self, hour, alternate = False):
        numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
        numOfHours = [24 * numOfDay for numOfDay in numOfDays]
        #print hour/24
        if hour%8760==0: return `31`+ ' ' + 'DEC' + ' 24:00'
    
        for h in range(len(numOfHours)-1):
            if hour <= numOfHours[h+1]: month = self.monthList[h]; break
        try: month
        except: month = self.monthList[h] # for the last hour of the year
    
        if (hour)%24 == 0:
            day = int((hour - numOfHours[h]) / 24)
            time = `24` + ':00'
            hour = 24
        else:
            day = int((hour - numOfHours[h]) / 24) + 1
            minutes = `int(round((hour - math.floor(hour)) * 60))`
            if len(minutes) == 1: minutes = '0' + minutes
            time = `int(hour%24)` + ':' + minutes
        if alternate:
            time = hour%24
            month = self.monthList.index(month)
            return day, month, time
            
        return (`day` + ' ' + month + ' ' + time)

    def tupleStr2Tuple(self, str):
        strSplit = str[1:-1].split(',')
        return (int(strSplit[0]), int(strSplit[1]), int(strSplit[2]))

    def date2Hour(self, month, day, hour):
        # fix the end day
        numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        # dd = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        JD = numOfDays[int(month)-1] + int(day)
        return (JD - 1) * 24 + hour
    
    def getHour(self, JD, hour):
        return (JD - 1) * 24 + hour
    
    def getJD(self, month, day):
        numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        return numOfDays[int(month)-1] + int(day)
        
    def getCenPt(self, cenPt):
        if cenPt is None:
            return rc.Geometry.Point3d.Origin
        else:
            try: return rs.coerce3dpoint(cenPt)
            except:
                try: return rc.Geometry.Point3d(cenPt)
                except: return rc.Geometry.Point3d.Origin
    
    def readLegendParameters(self, legendPar, getCenter = True):
        if legendPar == []: legendPar = [None] * 6
        if legendPar[0] == None: lowB = 'min'
        elif legendPar[0] == 'min': lowB = 'min'
        else: lowB = float(legendPar[0])
        if legendPar[1] == None: highB = 'max'
        elif legendPar[1] == 'max': highB = 'max'
        else: highB = int(legendPar[1])
        if legendPar[2] == None: numSeg = 11
        else: numSeg = float(legendPar[2])
        if not legendPar[3] or legendPar[3][0] == None:
            customColors = [System.Drawing.Color.FromArgb(75, 107, 169), System.Drawing.Color.FromArgb(115, 147, 202),
                        System.Drawing.Color.FromArgb(170, 200, 247), System.Drawing.Color.FromArgb(193, 213, 208),
                        System.Drawing.Color.FromArgb(245, 239, 103), System.Drawing.Color.FromArgb(252, 230, 74),
                        System.Drawing.Color.FromArgb(239, 156, 21), System.Drawing.Color.FromArgb(234, 123, 0),
                        System.Drawing.Color.FromArgb(234, 74, 0), System.Drawing.Color.FromArgb(234, 38, 0)]
        else: customColors = legendPar[3]
        
        # get the base point
        if legendPar[4] or getCenter: legendBasePoint = self.getCenPt(legendPar[4])
        else: legendBasePoint = None
        
        # print len(legendPar)
        if legendPar[5] == None or float(legendPar[5])==0: legendScale = 1
        else: legendScale = legendPar[5]
        
        return lowB, highB, numSeg, customColors, legendBasePoint, legendScale
    
    def readOrientationParameters(self, orientationStudyP):
        try:
            runOrientation = orientationStudyP[0]
            if orientationStudyP[1] != True: rotateContext = False
            else: rotateContext = True
            
            if orientationStudyP[2] != None: rotationBasePt = rs.coerce3dpoint(orientationStudyP[2])
            else: rotationBasePt = 'set2center'
            angles = orientationStudyP[3]
            return runOrientation, rotateContext, rotationBasePt, angles
        
        except:
            return False, False, None, [0]
    
    def cleanAndCoerceList(self, brepList):
        """ This definition clean the list and add them to RhinoCommon"""
        outputMesh = []
        outputBrep = []
        
        for id in brepList:
            if rs.IsMesh(id):
                geo = rs.coercemesh(id)
                if geo is not None:
                    outputMesh.append(geo)
                    try: rs.DeleteObject(id)
                    except: pass
                
            elif rs.IsBrep(id):
                geo = rs.coercebrep(id)
                if geo is not None:
                    outputBrep.append(geo)
                    try: rs.DeleteObject(id)
                    except: pass
                    
                else:
                    # the idea was to remove the problematice surfaces
                    # not all the geometry which is not possible since
                    # badGeometries won't pass rs.IsBrep()
                    tempBrep = []
                    surfaces = rs.ExplodePolysurfaces(id)
                    for surface in surfaces:
                        geo = rs.coercesurface(surface)
                        if geo is not None:
                            tempBrep.append(geo)
                            try: rs.DeleteObject(surface)
                            except: pass
                    geo = rc.Geometry.Brep.JoinBreps(tempBrep, sc.doc.ModelAbsoluteTolerance)
                    for Brep in tempBrep:
                        Brep.Dispose()
                        try: rs.DeleteObject(id)
                        except: pass
                    outputBrep.append(geo)
        return outputMesh, outputBrep
    
    def flattenList(self, l):
        return list(chain.from_iterable(l))
    
    def makeWorkingDir(self, workingDir, default = "c:\\ladybug"):
        if not workingDir: workingDir = default
        if not os.path.exists(workingDir):
            try:
                os.makedirs(workingDir)
                # print 'current working directory is set to: ', workingDir
            except:
                print 'cannot create the working directory as: ', workingDir + \
                      '\nPlease set a new working directory'
                return -1
        return workingDir

    def downloadGenCumulativeSky(self, workingDir):
        ## download File
        def downloadFile(url, workingDir):
            import urllib
            webFile = urllib.urlopen(url)
            localFile = open(workingDir + '/' + url.split('/')[-1], 'wb')
            localFile.write(webFile.read())
            webFile.close()
            localFile.close()

        # download the Gencumulative Sky
        if not os.path.isfile(workingDir + '\GenCumulativeSky.exe'):
            try:
                print 'Downloading GenCumulativeSky.exe to ', workingDir
                downloadFile('http://dl.dropbox.com/u/16228160/GenCumulativeSky/GenCumulativeSky.exe', workingDir)
                print 'Download complete!'
            except:
                allSet = False
                print 'Download failed!!! You need GenCumulativeSky.exe to use this component.' + \
                '\nPlease check your internet connection, and try again!'
        else:
            pass
            #print 'GenCumulativeSky.exe is already available at ', workingDir + \
            #'\nPlease make sure you are using the latest version of GenCumulativeSky.exe'

    def separateList(self, list, key):
            indexList = []; listInfo = [];
            for item in range(len(list)):
                if list[item] == key:
                    indexList.append(item)
                    listInfo.append(list[item : item+7])
            # in case of numbers with no str information
            if len(indexList) == 0:
                indexList = [-7, len(list)];
                listInfo = [key, 'somewhere','someData','?','?','?','?']
            else: indexList.append(len(list))
            #
            return indexList, listInfo

    ## read epw file
    def epwLocation(self, epw_file):
        epwfile = open(epw_file,"r")
        headline = epwfile.readline()
        csheadline = headline.split(',')
        while 1>0: #remove empty cells from the end of the list if any
            try: float(csheadline[-1]); break
            except: csheadline.pop()
        locName = ''
        for hLine in range(1,4):
            if csheadline[hLine] != '-':
                locName = locName + csheadline[hLine] + '_'
        locName = locName[:-1]
        lat = csheadline[-4]
        lngt = csheadline[-3]
        timeZone = csheadline[-2]
        elev = csheadline[-1][:-1]
        locationString = "Site:Location,\n" + \
            locName + ',\n' + \
            lat+',      !Latitude\n' + \
            lngt+',     !Longitude\n' + \
            timeZone+',     !Time Zone\n' + \
            elev + ';       !Elevation'
        epwfile.close
        return locName, lat, lngt, timeZone, locationString
    
    def separateHeader(self, inputList):
        num = []; str = []
        for item in inputList:
            try: num.append(float(item))
            except: str.append(item)
        return num, str
    
    strToBeFound = 'key:location/dataType/units/frequency/startsAt/endsAt'
    
    def epwDataReader(self, epw_file, location = 'Somewhere!'):
        # weather data
        dbTemp = [self.strToBeFound, location, 'Dry Bulb Temperature', '°C', 'Hourly', (1, 1, 1), (12, 31, 24)];
        dewPoint = [self.strToBeFound, location, 'Dew Point Temperature', '°C', 'Hourly', (1, 1, 1), (12, 31, 24)];
        RH = [self.strToBeFound, location, 'Relative Humidity', '%', 'Hourly', (1, 1, 1), (12, 31, 24)]
        windSpeed = [self.strToBeFound, location, 'Wind Speed', 'm/s', 'Hourly', (1, 1, 1), (12, 31, 24)];
        windDir = [self.strToBeFound, location, 'Wind Direction', 'degrees', 'Hourly', (1, 1, 1), (12, 31, 24)];
        dirRad = [self.strToBeFound, location, 'Direct Normal Radiation', 'Wh/m2', 'Hourly', (1, 1, 1), (12, 31, 24)];
        difRad = [self.strToBeFound, location, 'Diffuse Horizontal Radiation', 'Wh/m2', 'Hourly', (1, 1, 1), (12, 31, 24)];
        glbRad = [self.strToBeFound, location, 'Global Horizontal Radiation', 'Wh/m2', 'Hourly', (1, 1, 1), (12, 31, 24)];
        dirIll = [self.strToBeFound, location, 'Direct Normal Illuminance', 'lux', 'Hourly', (1, 1, 1), (12, 31, 24)];
        difIll = [self.strToBeFound, location, 'Diffuse Horizontal Illuminance', 'lux', 'Hourly', (1, 1, 1), (12, 31, 24)];
        glbIll = [self.strToBeFound, location, 'Global Horizontal Illuminance', 'lux', 'Hourly', (1, 1, 1), (12, 31, 24)];
        cloudCov = [self.strToBeFound, location, 'Total Cloud Cover', 'tenth', 'Hourly', (1, 1, 1), (12, 31, 24)];
        rainDepth = [self.strToBeFound, location, 'Liquid Precipitation Depth', 'mm', 'Hourly', (1, 1, 1), (12, 31, 24)];
        epwfile = open(epw_file,"r")
        lnum = 1 # line number
        for line in epwfile:
            if lnum > 8:
                dbTemp.append(float(line.split(',')[6]))
                dewPoint.append(float(line.split(',')[7]))
                RH.append(float(line.split(',')[8]))
                windSpeed.append(float(line.split(',')[21]))
                windDir.append(float(line.split(',')[20]))
                dirRad.append(float(line.split(',')[14]))
                difRad.append(float(line.split(',')[15]))
                glbRad.append(float(line.split(',')[13]))
                dirIll.append(float(line.split(',')[17]))
                difIll.append(float(line.split(',')[18]))
                glbIll.append(float(line.split(',')[16]))
                cloudCov.append(float(line.split(',')[22]))
                try:
                    if float(line.split(',')[33])!=999: rainDepth.append(float(line.split(',')[33]))
                    else: rainDepth.append(0.0)
                except: pass
            lnum += 1
        return dbTemp, dewPoint, RH, windSpeed, windDir, dirRad, difRad, glbRad, dirIll, difIll, glbIll, cloudCov, rainDepth
    
    ##### Start of Gencumulative Sky
    def removeBlank(self, str):
        newStr = ''
        chars = [' ', ',', '.', '-', '   ', '    ', '\\', '/']
        for c in str:
            if c in chars: newStr = newStr + '_'
            else: newStr = newStr + c
        return newStr
    
    def removeBlankLight(self, str):
        newStr = ''
        chars = [' ', ',', '.', '-', '   ', '    ']
        for c in str:
            if c in chars: newStr = newStr + '_'
            else: newStr = newStr + c
        return newStr
    
    def copyFile(self, inputFile, copyFullpath):
        if not os.path.isfile(copyFullpath): shutil.copyfile(inputFile, copyFullpath)
    
    def genCumSkyStr(self, runningPeriod, subWorkingDir, workingDir, newLocName, lat, lngt, timeZone):
        # read running period
        stMonth, stDay, stHour, endMonth, endDay, endHour = self.readRunPeriod(runningPeriod)
        
        # sun modes: +s1 is "smeared sun" approach, and +s2 use "binned sun" approach
        # read this paper for more information:
        # http://plea-arch.net/PLEA/ConferenceResources/PLEA2004/Proceedings/p1153final.pdf
        sunModes = ['+s1', '+s2']
        batchStr = workingDir[0:2] + "\ncd " + subWorkingDir + "\n"
        for sunMode in sunModes:
            calFileName = subWorkingDir + "\\" + newLocName + '_' + sunMode[-1] + '.cal'
            reportFileName = subWorkingDir + "\\" + newLocName + '_' + sunMode[-1] + '_report.txt' 
            newLine = workingDir + "\GenCumulativeSky " + sunMode + \
                " -a " + lat + \
                " -o " + `-1 * float(lngt)` + \
                " -m " + `-15* float(timeZone)` + \
                " -p -E -time " + `stHour` + " " + `endHour` + \
                " -date " + `stMonth` + " " + `stDay` + \
                " " + `endMonth` + " " + `endDay` + \
                " " + subWorkingDir + "\\" + newLocName + '.epw' + \
                " 1> " + calFileName + \
                " 2> " + reportFileName + "\n"
            batchStr = batchStr + newLine
        batchStr = batchStr + 'cd\\'
        return batchStr
    
    def readCalFile(self, calFileName):
        # this functions comes from trial and error
        # Even though I figured out how to read it for GenCummulativeSky,
        # I still don't underestand the structure of a cal file 100%
        try:
            calRes = open(calFileName, "r")
            lines = calRes.readlines()
            segNum = [30, 30, 24, 24, 18, 12, 6, 1]
            strConv = [0.0435, 0.0416, 0.0474, 0.0407, 0.0429, 0.0445, 0.0455, 0.0344] #steradians conversion
            result = []
            for rowNum in range(7):
                countLine = 0
                for l in range(len(lines)):
                    if lines[l][:4] == 'row'+`rowNum`:
                        for ll in range(l+1,l+1+segNum[rowNum]):
                            result.append (strConv[rowNum] * float(lines[ll][0:-2]))
            for l in range(len(lines)):
                if lines[l][:4] == 'row7':
                    result.append(strConv[7] * float(lines[l][15:-5]))
                calRes.close()
            return result
        except:
            print "There is an error in the result file" #+ \
                    #"\nCheck the report file at " + reportFileName + \
                    #"\n\nEmail me at (sadeghipour@gmail.com) if you couldn't solve the problem."
            return -1
    
    def printReportFile(self, reportFileName):
        try:
            reportFile = open(reportFileName, "r")
            SUH = []; lineCount = 0
            for line in reportFile:
                if lineCount == 0:
                    print line[:-1] + "."
                    for ch in line:
                        try: num = int(ch); SUH.append(num)
                        except: pass
                    break
            #sunUpHours = 0; numCount = 0
            #for num in SUH:
            #    sunUpHours = sunUpHours + num * (10 ** (len(SUH) - numCount -1))
            #    numCount += 1
            #reportFile.close()
            #return sunUpHours 
        except:
            print "There is no report file!!"
            return -1
            
    #### End of Gencumulative Sky
    
    # Tregenza Sky Dome
    def generateTregenzaSkyGeo(self, cenPt, scale):
        patches = []; baseArcs = []; Pts = [];
        numSeg = [30, 30, 24, 24, 18, 12, 6, 1]
        # draw the base arc
        basePlane = rs.PlaneFromNormal(cenPt,(1,0,0))
        mainArc = rs.AddArc(basePlane, 100 * scale , 90)
        startPt = rs.CurveStartPoint(mainArc)
        endPt = rs.CurveEndPoint(mainArc)
        Pts.append(startPt)
    
        # base curves
        for angle in rs.frange(5.75,90, 5.75):
            rotatedPt = rs.RotateObject(rs.AddPoint(startPt[0],startPt[1],startPt[2]), cenPt, angle, (1,0,0), True)
            Pts.append(rotatedPt)
        Pts.append(endPt)
    
        for i in range(0,16,2):
            arc = rs.AddArc3Pt(Pts[0+i], Pts[2+i], Pts[1+i])
            baseArcs.append(arc)
    
        assert len(baseArcs) == 8
        revAx = rs.AddLine(cenPt,endPt)
        for j in range(len(baseArcs)):
            incDeg = (360/numSeg[j])/2
            rotationDeg = -(360/numSeg[j])
            startArc = rs.RotateObject(baseArcs[j], cenPt, incDeg, rs.VectorCreate(endPt,cenPt), False)
            for num in range(numSeg[j]):
                patches.append(rs.AddRevSrf(startArc, revAx, rotationDeg + (rotationDeg * num), (rotationDeg * num)))
        
        patchesInRC = [rs.coercesurface(patch) for patch in patches]
        
        return patchesInRC

    
    def genRadRoseArrows(self, movingVectors, radResult, cenPt, sc, internalSc = 0.2):
        radArrows = []; vecNum = 0
        # this is a copy/paste. should be fixed later
        cenPt = rs.AddPoint(cenPt.X, cenPt.Y, cenPt.Z)
        for vec in movingVectors:
            movingVec = (sc* internalSc * vec * radResult[vecNum])
            ptMoveDis = 20 * internalSc
            ptMovingVec_right = rs.VectorRotate((vec * sc * ptMoveDis), 90, (0,0,1))
            ptMovingVec_left = rs.VectorRotate((vec * sc * ptMoveDis), -90, (0,0,1))
            arrowEndpt = rs.MoveObject(rs.CopyObject(cenPt), movingVec)
            baseLine = rs.AddLine(cenPt, arrowEndpt)
            pt = rs.EvaluateCurve(baseLine, 0.85* rs.CurveLength(baseLine))
            pt = rs.AddPoint(pt[0], pt[1], pt[2])
            rightPt = rs.MoveObject(rs.CopyObject(pt), ptMovingVec_right)
            leftPt = rs.MoveObject(rs.CopyObject(pt), ptMovingVec_left)
            # change this to mesh
            # arrowSrf = rs.AddSrfPt((cenPt, rightPt, arrowEndpt, leftPt))
            
            tempMesh = rc.Geometry.Mesh()
            tempMesh.Vertices.Add(rs.coerce3dpoint(cenPt)) #0
            tempMesh.Vertices.Add(rs.coerce3dpoint(rightPt)) #1
            tempMesh.Vertices.Add(rs.coerce3dpoint(arrowEndpt)) #2
            tempMesh.Vertices.Add(rs.coerce3dpoint(leftPt)) #3
            tempMesh.Faces.AddFace(0, 1, 2, 3)
            
            
            radArrows.append(tempMesh)
            vecNum += 1
        
        return radArrows
    
    TregenzaPatchesNormalVectors = [
    (0.0,0.994969,0.100188),(0.206866,0.973226,0.100188),
    (0.40469,0.908949,0.100188), (0.584828,0.804946,0.100188),
    (0.739406,0.665764,0.100188), (0.861668,0.497484,0.100188),
    (0.946271,0.307462,0.100188), (0.989518,0.104003,0.100188),
    (0.989518,-0.104003,0.100188), (0.946271,-0.307462,0.100188),
    (0.861668,-0.497484,0.100188), (0.739406,-0.665764,0.100188),
    (0.584828,-0.804946,0.100188), (0.40469,-0.908949,0.100188),
    (0.206866,-0.973226,0.100188), (0.00,-0.994969,0.100188),
    (-0.206866,-0.973226,0.100188), (-0.40469,-0.908949,0.100188),
    (-0.584828,-0.804946,0.100188), (-0.739406,-0.665764,0.100188),
    (-0.861668,-0.497484,0.100188), (-0.946271,-0.307462,0.100188),
    (-0.989518,-0.104003,0.100188), (-0.989518,0.104003,0.100188),
    (-0.946271,0.307462,0.100188), (-0.861668,0.497484,0.100188),
    (-0.739406,0.665764,0.100188), (-0.584828,0.804946,0.100188),
    (-0.40469,0.908949,0.100188), (-0.206866,0.973226,0.100188),
    (0.0,0.95502,0.296542), (0.19856,0.93415,0.296542),
    (0.388442,0.872454,0.296542), (0.561347,0.772627,0.296542),
    (0.709718,0.639033,0.296542), (0.827072,0.47751,0.296542),
    (0.908278,0.295117,0.296542), (0.949788,0.099827,0.296542),
    (0.949788,-0.099827,0.296542), (0.908278,-0.295117,0.296542),
    (0.827072,-0.47751,0.296542), (0.709718,-0.639033,0.296542),
    (0.561347,-0.772627,0.296542), (0.388442,-0.872454,0.296542),
    (0.19856,-0.93415,0.296542), (0.00,-0.95502,0.296542),
    (-0.19856,-0.93415,0.296542), (-0.388442,-0.872454,0.296542),
    (-0.561347,-0.772627,0.296542), (-0.709718,-0.639033,0.296542),
    (-0.827072,-0.47751,0.296542), (-0.908278,-0.295117,0.296542),
    (-0.949788,-0.099827,0.296542), (-0.949788,0.099827,0.296542),
    (-0.908278,0.295117,0.296542), (-0.827072,0.47751,0.296542),
    (-0.709718,0.639033,0.296542), (-0.561347,0.772627,0.296542),
    (-0.388442,0.872454,0.296542), (-0.19856,0.93415,0.296542),
    (0.00,0.876727,0.480989), (0.226914,0.846853,0.480989),
    (0.438363,0.759268,0.480989), (0.619939,0.619939,0.480989),
    (0.759268,0.438363,0.480989), (0.846853,0.226914,0.480989),
    (0.876727,0.00,0.480989), (0.846853,-0.226914,0.480989),
    (0.759268,-0.438363,0.480989), (0.619939,-0.619939,0.480989),
    (0.438363,-0.759268,0.480989), (0.226914,-0.846853,0.480989),
    (1.9641e-16,-0.876727,0.480989), (-0.226914,-0.846853,0.480989),
    (-0.438363,-0.759268,0.480989), (-0.619939,-0.619939,0.480989),
    (-0.759268,-0.438363,0.480989), (-0.846853,-0.226914,0.480989),
    (-0.876727,-2.3838e-16,0.480989), (-0.846853,0.226914,0.480989),
    (-0.759268,0.438363,0.480989), (-0.619939,0.619939,0.480989),
    (-0.438363,0.759268,0.480989), (-0.226914,0.846853,0.480989),
    (0.00,0.763232,0.646124), (0.197539,0.737226,0.646124),
    (0.381616,0.660979,0.646124), (0.539687,0.539687,0.646124),
    (0.660979,0.381616,0.646124), (0.737226,0.197539,0.646124),
    (0.763232,0.00,0.646124), (0.737226,-0.197539,0.646124),
    (0.660979,-0.381616,0.646124), (0.539687,-0.539687,0.646124),
    (0.381616,-0.660979,0.646124), (0.197539,-0.737226,0.646124),
    (1.4285e-16,-0.763232,0.646124), (-0.197539,-0.737226,0.646124),
    (-0.381616,-0.660979,0.646124), (-0.539687,-0.539687,0.646124),
    (-0.660979,-0.381616,0.646124), (-0.737226,-0.197539,0.646124),
    (-0.763232,-1.7471e-16,0.646124), (-0.737226,0.197539,0.646124),
    (-0.660979,0.381616,0.646124), (-0.539687,0.539687,0.646124),
    (-0.381616,0.660979,0.646124), (-0.197539,0.737226,0.646124),
    (0.00,0.619094,0.785317), (0.211743,0.581758,0.785317),
    (0.397946,0.474253,0.785317), (0.536151,0.309547,0.785317),
    (0.609689,0.107505,0.785317), (0.609689,-0.107505,0.785317),
    (0.536151,-0.309547,0.785317), (0.397946,-0.474253,0.785317),
    (0.211743,-0.581758,0.785317), (1.6070e-16,-0.619094,0.785317),
    (-0.211743,-0.581758,0.785317), (-0.397946,-0.474253,0.785317),
    (-0.536151,-0.309547,0.785317), (-0.609689,-0.107505,0.785317),
    (-0.609689,0.107505,0.785317), (-0.536151,0.309547,0.785317),
    (-0.397946,0.474253,0.785317), (-0.211743,0.581758,0.785317),
    (0.00,0.450098,0.892979), (0.225049,0.389797,0.892979),
    (0.389797,0.225049,0.892979), (0.450098,1.4396e-16,0.892979),
    (0.389797,-0.225049,0.892979), (0.225049,-0.389797,0.892979),
    (0.00,-0.450098,0.892979), (-0.225049,-0.389797,0.892979),
    (-0.389797,-0.225049,0.892979), (-0.450098,-1.7745e-16,0.892979),
    (-0.389797,0.225049,0.892979), (-0.225049,0.389797,0.892979),
    (0.00,0.263031,0.964787), (0.227792,0.131516,0.964787),
    (0.227792,-0.131516,0.964787), (1.0713e-16,-0.263031,0.964787),
    (-0.227792,-0.131516,0.964787), (-0.227792,0.131516,0.964787),
    (0.0,0.0,1.0)]


class Sunpath(object):
    """
    The sun-path Class is a Python version of RADIANCE sun-path script by Greg Ward. RADIANCE source code can be accessed at:
    http://www.radiance-online.org/download-install/CVS%20source%20code
    The difference of the results with NREL version is less than 1 degree
    """
    def __init__(self):
        pass
    
    def initTheClass(self, latitude, northAngle = 0, cenPt = rc.Geometry.Point3d.Origin, scale = 100, longtitude = 0, timeZone = 0):
        self.solLat = math.radians(float(latitude));
        self.s_longtitude =  math.radians(longtitude) #2.13; # site longtitude (radians)
        self.s_meridian = math.radians(timeZone * 15) #2.13 #.0944; # standard meridian (radians)
        self. angle2North = northAngle
        self.basePlane = rc.Geometry.Plane(cenPt, rc.Geometry.Vector3d.ZAxis)
        self.cenPt = cenPt
        self.scale = scale

    def JulianDate(self, month, day):
        numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        self.JD = numOfDays[int(month)-1] + int(day)

    def solarTime(self, hour):
        self.solTime = (0.170 * math.sin((4 * PI/373) * (self.JD - 80))
        - 0.129 * math.sin((2 * PI/355) * (self.JD - 8))
        + 12 * (self.s_meridian - self.s_longtitude) / PI) - hour  # Here!

    def solarDeclination(self):
        self.solDec = 0.4093 * math.sin((2 * PI / 368) * (self.JD - 81))

    def solarAlt(self):
        self.solAlt = math.asin(math.sin(self.solLat) * math.sin(self.solDec)
        - math.cos(self.solLat) * math.cos(self.solDec) * math.cos(self.solTime * (PI/12)))

    def solarAz(self):
        self.solAz = -math.atan2(math.cos(self.solDec) * math.sin(self.solTime * (PI/12)),
        -math.cos(self.solLat) * math.sin(self.solDec) - math.sin(self.solLat)
        * math.cos(self.solDec) * math.cos(self.solTime * (PI/12)))

    def solInitOutput(self, month, day, hour):
        self.JulianDate(month, day)
        self.solarTime(hour)
        self.solarDeclination()
        self.solarAlt()
        self.solarAz()

    def sunPosPt(self, sunScale = 1):
        # print 'altitude is:', math.degrees(solAlt), 'and azimuth is:', math.degrees(solAz)
        basePoint = rc.Geometry.Point3d.Add(self.cenPt,rc.Geometry.Vector3f(0,self.scale,0))
        basePoint = rc.Geometry.Point(basePoint)
        basePoint.Rotate(self.solAlt, rc.Geometry.Vector3d.XAxis, self.cenPt)
        basePoint.Rotate((self.angle2North + self.solAz) + PI, rc.Geometry.Vector3d.ZAxis, self.cenPt)
        sunVector = rc.Geometry.Vector3d(self.cenPt - basePoint.Location)
        sunVector.Unitize()
        
        raduis = 3 * sunScale
        sunSphere = rc.Geometry.Sphere(basePoint.Location, raduis)
        sunSphereMesh = rc.Geometry.Mesh.CreateFromSphere(sunSphere, 10, 10)
        return sunSphereMesh, sunVector, basePoint.Location

    def drawDailyPath(self, month, day):
        # find the sun position for midnight, noon - 10 min, noon + 10 min!
        hours = [0, 11.9, 12.1]
        sunP = []
        validCircle =  False
        for hour in hours:
            self.solInitOutput(month, day, hour)
            sunPos = self.sunPosPt()[2]
            sunP.append(sunPos)
            if sunPos.Z > self.cenPt.Z: validCircle = True
        if validCircle:
            # draw the circle base on these three points
            circle = rc.Geometry.Circle(*sunP)
            # intersect with the plan
            intersection = rc.Geometry.Intersect.Intersection.PlaneCircle(self.basePlane, circle)
        
            #if intersection draw the new curve for intersections and noon
            if intersection[1] != intersection[2]:
                startPt = circle.PointAt(intersection[1])
                endPt = circle.PointAt(intersection[2])
                midPt = sunP[1]
                return rc.Geometry.Arc(startPt, midPt, endPt)
            else:
                # add to check to be above the plane
                return circle
        else:
                pass

    def drawSunPath(self):
        # draw daily curves for 21st of all the months
        
        monthlyCrvs = []
        for m in range(1,13):
            crv = self.drawDailyPath(m, 21)
            if crv: monthlyCrvs.append(crv)
        
        # draw hourly curves for each of hours for 1st and 21st of all month
        hourlyCrvs = []
        days = [1, 7, 14, 21]
        sunP = []; selHours = []
        if math.degrees(self.solLat)>0: month = 6
        else: month = 12
        
        # find the hours that the sun is up
        for hour in range(0,25):
            self.solInitOutput(month, 21, hour)
            if self.sunPosPt()[2].Z > self.cenPt.Z: selHours.append(hour)
        
        for hour in selHours:
            for day in days:
                sunP = []
                for month in range(1,13):
                    self.solInitOutput(month, day, hour)
                    sunP.append(self.sunPosPt()[2])
            sunP.append(sunP[0])
            knotStyle = rc.Geometry.CurveKnotStyle.UniformPeriodic
            crv = rc.Geometry.Curve.CreateInterpolatedCurve(sunP, 3, knotStyle)
            intersectionEvents = rc.Geometry.Intersect.Intersection.CurvePlane(crv, self.basePlane, sc.doc.ModelAbsoluteTolerance)
            
            try:
                if len(intersectionEvents) != 0:
                    crvDomain = crv.Domain
                    crv1 = rc.Geometry.Curve.Trim(crv, intersectionEvents[0].ParameterA, intersectionEvents[1].ParameterA)
                    crv2 = rc.Geometry.Curve.Trim(crv, intersectionEvents[1].ParameterA, intersectionEvents[0].ParameterA)
                    # calculate the bounding box to find thr center
                    
                    pt1 = ResultVisualization().calculateBB([crv1])[1]
                    pt2 = ResultVisualization().calculateBB([crv2])[1] 
                    
                    if pt1.Z > pt2.Z: crv = crv1
                    else: crv = crv2
            except: pass
            
            if crv: hourlyCrvs.append(crv)
        
        return monthlyCrvs, hourlyCrvs
        
        
    def drawBaseLines(self):
        circle1 = rc.Geometry.Circle(self.basePlane, self.scale)
        circle2 = rc.Geometry.Circle(self.basePlane, 1.03 * self.scale)
        lines= [] # will fix this part later. circles and lines will have different graphics
        lines.append(circle1.ToNurbsCurve())
        lines.append(circle2.ToNurbsCurve())
        # prepare direction lines
        movingVec = rc.Geometry.Vector3d.YAxis
        movingVec.Rotate(self.angle2North, rc.Geometry.Vector3d.ZAxis)
        shortNLineStart = rc.Geometry.Point3d.Add(self.cenPt, movingVec * 0.97 * self.scale)
        shortNLineEnd = rc.Geometry.Point3d.Add(self.cenPt, movingVec * 1.07 * self.scale)
        
        for i in range(4):
            northLine = rc.Geometry.Line(self.cenPt, movingVec, 1.1 * self.scale)
            shortNorthLine = rc.Geometry.Line(shortNLineStart, shortNLineEnd)
            xf = rc.Geometry.Transform.Rotation(PI/2 * i, rc.Geometry.Vector3d.ZAxis, self.cenPt)
            shortxf = rc.Geometry.Transform.Rotation(PI/2 * i + PI/4, rc.Geometry.Vector3d.ZAxis, self.cenPt)
            northLine.Transform(xf)
            shortNorthLine.Transform(shortxf)
            lines.append(northLine.ToNurbsCurve())
            lines.append(shortNorthLine.ToNurbsCurve())
        
        return lines


class MeshPreparation(object):
    
    def parallel_makeSurfaceMesh(self, brep, gridSize):
        ## mesh breps
        def makeMeshFromSrf(i, inputBrep):
            try:
                mesh[i] = rc.Geometry.Mesh.CreateFromBrep(inputBrep, meshParam)
                inputBrep.Dispose()
            except:
                print 'Error in converting Brep to Mesh...'
                pass

        # prepare bulk list for each surface
        mesh = [None] * len(brep)

        # set-up mesh parameters for each surface based on surface size
        aspectRatio = 1
        meshParam = rc.Geometry.MeshingParameters.Default
        rc.Geometry.MeshingParameters.MaximumEdgeLength.__set__(meshParam, (gridSize))
        rc.Geometry.MeshingParameters.MinimumEdgeLength.__set__(meshParam, (gridSize))
        rc.Geometry.MeshingParameters.GridAspectRatio.__set__(meshParam, aspectRatio)
    
        ## Call the mesh function
        if 1 < 0: #parallel: # for some reason parallel meshing gives error
            tasks.Parallel.ForEach(xrange(len(brep)),makeMeshFromSrf)
        else:
            for i in range(len(mesh)):
                makeMeshFromSrf(i, brep[i])

        meshGeometries = mesh
        return meshGeometries
    
    def parallel_makeContextMesh(self, brep):
        ## mesh breps
        def makeMeshFromSrf(i, inputBrep):
            try:
                mesh[i] = rc.Geometry.Mesh.CreateFromBrep(inputBrep, meshParam)
                inputBrep.Dispose()
            except:
                print 'Error in converting Brep to Mesh...'
                pass

        # prepare bulk list for each surface
        mesh = [None] * len(brep)

        # set-up mesh parameters for each surface based on surface size
        meshParam = rc.Geometry.MeshingParameters.Default #Coarse
        rc.Geometry.MeshingParameters.GridMaxCount.__set__(meshParam, 1)
        rc.Geometry.MeshingParameters.SimplePlanes.__set__(meshParam, True)
        rc.Geometry.MeshingParameters.GridAmplification.__set__(meshParam, 1.5)
    
        ## Call the mesh function
        if 1 < 0: #parallel: # for some reason parallel meshing gives error
            tasks.Parallel.ForEach(xrange(len(brep)),makeMeshFromSrf)
        else:
            for i in range(len(mesh)):
                makeMeshFromSrf(i, brep[i])

        meshGeometries = mesh
        return meshGeometries

    def parallel_testPointCalculator(self, analysisSrfs, disFromBase, parallel = True):
        # Mesh functions should be modified and be written interrelated as a class
        movingDis = disFromBase
    
        # preparing bulk lists
        testPoint = [[]] * len(analysisSrfs)
        srfNormals = [[]] * len(analysisSrfs)
        meshSrfCen = [[]] * len(analysisSrfs)
        meshSrfArea = [[]] * len(analysisSrfs)
        
        srfCount = 0
        for srf in analysisSrfs:
            testPoint[srfCount] = range(srf.Faces.Count)
            srfNormals[srfCount] = range(srf.Faces.Count)
            meshSrfCen[srfCount] = range(srf.Faces.Count)
            meshSrfArea[srfCount] = range(srf.Faces.Count)
            srfCount += 1

        try:
            def srfPtCalculator(i):
                # calculate face normals
                analysisSrfs[i].FaceNormals.ComputeFaceNormals()
                analysisSrfs[i].FaceNormals.UnitizeFaceNormals()
                
                for face in range(analysisSrfs[i].Faces.Count):
                    srfNormals[i][face] = (analysisSrfs[i].FaceNormals)[face] # store face normals
                    meshSrfCen[i][face] = analysisSrfs[i].Faces.GetFaceCenter(face) # store face centers
                    # calculate test points
                    if srfNormals[i][face]:
                        movingVec = rc.Geometry.Vector3f.Multiply(movingDis,srfNormals[i][face])
                        testPoint[i][face] = rc.Geometry.Point3d.Add(rc.Geometry.Point3d(meshSrfCen[i][face]), movingVec)
                    # make mesh surface, calculate the area, dispose the mesh and mass area calculation
                    tempMesh = rc.Geometry.Mesh()
                    tempMesh.Vertices.Add(analysisSrfs[i].Vertices[analysisSrfs[i].Faces[face].A]) #0
                    tempMesh.Vertices.Add(analysisSrfs[i].Vertices[analysisSrfs[i].Faces[face].B]) #1
                    tempMesh.Vertices.Add(analysisSrfs[i].Vertices[analysisSrfs[i].Faces[face].C]) #2
                    tempMesh.Vertices.Add(analysisSrfs[i].Vertices[analysisSrfs[i].Faces[face].D]) #3
                    tempMesh.Faces.AddFace(0, 1, 3, 2)
                    massData = rc.Geometry.AreaMassProperties.Compute(tempMesh)
                    meshSrfArea[i][face] = massData.Area
                    massData.Dispose()
                    tempMesh.Dispose()
                    
                    
        except:
            print 'Error in Extracting Test Points'
            pass
        
        # calling the function
        if parallel:
            tasks.Parallel.ForEach(range(len(analysisSrfs)),srfPtCalculator)
        else:
            for i in range(len(analysisSrfs)):
                srfPtCalculator(i)
    
        return testPoint, srfNormals, meshSrfArea

class RunAnalysisInsideGH(object):
    #
    def calRadRoseRes(self, tiltedRoseVectors, TregenzaPatchesNormalVectors, genCumSkyResult, groundRef = 0):
        radResult = []; sunUpHours = 1
        for vec in tiltedRoseVectors:
            radiation = 0; groundRadiation = 0; patchNum = 0;
            for patchVec in TregenzaPatchesNormalVectors:
                vecAngle = rs.VectorAngle(patchVec, vec)
                if  vecAngle < 90:
                    radiation = radiation + genCumSkyResult[patchNum] * math.cos(math.radians(vecAngle))
                    groundRadiation = groundRadiation + genCumSkyResult[patchNum] * math.cos(math.radians(vecAngle)) * (groundRef/100) * 0.5
                    #radchk.append((vecAngle))
                patchNum += 1
            # print radiation, groundRadiation 
            radResult.append((groundRadiation + radiation)/sunUpHours)
        return radResult
    
    def parallel_radCalculator(self, testPts, testVec, meshSrfArea, bldgMesh,
                                contextMesh, parallel, cumSkyResult, TregenzaPatches,
                                conversionFac, contextHeight = 2200000000000000,
                                northVector = rc.Geometry.Vector3d.YAxis):
        # preparing bulk lists
        radiation = [0] * len(testPts)
        groundRadiation = [0] * len(testPts)
        radResult = [0] * len(testPts)
        groundRef = 30
        intersectionStTime = time.time()
        YAxis = rc.Geometry.Vector3d.YAxis
        ZAxis = rc.Geometry.Vector3d.ZAxis
        # Converting vectors to Rhino 3D Vectors
        sunUpHours = cumSkyResult [-1]
        TregenzaVectors = []
        for vector in TregenzaPatches: TregenzaVectors.append(rc.Geometry.Vector3d(*vector))
        
        angle = rc.Geometry.Vector3d.VectorAngle(northVector, YAxis)
        if northVector.X > 0 : angle = -angle
        
        if angle != 0: [vec.Rotate(angle, ZAxis) for vec in TregenzaVectors]
        PI = math.pi
        
        try:
            def srfRadCalculator(i):
                patchNum = 0
                for patchVec in TregenzaVectors:
                    vecAngle = rc.Geometry.Vector3d.VectorAngle(patchVec, testVec[i]) # calculate the angle between the surface and sky patch
                    
                    if vecAngle < (PI/2):
                        check = 1; # this is simply here becuse I can't trust the break!! Isn't it stupid?
                        ray = rc.Geometry.Ray3d(testPts[i], patchVec) # generate the ray
                        
                        if bldgMesh!=None:
                            for bldg in bldgMesh: # bldgMesh is all joined as one mesh
                                if rc.Geometry.Intersect.Intersection.MeshRay(bldg, ray) >= 0.0: check = 0; break
                        
                        if check != 0 and contextMesh!=None: #and testPts[i].Z < contextHeight:
                            for bldg in contextMesh:
                                if rc.Geometry.Intersect.Intersection.MeshRay(bldg,ray) >= 0.0: check = 0; break
                        
                        if check != 0:
                            radiation[i] = radiation[i] + (cumSkyResult[patchNum] * math.cos(vecAngle))
                            # print groundRadiation
                            groundRadiation[i] = 0 #groundRadiation[i] + cumSkyResult[patchNum] * math.cos(vecAngle) * (groundRef/100) * 0.5
                    patchNum += 1
                
                radResult[i] = (groundRadiation[i] + radiation[i]) #/sunUpHours
        
        except:
            print 'Error in Radiation calculation...'
            pass
        
        # calling the function
        if parallel:
            tasks.Parallel.ForEach(range(len(testPts)),srfRadCalculator)
        else:
            for i in range(len(testPts)):
                srfRadCalculator(i)
        
        intersectionEndTime = time.time()
        print 'Radiation study time = ', ("%.3f" % (intersectionEndTime - intersectionStTime)), 'Seconds...'
        
        # total radiation
        totalRadiation = 0;
        for r in range(len(testPts)):
            totalRadiation = totalRadiation + (radResult[r] * meshSrfArea[r] * (conversionFac * conversionFac))
        
        return radResult, totalRadiation
    
    
    def parallel_sunlightHoursCalculator(self, testPts, testVec, meshSrfArea, bldgMesh, contextMesh, parallel, sunVectors, conversionFac, northVector):
        # preparing bulk lists
        sunlightHours = [0] * len(testPts)
        sunlightHoursResult = [0] * len(testPts)
        intersectionStTime = time.time()
        YAxis = rc.Geometry.Vector3d.YAxis
        ZAxis = rc.Geometry.Vector3d.ZAxis
        PI = math.pi
        
        # Converting vectors to Rhino 3D Vectors
        sunV = [];
        sunVectorCount = 0;
        for vector in sunVectors:
            if vector[2] < 0: print "Sun vector " + `sunVectorCount + 1` + " removed since it represents a vector with negative Z!" 
            else: sunV.append(rc.Geometry.Vector3d(vector))
            sunVectorCount =+ 1
            
        angle = rc.Geometry.Vector3d.VectorAngle(northVector, YAxis)
        if northVector.X > 0 : angle = -angle
        # print math.degrees(angle)
        if angle != 0: [vec.Rotate(angle, ZAxis) for vec in sunV]
        
        
        try:
            def sunlightHoursCalculator(i):
                for vector in sunV:
                    vecAngle = rc.Geometry.Vector3d.VectorAngle(vector, testVec[i]) # calculate the angle between the surface and sun vector
                    if vecAngle < (PI/2):
                        check = 1; # this is simply here becuse I can't trust the break! Isn't it stupid?
                        ray = rc.Geometry.Ray3d(testPts[i], vector) # generate the ray
                        
                        if bldgMesh!=None:
                            for bldg in bldgMesh: # bldgMesh is all joined as one mesh
                                if rc.Geometry.Intersect.Intersection.MeshRay(bldg, ray) >= 0.0: check = 0; break
                        if check != 0 and contextMesh!=None: #and testPts[i].Z < contextHeight:
                            for bldg in contextMesh:
                                if rc.Geometry.Intersect.Intersection.MeshRay(bldg,ray) >= 0.0: check = 0; break
                        
                        if check != 0:
                            sunlightHours[i] += 1
                
                sunlightHoursResult[i] = sunlightHours[i] # This is stupid but I'm tired to change it now...
        
        except:
            print 'Error in Sunligh Hours calculation...'
            pass
        
        # calling the function
        if parallel:
            tasks.Parallel.ForEach(range(len(testPts)), sunlightHoursCalculator)
        else:
            for i in range(len(testPts)):
                sunlightHoursCalculator(i)
        
        intersectionEndTime = time.time()
        print 'Sunlight hours calculation time = ', ("%.3f" % (intersectionEndTime - intersectionStTime)), 'Seconds...'
        
        # total sunlight hours
        totalSLH = 0;
        for r in range(len(testPts)):
            totalSLH = totalSLH + (sunlightHoursResult[r] * meshSrfArea[r] * (conversionFac * conversionFac))
        
        return sunlightHoursResult, totalSLH
    
    
    def parallel_viewCalculator(self, testPts, testVec, meshSrfArea, bldgMesh, contextMesh, parallel, viewPoints, viewFields_Angles, conversionFac):
        
        viewPoints = rs.coerce3dpointlist(viewPoints)
        
        # preparing bulk lists
        view = [0] * len(testPts)
        viewResult = [0] * len(testPts)
        intersectionStTime = time.time()
        PI = math.pi
        
        # Converting vectors to Rhino 3D Vectors
        pViewVectors = [[] for pt in testPts]
        viewVectors = [[] for pt in testPts]
        ptCount = 0
        
        #
        if len(viewFields_Angles)!=0:
            VFA1 = math.radians(viewFields_Angles[0])
            VFA2 = math.radians(viewFields_Angles[0] + viewFields_Angles[1])
        else:
            VFA1 = PI/2
            VFA2 = 0
        
        # I should add index to viewField options so users will have the full control
        VFA1Index = 100
        VFA2Index = 60
        VFA3Index = 30
        
        print 'Angle for view Field1 is set between 0.0 and ' + `math.degrees(VFA1)` + ' Degrees. Result for Field1 will be multiplied by ' + `VFA1Index` + '%.'
        if math.degrees(VFA1)<90:
            print 'Angle for view field 2 is set between ' + `math.degrees(VFA1)` + ' and ' + `math.degrees(VFA1 + VFA2)` + ' Degrees. Result for Field2 will be multiplied by ' + `VFA2Index` + '%.'
        if math.degrees(VFA1 + VFA2)<90:
            print 'Angle for view field 3 is set  between ' + `math.degrees(VFA1 + VFA2)` + ' and ' + `math.degrees(PI/2 - (VFA1 + VFA2))` + ' Degrees. Result for Field3 will be multiplied by ' + `VFA3Index` + '%.'
        
        for point in testPts:
            for vPoint in viewPoints:
                # I had to project the vectors so the heights of the points not affects the result
                pViewVectors[ptCount].append(rc.Geometry.Vector3d((vPoint.X - point.X), (vPoint.Y - point.Y), 0 ))
                viewVectors[ptCount].append(rc.Geometry.Vector3d((vPoint.X - point.X), (vPoint.Y - point.Y), (vPoint.Z - point.Z)))
                # MeshLine intersection is so slow for some reason but I couldn't find a better way to get the view calculator
                # to work with meshRay... Unfortunate!
            ptCount += 1
            
        try:
            def viewCalculator(i):
                ##
                viewField1 = []; viewField2 = []; viewField3 = [];
                view1 = 0; view2 = 0; view3 = 0;
                v1 = 0; v2 = 0; v3 = 0; pointsLeft = 1
                ##
                vecCount = 0
                for vector in pViewVectors[i]:
                    vecAngle = round(rc.Geometry.Vector3d.VectorAngle(vector, testVec[i])) # calculate the angle between the surface and view vector
                    if vecAngle < (PI/2):
                        # ray = rc.Geometry.Ray3d(testPts[i], viewVectors[i][vecCount])
                        line = rc.Geometry.Line(testPts[i], viewPoints[vecCount])
                        # Separate points and rays in view fields
                        if  vecAngle <= (VFA1):
                            # viewField1.append((ray, vecAngle))
                            viewField1.append((line, vecAngle))
                            
                        elif (VFA1) < vecAngle <= (VFA2):
                            #viewField2.append((ray, vecAngle))
                            viewField2.append((line, vecAngle))
                            
                        elif (VFA2) <= vecAngle:
                            #viewField3.append((ray, vecAngle))
                            viewField3.append((line, vecAngle))
                            
                    vecCount += 1
                
                def isVisible(ray, vecAngle):
                    check = 1; # this is simply here becuse I can't trust the break! Isn't it stupid?
                    if bldgMesh!=None:
                        for bldg in bldgMesh: # bldgMesh is all joined as one mesh
                            #if rc.Geometry.Intersect.Intersection.MeshRay(bldg, ray) >= 0.0: check = 0; return 0; break
                            if rc.Geometry.Intersect.Intersection.MeshLine(bldg, line)[1] != None:
                                # I need to also check the distance
                                check = 0; return 0; break
                            
                    if check != 0 and contextMesh!=None: #and testPts[i].Z < contextHeight:
                        for bldg in contextMesh:
                            #if rc.Geometry.Intersect.Intersection.MeshRay(bldg,ray) >= 0.0: check = 0; return 0; break
                            # print rc.Geometry.Intersect.Intersection.MeshLine(bldg, line)
                            if rc.Geometry.Intersect.Intersection.MeshLine(bldg, line)[1] != None:
                                check = 0; return 0; break
                            
                    if check != 0: return 1 * math.cos(vecAngle)
                    return 0

                ## do the calculation for points
                while view[i] < 100 and pointsLeft!=0:
                    if len(viewField1) > 0:
                        for ray in viewField1: view1 = view1 + isVisible(*ray)
                        view [i] = view[i] + (view1/len(viewField1)) * VFA1Index #100
                    if len(viewField2) > 0:
                        for ray in viewField2: view2 = view2 + isVisible(*ray)
                        view [i] = view[i] + (view2/len(viewField2)) * VFA2Index #60
                    if len(viewField3) > 0:
                        for ray in viewField3: view3 = view3 + isVisible(*ray)
                        view [i] = view[i] + (view3/len(viewField3)) * VFA3Index #25
                    pointsLeft = 0
                    
                viewResult[i] = view[i] #Stupid! But if you think I go and change all views to viewResult you don't know me!
                if viewResult[i] > 100: viewResult[i] = 100
        except:
            print 'Error in View calculation...'
            pass
        
        # calling the function
        if parallel:
            tasks.Parallel.ForEach(range(len(testPts)), viewCalculator)
        else:
            for i in range(len(testPts)):
                viewCalculator(i)
        
        intersectionEndTime = time.time()
        print 'View calculation time = ', ("%.3f" % (intersectionEndTime - intersectionStTime)), 'Seconds...'
        
        # total view [?!]
        totalView = 0;
        for r in range(len(testPts)):
            totalView = totalView + (viewResult[r] * meshSrfArea[r] * (conversionFac * conversionFac))
            
        return viewResult, totalView
        

class ExportAnalysis2Radiance(object):
    pass
        

class ResultVisualization(object):
    
    # This wasn't agood idea since multiple studies have different Bounding boxes
    def __init__(self):
        self.BoundingBoxPar = None
        self.monthList = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    
    def readRunPeriod(self, runningPeriod, p = True, full = True):
        if not runningPeriod or runningPeriod[0]==None:
            runningPeriod = ((1, 1, 1),(12, 31, 24))
            
        stMonth = runningPeriod [0][0]; stDay = runningPeriod [0][1]; stHour = runningPeriod [0][2];
        endMonth = runningPeriod [1][0]; endDay = runningPeriod [1][1]; endHour = runningPeriod [1][2];
        
        if p:
            if full: print 'Simulation period is:', self.hour2Date(self.date2Hour(stMonth, stDay, stHour)), ' to ', self.hour2Date(self.date2Hour(endMonth, endDay, endHour))
            else: print self.hour2Date(self.date2Hour(stMonth, stDay, stHour)), ' - ', self.hour2Date(self.date2Hour(endMonth, endDay, endHour))
             
        return stMonth, stDay, stHour, endMonth, endDay, endHour
    
    
    def colorMesh(self, colors, meshList):
        
        joinedMesh = rc.Geometry.Mesh()
        try:
            for face in range(meshList[0].Faces.Count):
                joinedMesh.Append(meshList[0].Faces[face]) #join the mesh
        except:
            try:
                for face in meshList: joinedMesh.Append(face)
            except:
                joinedMesh.Append(meshList)
        
        joinedMesh.Unweld(0, False)
        
        if joinedMesh.Faces.Count == 0:
            print "Invalid Mesh!"
            return -1
            
        try:
            assert joinedMesh.Faces.Count == len(colors)
        except:
            print 'number of mesh:' + `joinedMesh.Faces.Count` + ' != number of values:' + `len(colors)`
            return -1
            
        # make a monotonemesh
        joinedMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.White)
        #color the mesh based on the results
        for srfCount in range (joinedMesh.Faces.Count):
            joinedMesh.VertexColors[joinedMesh.Faces[srfCount].A] = colors[srfCount]
            joinedMesh.VertexColors[joinedMesh.Faces[srfCount].B] = colors[srfCount]
            joinedMesh.VertexColors[joinedMesh.Faces[srfCount].C] = colors[srfCount]
            joinedMesh.VertexColors[joinedMesh.Faces[srfCount].D] = colors[srfCount]
        return joinedMesh
    
    def gradientColor(self, values, lowB, highB, colors):
        if highB == 'max': highB = max(values)
        if lowB == 'min': lowB = min(values)
        
        # this function inputs values, and custom colors and outputs gradient colors
        def parNum(num, lowB, highB):
            """This function normalizes all the values"""
            if num > highB: numP = 1
            elif num < lowB: numP = 0
            elif highB == lowB: numP = 0
            else: numP = (num - lowB)/(highB - lowB)
            return numP

        def calColor(valueP, rangeMinP, rangeMaxP, minColor, maxColor):
            # range is between 0 and 1
            rangeP = rangeMaxP - rangeMinP
            red = round(((valueP - rangeMinP)/rangeP) * (maxColor.R - minColor.R) + minColor.R)
            blue = round(((valueP - rangeMinP)/rangeP) * (maxColor.B - minColor.B) + minColor.B)
            green = round(((valueP - rangeMinP)/rangeP) * (maxColor.G - minColor.G) + minColor.G) 
            color = System.Drawing.Color.FromArgb(red, green, blue)
            return color
        
        numofColors = len(colors)
        colorBounds = rs.frange(0, 1, round(1/(numofColors-1),6))
        if len(colorBounds) != numofColors: colorBounds.append(1)
        colorBounds = [round(x,3) for x in colorBounds]
        
        numP = []
        for num in values: numP.append(parNum(num, lowB, highB))
            
        colorTemp = []
        for num in numP:
            for i in range(numofColors):
                if  colorBounds[i] <= num <= colorBounds[i + 1]:
                    colorTemp.append(calColor(num, colorBounds[i], colorBounds[i+1], colors[i], colors[i+1]))
                    break
        color = colorTemp
        return color
    
    def calculateBB(self, geometries, restricted = False):
        bbox = None
        plane = rc.Geometry.Plane.WorldXY
        if geometries:
            flattenGeo = []
            for geometry in geometries:
                #print geometry
                if isinstance(geometry, list):
                    # geometry = list(chain.from_iterable(geometry)) # it gives me errors for
                    [flattenGeo.append(g) for g in geometry]
                    #geometry = flatten
                else:
                    flattenGeo.append(geometry)
                #print flattenGeo
                for geo in flattenGeo:
                    if(bbox==None ): bbox = geo.GetBoundingBox(restricted)
                    else: bbox = rc.Geometry.BoundingBox.Union( bbox, geo.GetBoundingBox(restricted))
                
        minZPt = bbox.Corner(False, True, True)
        maxZPt = bbox.Corner(False, True, False)
        titleBasePt = bbox.Corner(True, True, True)
        BBXlength = titleBasePt.DistanceTo(minZPt)
        BBYlength = titleBasePt.DistanceTo(bbox.Corner(True, False, True))
        BBZlength = titleBasePt.DistanceTo(bbox.Corner(True, True, False))
        CENTERPoint = (bbox.Corner(False, True, True) + bbox.Corner( True, False, False))/2
        
        # this is just here because I'm using it in number of components and I don't want to go and fix them right now.
        # else it doesn't make sense to store the parameters in this Class
        self.BoundingBoxPar = minZPt, BBXlength, BBYlength, BBZlength, CENTERPoint, titleBasePt, maxZPt
        
        return minZPt, CENTERPoint, maxZPt
    
    def createLegend(self, results, lowB, highB, numOfSeg, legendTitle, BoundingBoxP, legendBasePoint, legendScale = 1):
        if numOfSeg: numOfSeg = int(numOfSeg)
        if highB == 'max': highB = max(results)
        if lowB == 'min': lowB = min(results)
        
        if legendBasePoint == None: basePt = BoundingBoxP[0]
        else: basePt = legendBasePoint
            
        BBYlength = BoundingBoxP[2]
        
        def legend(basePt, legendHeight, legendWidth, numofSeg):
            basePt = rc.Geometry.Point3d.Add(basePt, rc.Geometry.Vector3f(legendWidth, 0, 0))
            numPt = int(4 + 2 * (numOfSeg - 1))
            # make the point list
            ptList = []
            for pt in range(numPt):
                point = rc.Geometry.Point3d(basePt[0] + (pt%2) * legendWidth, basePt[1] + int(pt/2) * legendHeight, basePt[2])
                ptList.append(point)
    
            meshVertices = ptList; textPt = []
            legendSrf = rc.Geometry.Mesh()
            for segNum in  range(numOfSeg):
                # generate the surface
                mesh = rc.Geometry.Mesh()
                mesh.Vertices.Add(meshVertices[segNum * 2]) #0
                mesh.Vertices.Add(meshVertices[segNum * 2 + 1]) #1
                mesh.Vertices.Add(meshVertices[segNum * 2 + 2]) #2
                mesh.Vertices.Add(meshVertices[segNum * 2 + 3]) #3
                mesh.Faces.AddFace(0, 1, 3, 2)
                legendSrf.Append(mesh)
                
                textPt.append(meshVertices[segNum * 2 + 1])
            textPt.append(meshVertices[-1]) # one more point for legend title
            return legendSrf, textPt
        
        # numbers
        # rs.frange(0, 1, round(1/(numofColors-1),6))
        if round((highB - lowB)) == 0: numbers = [highB]; numOfSeg = 1
        else: numbers = rs.frange(lowB, highB, round((highB - lowB) / (numOfSeg -1), 6))
        ###
        if len(numbers) != numOfSeg: numbers.append(highB)
        numbersStr = [("%.2f" % x) for x in numbers]
        numbersStr[0] = "<=" + numbersStr[0]
        numbersStr[-1] = numbersStr[-1] + "<="
        numbersStr.append(legendTitle)
        numbers.append(legendTitle)
        legendHeight = legendWidth = (BBYlength/10) * legendScale
        
        # mesh surfaces and legend text
        legendSrf, textPt = legend(basePt, legendHeight, legendWidth, numOfSeg)
        #print numOfSeg
        textSize = (legendHeight/3) * legendScale
        numbersCrv = self.text2crv(numbersStr, textPt, 'Verdana', textSize)
        
        return legendSrf, numbers, numbersCrv, textPt, textSize
    
    def openLegend(self, legendRes):
        if len(legendRes)!=0:
            meshAndCrv = []
            meshAndCrv.append(legendRes[0])
            [meshAndCrv.append(c) for c in legendRes[1]]
            return meshAndCrv
        else: return -1
    
    def chartGeometry(self, values, xSize, xScale, yScale, zScale, basePoint = rc.Geometry.Point3d.Origin):
        # make a monocolor mesh
        meshVertices = range(len(values))
        ySize = int(len(values)/xSize)

        for i in range(len(values)):
            xMove = - xScale * (i % xSize)
            yMove = yScale * int(i / xSize)
            zMove = zScale * values[i]
            movingVec = rc.Geometry.Vector3f(xMove,yMove,zMove)
            newPoint = rc.Geometry.Point3d.Add(basePoint, movingVec)
            meshVertices[i] = newPoint
        
        joinedMesh = rc.Geometry.Mesh()
        for i in  range(len(meshVertices)):
            # check the point not to be in the last row or the last column
            if (i + 1) % xSize != 0 and i + 1 < xSize * (ySize - 1):
                # draw each mesh surface
                mesh = rc.Geometry.Mesh()
                mesh.Vertices.Add(meshVertices[i]) #0
                mesh.Vertices.Add(meshVertices[i + 1]) #1
                mesh.Vertices.Add(meshVertices[i + xSize + 1]) #2
                mesh.Vertices.Add(meshVertices[i + xSize]) #3
                mesh.Faces.AddFace(0, 1, 2, 3)
                joinedMesh.Append(mesh)
        return joinedMesh


    def colorMeshChart(self, joinedMesh, xSize, colors, basePoint = rc.Geometry.Point3d.Origin):
        # color mesh surface
        joinedMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.White)
    
        # Colors = [System.Drawing.Color.Green, System.Drawing.Color.Red, System.Drawing.Color.Blue]
        for srfNum in range (joinedMesh.Faces.Count):
            joinedMesh.VertexColors[4 * srfNum + 0] = colors[srfNum + int(srfNum/(xSize -1))]
            joinedMesh.VertexColors[4 * srfNum + 1] = colors[srfNum + int(srfNum/(xSize -1)) + 1]
            joinedMesh.VertexColors[4 * srfNum + 3] = colors[srfNum + int(srfNum/(xSize -1)) + xSize + 1]
            joinedMesh.VertexColors[4 * srfNum + 2] = colors[srfNum + int(srfNum/(xSize -1)) + xSize]
    
        rotate90 = True
        if rotate90: joinedMesh.Rotate(-math.pi/2, rc.Geometry.Vector3d.ZAxis, basePoint)
        
        return joinedMesh

    def text2crv(self, text, textPt, font = 'Verdana', textHeight = 20):
        # Thanks to Giulio Piacentino for his version of text to curve
        textCrvs = []
        for n in range(len(text)):
            plane = rc.Geometry.Plane(textPt[n], rc.Geometry.Vector3d(0,0,1))
            if type(text[n]) is not str:
                preText = rc.RhinoDoc.ActiveDoc.Objects.AddText(`text[n]`, plane, textHeight, font, True, False)
            else:
                preText = rc.RhinoDoc.ActiveDoc.Objects.AddText( text[n], plane, textHeight, font, True, False)
                
            postText = rc.RhinoDoc.ActiveDoc.Objects.Find(preText)
            TG = postText.Geometry
            crv = TG.Explode()
            textCrvs.append(crv)
            rc.RhinoDoc.ActiveDoc.Objects.Delete(postText, True) # find and delete the text
        return textCrvs
    
    def createTitle(self, listInfo, boundingBoxPar, legendScale = 1, Heading = None, shortVersion = False):
        if Heading==None: Heading = listInfo[0][2] + ' (' + listInfo[0][3] + ')' + ' - ' + listInfo[0][4]
        
        stMonth, stDay, stHour, endMonth, endDay, endHour = self.readRunPeriod((listInfo[0][5], listInfo[0][6]), False)
        
        period = `stDay`+ ' ' + self.monthList[stMonth-1] + ' ' + `stHour` + ':00' + \
                 " - " + `endDay`+ ' ' + self.monthList[endMonth-1] + ' ' + `endHour` + ':00'
        
        if shortVersion: titleStr = '\n' + Heading
        else: titleStr = '\n' + Heading + '\n' + listInfo[0][1] + '\n' + period
        
        titlebasePt = boundingBoxPar[-2]
        titleTextCurve = self.text2crv([titleStr], [titlebasePt], 'Veranda', (boundingBoxPar[2]/30) * legendScale)
        
        return titleTextCurve, titleStr, titlebasePt

    def compassCircle(self, cenPt = rc.Geometry.Point3d.Origin, northVector = rc.Geometry.Vector3d.YAxis, radius = 200, angles = range(0,360,30), xMove = 10, centerLine = False):
        baseCircle = rc.Geometry.Circle(cenPt, radius).ToNurbsCurve()
        outerCircle = rc.Geometry.Circle(cenPt, 1.02*radius).ToNurbsCurve()
        
        def drawLine(cenPt, vector, radius, mainLine = False, xMove = 10):
            stPtRatio = 1
            endPtRatio = 1.08
            textPtRatio = endPtRatio + 0.03
            if mainLine: endPtRatio = 1.15; textPtRatio = 1.17
            stPt = rc.Geometry.Point3d.Add(cenPt, stPtRatio * radius * vector)
            if centerLine: stPt = cenPt
            endPt = rc.Geometry.Point3d.Add(cenPt, endPtRatio * radius * vector)
            textBasePt = rc.Geometry.Point3d.Add(cenPt, textPtRatio * radius * vector)
            
            if not mainLine: textBasePt = rc.Geometry.Point3d.Add(textBasePt, -xMove* rc.Geometry.Vector3d.XAxis)
            
            return rc.Geometry.Line(stPt, endPt).ToNurbsCurve(), textBasePt, baseCircle, outerCircle
        
        lines = []; textBasePts = []
        mainAngles = [0, 90, 180, 270]
        mainText = ['N', 'E', 'S', 'W']
        compassText = []
        for angle in angles:
            mainLine = False
            if angle in mainAngles: mainLine = True
            vector = rc.Geometry.Vector3d(northVector)
            vector.Rotate(-math.radians(angle), rc.Geometry.Vector3d.ZAxis)
            line, basePt, baseCircle, outerCircle = drawLine(cenPt, vector, radius, mainLine, xMove)
            if mainLine == True: compassText.append(mainText[mainAngles.index(angle)])
            else: compassText.append("%.2f"%angle)
                
            textBasePts.append(basePt)
            lines.append(line)
        lines.append(baseCircle)
        lines.append(outerCircle)
        return lines, textBasePts, compassText
    
    
    
    
    def setupLayers(self, result = 'No result', parentLayerName = 'LADYBUG', projectName = 'Option',
                        studyLayerName = 'RADIATION_KWH', CheckTheName = True,
                        OrientationStudy = False, rotationAngle = 0, l = 0):
                            
            # studyLayerName is actually component name
            # project name will be city name for sun-path, radRose , etc.
            # OrientationStudy for result layer name
            
            layerT = rc.RhinoDoc.ActiveDoc.Layers #layer table
            
            # Add Parent layer properties
            parentLayer = rc.DocObjects.Layer()
            parentLayer.Name = parentLayerName
            parentLayer.IsVisible = True
            parentLayer.Color =  System.Drawing.Color.Pink
            
            # Add Parent layer if it's not already created
            parentLayerIndex = rc.DocObjects.Tables.LayerTable.Find(layerT, parentLayerName, True)
            if parentLayerIndex < 0: parentLayerIndex = layerT.Add(parentLayer)
        
            # Make Study Folder
            studyLayer = rc.DocObjects.Layer()
            studyLayer.Name = studyLayerName
            studyLayer.Color =  System.Drawing.Color.Yellow
            studyLayer.IsVisible = True
            studyLayer.ParentLayerId = layerT[parentLayerIndex].Id
            studyLayerPath = parentLayer.Name + '::' + studyLayer.Name
            # Add The layer if it's not already created
            studyLayerIndex = rc.DocObjects.Tables.LayerTable.FindByFullPath(layerT, studyLayerPath, True)
            if studyLayerIndex < 0: studyLayerIndex = layerT.Add(studyLayer)
            
            # make a sub-layer for current project
            if projectName: layerName = str(projectName)
            else: layerName = 'Option'
            
            if rc.DocObjects.Layer.IsValidName(layerName) != True:
                print 'The layer name: ' +  `layerName` + ' is not a valid layer name.'
                return
                #layerIndex = 0; newLayerIndex = layerIndex;
            else:
                layerPath = parentLayer.Name + '::' + studyLayer.Name + '::'+ layerName + '_' + `l`
                layerIndex = rc.DocObjects.Tables.LayerTable.FindByFullPath(layerT, layerPath, True)
                if CheckTheName:
                    while layerIndex > 0: # if layer existed rename the layer
                        l = l + 1
                        layerPath = parentLayer.Name + '::' + studyLayer.Name + '::'+ layerName + '_' + `l`
                        layerIndex = rc.DocObjects.Tables.LayerTable.FindByFullPath(layerT, layerPath, True)
                        
                # creat the new sub layer for each geometry
                nLayer = rc.DocObjects.Layer()
                nLayer.Name = layerName + '_' + `l`
                nLayer.IsVisible = False
                nLayer.ParentLayerId = layerT[studyLayerIndex].Id
                # nLayerIndex = rc.DocObjects.Tables.LayerTable.Find(layerT, nLayer.Name, True)
                
                nLayerIndex = rc.DocObjects.Tables.LayerTable.FindByFullPath(layerT, layerPath, True)
                if nLayerIndex < 0: nLayerIndex = layerT.Add(nLayer)
                # study = 1; # do it once in a rotation study
                # add layer for
                newLayer = rc.DocObjects.Layer()
                if OrientationStudy:
                    newLayer.Name = ("%.3f" % (result)) + '<-' + layerName + '_' + `l` +'_Angle '+ `rotationAngle`
                else:
                    try: newLayer.Name = ("%.3f" % (result)) + '<-Result for '+ layerName + '_' + `l`
                    except: newLayer.Name = result
                        
                newLayerFullPath = parentLayer.Name + '::' + studyLayer.Name + '::'+ layerName + '_' + `l` + '::' + newLayer.Name
                newLayerIndex = rc.DocObjects.Tables.LayerTable.FindByFullPath(layerT, newLayerFullPath, True)
                # newLayerIndex = rc.DocObjects.Tables.LayerTable.Find(layerT, newLayer.Name, True)
                if newLayerIndex < 0:
                    newLayer.IsVisible = True
                    newLayer.ParentLayerId = layerT[nLayerIndex].Id
                    newLayerIndex = layerT.Add(newLayer)
                
            return newLayerIndex, l

    def bakeObjects(self, newLayerIndex, testGeomety, legendGeometry, legendText, textPt, textSize, fontName = 'Verdana', crvs = None):
            attr = rc.DocObjects.ObjectAttributes()
            attr.LayerIndex = newLayerIndex
            attr.ColorSource = rc.DocObjects.ObjectColorSource.ColorFromObject
            attr.PlotColorSource = rc.DocObjects.ObjectPlotColorSource.PlotColorFromObject
            try:
                for mesh in testGeomety: rc.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh, attr)
            except:
                rc.RhinoDoc.ActiveDoc.Objects.AddMesh(testGeomety, attr)
            
            rc.RhinoDoc.ActiveDoc.Objects.AddMesh(legendGeometry, attr)
            if crvs != None:
                for crv in crvs: rc.RhinoDoc.ActiveDoc.Objects.AddCurve(crv, attr)
            for text in range(len(legendText)):
                plane = rc.Geometry.Plane(textPt[text], rc.Geometry.Vector3d(0,0,1))
                if type(legendText[text]) is not str: legendText[text] = ("%.2f" % legendText[text])
                rc.RhinoDoc.ActiveDoc.Objects.AddText(legendText[text], plane, textSize, fontName, True, False, attr)
                # end of the script

now = datetime.datetime.now()
if now.day + now.month + now.year < 2055 + 365: # should work until the end of 2013
    if letItFly:
        if not sc.sticky.has_key("ladybug_release") or 1>0:
            sc.sticky["ladybug_release"] = True
            sc.sticky["ladybug_Preparation"] = Preparation
            sc.sticky["ladybug_Mesh"] = MeshPreparation
            sc.sticky["ladybug_RunAnalysis"] = RunAnalysisInsideGH
            sc.sticky["ladybug_Export2Radiance"] = ExportAnalysis2Radiance
            sc.sticky["ladybug_ResultVisualization"] = ResultVisualization
            sc.sticky["ladybug_SunPath"] = Sunpath
    # sc.sticky.clear()

    if not sc.sticky.has_key("ladybug_release"):
        w = gh.GH_RuntimeMessageLevel.Warning
        try:
            print "Hi " + os.getenv("USERNAME")+ "! \nPlease let me fly!..."
            ghenv.Component.AddRuntimeMessage(w, "Hi " + os.getenv("USERNAME")+ "! \nPlease let me fly!...")
            if 0 <= datetime.datetime.timetuple(now)[3] <= 6: print "Wait! This is after midnight... Time to go to bed! ;)"
        except:
            print "Please let me fly!..."
            ghenv.Component.AddRuntimeMessage(w, "Please let me fly!...")
    elif sc.sticky.has_key("ladybug_release"):
        print "Hooohooho...Flying!!\nVviiiiiiizzz..."
else:
    sc.sticky.clear()
    w = gh.GH_RuntimeMessageLevel.Warning
    warning = "Hi! You were using a test version of ladybug which is expired now\nPlease check the Grasshopper group page for a newer version"
    print warning
    ghenv.Component.AddRuntimeMessage(w, warning)
    