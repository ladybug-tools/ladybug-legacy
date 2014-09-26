# This is the heart of the Ladybug
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component carries all of Ladybug's main classes. Other components refer to these
classes to run the studies. Therefore, you need to let her fly before running the studies so the
classes will be copied to Rhinos shared space. So let her fly!
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
Provided by Ladybug 0.0.58
    
    Returns:
        report: Current Ladybug mood!!!
"""

ghenv.Component.Name = "Ladybug_Ladybug"
ghenv.Component.NickName = 'Ladybug'
ghenv.Component.Message = 'VER 0.0.58\nSEP_15_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
from clr import AddReference
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
import urllib

PI = math.pi
letItFly = True
rc.Runtime.HostUtils.DisplayOleAlerts(False)



#set up default pass
if os.path.exists("c:\\ladybug\\") and os.access(os.path.dirname("c:\\ladybug\\"), os.F_OK):
    # folder already exists so it is all fine
    sc.sticky["Ladybug_DefaultFolder"] = "c:\\ladybug\\"
elif os.access(os.path.dirname("c:\\"), os.F_OK):
    #the folder does not exists but write privileges are given so it is fine
    sc.sticky["Ladybug_DefaultFolder"] = "c:\\ladybug\\"
else:
    # let's use the user folder
    sc.sticky["Ladybug_DefaultFolder"] = os.path.join("C:\\Users\\", os.getenv("USERNAME"), "AppData\\Roaming\\Ladybug\\")

class CheckIn():
    
    def __init__(self):
        #set up default pass
        if os.path.exists("c:\\ladybug\\") and os.access(os.path.dirname("c:\\ladybug\\"), os.F_OK):
            # folder already exists so it is all fine
            sc.sticky["Ladybug_DefaultFolder"] = "c:\\ladybug\\"
        elif os.access(os.path.dirname("c:\\"), os.F_OK):
            #the folder does not exists but write privileges are given so it is fine
            sc.sticky["Ladybug_DefaultFolder"] = "c:\\ladybug\\"
        else:
            # let's use the user folder
            sc.sticky["Ladybug_DefaultFolder"] = os.path.join("C:\\Users\\", os.getenv("USERNAME"), "AppData\\Roaming\\Ladybug\\")
    
    def getComponentVersion(self):
        monthDict = {'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06',
                     'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10', 'NOV':'11', 'DEC':'12'}
        # convert component version to standard versioning
        ver, verDate = ghenv.Component.Message.split("\n")
        ver = ver.split(" ")[1].strip()
        month, day, year = verDate.split("_")
        month = monthDict[month.upper()]
        version = ".".join([year, month, day, ver])
        return version
        
    def isNewerVersionAvailable(self, currentVersion, availableVersion):
        # print int(availableVersion.replace(".", "")), int(currentVersion.replace(".", ""))
        return int(availableVersion.replace(".", "")) > int(currentVersion.replace(".", ""))
    
    def checkForUpdates(self, LB= True, HB= True, OpenStudio = True, template = True):
        
        url = "https://dl.dropboxusercontent.com/u/16228160/honeybee/versions.txt"
        webFile = urllib.urlopen(url)
        versions= eval(webFile.read())
        webFile.close()
        
        if LB:
            ladybugVersion = versions['Ladybug']
            currentLadybugVersion = self.getComponentVersion() # I assume that this function will be called inside Ladybug_ladybug Component
            if self.isNewerVersionAvailable(currentLadybugVersion, ladybugVersion):
                msg = "There is a newer version of Ladybug available to download! " + \
                      "We strongly recommend you to download the newer version from Food4Rhino: " + \
                      "http://www.food4rhino.com/project/ladybug-honeybee"
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        if HB:
            honeybeeVersion = versions['Honeybee']
            currentHoneybeeVersion = self.getComponentVersion() # I assume that this function will be called inside Honeybee_Honeybee Component
            if self.isNewerVersionAvailable(currentHoneybeeVersion, honeybeeVersion):
                msg = "There is a newer version of Honeybee available to download! " + \
                      "We strongly recommend you to download the newer version from Food4Rhino: " + \
                      "http://www.food4rhino.com/project/ladybug-honeybee"
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            
        if OpenStudio:
            # This should be called inside OpenStudio component which means Honeybee is already flying
            # check if the version file exist
            openStudioLibFolder = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "OpenStudio")
            versionFile = os.path.join(openStudioLibFolder, "osversion.txt")
            isNewerOSAvailable= False
            if not os.path.isfile(versionFile):
                isNewerOSAvailable= True
            else:
                # read the file
                with open(versionFile) as verFile:
                    currentOSVersion= eval(verFile.read())['version']
            
            OSVersion = versions['OpenStudio']
            
            if isNewerOSAvailable or self.isNewerVersionAvailable(currentOSVersion, OSVersion):
                sc.sticky["isNewerOSAvailable"] = True
            else:
                sc.sticky["isNewerOSAvailable"] = False
                
        if template:
            honeybeeDefaultFolder = sc.sticky["Honeybee_DefaultFolder"]
            templateFile = os.path.join(honeybeeDefaultFolder, 'OpenStudioMasterTemplate.idf')
            
            # check file doesn't exist then it should be downloaded
            if not os.path.isfile(templateFile):
                return True
            
            # find the version
            try:
                with open(templateFile) as tempFile:
                    templateVersion = eval(tempFile.readline().split("!")[-1].strip())["version"]
            except Exception, e:
                return True
            
            # finally if the file exist and already has a version, compare the versions
            currentTemplateVersion = versions['Template']
            
            return self.isNewerVersionAvailable(currentTemplateVersion, templateVersion)
            

checkIn = CheckIn()


class versionCheck(object):
    
    def __init__(self):
        self.version = self.getVersion(ghenv.Component.Message)
    
    def getVersion(self, LBComponentMessage):
        monthDict = {'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06',
                     'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10', 'NOV':'11', 'DEC':'12'}
        # convert component version to standard versioning
        try: ver, verDate = LBComponentMessage.split("\n")
        except: ver, verDate = LBComponentMessage.split("\\n")
        ver = ver.split(" ")[1].strip()
        month, day, year = verDate.split("_")
        month = monthDict[month.upper()]
        version = ".".join([year, month, day, ver])
        return version
    
    def isCurrentVersionNewer(self, desiredVersion):
        return int(self.version.replace(".", "")) >= int(desiredVersion.replace(".", ""))
    
    def isCompatible(self, LBComponent):
        code = LBComponent.Code
        # find the version that is supposed to be flying
        try: version = code.split("compatibleLBVersion")[1].split("=")[1].split("\n")[0].strip()
        except: self.giveWarning(LBComponent)
        
        desiredVersion = self.getVersion(version)
        
        if not self.isCurrentVersionNewer(desiredVersion):
            self.giveWarning(LBComponent)
            return False
        
        return True
        
    def giveWarning(self, GHComponent):
        warningMsg = "You need a newer version of Ladybug to use this compoent." + \
                     "Use updateLadybug component to update userObjects.\n" + \
                     "If you have already updated userObjects drag Ladybug_Ladybug component " + \
                     "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        GHComponent.AddRuntimeMessage(w, warningMsg)


class Preparation(object):
    """ Set of functions to prepare the environment for running the studies"""
    def __init__(self):
        self.monthList = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        self.numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
        self.numOfDaysEachMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        self.numOfHours = [24 * numOfDay for numOfDay in self.numOfDays]
    
    def giveWarning(self, warningMsg, GHComponent):
        w = gh.GH_RuntimeMessageLevel.Warning
        GHComponent.AddRuntimeMessage(w, warningMsg)
        
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
    
    def nukedir(self, dir, rmdir = True):
        # copied from 
        if dir[-1] == os.sep: dir = dir[:-1]
        files = os.listdir(dir)
        for file in files:
            if file == '.' or file == '..': continue
            path = dir + os.sep + file
            if os.path.isdir(path):
                self.nukedir(path)
            else:
                os.unlink(path)
        if rmdir: os.rmdir(dir)
    
    def readRunPeriod(self, runningPeriod, p = True, full = True):
        if not runningPeriod or runningPeriod[0]==None:
            runningPeriod = ((1, 1, 1),(12, 31, 24))
            
        stMonth = runningPeriod [0][0]; stDay = runningPeriod [0][1]; stHour = runningPeriod [0][2];
        endMonth = runningPeriod [1][0]; endDay = runningPeriod [1][1]; endHour = runningPeriod [1][2];
        
        if p:
            startDay = self.hour2Date(self.date2Hour(stMonth, stDay, stHour))
            startHour = startDay.split(' ')[-1]
            startDate = startDay.Replace(startHour, "")[:-1]
            
            endingDay = self.hour2Date(self.date2Hour(endMonth, endDay, endHour))
            endingHour = endingDay.split(' ')[-1]
            endingDate = endingDay.Replace(endingHour, "")[:-1]
            
            if full:
                print 'Analysis period is from', startDate, 'to', endingDate
                print 'Between hours ' + startHour + ' to ' + endingHour
            
            else: print startDay, ' - ', endingDay
             
        return stMonth, stDay, stHour, endMonth, endDay, endHour
    
    def checkPlanarity(self, brep, tol = 1e-3):
        # planarity tolerance should change for different 
        return brep.Faces[0].IsPlanar(tol)
    
    def findDiscontinuity(self, curve, style, includeEndPts = True):
        # copied and modified from rhinoScript (@Steve Baer @GitHub)
        """Search for a derivatitive, tangent, or curvature discontinuity in
        a curve object.
        Parameters:
          curve_id = identifier of curve object
          style = The type of continuity to test for. The types of
              continuity are as follows:
              Value    Description
              1        C0 - Continuous function
              2        C1 - Continuous first derivative
              3        C2 - Continuous first and second derivative
              4        G1 - Continuous unit tangent
              5        G2 - Continuous unit tangent and curvature
        Returns:
          List 3D points where the curve is discontinuous
        """
        dom = curve.Domain
        t0 = dom.Min
        t1 = dom.Max
        points = []
        #if includeEndPts: points.append(curve.PointAtStart)
        get_next = True
        while get_next:
            get_next, t = curve.GetNextDiscontinuity(System.Enum.ToObject(rc.Geometry.Continuity, style), t0, t1)
            if get_next:
                points.append(curve.PointAt(t))
                t0 = t # Advance to the next parameter
        if includeEndPts: points.append(curve.PointAtEnd)
        return points
    
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
        if hour%8760==0 and not alternate: return `31`+ ' ' + 'DEC' + ' 24:00'
        elif hour%8760==0: return 31, 11, 24
    
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
    
    def selectHourlyData(self, hourlyData, analysisPeriod):
        # separate data
        indexList, listInfo = self.separateList(hourlyData, self.strToBeFound)
    
        #separate lists of lists
        separatedLists = []
        for i in range(len(indexList)-1):
            selList = []
            [selList.append(float(x)) for x in hourlyData[indexList[i]+7:indexList[i+1]]]
            separatedLists.append(selList)
    
        # read analysis period
        stMonth, stDay, stHour, endMonth, endDay, endHour = self.readRunPeriod(analysisPeriod)
        
        selHourlyData =[];
        
        for l in range(len(separatedLists)):
            [selHourlyData.append(item) for item in listInfo[l][:4]]
            selHourlyData.append('Hourly')
            selHourlyData.append((stMonth, stDay, stHour))
            selHourlyData.append((endMonth, endDay, endHour))
            # select data
            stAnnualHour = self.date2Hour(stMonth, stDay, stHour)
            endAnnualHour = self.date2Hour(endMonth, endDay, endHour)
            
            # check it goes from the end of the year to the start of the year
            if stAnnualHour < endAnnualHour:
                for i, item in enumerate(separatedLists[l][stAnnualHour-1:endAnnualHour]):
                    if stHour-1 <= (i + stHour - 1)%24 <= endHour-1: selHourlyData.append(item)
                type = True
            else:
                for i, item in enumerate(separatedLists[l][stAnnualHour-1:]):
                    if stHour-1 <= (i + stHour - 1)%24 <= endHour-1: selHourlyData.append(item)
                
                for i, item in enumerate(separatedLists[l][:endAnnualHour]):
                    if stHour-1 <= i %24 <= endHour-1: selHourlyData.append(item)
                type = False
        
        return selHourlyData
    
    
    def getHOYs(self, hours, days, months, timeStep, method = 0):
        
        if method == 1: stDay, endDay = days
            
        numberOfDaysEachMonth = self.numOfDaysEachMonth
        
        if timeStep != 1: hours = rs.frange(hours[0], hours[-1] + 1 - 1/timeStep, 1/timeStep)
        
        HOYS = []
        
        for monthCount, m in enumerate(months):
            # just a single day
            if method == 1 and len(months) == 1 and stDay - endDay == 0:
                days = [stDay]
            # few days in a single month
            
            elif method == 1 and len(months) == 1:
                days = range(stDay, endDay + 1)
            
            elif method == 1:
                #based on analysis period
                if monthCount == 0:
                    # first month
                    days = range(stDay, numberOfDaysEachMonth[monthCount] + 1)
                elif monthCount == len(months) - 1:
                    # last month
                    days = range(1, self.checkDay(endDay, m) + 1)
                else:
                    #rest of the months
                    days = range(1, numberOfDaysEachMonth[monthCount] + 1)
            
            for d in days:
                for h in hours:
                    h = self.checkHour(float(h))
                    m  = self.checkMonth(int(m))
                    d = self.checkDay(int(d), m)
                    HOY = self.date2Hour(m, d, h)
                    if HOY not in HOYS: HOYS.append(int(HOY))
        
        return HOYS
    
    
    def getHOYsBasedOnPeriod(self, analysisPeriod, timeStep):
        
        stMonth, stDay, stHour, endMonth, endDay, endHour = self.readRunPeriod(analysisPeriod, True, False)
        
        if stMonth > endMonth:
            months = range(stMonth, 13) + range(1, endMonth + 1)
        else:
            months = range(stMonth, endMonth + 1)
        
        # end hour shouldn't be included
        hours  = range(stHour, endHour+1)
        
        days = stDay, endDay
        
        HOYS = self.getHOYs(hours, days, months, timeStep, method = 1)
        
        return HOYS, months, days
    
    
    
    def readLegendParameters(self, legendPar, getCenter = True):
        if legendPar == []: legendPar = [None] * 8
        if legendPar[0] == None: lowB = 'min'
        elif legendPar[0] == 'min': lowB = 'min'
        else: lowB = float(legendPar[0])
        if legendPar[1] == None: highB = 'max'
        elif legendPar[1] == 'max': highB = 'max'
        else: highB = float(legendPar[1])
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
        
        if legendPar[6] == None: legendFont = 'Verdana'
        else: legendFont = legendPar[6]
        
        if legendPar[7] == None: legendFontSize = None
        else: legendFontSize = legendPar[7]
        
        return lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize
    
    def readOrientationParameters(self, orientationStudyP):
        try:
            runOrientation = orientationStudyP[0]
            
            if orientationStudyP[1]==[] or orientationStudyP[1]==False: rotateContext = False
            elif orientationStudyP[1]==True: rotateContext = True
            else:
                # just carry the geometries to next component
                rotateContext = orientationStudyP[1]
            
            if orientationStudyP[2] != None: rotationBasePt = rs.coerce3dpoint(orientationStudyP[2])
            else: rotationBasePt = 'set2center'
            angles = orientationStudyP[3]
            return runOrientation, rotateContext, rotationBasePt, angles
        
        except Exception, e:
            #print `e`
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
    
    def makeWorkingDir(self, workingDir, default = sc.sticky["Ladybug_DefaultFolder"]):
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

    def downloadGendaymtx(self, workingDir):
        ## download File
        def downloadFile(url, workingDir):
            import urllib
            webFile = urllib.urlopen(url)
            localFile = open(workingDir + '/' + url.split('/')[-1], 'wb')
            localFile.write(webFile.read())
            webFile.close()
            localFile.close()

        # download the Gencumulative Sky
        if not os.path.isfile(workingDir + '\gendaymtx.exe'):
            try:
                print 'Downloading gendaymtx.exe to ', workingDir
                downloadFile('http://dl.dropbox.com/u/16228160/GenCumulativeSky/gendaymtx.exe', workingDir)
                print 'Download complete!'
            except:
                allSet = False
                print 'Download failed!!! You need gendaymtx.exe to use this component.' + \
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
                listInfo = [[key, 'somewhere','someData', 'someUnits', 'someTimeStep',(1, 1, 1),(12, 31, 24)]]
            else:
                indexList.append(len(list))
                
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
        elev = csheadline[-1].strip()
        locationString = "Site:Location,\n" + \
            locName + ',\n' + \
            lat+',      !Latitude\n' + \
            lngt+',     !Longitude\n' + \
            timeZone+',     !Time Zone\n' + \
            elev + ';       !Elevation'
        epwfile.close
        return locName, lat, lngt, timeZone, elev, locationString
    
    def separateHeader(self, inputList):
        num = []; str = []
        for item in inputList:
            try: num.append(float(item))
            except: str.append(item)
        return num, str
    
    strToBeFound = 'key:location/dataType/units/frequency/startsAt/endsAt'
    
    def epwDataReader(self, epw_file, location = 'Somewhere!'):
        # weather data
        dbTemp = [self.strToBeFound, location, 'Dry Bulb Temperature', 'C', 'Hourly', (1, 1, 1), (12, 31, 24)];
        dewPoint = [self.strToBeFound, location, 'Dew Point Temperature', 'C', 'Hourly', (1, 1, 1), (12, 31, 24)];
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
        barPress = [self.strToBeFound, location, 'Barometric Pressure', 'Pa', 'Hourly', (1, 1, 1), (12, 31, 24)];
        epwfile = open(epw_file,"r")
        lnum = 1 # line number
        for line in epwfile:
            if lnum > 8:
                dbTemp.append(float(line.split(',')[6]))
                dewPoint.append(float(line.split(',')[7]))
                RH.append(float(line.split(',')[8]))
                barPress.append(float(line.split(',')[9]))
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
        return dbTemp, dewPoint, RH, windSpeed, windDir, dirRad, difRad, glbRad, dirIll, difIll, glbIll, cloudCov, rainDepth, barPress
    
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
        return copyFullpath
        
    def genCumSkyStr(self, runningPeriod, subWorkingDir, workingDir, newLocName, lat, lngt, timeZone):
        # read running period
        stMonth, stDay, stHour, endMonth, endDay, endHour = self.readRunPeriod(runningPeriod)
        
        # sun modes: +s1 is "smeared sun" approach, and +s2 use "binned sun" approach
        # read this paper for more information:
        # http://plea-arch.net/PLEA/ConferenceResources/PLEA2004/Proceedings/p1153final.pdf
        sunModes = ['+s1']
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
    
    def generateSkyGeo(self, cenPt, skyType, scale):
        """
        This script is based of the Treganza sky
        skyType:
            0 is Tregenza Sky with 145 + 1 patches
            1 is Reinhart Sky with 577 + 3 patches
        # number of segments in each row of the sky
        # 15 rows - total 580
        """
        
        originalNumSeg = [30, 30, 24, 24, 18, 12, 6]
        
        if skyType==0:
            numSeg = originalNumSeg + [1]
        else:
            numSeg =[]
            for numOfSeg in originalNumSeg:
                for i in range(skyType+1):
                    numSeg.append(numOfSeg * (skyType+1))
            numSeg = numSeg + [1]
        
        # rotation line axis
        lineVector = rc.Geometry.Vector3d.ZAxis
        lineVector.Reverse()
        lineAxis = rc.Geometry.Line(cenPt, lineVector)
        
        # base plane to draw the arcs
        basePlane = rc.Geometry.Plane(cenPt, rc.Geometry.Vector3d.XAxis)
        baseVector = rc.Geometry.Vector3d.YAxis
        
        
        # 29 is the total number of devisions 14 + 1 + 14
        eachSegVerticalAngle = (math.pi)/ (2 * len(numSeg) - 1)/2
        
        skyPatches = []
        for row in range(len(numSeg)):
            # create the base arc
            stPt = rc.Geometry.Point3d.Add(cenPt, scale* baseVector)
            
            if row == len(numSeg)-1:
                eachSegVerticalAngle = eachSegVerticalAngle/2
                
            baseVector.Rotate(eachSegVerticalAngle, rc.Geometry.Vector3d.XAxis)
            midPt = rc.Geometry.Point3d.Add(cenPt, scale* baseVector) 
            
            baseVector.Rotate(eachSegVerticalAngle, rc.Geometry.Vector3d.XAxis)
            endPt = rc.Geometry.Point3d.Add(cenPt, scale* baseVector) 
            
            baseArc = rc.Geometry.Arc(stPt, midPt, endPt).ToNurbsCurve()
            
            # create the row
            numOfSeg = numSeg[row]
            angleDiv = 2 * math.pi / numOfSeg
            
            for patchNum in range(numOfSeg):
                start_angle = (patchNum * angleDiv) -(angleDiv/2)
                end_angle = ((patchNum + 1) * angleDiv) - (angleDiv/2)
                patch = rc.Geometry.RevSurface.Create(baseArc, lineAxis, start_angle, end_angle)
                skyPatches.append(patch.ToBrep())
                
        return skyPatches
    
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

    
    def genRadRoseArrows(self, movingVectors, radResult, cenPt, sc, internalSc = 0.2, arrowHeadScale = 1):
        radArrows = []; vecNum = 0
        # this is a copy/paste. should be fixed later
        cenPt = rs.AddPoint(cenPt.X, cenPt.Y, cenPt.Z)
        for vec in movingVectors:
            movingVec = (sc* internalSc * vec * radResult[vecNum])
            ptMoveDis = 20 * internalSc * arrowHeadScale
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
    
    def getReinhartPatchesNormalVectors(self):
        ReinhartPatchesNormalVectors = [
        (0.0,0.998533,0.054139),(0.104375,0.993063,0.054139),(0.207607,0.976713,0.054139),
    (0.308564,0.949662,0.054139),(0.40614,0.912206,0.054139),(0.499267,0.864755,0.054139),
    (0.586923,0.807831,0.054139),(0.668149,0.742055,0.054139),(0.742055,0.668149,0.054139),
    (0.807831,0.586923,0.054139),(0.864755,0.499267,0.054139),(0.912206,0.40614,0.054139),
    (0.949662,0.308564,0.054139),(0.976713,0.207607,0.054139),(0.993063,0.104375,0.054139),
    (0.998533,0.0,0.054139),(0.993063,-0.104375,0.054139),(0.976713,-0.207607,0.054139),
    (0.949662,-0.308564,0.054139),(0.912206,-0.40614,0.054139),(0.864755,-0.499267,0.054139),
    (0.807831,-0.586923,0.054139),(0.742055,-0.668149,0.054139),(0.668149,-0.742055,0.054139),
    (0.586923,-0.807831,0.054139),(0.499267,-0.864755,0.054139),(0.40614,-0.912206,0.054139),
    (0.308564,-0.949662,0.054139),(0.207607,-0.976713,0.054139),(0.104375,-0.993063,0.054139),
    (0.0,-0.998533,0.054139),(-0.104375,-0.993063,0.054139),(-0.207607,-0.976713,0.054139),
    (-0.308564,-0.949662,0.054139),(-0.40614,-0.912206,0.054139),(-0.499267,-0.864755,0.054139),
    (-0.586923,-0.807831,0.054139),(-0.668149,-0.742055,0.054139),(-0.742055,-0.668149,0.054139),
    (-0.807831,-0.586923,0.054139),(-0.864755,-0.499267,0.054139),(-0.912206,-0.40614,0.054139),
    (-0.949662,-0.308564,0.054139),(-0.976713,-0.207607,0.054139),(-0.993063,-0.104375,0.054139),
    (-0.998533,0.0,0.054139),(-0.993063,0.104375,0.054139),(-0.976713,0.207607,0.054139),
    (-0.949662,0.308564,0.054139),(-0.912206,0.40614,0.054139),(-0.864755,0.499267,0.054139),
    (-0.807831,0.586923,0.054139),(-0.742055,0.668149,0.054139),(-0.668149,0.742055,0.054139),
    (-0.586923,0.807831,0.054139),(-0.499267,0.864755,0.054139),(-0.40614,0.912206,0.054139),
    (-0.308564,0.949662,0.054139),(-0.207607,0.976713,0.054139),(-0.104375,0.993063,0.054139),
    (0.0,0.986827,0.161782),(0.103151,0.981421,0.161782),(0.205173,0.965262,0.161782),
    (0.304946,0.938528,0.161782),(0.401379,0.901511,0.161782),(0.493413,0.854617,0.161782),
    (0.580042,0.798359,0.161782),(0.660316,0.733355,0.161782),(0.733355,0.660316,0.161782),
    (0.798359,0.580042,0.161782),(0.854617,0.493413,0.161782),(0.901511,0.401379,0.161782),
    (0.938528,0.304946,0.161782),(0.965262,0.205173,0.161782),(0.981421,0.103151,0.161782),
    (0.986827,0.0,0.161782),(0.981421,-0.103151,0.161782),(0.965262,-0.205173,0.161782),
    (0.938528,-0.304946,0.161782),(0.901511,-0.401379,0.161782),(0.854617,-0.493413,0.161782),
    (0.798359,-0.580042,0.161782),(0.733355,-0.660316,0.161782),(0.660316,-0.733355,0.161782),
    (0.580042,-0.798359,0.161782),(0.493413,-0.854617,0.161782),(0.401379,-0.901511,0.161782),
    (0.304946,-0.938528,0.161782),(0.205173,-0.965262,0.161782),(0.103151,-0.981421,0.161782),
    (0.0,-0.986827,0.161782),(-0.103151,-0.981421,0.161782),(-0.205173,-0.965262,0.161782),
    (-0.304946,-0.938528,0.161782),(-0.401379,-0.901511,0.161782),(-0.493413,-0.854617,0.161782),
    (-0.580042,-0.798359,0.161782),(-0.660316,-0.733355,0.161782),(-0.733355,-0.660316,0.161782),
    (-0.798359,-0.580042,0.161782),(-0.854617,-0.493413,0.161782),(-0.901511,-0.401379,0.161782),
    (-0.938528,-0.304946,0.161782),(-0.965262,-0.205173,0.161782),(-0.981421,-0.103151,0.161782),
    (-0.986827,0.0,0.161782),(-0.981421,0.103151,0.161782),(-0.965262,0.205173,0.161782),
    (-0.938528,0.304946,0.161782),(-0.901511,0.401379,0.161782),(-0.854617,0.493413,0.161782),
    (-0.798359,0.580042,0.161782),(-0.733355,0.660316,0.161782),(-0.660316,0.733355,0.161782),
    (-0.580042,0.798359,0.161782),(-0.493413,0.854617,0.161782),(-0.401379,0.901511,0.161782),
    (-0.304946,0.938528,0.161782),(-0.205173,0.965262,0.161782),(-0.103151,0.981421,0.161782),
    (0.0,0.96355,0.267528),(0.100718,0.958272,0.267528),(0.200333,0.942494,0.267528),
    (0.297753,0.91639,0.267528),(0.391911,0.880247,0.267528),(0.481775,0.834459,0.267528),
    (0.56636,0.779528,0.267528),(0.644741,0.716057,0.267528),(0.716057,0.644741,0.267528),
    (0.779528,0.56636,0.267528),(0.834459,0.481775,0.267528),(0.880247,0.391911,0.267528),
    (0.91639,0.297753,0.267528),(0.942494,0.200333,0.267528),(0.958272,0.100718,0.267528),
    (0.96355,0.0,0.267528),(0.958272,-0.100718,0.267528),(0.942494,-0.200333,0.267528),
    (0.91639,-0.297753,0.267528),(0.880247,-0.391911,0.267528),(0.834459,-0.481775,0.267528),
    (0.779528,-0.56636,0.267528),(0.716057,-0.644741,0.267528),(0.644741,-0.716057,0.267528),
    (0.56636,-0.779528,0.267528),(0.481775,-0.834459,0.267528),(0.391911,-0.880247,0.267528),
    (0.297753,-0.91639,0.267528),(0.200333,-0.942494,0.267528),(0.100718,-0.958272,0.267528),
    (0.0,-0.96355,0.267528),(-0.100718,-0.958272,0.267528),(-0.200333,-0.942494,0.267528),
    (-0.297753,-0.91639,0.267528),(-0.391911,-0.880247,0.267528),(-0.481775,-0.834459,0.267528),
    (-0.56636,-0.779528,0.267528),(-0.644741,-0.716057,0.267528),(-0.716057,-0.644741,0.267528),
    (-0.779528,-0.56636,0.267528),(-0.834459,-0.481775,0.267528),(-0.880247,-0.391911,0.267528),
    (-0.91639,-0.297753,0.267528),(-0.942494,-0.200333,0.267528),(-0.958272,-0.100718,0.267528),
    (-0.96355,0.0,0.267528),(-0.958272,0.100718,0.267528),(-0.942494,0.200333,0.267528),
    (-0.91639,0.297753,0.267528),(-0.880247,0.391911,0.267528),(-0.834459,0.481775,0.267528),
    (-0.779528,0.56636,0.267528),(-0.716057,0.644741,0.267528),(-0.644741,0.716057,0.267528),
    (-0.56636,0.779528,0.267528),(-0.481775,0.834459,0.267528),(-0.391911,0.880247,0.267528),
    (-0.297753,0.91639,0.267528),(-0.200333,0.942494,0.267528),(-0.100718,0.958272,0.267528),
    (0.0,0.928977,0.370138),(0.097105,0.923888,0.370138),(0.193145,0.908676,0.370138),
    (0.28707,0.883509,0.370138),(0.377849,0.848662,0.370138),(0.464488,0.804517,0.370138),
    (0.546039,0.751558,0.370138),(0.621607,0.690364,0.370138),(0.690364,0.621607,0.370138),
    (0.751558,0.546039,0.370138),(0.804517,0.464488,0.370138),(0.848662,0.377849,0.370138),
    (0.883509,0.28707,0.370138),(0.908676,0.193145,0.370138),(0.923888,0.097105,0.370138),
    (0.928977,0.0,0.370138),(0.923888,-0.097105,0.370138),(0.908676,-0.193145,0.370138),
    (0.883509,-0.28707,0.370138),(0.848662,-0.377849,0.370138),(0.804517,-0.464488,0.370138),
    (0.751558,-0.546039,0.370138),(0.690364,-0.621607,0.370138),(0.621607,-0.690364,0.370138),
    (0.546039,-0.751558,0.370138),(0.464488,-0.804517,0.370138),(0.377849,-0.848662,0.370138),
    (0.28707,-0.883509,0.370138),(0.193145,-0.908676,0.370138),(0.097105,-0.923888,0.370138),
    (0.0,-0.928977,0.370138),(-0.097105,-0.923888,0.370138),(-0.193145,-0.908676,0.370138),
    (-0.28707,-0.883509,0.370138),(-0.377849,-0.848662,0.370138),(-0.464488,-0.804517,0.370138),
    (-0.546039,-0.751558,0.370138),(-0.621607,-0.690364,0.370138),(-0.690364,-0.621607,0.370138),
    (-0.751558,-0.546039,0.370138),(-0.804517,-0.464488,0.370138),(-0.848662,-0.377849,0.370138),
    (-0.883509,-0.28707,0.370138),(-0.908676,-0.193145,0.370138),(-0.923888,-0.097105,0.370138),
    (-0.928977,0.0,0.370138),(-0.923888,0.097105,0.370138),(-0.908676,0.193145,0.370138),
    (-0.883509,0.28707,0.370138),(-0.848662,0.377849,0.370138),(-0.804517,0.464488,0.370138),
    (-0.751558,0.546039,0.370138),(-0.690364,0.621607,0.370138),(-0.621607,0.690364,0.370138),
    (-0.546039,0.751558,0.370138),(-0.464488,0.804517,0.370138),(-0.377849,0.848662,0.370138),
    (-0.28707,0.883509,0.370138),(-0.193145,0.908676,0.370138),(-0.097105,0.923888,0.370138),
    (0.0,0.883512,0.468408),(0.115321,0.875953,0.468408),(0.22867,0.853407,0.468408),
    (0.338105,0.816259,0.468408),(0.441756,0.765144,0.468408),(0.537848,0.700937,0.468408),
    (0.624737,0.624737,0.468408),(0.700937,0.537848,0.468408),(0.765144,0.441756,0.468408),
    (0.816259,0.338105,0.468408),(0.853407,0.22867,0.468408),(0.875953,0.115321,0.468408),
    (0.883512,0.0,0.468408),(0.875953,-0.115321,0.468408),(0.853407,-0.22867,0.468408),
    (0.816259,-0.338105,0.468408),(0.765144,-0.441756,0.468408),(0.700937,-0.537848,0.468408),
    (0.624737,-0.624737,0.468408),(0.537848,-0.700937,0.468408),(0.441756,-0.765144,0.468408),
    (0.338105,-0.816259,0.468408),(0.22867,-0.853407,0.468408),(0.115321,-0.875953,0.468408),
    (0.0,-0.883512,0.468408),(-0.115321,-0.875953,0.468408),(-0.22867,-0.853407,0.468408),
    (-0.338105,-0.816259,0.468408),(-0.441756,-0.765144,0.468408),(-0.537848,-0.700937,0.468408),
    (-0.624737,-0.624737,0.468408),(-0.700937,-0.537848,0.468408),(-0.765144,-0.441756,0.468408),
    (-0.816259,-0.338105,0.468408),(-0.853407,-0.22867,0.468408),(-0.875953,-0.115321,0.468408),
    (-0.883512,0.0,0.468408),(-0.875953,0.115321,0.468408),(-0.853407,0.22867,0.468408),
    (-0.816259,0.338105,0.468408),(-0.765144,0.441756,0.468408),(-0.700937,0.537848,0.468408),
    (-0.624737,0.624737,0.468408),(-0.537848,0.700937,0.468408),(-0.441756,0.765144,0.468408),
    (-0.338105,0.816259,0.468408),(-0.22867,0.853407,0.468408),(-0.115321,0.875953,0.468408),
    (0.0,0.827689,0.561187),(0.108035,0.820608,0.561187),(0.214222,0.799486,0.561187),
    (0.316743,0.764685,0.561187),(0.413844,0.7168,0.561187),(0.503865,0.65665,0.561187),
    (0.585265,0.585265,0.561187),(0.65665,0.503865,0.561187),(0.7168,0.413844,0.561187),
    (0.764685,0.316743,0.561187),(0.799486,0.214222,0.561187),(0.820608,0.108035,0.561187),
    (0.827689,0.0,0.561187),(0.820608,-0.108035,0.561187),(0.799486,-0.214222,0.561187),
    (0.764685,-0.316743,0.561187),(0.7168,-0.413844,0.561187),(0.65665,-0.503865,0.561187),
    (0.585265,-0.585265,0.561187),(0.503865,-0.65665,0.561187),(0.413844,-0.7168,0.561187),
    (0.316743,-0.764685,0.561187),(0.214222,-0.799486,0.561187),(0.108035,-0.820608,0.561187),
    (0.0,-0.827689,0.561187),(-0.108035,-0.820608,0.561187),(-0.214222,-0.799486,0.561187),
    (-0.316743,-0.764685,0.561187),(-0.413844,-0.7168,0.561187),(-0.503865,-0.65665,0.561187),
    (-0.585265,-0.585265,0.561187),(-0.65665,-0.503865,0.561187),(-0.7168,-0.413844,0.561187),
    (-0.764685,-0.316743,0.561187),(-0.799486,-0.214222,0.561187),(-0.820608,-0.108035,0.561187),
    (-0.827689,0.0,0.561187),(-0.820608,0.108035,0.561187),(-0.799486,0.214222,0.561187),
    (-0.764685,0.316743,0.561187),(-0.7168,0.413844,0.561187),(-0.65665,0.503865,0.561187),
    (-0.585265,0.585265,0.561187),(-0.503865,0.65665,0.561187),(-0.413844,0.7168,0.561187),
    (-0.316743,0.764685,0.561187),(-0.214222,0.799486,0.561187),(-0.108035,0.820608,0.561187),
    (0.0,0.762162,0.647386),(0.099482,0.755642,0.647386),(0.197262,0.736192,0.647386),
    (0.291667,0.704146,0.647386),(0.381081,0.660052,0.647386),(0.463975,0.604664,0.647386),
    (0.53893,0.53893,0.647386),(0.604664,0.463975,0.647386),(0.660052,0.381081,0.647386),
    (0.704146,0.291667,0.647386),(0.736192,0.197262,0.647386),(0.755642,0.099482,0.647386),
    (0.762162,0.0,0.647386),(0.755642,-0.099482,0.647386),(0.736192,-0.197262,0.647386),
    (0.704146,-0.291667,0.647386),(0.660052,-0.381081,0.647386),(0.604664,-0.463975,0.647386),
    (0.53893,-0.53893,0.647386),(0.463975,-0.604664,0.647386),(0.381081,-0.660052,0.647386),
    (0.291667,-0.704146,0.647386),(0.197262,-0.736192,0.647386),(0.099482,-0.755642,0.647386),
    (0.0,-0.762162,0.647386),(-0.099482,-0.755642,0.647386),(-0.197262,-0.736192,0.647386),
    (-0.291667,-0.704146,0.647386),(-0.381081,-0.660052,0.647386),(-0.463975,-0.604664,0.647386),
    (-0.53893,-0.53893,0.647386),(-0.604664,-0.463975,0.647386),(-0.660052,-0.381081,0.647386),
    (-0.704146,-0.291667,0.647386),(-0.736192,-0.197262,0.647386),(-0.755642,-0.099482,0.647386),
    (-0.762162,0.0,0.647386),(-0.755642,0.099482,0.647386),(-0.736192,0.197262,0.647386),
    (-0.704146,0.291667,0.647386),(-0.660052,0.381081,0.647386),(-0.604664,0.463975,0.647386),
    (-0.53893,0.53893,0.647386),(-0.463975,0.604664,0.647386),(-0.381081,0.660052,0.647386),
    (-0.291667,0.704146,0.647386),(-0.197262,0.736192,0.647386),(-0.099482,0.755642,0.647386),
    (0.0,0.687699,0.725995),(0.089763,0.681816,0.725995),(0.17799,0.664267,0.725995),
    (0.263171,0.635351,0.725995),(0.34385,0.595565,0.725995),(0.418645,0.545589,0.725995),
    (0.486277,0.486277,0.725995),(0.545589,0.418645,0.725995),(0.595565,0.34385,0.725995),
    (0.635351,0.263171,0.725995),(0.664267,0.17799,0.725995),(0.681816,0.089763,0.725995),
    (0.687699,0.0,0.725995),(0.681816,-0.089763,0.725995),(0.664267,-0.17799,0.725995),
    (0.635351,-0.263171,0.725995),(0.595565,-0.34385,0.725995),(0.545589,-0.418645,0.725995),
    (0.486277,-0.486277,0.725995),(0.418645,-0.545589,0.725995),(0.34385,-0.595565,0.725995),
    (0.263171,-0.635351,0.725995),(0.17799,-0.664267,0.725995),(0.089763,-0.681816,0.725995),
    (0.0,-0.687699,0.725995),(-0.089763,-0.681816,0.725995),(-0.17799,-0.664267,0.725995),
    (-0.263171,-0.635351,0.725995),(-0.34385,-0.595565,0.725995),(-0.418645,-0.545589,0.725995),
    (-0.486277,-0.486277,0.725995),(-0.545589,-0.418645,0.725995),(-0.595565,-0.34385,0.725995),
    (-0.635351,-0.263171,0.725995),(-0.664267,-0.17799,0.725995),(-0.681816,-0.089763,0.725995),
    (-0.687699,0.0,0.725995),(-0.681816,0.089763,0.725995),(-0.664267,0.17799,0.725995),
    (-0.635351,0.263171,0.725995),(-0.595565,0.34385,0.725995),(-0.545589,0.418645,0.725995),
    (-0.486277,0.486277,0.725995),(-0.418645,0.545589,0.725995),(-0.34385,0.595565,0.725995),
    (-0.263171,0.635351,0.725995),(-0.17799,0.664267,0.725995),(-0.089763,0.681816,0.725995),
    (0.0,0.605174,0.796093),(0.105087,0.59598,0.796093),(0.206982,0.568678,0.796093),
    (0.302587,0.524096,0.796093),(0.388998,0.46359,0.796093),(0.46359,0.388998,0.796093),
    (0.524096,0.302587,0.796093),(0.568678,0.206982,0.796093),(0.59598,0.105087,0.796093),
    (0.605174,0.0,0.796093),(0.59598,-0.105087,0.796093),(0.568678,-0.206982,0.796093),
    (0.524096,-0.302587,0.796093),(0.46359,-0.388998,0.796093),(0.388998,-0.46359,0.796093),
    (0.302587,-0.524096,0.796093),(0.206982,-0.568678,0.796093),(0.105087,-0.59598,0.796093),
    (0.0,-0.605174,0.796093),(-0.105087,-0.59598,0.796093),(-0.206982,-0.568678,0.796093),
    (-0.302587,-0.524096,0.796093),(-0.388998,-0.46359,0.796093),(-0.46359,-0.388998,0.796093),
    (-0.524096,-0.302587,0.796093),(-0.568678,-0.206982,0.796093),(-0.59598,-0.105087,0.796093),
    (-0.605174,0.0,0.796093),(-0.59598,0.105087,0.796093),(-0.568678,0.206982,0.796093),
    (-0.524096,0.302587,0.796093),(-0.46359,0.388998,0.796093),(-0.388998,0.46359,0.796093),
    (-0.302587,0.524096,0.796093),(-0.206982,0.568678,0.796093),(-0.105087,0.59598,0.796093),
    (0.0,0.515554,0.856857),(0.089525,0.507721,0.856857),(0.17633,0.484462,0.856857),
    (0.257777,0.446483,0.856857),(0.331392,0.394937,0.856857),(0.394937,0.331392,0.856857),
    (0.446483,0.257777,0.856857),(0.484462,0.17633,0.856857),(0.507721,0.089525,0.856857),
    (0.515554,0.0,0.856857),(0.507721,-0.089525,0.856857),(0.484462,-0.17633,0.856857),
    (0.446483,-0.257777,0.856857),(0.394937,-0.331392,0.856857),(0.331392,-0.394937,0.856857),
    (0.257777,-0.446483,0.856857),(0.17633,-0.484462,0.856857),(0.089525,-0.507721,0.856857),
    (0.0,-0.515554,0.856857),(-0.089525,-0.507721,0.856857),(-0.17633,-0.484462,0.856857),
    (-0.257777,-0.446483,0.856857),(-0.331392,-0.394937,0.856857),(-0.394937,-0.331392,0.856857),
    (-0.446483,-0.257777,0.856857),(-0.484462,-0.17633,0.856857),(-0.507721,-0.089525,0.856857),
    (-0.515554,0.0,0.856857),(-0.507721,0.089525,0.856857),(-0.484462,0.17633,0.856857),
    (-0.446483,0.257777,0.856857),(-0.394937,0.331392,0.856857),(-0.331392,0.394937,0.856857),
    (-0.257777,0.446483,0.856857),(-0.17633,0.484462,0.856857),(-0.089525,0.507721,0.856857),
    (0.0,0.419889,0.907575),(0.108675,0.405582,0.907575),(0.209945,0.363635,0.907575),
    (0.296906,0.296906,0.907575),(0.363635,0.209945,0.907575),(0.405582,0.108675,0.907575),
    (0.419889,0.0,0.907575),(0.405582,-0.108675,0.907575),(0.363635,-0.209945,0.907575),
    (0.296906,-0.296906,0.907575),(0.209945,-0.363635,0.907575),(0.108675,-0.405582,0.907575),
    (0.0,-0.419889,0.907575),(-0.108675,-0.405582,0.907575),(-0.209945,-0.363635,0.907575),
    (-0.296906,-0.296906,0.907575),(-0.363635,-0.209945,0.907575),(-0.405582,-0.108675,0.907575),
    (-0.419889,0.0,0.907575),(-0.405582,0.108675,0.907575),(-0.363635,0.209945,0.907575),
    (-0.296906,0.296906,0.907575),(-0.209945,0.363635,0.907575),(-0.108675,0.405582,0.907575),
    (0.0,0.319302,0.947653),(0.082641,0.308422,0.947653),(0.159651,0.276523,0.947653),
    (0.22578,0.22578,0.947653),(0.276523,0.159651,0.947653),(0.308422,0.082641,0.947653),
    (0.319302,0.0,0.947653),(0.308422,-0.082641,0.947653),(0.276523,-0.159651,0.947653),
    (0.22578,-0.22578,0.947653),(0.159651,-0.276523,0.947653),(0.082641,-0.308422,0.947653),
    (0.0,-0.319302,0.947653),(-0.082641,-0.308422,0.947653),(-0.159651,-0.276523,0.947653),
    (-0.22578,-0.22578,0.947653),(-0.276523,-0.159651,0.947653),(-0.308422,-0.082641,0.947653),
    (-0.319302,0.0,0.947653),(-0.308422,0.082641,0.947653),(-0.276523,0.159651,0.947653),
    (-0.22578,0.22578,0.947653),(-0.159651,0.276523,0.947653),(-0.082641,0.308422,0.947653),
    (0.0,0.21497,0.976621),(0.107485,0.18617,0.976621),(0.18617,0.107485,0.976621),
    (0.21497,0.0,0.976621),(0.18617,-0.107485,0.976621),(0.107485,-0.18617,0.976621),
    (0.0,-0.21497,0.976621),(-0.107485,-0.18617,0.976621),(-0.18617,-0.107485,0.976621),
    (-0.21497,0.0,0.976621),(-0.18617,0.107485,0.976621),(-0.107485,0.18617,0.976621),
    (0.0,0.108119,0.994138),(0.05406,0.093634,0.994138),(0.093634,0.05406,0.994138),
    (0.108119,0.0,0.994138),(0.093634,-0.05406,0.994138),(0.05406,-0.093634,0.994138),
    (0.0,-0.108119,0.994138),(-0.05406,-0.093634,0.994138),(-0.093634,-0.05406,0.994138),
    (-0.108119,0.0,0.994138),(-0.093634,0.05406,0.994138),(-0.05406,0.093634,0.994138),
    (0.0,0.0,1.0)]
        
        return ReinhartPatchesNormalVectors
    
    TregenzaPatchesNormalVectors = [
    (0.0,0.994522,0.104528),(0.206773,0.972789,0.104528),(0.404508,0.908541,0.104528),
    (0.584565,0.804585,0.104528),(0.739074,0.665465,0.104528),(0.861281,0.497261,0.104528),
    (0.945847,0.307324,0.104528),(0.989074,0.103956,0.104528),(0.989074,-0.103956,0.104528),
    (0.945847,-0.307324,0.104528),(0.861281,-0.497261,0.104528),(0.739074,-0.665465,0.104528),
    (0.584565,-0.804585,0.104528),(0.404508,-0.908541,0.104528),(0.206773,-0.972789,0.104528),
    (0.0,-0.994522,0.104528),(-0.206773,-0.972789,0.104528),(-0.404508,-0.908541,0.104528),
    (-0.584565,-0.804585,0.104528),(-0.739074,-0.665465,0.104528),(-0.861281,-0.497261,0.104528),
    (-0.945847,-0.307324,0.104528),(-0.989074,-0.103956,0.104528),(-0.989074,0.103956,0.104528),
    (-0.945847,0.307324,0.104528),(-0.861281,0.497261,0.104528),(-0.739074,0.665465,0.104528),
    (-0.584565,0.804585,0.104528),(-0.404508,0.908541,0.104528),(-0.206773,0.972789,0.104528),
    (0.0,0.951057,0.309017),(0.197736,0.930274,0.309017),(0.38683,0.868833,0.309017),
    (0.559017,0.769421,0.309017),(0.706773,0.636381,0.309017),(0.823639,0.475528,0.309017),
    (0.904508,0.293893,0.309017),(0.945847,0.099412,0.309017),(0.945847,-0.099412,0.309017),
    (0.904508,-0.293893,0.309017),(0.823639,-0.475528,0.309017),(0.706773,-0.636381,0.309017),
    (0.559017,-0.769421,0.309017),(0.38683,-0.868833,0.309017),(0.197736,-0.930274,0.309017),
    (0.0,-0.951057,0.309017),(-0.197736,-0.930274,0.309017),(-0.38683,-0.868833,0.309017),
    (-0.559017,-0.769421,0.309017),(-0.706773,-0.636381,0.309017),(-0.823639,-0.475528,0.309017),
    (-0.904508,-0.293893,0.309017),(-0.945847,-0.099412,0.309017),(-0.945847,0.099412,0.309017),
    (-0.904508,0.293893,0.309017),(-0.823639,0.475528,0.309017),(-0.706773,0.636381,0.309017),
    (-0.559017,0.769421,0.309017),(-0.38683,0.868833,0.309017),(-0.197736,0.930274,0.309017),
    (0.0,0.866025,0.5),(0.224144,0.836516,0.5),(0.433013,0.75,0.5),(0.612372,0.612372,0.5),
    (0.75,0.433013,0.5),(0.836516,0.224144,0.5),(0.866025,0.0,0.5),(0.836516,-0.224144,0.5),
    (0.75,-0.433013,0.5),(0.612372,-0.612372,0.5),(0.433013,-0.75,0.5),(0.224144,-0.836516,0.5),
    (0.0,-0.866025,0.5),(-0.224144,-0.836516,0.5),(-0.433013,-0.75,0.5),(-0.612372,-0.612372,0.5),
    (-0.75,-0.433013,0.5),(-0.836516,-0.224144,0.5),(-0.866025,0.0,0.5),(-0.836516,0.224144,0.5),
    (-0.75,0.433013,0.5),(-0.612372,0.612372,0.5),(-0.433013,0.75,0.5),(-0.224144,0.836516,0.5),
    (0.0,0.743145,0.669131),(0.19234,0.717823,0.669131),(0.371572,0.643582,0.669131),(0.525483,0.525483,0.669131),
    (0.643582,0.371572,0.669131),(0.717823,0.19234,0.669131),(0.743145,0.0,0.669131),(0.717823,-0.19234,0.669131),
    (0.643582,-0.371572,0.669131),(0.525483,-0.525483,0.669131),(0.371572,-0.643582,0.669131),
    (0.19234,-0.717823,0.669131),(0.0,-0.743145,0.669131),(-0.19234,-0.717823,0.669131),
    (-0.371572,-0.643582,0.669131),(-0.525483,-0.525483,0.669131),(-0.643582,-0.371572,0.669131),
    (-0.717823,-0.19234,0.669131),(-0.743145,0.0,0.669131),(-0.717823,0.19234,0.669131),
    (-0.643582,0.371572,0.669131),(-0.525483,0.525483,0.669131),(-0.371572,0.643582,0.669131),
    (-0.19234,0.717823,0.669131),(0.0,0.587785,0.809017),(0.201034,0.552337,0.809017),
    (0.377821,0.45027,0.809017),(0.509037,0.293893,0.809017),(0.578855,0.102068,0.809017),
    (0.578855,-0.102068,0.809017),(0.509037,-0.293893,0.809017),(0.377821,-0.45027,0.809017),
    (0.201034,-0.552337,0.809017),(0.0,-0.587785,0.809017),(-0.201034,-0.552337,0.809017),
    (-0.377821,-0.45027,0.809017),(-0.509037,-0.293893,0.809017),(-0.578855,-0.102068,0.809017),
    (-0.578855,0.102068,0.809017),(-0.509037,0.293893,0.809017),(-0.377821,0.45027,0.809017),
    (-0.201034,0.552337,0.809017),(0.0,0.406737,0.913545),(0.203368,0.352244,0.913545),
    (0.352244,0.203368,0.913545),(0.406737,0.0,0.913545),(0.352244,-0.203368,0.913545),
    (0.203368,-0.352244,0.913545),(0.0,-0.406737,0.913545),(-0.203368,-0.352244,0.913545),
    (-0.352244,-0.203368,0.913545),(-0.406737,0.0,0.913545),(-0.352244,0.203368,0.913545),
    (-0.203368,0.352244,0.913545),(0.0,0.207912,0.978148),(0.180057,0.103956,0.978148),
    (0.180057,-0.103956,0.978148),(0.0,-0.207912,0.978148),(-0.180057,-0.103956,0.978148),
    (-0.180057,0.103956,0.978148),(0.0,0.0,1)]


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
        self.timeZone = timeZone
    
    #This part is written by Trygve Wastvedt (Trygve.Wastvedt@gmail.com).
    def solInitOutput(self, month, day, hour):
        year = 2014
        self.time = hour
        
        a = 1 if (month < 3) else 0
        y = year + 4800 - a
        m = month + 12*a - 3
        self.julianDay = day + math.floor((153*m + 2)/5) + 59
        
        self.julianDay += (self.time - self.timeZone)/24.0  + 365*y + math.floor(y/4) \
            - math.floor(y/100) + math.floor(y/400) - 32045.5 - 59
        
        julianCentury = (self.julianDay - 2451545) / 36525
        #degrees
        geomMeanLongSun = (280.46646 + julianCentury * (36000.76983 + julianCentury*0.0003032)) % 360
        #degrees
        geomMeanAnomSun = 357.52911 + julianCentury*(35999.05029 - 0.0001537*julianCentury)
        eccentOrbit = 0.016708634 - julianCentury*(0.000042037 + 0.0000001267*julianCentury)
        sunEqOfCtr = math.sin(math.radians(geomMeanAnomSun))*(1.914602 - julianCentury*(0.004817+0.000014*julianCentury)) + \
            math.sin(math.radians(2*geomMeanAnomSun))*(0.019993-0.000101*julianCentury) + \
            math.sin(math.radians(3*geomMeanAnomSun))*0.000289
        #degrees
        sunTrueLong = geomMeanLongSun + sunEqOfCtr
        #AUs
        sunTrueAnom = geomMeanAnomSun + sunEqOfCtr
        #AUs
        sunRadVector = (1.000001018*(1 - eccentOrbit**2))/ \
            (1 + eccentOrbit*math.cos(math.radians(sunTrueLong)))
        #degrees
        sunAppLong = sunTrueLong - 0.00569 - 0.00478*math.sin(math.radians(125.04-1934.136*julianCentury))
        #degrees
        meanObliqEcliptic = 23 + (26 + ((21.448 - julianCentury*(46.815 + \
            julianCentury*(0.00059 - julianCentury*0.001813))))/60)/60
        #degrees
        obliqueCorr = meanObliqEcliptic + 0.00256*math.cos(math.radians(125.04 - 1934.136*julianCentury))
        #degrees
        sunRightAscen = math.degrees(math.atan2(math.cos(math.radians(obliqueCorr))* \
            math.sin(math.radians(sunAppLong)), math.cos(math.radians(sunAppLong))))
        #RADIANS
        self.solDec = math.asin(math.sin(math.radians(obliqueCorr))*math.sin(math.radians(sunAppLong)))
        
        varY = math.tan(math.radians(obliqueCorr/2))*math.tan(math.radians(obliqueCorr/2))
        #minutes
        eqOfTime = 4*math.degrees(varY*math.sin(2*math.radians(geomMeanLongSun)) \
            - 2*eccentOrbit*math.sin(math.radians(geomMeanAnomSun)) \
            + 4*eccentOrbit*varY*math.sin(math.radians(geomMeanAnomSun))*math.cos(2*math.radians(geomMeanLongSun)) \
            - 0.5*(varY**2)*math.sin(4*math.radians(geomMeanLongSun)) \
            - 1.25*(eccentOrbit**2)*math.sin(2*math.radians(geomMeanAnomSun)))
        #hours
        self.solTime = ((self.time*60 + eqOfTime + 4*math.degrees(self.s_longtitude) - 60*self.timeZone) % 1440)/60
        #degrees
        hourAngle = (self.solTime*15 + 180) if (self.solTime*15 < 0) else (self.solTime*15 - 180)
        #RADIANS
        self.zenith = math.acos(math.sin(self.solLat)*math.sin(self.solDec) \
            + math.cos(self.solLat)*math.cos(self.solDec)*math.cos(math.radians(hourAngle)))
        self.solAlt = (math.pi/2) - self.zenith
        
        self.solAz = ((math.acos(((math.sin(self.solLat)*math.cos(self.zenith)) \
            - math.sin(self.solDec))/(math.cos(self.solLat)*math.sin(self.zenith))) + math.pi) % (2*math.pi)) \
            if (hourAngle > 0) else \
                ((3*math.pi - math.acos(((math.sin(self.solLat)*math.cos(self.zenith)) \
                - math.sin(self.solDec))/(math.cos(self.solLat)*math.sin(self.zenith)))) % (2*math.pi))
    
    def sunReverseVectorCalc(self):
        basePoint = rc.Geometry.Point3d.Add(rc.Geometry.Point3d.Origin,rc.Geometry.Vector3f(0,1,0))
        basePoint = rc.Geometry.Point(basePoint)
        basePoint.Rotate(self.solAlt, rc.Geometry.Vector3d.XAxis, rc.Geometry.Point3d.Origin)
        basePoint.Rotate(-(self.solAz - self.angle2North), rc.Geometry.Vector3d.ZAxis, rc.Geometry.Point3d.Origin)
        sunVector = rc.Geometry.Vector3d(basePoint.Location - rc.Geometry.Point3d.Origin)
        sunVector.Unitize()
        
        return sunVector
    
    def sunPosPt(self, sunScale = 1):
        #print 'altitude is:', math.degrees(self.solAlt), 'and azimuth is:', math.degrees(self.solAz)
        basePoint = rc.Geometry.Point3d.Add(self.cenPt,rc.Geometry.Vector3f(0,self.scale,0))
        basePoint = rc.Geometry.Point(basePoint)
        basePoint.Rotate(self.solAlt, rc.Geometry.Vector3d.XAxis, self.cenPt)
        basePoint.Rotate(-(self.solAz - self.angle2North), rc.Geometry.Vector3d.ZAxis, self.cenPt)
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


class Vector:
    
    def __init__(self, items):
        self.v = items
    
    def dot(self, u):
        if (len(self.v) == len(u.v)):
            t = 0
            for i,j in zip(self.v, u.v):
                t += i*j
            return t
        else:
            return None
    
    def __add__(self, b):
        v = []
        for i,j in zip(self.v, b.v):
            v.append(i+j)
        return Vector(v)
    
    def __sub__(self, b):
        v = []
        for i, v in zip(self.v, b.v):
            v.append(i-j)
        return Vector(v)
    
    def __mul__(self, other):
        return self.__class__(self.v).__imul__(other)
    
    def __rmul__(self, other):
        # The __rmul__ is called in scalar * vector case; it's commutative.
        return self.__class__(self.v).__imul__(other)
    
    def __imul__(self, other):
        '''Vectors can be multipled by a scalar. Two 3d vectors can cross.'''
        if isinstance(other, Vector):
            self.v = self.cross(other).v
        else:
            self.v = [i * other for i in self.v]
        return self


class Sun:
    pass


class Coeff:
    A = None
    B = None
    C = None
    D = None
    E = None


class Sky:
    def __init__(self):
        pass
    
    def createSky(self, doy, year, hour, timeZone, latitude, longitude, turbidity):
        self.doy = doy
        self.year = year
        self.hour = hour
        self.timeZone = timeZone
        self.latitude = latitude
        self.longitude = longitude
        self.turbidity = turbidity
        
        self.sun = Sun()
        
        self.setTime()
        
        self.setSunPosition()
        
        self.setZenitalAbsolutes()
        
        self.setCoefficents()
    
    def info(self):
        print(  "doy: {0}\n"
                "julian day: {9}\n"
                "year: {10}\n"
                "time: {1}\n"
                "solar time: {2}\n"
                "latitude: {3}\n"
                "longitude: {4}\n"
                "turbidity: {5}\n"
                "sun azimuth: {6}\n"
                "sun zenith: {7}\n"
                "sun declination: {8}\n" \
                .format(self.doy, self.time, self.sun.time, self.latitude, \
                self.longitude, self.turbidity, math.degrees(self.sun.azimuth), math.degrees(self.sun.zenith), \
                math.degrees(self.sun.declination), self.julianDay, self.year))
    
    def setZenitalAbsolutes(self):
        Yz = (4.0453*self.turbidity - 4.9710) \
            * math.tan((4/9 - self.turbidity /120) * (math.pi - 2*self.sun.zenith)) \
            - 0.2155*self.turbidity + 2.4192
        Y0 = (4.0453*self.turbidity - 4.9710) \
            * math.tan((4/9 - self.turbidity /120) * (math.pi)) \
            - 0.2155*self.turbidity + 2.4192
        self.Yz = Yz/Y0
     
        z3 = self.sun.zenith ** 3
        z2 = self.sun.zenith ** 2
        z = self.sun.zenith
        T_vec = Vector([self.turbidity ** 2, self.turbidity, 1])
     
        x = Vector([0.00166 * z3 - 0.00375 * z2 + 0.00209 * z,
            -0.02903 * z3 + 0.06377 * z2 - 0.03202 * z + 0.00394,
            0.11693 * z3 - 0.21196 * z2 + 0.06052 * z + 0.25886])
        self.xz = T_vec.dot(x)
        
        y = Vector([0.00275 * z3 - 0.00610 * z2 + 0.00317 * z,
            -0.04214 * z3 + 0.08970 * z2 - 0.04153 * z + 0.00516,
            0.15346 * z3 - 0.26756 * z2 + 0.06670 * z + 0.26688])
        self.yz = T_vec.dot(y)
     
    def setCoefficents(self):
        #A: darkening or brightening of the horizon
        #B: luminance gradient near the horizon
        #C: relative intensity of the circumsolar region
        #D: width of the circumsolar region
        #E: relative backscattered light
        
        #values derived by 
        self.coeffsY = Coeff()
        self.coeffsY.A = 0.1787 * self.turbidity - 1.4630
        self.coeffsY.B = -0.3554 * self.turbidity + 0.4275
        self.coeffsY.C = -0.0227 * self.turbidity + 5.3251
        self.coeffsY.D = 0.1206 * self.turbidity - 2.5771
        self.coeffsY.E = -0.0670 * self.turbidity + 0.3703
     
        self.coeffsx = Coeff()
        self.coeffsx.A = -0.0193 * self.turbidity - 0.2592
        self.coeffsx.B = -0.0665 * self.turbidity + 0.0008
        self.coeffsx.C = -0.0004 * self.turbidity + 0.2125
        self.coeffsx.D = -0.0641 * self.turbidity - 0.8989
        self.coeffsx.E = -0.0033 * self.turbidity + 0.0452
     
        self.coeffsy = Coeff()
        self.coeffsy.A = -0.0167 * self.turbidity - 0.2608
        self.coeffsy.B = -0.0950 * self.turbidity + 0.0092
        self.coeffsy.C = -0.0079 * self.turbidity + 0.2102
        self.coeffsy.D = -0.0441 * self.turbidity - 1.6537
        self.coeffsy.E = -0.0109 * self.turbidity + 0.0529
    
    def perez(self, zen, g, coeffs):
        return (1 + coeffs.A*math.exp(coeffs.B/math.cos(zen))) * \
        (1 + coeffs.C*math.exp(coeffs.D*g) + coeffs.E*(math.cos(g) ** 2))
    
    def YxyToXYZ(self, vec):
        Y = vec.v[0]
        x = vec.v[1]
        y = vec.v[2]
        
        X = x/y*Y
        Z = (1-x-y)/y*Y
        
        return Vector([X, Y, Z])
    
    def YxyToRGB(self, vec):
        [X,Y,Z] = self.YxyToXYZ(vec).v
        
        return Vector([3.2406 * X - 1.5372 * Y - 0.4986 * Z, \
            -0.9689 * X + 1.8758 * Y + 0.0415 * Z, \
            0.0557 * X - 0.2040 * Y + 1.0570 * Z])
    
    def gamma(self, zenith, azimuth):
        return math.acos(math.sin(self.sun.zenith)*math.sin(zenith)*math.cos(azimuth-self.sun.azimuth)+math.cos(self.sun.zenith)*math.cos(zenith))
    
    def sunlight(self):
        optMass = 1/(math.cos(self.sun.zenith) + 0.15*(98.885 - self.sun.zenith)**(-1.253))
        
        #constants
        a = 1.3 #wavelength exponent (sunsky: suggested by Angstrom?)
        w = 2 #(sunsky)
        l = 35 #ozone_thickness (sunsky)
        
        turbCoeff = 0.04608*self.turbidity - 0.04586 #sunsky: approximation
        
        trans_rayleigh = math.exp(-0.008735*wavelength**(-4.08*optMass))
        
        trans_aerosol = math.exp(-turbCoeff*wavelength**(-a*optMass))
        
        trans_ozone = math.exp(-k_o*l*optMass)
        
        trans_gass = math.exp(-1.41*k_g*optMass / (1 + 118.93*k_g*optMass)**0.45)
        
        trans_vapor = math.exp(-0.2385*k_wa*w*optMass / (1 + 20.07*k_wa*w*optMass)**0.45)
    
    def setTime(self):
        self.time = self.hour
        
        self.julianDay = self.doy
        y = self.year + 4800
        
        self.julianDay += (self.time - self.timeZone)/24.0  + 365*y + math.floor(y/4) \
            - math.floor(y/100) + math.floor(y/400) - 32045.5 - 59
    
    def setSunPosition(self):
        julianCentury = (self.julianDay - 2451545) / 36525
        #degrees
        geomMeanLongSun = (280.46646 + julianCentury * (36000.76983 + julianCentury*0.0003032)) % 360
        #degrees
        geomMeanAnomSun = 357.52911 + julianCentury*(35999.05029 - 0.0001537*julianCentury)
        eccentOrbit = 0.016708634 - julianCentury*(0.000042037 + 0.0000001267*julianCentury)
        sunEqOfCtr = math.sin(math.radians(geomMeanAnomSun))*(1.914602 - julianCentury*(0.004817+0.000014*julianCentury)) + \
            math.sin(math.radians(2*geomMeanAnomSun))*(0.019993-0.000101*julianCentury) + \
            math.sin(math.radians(3*geomMeanAnomSun))*0.000289
        #degrees
        sunTrueLong = geomMeanLongSun + sunEqOfCtr
        #AUs
        sunTrueAnom = geomMeanAnomSun + sunEqOfCtr
        #AUs
        sunRadVector = (1.000001018*(1 - eccentOrbit**2))/ \
            (1 + eccentOrbit*math.cos(math.radians(sunTrueLong)))
        #degrees
        sunAppLong = sunTrueLong - 0.00569 - 0.00478*math.sin(math.radians(125.04-1934.136*julianCentury))
        #degrees
        meanObliqEcliptic = 23 + (26 + ((21.448 - julianCentury*(46.815 + \
            julianCentury*(0.00059 - julianCentury*0.001813))))/60)/60
        #degrees
        obliqueCorr = meanObliqEcliptic + 0.00256*math.cos(math.radians(125.04 - 1934.136*julianCentury))
        #degrees
        sunRightAscen = math.degrees(math.atan2(math.cos(math.radians(obliqueCorr))* \
            math.sin(math.radians(sunAppLong)), math.cos(math.radians(sunAppLong))))
        #RADIANS
        self.sun.declination = math.asin(math.sin(math.radians(obliqueCorr))*math.sin(math.radians(sunAppLong)))
        
        varY = math.tan(math.radians(obliqueCorr/2))*math.tan(math.radians(obliqueCorr/2))
        #minutes
        eqOfTime = 4*math.degrees(varY*math.sin(2*math.radians(geomMeanLongSun)) \
            - 2*eccentOrbit*math.sin(math.radians(geomMeanAnomSun)) \
            + 4*eccentOrbit*varY*math.sin(math.radians(geomMeanAnomSun))*math.cos(2*math.radians(geomMeanLongSun)) \
            - 0.5*(varY**2)*math.sin(4*math.radians(geomMeanLongSun)) \
            - 1.25*(eccentOrbit**2)*math.sin(2*math.radians(geomMeanAnomSun)))
        #hours
        self.sun.time = ((self.time*60 + eqOfTime + 4*self.longitude - 60*self.timeZone) % 1440)/60
        #degrees
        hourAngle = (self.sun.time*15 + 180) if (self.sun.time*15 < 0) else (self.sun.time*15 - 180)
        #RADIANS
        self.sun.zenith = math.acos(math.sin(math.radians(self.latitude))*math.sin(self.sun.declination) \
            + math.cos(math.radians(self.latitude))*math.cos(self.sun.declination)*math.cos(math.radians(hourAngle)))
        #degrees
        atmosphRefrac = 0 if (self.sun.zenith < 0.087) else \
            (58.1/math.tan(math.pi/2 - self.sun.zenith) \
            - 0.07/(math.tan(math.pi/2 - self.sun.zenith))**3 \
            + 0.000086/(math.tan(math.pi/2 - self.sun.zenith))**5)/3600 \
            if (self.sun.zenith < 1.484) else \
                (1735 + (90-math.degrees(self.sun.zenith)) \
                *(-518.2 + (90-math.degrees(self.sun.zenith)) \
                *(103.4+(90-math.degrees(self.sun.zenith)) \
                *(-12.79+(90-math.degrees(self.sun.zenith))*0.711))))/3600 \
                if (self.sun.zenith < -1.581) else \
                    (-20.772/math.tan(math.pi/2 - self.sun.zenith))/3600
        #RADIANS
        self.sun.zenithCorr = self.sun.zenith - math.radians(atmosphRefrac)
        #RADIANS cw from N
        self.sun.azimuth = ((math.acos(((math.sin(math.radians(self.latitude))*math.cos(self.sun.zenith)) \
            - math.sin(self.sun.declination))/(math.cos(math.radians(self.latitude))*math.sin(self.sun.zenith))) + math.pi) % (2*math.pi)) \
            if (hourAngle > 0) else \
                ((3*math.pi - math.acos(((math.sin(math.radians(self.latitude))*math.cos(self.sun.zenith)) \
                - math.sin(self.sun.declination))/(math.cos(math.radians(self.latitude))*math.sin(self.sun.zenith)))) % (2*math.pi))
    
    def calcSkyColor(self, azimuth, zenith):
        gamma = self.gamma(zenith, azimuth)
        zenith = min(zenith, math.pi)
        Yp = self.Yz * self.perez(zenith, gamma, self.coeffsY) / self.perez(0, self.sun.zenith, self.coeffsY)
        xp = self.xz * self.perez(zenith, gamma, self.coeffsx) / self.perez(0, self.sun.zenith, self.coeffsx)
        yp = self.yz * self.perez(zenith, gamma, self.coeffsy) / self.perez(0, self.sun.zenith, self.coeffsy)
        
        return Vector([Yp, xp, yp])
    
    def calcLightColor(self):
        nightColor = Vector([0.2, 0.2, 0.5])
        
        if (self.sun.zenith > math.pi/2):
            return self.YxyToRGB(nightColor)
        
        Ys = self.Yz * self.perez(self.sun.zenith, 0, self.coeffsY) / self.perez(0, self.sun.zenith, self.coeffsY)
        xs = self.xz * self.perez(self.sun.zenith, 0, self.coeffsx) / self.perez(0, self.sun.zenith, self.coeffsx)
        ys = self.yz * self.perez(self.sun.zenith, 0, self.coeffsy) / self.perez(0, self.sun.zenith, self.coeffsy)
        dayColor = self.YxyToRGB(Vector([Ys, xs, ys]))
        
        interpolation = max(0, min(1, (self.sun.zenith - math.pi/2 + 0.2) / 0.2))
        return interpolation * nightColor + (1 - interpolation) * dayColor
    
    def calcFullSky(self, res):
        import ghpythonlib.components as ghcomp
        self.fullSky = []
        self.fullSkyXYZ = []
        for j in range(4*res):
            az = j/(4*res) * 2*math.pi
            for i in range(res+1):
                zen = (res-i)/res * math.pi/2
                color = self.YxyToXYZ(self.calcSkyColor(az, zen))
                self.fullSkyXYZ.append(str(color.v[0]) + ", " + str(color.v[1]) + ", " + str(color.v[2]))
                self.fullSky.append(ghcomp.ColourXYZ(1, *color.v))
        
        return self.fullSky, self.fullSkyXYZ
    
    def calcSkyAvg(self, res):
        self.colorAvg = Vector([0, 0, 0])
        fac = 1/(4 * res**2)
        for j in range(4*res):
            az = j/(4*res) * 2*math.pi
            for i in range(res):
                zen = (res-i)/res * math.pi/2
                self.colorAvg = self.colorAvg + (self.calcSkyColor(az, zen) * fac)
        
        return self.colorAvg


class MeshPreparation(object):
    
    def joinMesh(self, meshList):
        joinedMesh = rc.Geometry.Mesh()
        for m in meshList: joinedMesh.Append(m)
        return joinedMesh
    
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
    def calRadRoseRes(self, tiltedRoseVectors, TregenzaPatchesNormalVectors, genCumSkyResult, testPoint = rc.Geometry.Point3d.Origin, bldgMesh = [], 
groundRef = 0):
        radResult = []; sunUpHours = 1
        for vec in tiltedRoseVectors:
            radiation = 0; groundRadiation = 0; patchNum = 0;
            for patchVec in TregenzaPatchesNormalVectors:
                vecAngle = rs.VectorAngle(patchVec, vec)
                
                if  vecAngle < 90:
                    check = 1
                    
                    if bldgMesh!=[]:
                        #calculate intersection
                        ray = rc.Geometry.Ray3d(testPoint, rc.Geometry.Vector3d(*patchVec)) # generate the ray
                        if rc.Geometry.Intersect.Intersection.MeshRay(bldgMesh, ray) >= 0.0: check = 0;
                    
                    if check == 1:
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
        # create an empty dictionary for each point
        intersectionMtx = {}
        for pp in range(len(testPts)): intersectionMtx[pp] = {}
            
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
                    
                    # let the user cancel the process
                    if gh.GH_Document.IsEscapeKeyDown(): assert False
                    
                    vecAngle = rc.Geometry.Vector3d.VectorAngle(patchVec, testVec[i]) # calculate the angle between the surface and sky patch
                    
                    intersectionMtx[i][patchNum] = {'isIntersect' : 0,
                                                    'vecAngle' : vecAngle}
                    
                    if vecAngle < (PI/2):
                        check = 1; # this is simply here becuse I can't trust the break!! Isn't it stupid?
                        ray = rc.Geometry.Ray3d(testPts[i], patchVec) # generate the ray
                        
                        if bldgMesh!=None:
                            #for bldg in bldgMesh: # bldgMesh is all joined as one mesh
                            if rc.Geometry.Intersect.Intersection.MeshRay(bldgMesh, ray) >= 0.0: check = 0;
                        
                        if check != 0 and contextMesh!=None: #and testPts[i].Z < contextHeight:
                            #for bldg in contextMesh:
                            if rc.Geometry.Intersect.Intersection.MeshRay(contextMesh,ray) >= 0.0: check = 0;
                        
                        if check != 0:
                            radiation[i] = radiation[i] + (cumSkyResult[patchNum] * math.cos(vecAngle))
                            intersectionMtx[i][patchNum] =  {'isIntersect' : 1, 'vecAngle' : vecAngle}
                            # print groundRadiation
                            groundRadiation[i] = 0 #groundRadiation[i] + cumSkyResult[patchNum] * math.cos(vecAngle) * (groundRef/100) * 0.5
                    patchNum += 1
                
                radResult[i] = (groundRadiation[i] + radiation[i]) #/sunUpHours
        
        except:
            #print 'Error in Radiation calculation...'
            print "The calculation is terminated by user!"
            assert False
        
        # calling the function
        try:
            if parallel:
                tasks.Parallel.ForEach(range(len(testPts)),srfRadCalculator)
            else:
                for i in range(len(testPts)):
                    srfRadCalculator(i)
        except:
            return None, None, None
            
        intersectionEndTime = time.time()
        print 'Radiation study time = ', ("%.3f" % (intersectionEndTime - intersectionStTime)), 'Seconds...'
        
        # total radiation
        totalRadiation = 0;
        for r in range(len(testPts)):
            totalRadiation = totalRadiation + (radResult[r] * meshSrfArea[r] * (conversionFac * conversionFac))
        
        return radResult, totalRadiation, intersectionMtx
    
    
    def parallel_sunlightHoursCalculator(self, testPts, testVec, meshSrfArea, bldgMesh, contextMesh, parallel, sunVectors, conversionFac, northVector, 
timeStep = 1):
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
        
        sunVisibility = []
        for pt in testPts: sunVisibility.append(range(len(sunV)))
        
        try:
            def sunlightHoursCalculator(i):
                for vectorCount, vector in enumerate(sunV):
                    
                    # let the user cancel the process
                    if gh.GH_Document.IsEscapeKeyDown(): assert False
                    
                    vecAngle = rc.Geometry.Vector3d.VectorAngle(vector, testVec[i]) # calculate the angle between the surface and sun vector
                    check = 0
                    if vecAngle < (PI/2):
                        check = 1; # this is simply here becuse I can't trust the break! Isn't it stupid?
                        ray = rc.Geometry.Ray3d(testPts[i], vector) # generate the ray
                        
                        if bldgMesh!=None:
                            if rc.Geometry.Intersect.Intersection.MeshRay(bldgMesh, ray) >= 0.0: check = 0
                        if check != 0 and contextMesh!=None:
                            if rc.Geometry.Intersect.Intersection.MeshRay(contextMesh,ray) >= 0.0: check = 0
                        
                        if check != 0:
                            sunlightHours[i] += 1/timeStep
                        
                    sunVisibility[i][vectorCount] = check
                
                sunlightHoursResult[i] = sunlightHours[i] # This is stupid but I'm tired to change it now...
        except:
            #print 'Error in Sunligh Hours calculation...'
            print "The calculation is terminated by user!"
            assert False
        
        # calling the function
        try:
            # calling the function
            if parallel:
                tasks.Parallel.ForEach(range(len(testPts)), sunlightHoursCalculator)
            else:
                for i in range(len(testPts)):
                    sunlightHoursCalculator(i)
        except:
            return None, None, None
            
        intersectionEndTime = time.time()
        print 'Sunlight hours calculation time = ', ("%.3f" % (intersectionEndTime - intersectionStTime)), 'Seconds...'
        
        # total sunlight hours
        totalSLH = 0;
        for r in range(len(testPts)):
            totalSLH = totalSLH + (sunlightHoursResult[r] * meshSrfArea[r] * (conversionFac * conversionFac))
        
        
        return sunlightHoursResult, totalSLH, sunVisibility
    
    
    def parallel_viewCalculator(self, testPts, testVec, meshSrfArea, bldgMesh, contextMesh, parallel, viewPoints, viewPtsWeights, conversionFac):
        
        # preparing bulk lists
        view = [0] * len(testPts)
        viewResult = [0] * len(testPts)
        intersectionStTime = time.time()
        YAxis = rc.Geometry.Vector3d.YAxis
        ZAxis = rc.Geometry.Vector3d.ZAxis
        PI = math.pi
        
        targetViewsCount  = len(viewPoints)
        ptImportance = []
        for ptCount in range(targetViewsCount):
            try:
                
                if viewPtsWeights[ptCount] == 0:
                    ptImportance.append(100/targetViewsCount)
                else:
                    ptImportance.append(viewPtsWeights[ptCount]*100)
            except:
                ptImportance.append(100/targetViewsCount)
        
        
        viewVector = []
        
        ptVisibility = []
        for pt in testPts: ptVisibility.append(range(len(viewPoints)))
        
        try:
            def viewCalculator(i):
                for ptCount, viewPt in enumerate(viewPoints):
                    
                    # let the user cancel the process
                    if gh.GH_Document.IsEscapeKeyDown(): assert False
                    
                    vector = rc.Geometry.Vector3d(viewPt - testPts[i])
                    vecAngle = rc.Geometry.Vector3d.VectorAngle(vector, testVec[i]) # calculate the angle between the surface and sun vector
                    check = 0
                    if vecAngle < (PI/2):
                        check = 1; # this is simply here becuse I can't trust the break! Isn't it stupid?
                        line = rc.Geometry.Line(testPts[i], viewPt)
                        
                        if bldgMesh!=None:
                            if rc.Geometry.Intersect.Intersection.MeshLine(bldgMesh, line)[1] != None: check = 0
                        if check != 0 and contextMesh!=None:
                            if rc.Geometry.Intersect.Intersection.MeshLine(contextMesh, line)[1] != None: check = 0
                        
                        if check != 0:
                            view[i] += ptImportance[ptCount]
                        
                    ptVisibility[i][ptCount] = check
                viewResult[i] = view[i] # This is stupid but I'm tired to change it now...
                
                if viewResult[i] > 100: viewResult[i] = 100
        except Exception, e:
            # print `e`
            # print 'Error in View calculation...'
            print "The calculation is terminated by user!"
            assert False
        
        # calling the function
        try:
            # calling the function
            if parallel:
                tasks.Parallel.ForEach(range(len(testPts)), viewCalculator)
            else:
                for i in range(len(testPts)):
                    viewCalculator(i)
        except:
            return None, None, None
            
        intersectionEndTime = time.time()
        print 'View calculation time = ', ("%.3f" % (intersectionEndTime - intersectionStTime)), 'Seconds...'
        
        # average view
        averageView = sum(viewResult)/len(viewResult)
            
        return viewResult, averageView, ptVisibility
        

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
            startDay = self.hour2Date(self.date2Hour(stMonth, stDay, stHour))
            startHour = startDay.split(' ')[-1]
            startDate = startDay.Replace(startHour, "")[:-1]
            
            endingDay = self.hour2Date(self.date2Hour(endMonth, endDay, endHour))
            endingHour = endingDay.split(' ')[-1]
            endingDate = endingDay.Replace(endingHour, "")[:-1]
            
            if full:
                print 'Analysis period is from', startDate, 'to', endingDate
                print 'Between hours ' + startHour + ' and ' + endingHour
            
            else: print startDay, ' - ', endingDay
             
        return stMonth, stDay, stHour, endMonth, endDay, endHour
    
    
    def colorMesh(self, colors, meshList, unweld = True):
        
        joinedMesh = rc.Geometry.Mesh()
        try:
            for face in range(meshList[0].Faces.Count):
                joinedMesh.Append(meshList[0].Faces[face]) #join the mesh
        except:
            try:
                for face in meshList: joinedMesh.Append(face)
            except:
                joinedMesh.Append(meshList)
        
        if unweld: joinedMesh.Unweld(0, False)
        
        
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
    
    def createLegend(self, results, lowB, highB, numOfSeg, legendTitle, BoundingBoxP, legendBasePoint, legendScale = 1, font = None, textSize = None):
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
        try:
            numbers = rs.frange(lowB, highB, round((highB - lowB) / (numOfSeg -1), 6))
        except:
            if highB - lowB < 10**(-12):
                numbers = [lowB]; numOfSeg = 1
            else:
                numbers = [lowB, lowB + ((highB-lowB)/4), lowB + ((highB-lowB)/2), lowB + (3*(highB-lowB)/4), highB]; numOfSeg = 5
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
        
        # check for user input
        if font == None:
            font = 'Verdana'
        if  textSize == None:
            textSize = (legendHeight/3) * legendScale
        
        numbersCrv = self.text2srf(numbersStr, textPt, font, textSize)
        
        return legendSrf, numbers, numbersCrv, textPt, textSize
    
    def openLegend(self, legendRes):
        if len(legendRes)!=0:
            meshAndCrv = []
            meshAndCrv.append(legendRes[0])
            [meshAndCrv.append(c) for c in legendRes[1]]
            return meshAndCrv
        else: return -1
    
    def text2crv(self, text, textPt, font = 'Verdana', textHeight = 20, justIndex = 0):
        # Thanks to Giulio Piacentino for his version of text to curve
        
        # justIndex (justification and alignment indexes):
        # 0 - bottom left(default)
        # 2 - bottom center
        # 4 - bottom right
        # 131072 - middle left
        # 262144 - top left
        # 131074 - center
        # 131076 - middle right
        # 262146 - top middle
        # 262148 - top right
        
        textCrvs = []
        just = System.Enum.ToObject(Rhino.Geometry.TextJustification, justIndex)
        for n in range(len(text)):
            plane = rc.Geometry.Plane(textPt[n], rc.Geometry.Vector3d(0,0,1))
            if type(text[n]) is not str:
                preText = rc.RhinoDoc.ActiveDoc.Objects.AddText(`text[n]`, plane, textHeight, font, True, False, just)
            else:
                preText = rc.RhinoDoc.ActiveDoc.Objects.AddText( text[n], plane, textHeight, font, True, False, just)
                
            postText = rc.RhinoDoc.ActiveDoc.Objects.Find(preText)
            TG = postText.Geometry
            crv = TG.Explode()
            textCrvs.append(crv)
            rc.RhinoDoc.ActiveDoc.Objects.Delete(postText, True) # find and delete the text
        return textCrvs
    
    def text2srf(self, text, textPt, font = 'Verdana', textHeight = 20):
        # Thanks to Giulio Piacentino for his version of text to curve
        textSrfs = []
        for n in range(len(text)):
            plane = rc.Geometry.Plane(textPt[n], rc.Geometry.Vector3d(0,0,1))
            if type(text[n]) is not str:
                preText = rc.RhinoDoc.ActiveDoc.Objects.AddText(`text[n]`, plane, textHeight, font, True, False)
            else:
                preText = rc.RhinoDoc.ActiveDoc.Objects.AddText( text[n], plane, textHeight, font, True, False)
                
            postText = rc.RhinoDoc.ActiveDoc.Objects.Find(preText)
            TG = postText.Geometry
            crvs = TG.Explode()
            
            # join the curves
            joindCrvs = rc.Geometry.Curve.JoinCurves(crvs)
            
            # create the surface
            srfs = rc.Geometry.Brep.CreatePlanarBreps(joindCrvs)
            
            
            extraSrfCount = 0
            # = generate 2 surfaces
            if "=" in text[n]: extraSrfCount += -1
            if ":" in text[n]: extraSrfCount += -1
            
            if len(text[n].strip()) != len(srfs) + extraSrfCount:
                # project the curves to the place in case number of surfaces
                # doesn't match the text
                projectedCrvs = []
                for crv in joindCrvs:
                    projectedCrvs.append(rc.Geometry.Curve.ProjectToPlane(crv, plane))
                srfs = rc.Geometry.Brep.CreatePlanarBreps(projectedCrvs)
            
            textSrfs.append(srfs)
            
            #if len(text[n].strip()) == len(srfs)+ extraSrfCount:
            #    textSrfs.append(srfs)
            #else:
            #print len(text[n])
            #print len(text[n].strip())
            #print len(srfs)+ extraSrfCount
            #print extraSrfCount
            #textSrfs.append(projectedCrvs)
                
            rc.RhinoDoc.ActiveDoc.Objects.Delete(postText, True) # find and delete the text
            
        return textSrfs
    
    def createTitle(self, listInfo, boundingBoxPar, legendScale = 1, Heading = None, shortVersion = False, font = None, fontSize = None):
        #Define a function to create surfaces from input curves.
        
        if Heading==None: Heading = listInfo[0][2] + ' (' + listInfo[0][3] + ')' + ' - ' + listInfo[0][4]
        
        stMonth, stDay, stHour, endMonth, endDay, endHour = self.readRunPeriod((listInfo[0][5], listInfo[0][6]), False)
        
        period = `stDay`+ ' ' + self.monthList[stMonth-1] + ' ' + `stHour` + ':00' + \
                 " - " + `endDay`+ ' ' + self.monthList[endMonth-1] + ' ' + `endHour` + ':00'
        
        if shortVersion: titleStr = '\n' + Heading
        else: titleStr = '\n' + Heading + '\n' + listInfo[0][1] + '\n' + period
        
        if font == None: font = 'Veranda'
        
        if fontSize == None: fontSize = (boundingBoxPar[2]/30) * legendScale
        
        titlebasePt = boundingBoxPar[-2]
        
        titleTextSrf = self.text2srf([titleStr], [titlebasePt], font, fontSize)
        
        return titleTextSrf, titleStr, titlebasePt

    def compassCircle(self, cenPt = rc.Geometry.Point3d.Origin, northVector = rc.Geometry.Vector3d.YAxis, radius = 200, angles = range(0,360,30), xMove = 
                        10, centerLine = False):
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
                for crv in crvs:
                    try:
                        rc.RhinoDoc.ActiveDoc.Objects.AddCurve(crv, attr)
                    except:
                        # This is for breps surfaces as I changed curves to surfaces now
                        rc.RhinoDoc.ActiveDoc.Objects.AddBrep(crv, attr)
            for text in range(len(legendText)):
                plane = rc.Geometry.Plane(textPt[text], rc.Geometry.Vector3d(0,0,1))
                if type(legendText[text]) is not str: legendText[text] = ("%.2f" % legendText[text])
                rc.RhinoDoc.ActiveDoc.Objects.AddText(legendText[text], plane, textSize, fontName, True, False, attr)
                # end of the script


class ComfortModels(object):
    
    def comfPMVElevatedAirspeed(self, ta, tr, vel, rh, met, clo, wme):
        #This function accepts any input conditions (including low air speeds) but will return accurate values if the airspeed is above (>0.15m/s).
        #The function will return the following:
        #pmv : Predicted mean vote
        #ppd : Percent predicted dissatisfied [%]
        #ta_adj: Air temperature adjusted for air speed [C]
        #cooling_effect : The difference between the air temperature and adjusted air temperature [C]
        #set: The Standard Effective Temperature [C] (see below)
        
        r = []
        set = self.comfPierceSET(ta, tr, vel, rh, met , clo, wme)
        
        #This function is taken from the util.js script of the CBE comfort tool page and has been modified to include the fn inside the utilSecant function 
        def utilSecant(a, b, epsilon):
            # root-finding only
            res = []
            def fn(t):
                return (set - self.comfPierceSET(t, tr, 0.15, rh, met, clo, wme));
            f1 = fn(a)
            f2 = fn(b)
            if abs(f1) <= epsilon:
                res.append(a)
            elif abs(f2) <= epsilon:
                res.append(b)
            else:
                count = range(100)
                for i in count:
                    if (b - a) != 0 and (f2 - f1) != 0:
                        slope = (f2 - f1) / (b - a)
                        c = b - f2/slope
                        f3 = fn(c)
                        if abs(f3) < epsilon:
                            res.append(c)
                        a = b
                        b = c
                        f1 = f2
                        f2 = f3
                    else: pass
            res.append('NaN')
            return res[0]
        
        #This function is taken from the util.js script of the CBE comfort tool page and has been modified to include the fn inside the utilSecant function definition.
        def utilBisect(a, b, epsilon, target):
            def fn(t):
                return (set - self.comfPierceSET(t, tr, 0.15, rh, met, clo, wme))
            while abs(b - a) > (2 * epsilon):
                midpoint = (b + a) / 2
                a_T = fn(a)
                b_T = fn(b)
                midpoint_T = fn(midpoint)
                if (a_T - target) * (midpoint_T - target) < 0:
                    b = midpoint
                elif (b_T - target) * (midpoint_T - target) < 0:
                    a = midpoint
                else: return -999
            return midpoint
        
        
        if vel <= 0.15:
            pmv, ppd = self.comfPMV(ta, tr, vel, rh, met, clo, wme)
            ta_adj = ta
            ce = 0
        else:
            ta_adj_l = -200
            ta_adj_r = 200
            eps = 0.001  # precision of ta_adj
            
            ta_adj = utilSecant(ta_adj_l, ta_adj_r, eps)
            if ta_adj == 'NaN':
                ta_adj = utilBisect(ta_adj_l, ta_adj_r, eps, 0)
            
            pmv, ppd = self.comfPMV(ta_adj, tr, 0.15, rh, met, clo, wme)
            ce = abs(ta - ta_adj)
        
        r.append(pmv)
        r.append(ppd)
        r.append(set)
        r.append(ta_adj)
        r.append(ce)
        
        return r
    
    
    def comfPMV(self, ta, tr, vel, rh, met, clo, wme):
        #returns [pmv, ppd]
        #ta, air temperature (C)
        #tr, mean radiant temperature (C)
        #vel, relative air velocity (m/s)
        #rh, relative humidity (%) Used only this way to input humidity level
        #met, metabolic rate (met)
        #clo, clothing (clo)
        #wme, external work, normally around 0 (met)
        
        pa = rh * 10 * math.exp(16.6536 - 4030.183 / (ta + 235))
        
        icl = 0.155 * clo #thermal insulation of the clothing in M2K/W
        m = met * 58.15 #metabolic rate in W/M2
        w = wme * 58.15 #external work in W/M2
        mw = m - w #internal heat production in the human body
        if (icl <= 0.078):
            fcl = 1 + (1.29 * icl)
        else:
            fcl = 1.05 + (0.645 * icl)
        
        #heat transf. coeff. by forced convection
        hcf = 12.1 * math.sqrt(vel)
        taa = ta + 273
        tra = tr + 273
        tcla = taa + (35.5 - ta) / (3.5 * icl + 0.1)
    
        p1 = icl * fcl
        p2 = p1 * 3.96
        p3 = p1 * 100
        p4 = p1 * taa
        p5 = (308.7 - 0.028 * mw) + (p2 * math.pow(tra / 100, 4))
        xn = tcla / 100
        xf = tcla / 50
        eps = 0.00015
        
        n = 0
        while abs(xn - xf) > eps:
            xf = (xf + xn) / 2
            hcn = 2.38 * math.pow(abs(100.0 * xf - taa), 0.25)
            if (hcf > hcn):
                hc = hcf
            else:
                hc = hcn
            xn = (p5 + p4 * hc - p2 * math.pow(xf, 4)) / (100 + p3 * hc)
            n += 1
            if (n > 150):
                print 'Max iterations exceeded'
                return 1
            
        
        tcl = 100 * xn - 273
        
        #heat loss diff. through skin 
        hl1 = 3.05 * 0.001 * (5733 - (6.99 * mw) - pa)
        #heat loss by sweating
        if mw > 58.15:
            hl2 = 0.42 * (mw - 58.15)
        else:
            hl2 = 0
        #latent respiration heat loss 
        hl3 = 1.7 * 0.00001 * m * (5867 - pa)
        #dry respiration heat loss
        hl4 = 0.0014 * m * (34 - ta)
        #heat loss by radiation  
        hl5 = 3.96 * fcl * (math.pow(xn, 4) - math.pow(tra / 100, 4))
        #heat loss by convection
        hl6 = fcl * hc * (tcl - ta)
        
        ts = 0.303 * math.exp(-0.036 * m) + 0.028
        pmv = ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6)
        ppd = 100.0 - 95.0 * math.exp(-0.03353 * pow(pmv, 4.0) - 0.2179 * pow(pmv, 2.0))
        
        r = []
        r.append(pmv)
        r.append(ppd)
        
        return r
    
    
    def comfPierceSET(self, ta, tr, vel, rh, met, clo, wme):
        #Function to find the saturation vapor pressure, used frequently throughtout the comfPierceSET function.
        def findSaturatedVaporPressureTorr(T):
            #calculates Saturated Vapor Pressure (Torr) at Temperature T  (C)
            return math.exp(18.6686 - 4030.183 / (T + 235.0))
        
        #Key initial variables.
        VaporPressure = (rh * findSaturatedVaporPressureTorr(ta)) / 100
        AirVelocity = max(vel, 0.1)
        KCLO = 0.25
        BODYWEIGHT = 69.9
        BODYSURFACEAREA = 1.8258
        METFACTOR = 58.2
        SBC = 0.000000056697 # Stefan-Boltzmann constant (W/m2K4)
        CSW = 170
        CDIL = 120
        CSTR = 0.5
        
        TempSkinNeutral = 33.7 #setpoint (neutral) value for Tsk
        TempCoreNeutral = 36.49 #setpoint value for Tcr
        TempBodyNeutral = 36.49 #setpoint for Tb (.1*TempSkinNeutral + .9*TempCoreNeutral)
        SkinBloodFlowNeutral = 6.3 #neutral value for SkinBloodFlow
    
        #INITIAL VALUES - start of 1st experiment
        TempSkin = TempSkinNeutral
        TempCore = TempCoreNeutral
        SkinBloodFlow = SkinBloodFlowNeutral
        MSHIV = 0.0
        ALFA = 0.1
        ESK = 0.1 * met
        
        #Start new experiment here (for graded experiments)
        #UNIT CONVERSIONS (from input variables)
        
        p = 101325.0 / 1000 # This variable is the pressure of the atmosphere in kPa and was taken from the psychrometrics.js file of the CBE comfort tool.
        
        PressureInAtmospheres = p * 0.009869
        LTIME = 60
        TIMEH = LTIME / 60.0
        RCL = 0.155 * clo
        #AdjustICL(RCL, Conditions);  TH: I don't think this is used in the software
        
        FACL = 1.0 + 0.15 * clo #% INCREASE IN BODY SURFACE AREA DUE TO CLOTHING
        LR = 2.2 / PressureInAtmospheres #Lewis Relation is 2.2 at sea level
        RM = met * METFACTOR
        M = met * METFACTOR
        
        if clo <= 0:
            WCRIT = 0.38 * pow(AirVelocity, -0.29)
            ICL = 1.0
        else:
            WCRIT = 0.59 * pow(AirVelocity, -0.08)
            ICL = 0.45
        
        CHC = 3.0 * pow(PressureInAtmospheres, 0.53)
        CHCV = 8.600001 * pow((AirVelocity * PressureInAtmospheres), 0.53)
        CHC = max(CHC, CHCV)
        
        #initial estimate of Tcl
        CHR = 4.7
        CTC = CHR + CHC
        RA = 1.0 / (FACL * CTC) #resistance of air layer to dry heat transfer
        TOP = (CHR * tr + CHC * ta) / CTC
        TCL = TOP + (TempSkin - TOP) / (CTC * (RA + RCL))
    
        # ========================  BEGIN ITERATION
        #
        # Tcl and CHR are solved iteratively using: H(Tsk - To) = CTC(Tcl - To),
        # where H = 1/(Ra + Rcl) and Ra = 1/Facl*CTC
        
        TCL_OLD = TCL
        TIME = range(LTIME)
        flag = True
        for TIM in TIME:
            if flag == True:
                while abs(TCL - TCL_OLD) > 0.01:
                    TCL_OLD = TCL
                    CHR = 4.0 * SBC * pow(((TCL + tr) / 2.0 + 273.15), 3.0) * 0.72
                    CTC = CHR + CHC
                    RA = 1.0 / (FACL * CTC) #resistance of air layer to dry heat transfer
                    TOP = (CHR * tr + CHC * ta) / CTC
                    TCL = (RA * TempSkin + RCL * TOP) / (RA + RCL)
            flag = False
            DRY = (TempSkin - TOP) / (RA + RCL)
            HFCS = (TempCore - TempSkin) * (5.28 + 1.163 * SkinBloodFlow)
            ERES = 0.0023 * M * (44.0 - VaporPressure)
            CRES = 0.0014 * M * (34.0 - ta)
            SCR = M - HFCS - ERES - CRES - wme
            SSK = HFCS - DRY - ESK
            TCSK = 0.97 * ALFA * BODYWEIGHT
            TCCR = 0.97 * (1 - ALFA) * BODYWEIGHT
            DTSK = (SSK * BODYSURFACEAREA) / (TCSK * 60.0)# //deg C per minute
            DTCR = SCR * BODYSURFACEAREA / (TCCR * 60.0)# //deg C per minute
            TempSkin = TempSkin + DTSK
            TempCore = TempCore + DTCR
            TB = ALFA * TempSkin + (1 - ALFA) * TempCore
            SKSIG = TempSkin - TempSkinNeutral
            WARMS = (SKSIG > 0) * SKSIG
            COLDS = ((-1.0 * SKSIG) > 0) * (-1.0 * SKSIG)
            CRSIG = (TempCore - TempCoreNeutral)
            WARMC = (CRSIG > 0) * CRSIG
            COLDC = ((-1.0 * CRSIG) > 0) * (-1.0 * CRSIG)
            BDSIG = TB - TempBodyNeutral
            WARMB = (BDSIG > 0) * BDSIG
            COLDB = ((-1.0 * BDSIG) > 0) * (-1.0 * BDSIG)
            SkinBloodFlow = (SkinBloodFlowNeutral + CDIL * WARMC) / (1 + CSTR * COLDS)
            if SkinBloodFlow > 90.0: SkinBloodFlow = 90.0
            if SkinBloodFlow < 0.5: SkinBloodFlow = 0.5
            REGSW = CSW * WARMB * math.exp(WARMS / 10.7)
            if REGSW > 500.0: REGSW = 500.0
            ERSW = 0.68 * REGSW
            REA = 1.0 / (LR * FACL * CHC) #evaporative resistance of air layer
            RECL = RCL / (LR * ICL) #evaporative resistance of clothing (icl=.45)
            EMAX = (findSaturatedVaporPressureTorr(TempSkin) - VaporPressure) / (REA + RECL)
            PRSW = ERSW / EMAX
            PWET = 0.06 + 0.94 * PRSW
            EDIF = PWET * EMAX - ERSW
            ESK = ERSW + EDIF
            if PWET > WCRIT:
                PWET = WCRIT
                PRSW = WCRIT / 0.94
                ERSW = PRSW * EMAX
                EDIF = 0.06 * (1.0 - PRSW) * EMAX
                ESK = ERSW + EDIF
            if EMAX < 0:
                EDIF = 0
                ERSW = 0
                PWET = WCRIT
                PRSW = WCRIT
                ESK = EMAX
            ESK = ERSW + EDIF
            MSHIV = 19.4 * COLDS * COLDC
            M = RM + MSHIV
            ALFA = 0.0417737 + 0.7451833 / (SkinBloodFlow + .585417)
        
        
        #Define new heat flow terms, coeffs, and abbreviations
        STORE = M - wme - CRES - ERES - DRY - ESK #rate of body heat storage
        HSK = DRY + ESK #total heat loss from skin
        RN = M - wme #net metabolic heat production
        ECOMF = 0.42 * (RN - (1 * METFACTOR))
        if ECOMF < 0.0: ECOMF = 0.0 #from Fanger
        EREQ = RN - ERES - CRES - DRY
        EMAX = EMAX * WCRIT
        HD = 1.0 / (RA + RCL)
        HE = 1.0 / (REA + RECL)
        W = PWET
        PSSK = findSaturatedVaporPressureTorr(TempSkin)
        #Definition of ASHRAE standard environment... denoted "S"
        CHRS = CHR
        if met < 0.85:
            CHCS = 3.0
        else:
            CHCS = 5.66 * pow((met - 0.85), 0.39)
            if CHCS < 3.0: CHCS = 3.0
        
        CTCS = CHCS + CHRS
        RCLOS = 1.52 / ((met - wme / METFACTOR) + 0.6944) - 0.1835
        RCLS = 0.155 * RCLOS
        FACLS = 1.0 + KCLO * RCLOS
        FCLS = 1.0 / (1.0 + 0.155 * FACLS * CTCS * RCLOS)
        IMS = 0.45
        ICLS = IMS * CHCS / CTCS * (1 - FCLS) / (CHCS / CTCS - FCLS * IMS)
        RAS = 1.0 / (FACLS * CTCS)
        REAS = 1.0 / (LR * FACLS * CHCS)
        RECLS = RCLS / (LR * ICLS)
        HD_S = 1.0 / (RAS + RCLS)
        HE_S = 1.0 / (REAS + RECLS)
        
        #SET* (standardized humidity, clo, Pb, and CHC)
        #determined using Newton's iterative solution
        #FNERRS is defined in the GENERAL SETUP section above
        
        DELTA = .0001
        dx = 100.0
        X_OLD = TempSkin - HSK / HD_S #lower bound for SET
        while abs(dx) > .01:
            ERR1 = (HSK - HD_S * (TempSkin - X_OLD) - W * HE_S * (PSSK - 0.5 * findSaturatedVaporPressureTorr(X_OLD)))
            ERR2 = (HSK - HD_S * (TempSkin - (X_OLD + DELTA)) - W * HE_S * (PSSK - 0.5 * findSaturatedVaporPressureTorr((X_OLD + DELTA))))
            X = X_OLD - DELTA * ERR1 / (ERR2 - ERR1)
            dx = X - X_OLD
            X_OLD = X
        
        return X
    
    
    def calcBalTemp(self, initialGuess, windSpeed, relHumid, metRate, cloLevel, exWork):
        balTemper = initialGuess
        delta = 3
        while abs(delta) > 0.01:
            delta, ppd, set, taAdj, coolingEffect = self.comfPMVElevatedAirspeed(balTemper, balTemper, windSpeed, relHumid, metRate, cloLevel, exWork)
            balTemper = balTemper - delta
        return balTemper
    
    
    def calcComfRange(self, initialGuessUp, initialGuessDown, radTemp, windSpeed, relHumid, metRate, cloLevel, exWork, eightyPercent):
        upTemper = initialGuessUp
        upDelta = 3
        while abs(upDelta) > 0.01:
            pmv, ppd, set, taAdj, coolingEffect = self.comfPMVElevatedAirspeed(upTemper, radTemp, windSpeed, relHumid, metRate, cloLevel, exWork)
            if eightyPercent == True:
                upDelta = 1 - pmv
                upTemper = upTemper + upDelta
            else:
                upDelta = 0.5 - pmv
                upTemper = upTemper + upDelta
        
        if initialGuessDown == None:
            downTemper = upTemper - 6
        else: downTemper = initialGuessDown
        downDelta = 3
        while abs(downDelta) > 0.01:
            pmv, ppd, set, taAdj, coolingEffect = self.comfPMVElevatedAirspeed(downTemper, radTemp, windSpeed, relHumid, metRate, cloLevel, exWork)
            if eightyPercent == True:
                downDelta = -1 - pmv
                downTemper = downTemper + downDelta
            else:
                downDelta = -0.5 - pmv
                downTemper = downTemper + downDelta
        
        return upTemper, downTemper
    
    
    def comfAdaptiveComfortASH55(self, ta, tr, runningMean, vel, eightyOrNinety):
        r = []
        # Define the variables that will be used throughout the calculation.
        coolingEffect = 0
        if eightyOrNinety == True: offset = 3.5
        else: offset = 2.5
        to = (ta + tr) / 2
        # See if the running mean temperature is between 10 C and 33.5 C and, if not, label the data as too extreme for the adaptive method.
        if runningMean > 10.0 and runningMean < 33.5:
            # Define a function to tell if values are in the comfort range.
            def comfBetween (x, l, r):
                return (x > l and x < r)
            
            if (vel > 0.45 and to >= 25):
                # calculate cooling effect of elevated air speed
                # when top > 25 degC.
                if vel > 0.45 and vel < 0.75:
                    coolingEffect = 1.2
                elif vel > 0.75 and vel < 1.05:
                    coolingEffect = 1.8
                elif vel > 1.05:
                    coolingEffect = 2.2
                else: pass
            
            tComf = 0.31 * runningMean + 17.8
            tComfLower = tComf - offset
            tComfUpper = tComf + offset + coolingEffect
            r.append(tComf)
            r.append(to - tComf)
            r.append(tComfLower)
            r.append(tComfUpper)
            
            # See if the conditions are comfortable.
            if to > tComfLower and to < tComfUpper:
                # compliance
                acceptability = True
            else:
                # nonCompliance
                acceptability = False
            r.append(acceptability)
            
            # Append a number to the result list to show whether the values are too hot, too cold, or comfortable.
            if acceptability == True: r.append(1)
            elif to > tComfUpper: r.append(2)
            else: r.append(0)
            
        elif runningMean < 10.0:
            # The prevailing temperature is too cold for the adaptive method.
            tComf = 0.31 * 10 + 17.8
            tempDiff = to - tComf
            tComfLower = tComf - offset
            tComfUpper = tComf + offset
            if to > tComfLower and to < tComfUpper: acceptability = True
            else: acceptability = False
            outputs = [tComf, tempDiff, tComfLower, tComfUpper, acceptability, -1]
            r.extend(outputs)
        else:
            # The prevailing temperature is too hot for the adaptive method.
            tComf = 0.31 * 33.5 + 17.8
            tempDiff = to - tComf
            tComfLower = tComf - offset
            tComfUpper = tComf + offset
            if to > tComfLower and to < tComfUpper: acceptability = True
            else: acceptability = False
            outputs = [tComf, tempDiff, tComfLower, tComfUpper, acceptability, -1]
            r.extend(outputs)
        
        return r
    
    
    def comfUTCI(self, Ta, Tmrt, va, RH):
        # Define a function to change the RH to water saturation vapor pressure in hPa
        def es(ta):
            g = [-2836.5744, -6028.076559, 19.54263612, -0.02737830188, 0.000016261698, (7.0229056*(10**(-10))), (-1.8680009*(10**(-13)))]      
            tk = ta + 273.15 # air temp in K
            es = 2.7150305 * math.log(tk)
            for count, i in enumerate(g):
                es = es + (i * (tk**(count-2)))
            es = math.exp(es)*0.01	# convert Pa to hPa
            return es
        
        #Do a series of checks to be sure that the input values are within the bounds accepted by the model.
        check = True
        if Ta < -50.0 or Ta > 50.0: check = False
        else: pass
        if Tmrt-Ta < -30.0 or Tmrt-Ta > 70.0: check = False
        else: pass
        if va < 0.5: va = 0.5
        elif va > 17: va = 17
        else: pass
        
        #If everything is good, run the data through the model below to get the UTCI.
        #This is a python version of the UTCI_approx function, Version a 0.002, October 2009
        #Ta: air temperature, degree Celsius
        #ehPa: water vapour presure, hPa=hecto Pascal
        #Tmrt: mean radiant temperature, degree Celsius
        #va10m: wind speed 10 m above ground level in m/s
        
        if check == True:
            ehPa = es(Ta) * (RH/100.0)
            D_Tmrt = Tmrt - Ta
            Pa = ehPa/10.0  # convert vapour pressure to kPa
            
            
            UTCI_approx = Ta + \
            (0.607562052) + \
            (-0.0227712343) * Ta + \
            (8.06470249*(10**(-4))) * Ta * Ta + \
            (-1.54271372*(10**(-4))) * Ta * Ta * Ta + \
            (-3.24651735*(10**(-6))) * Ta * Ta * Ta * Ta + \
            (7.32602852*(10**(-8))) * Ta * Ta * Ta * Ta * Ta + \
            (1.35959073*(10**(-9))) * Ta * Ta * Ta * Ta * Ta * Ta + \
            (-2.25836520) * va + \
            (0.0880326035) * Ta * va + \
            (0.00216844454) * Ta * Ta * va + \
            (-1.53347087*(10**(-5))) * Ta * Ta * Ta * va + \
            (-5.72983704*(10**(-7))) * Ta * Ta * Ta * Ta * va + \
            (-2.55090145*(10**(-9))) * Ta * Ta * Ta * Ta * Ta * va + \
            (-0.751269505) * va * va + \
            (-0.00408350271) * Ta * va * va + \
            (-5.21670675*(10**(-5))) * Ta * Ta * va * va + \
            (1.94544667*(10**(-6))) * Ta * Ta * Ta * va * va + \
            (1.14099531*(10**(-8))) * Ta * Ta * Ta * Ta * va * va + \
            (0.158137256) * va * va * va + \
            (-6.57263143*(10**(-5))) * Ta * va * va * va + \
            (2.22697524*(10**(-7))) * Ta * Ta * va * va * va + \
            (-4.16117031*(10**(-8))) * Ta * Ta * Ta * va * va * va + \
            (-0.0127762753) * va * va * va * va + \
            (9.66891875*(10**(-6))) * Ta * va * va * va * va + \
            (2.52785852*(10**(-9))) * Ta * Ta * va * va * va * va + \
            (4.56306672*(10**(-4))) * va * va * va * va * va + \
            (-1.74202546*(10**(-7))) * Ta * va * va * va * va * va + \
            (-5.91491269*(10**(-6))) * va * va * va * va * va * va + \
            (0.398374029) * D_Tmrt + \
            (1.83945314*(10**(-4))) * Ta * D_Tmrt + \
            (-1.73754510*(10**(-4))) * Ta * Ta * D_Tmrt + \
            (-7.60781159*(10**(-7))) * Ta * Ta * Ta * D_Tmrt + \
            (3.77830287*(10**(-8))) * Ta * Ta * Ta * Ta * D_Tmrt + \
            (5.43079673*(10**(-10))) * Ta * Ta * Ta * Ta * Ta * D_Tmrt + \
            (-0.0200518269) * va * D_Tmrt + \
            (8.92859837*(10**(-4))) * Ta * va * D_Tmrt + \
            (3.45433048*(10**(-6))) * Ta * Ta * va * D_Tmrt + \
            (-3.77925774*(10**(-7))) * Ta * Ta * Ta * va * D_Tmrt + \
            (-1.69699377*(10**(-9))) * Ta * Ta * Ta * Ta * va * D_Tmrt + \
            (1.69992415*(10**(-4))) * va*va*D_Tmrt + \
            ( -4.99204314*(10**(-5)) ) * Ta*va*va*D_Tmrt + \
            ( 2.47417178*(10**(-7)) ) * Ta*Ta*va*va*D_Tmrt + \
            ( 1.07596466*(10**(-8)) ) * Ta*Ta*Ta*va*va*D_Tmrt + \
            ( 8.49242932*(10**(-5)) ) * va*va*va*D_Tmrt + \
            ( 1.35191328*(10**(-6)) ) * Ta*va*va*va*D_Tmrt + \
            ( -6.21531254*(10**(-9)) ) * Ta*Ta*va*va*va*D_Tmrt + \
            ( -4.99410301*(10**(-6)) ) * va*va*va*va*D_Tmrt + \
            ( -1.89489258*(10**(-8)) ) * Ta*va*va*va*va*D_Tmrt + \
            ( 8.15300114*(10**(-8)) ) * va*va*va*va*va*D_Tmrt + \
            ( 7.55043090*(10**(-4)) ) * D_Tmrt*D_Tmrt + \
            ( -5.65095215*(10**(-5)) ) * Ta*D_Tmrt*D_Tmrt + \
            ( -4.52166564*(10**(-7)) ) * Ta*Ta*D_Tmrt*D_Tmrt + \
            ( 2.46688878*(10**(-8)) ) * Ta*Ta*Ta*D_Tmrt*D_Tmrt + \
            ( 2.42674348*(10**(-10)) ) * Ta*Ta*Ta*Ta*D_Tmrt*D_Tmrt + \
            ( 1.54547250*(10**(-4)) ) * va*D_Tmrt*D_Tmrt + \
            ( 5.24110970*(10**(-6)) ) * Ta*va*D_Tmrt*D_Tmrt + \
            ( -8.75874982*(10**(-8)) ) * Ta*Ta*va*D_Tmrt*D_Tmrt + \
            ( -1.50743064*(10**(-9)) ) * Ta*Ta*Ta*va*D_Tmrt*D_Tmrt + \
            ( -1.56236307*(10**(-5)) ) * va*va*D_Tmrt*D_Tmrt + \
            ( -1.33895614*(10**(-7)) ) * Ta*va*va*D_Tmrt*D_Tmrt + \
            ( 2.49709824*(10**(-9)) ) * Ta*Ta*va*va*D_Tmrt*D_Tmrt + \
            ( 6.51711721*(10**(-7)) ) * va*va*va*D_Tmrt*D_Tmrt + \
            ( 1.94960053*(10**(-9)) ) * Ta*va*va*va*D_Tmrt*D_Tmrt + \
            ( -1.00361113*(10**(-8)) ) * va*va*va*va*D_Tmrt*D_Tmrt + \
            ( -1.21206673*(10**(-5)) ) * D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -2.18203660*(10**(-7)) ) * Ta*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 7.51269482*(10**(-9)) ) * Ta*Ta*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 9.79063848*(10**(-11)) ) * Ta*Ta*Ta*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 1.25006734*(10**(-6)) ) * va*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -1.81584736*(10**(-9)) ) * Ta*va*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -3.52197671*(10**(-10)) ) * Ta*Ta*va*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -3.36514630*(10**(-8)) ) * va*va*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 1.35908359*(10**(-10)) ) * Ta*va*va*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 4.17032620*(10**(-10)) ) * va*va*va*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -1.30369025*(10**(-9)) ) * D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 4.13908461*(10**(-10)) ) * Ta*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 9.22652254*(10**(-12)) ) * Ta*Ta*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -5.08220384*(10**(-9)) ) * va*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -2.24730961*(10**(-11)) ) * Ta*va*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 1.17139133*(10**(-10)) ) * va*va*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 6.62154879*(10**(-10)) ) * D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 4.03863260*(10**(-13)) ) * Ta*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 1.95087203*(10**(-12)) ) * va*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( -4.73602469*(10**(-12))) * D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt + \
            ( 5.12733497) * Pa + \
            ( -0.312788561) * Ta*Pa + \
            ( -0.0196701861 ) * Ta*Ta*Pa + \
            ( 9.99690870*(10**(-4)) ) * Ta*Ta*Ta*Pa + \
            ( 9.51738512*(10**(-6)) ) * Ta*Ta*Ta*Ta*Pa + \
            ( -4.66426341*(10**(-7)) ) * Ta*Ta*Ta*Ta*Ta*Pa + \
            ( 0.548050612 ) * va*Pa + \
            ( -0.00330552823) * Ta*va*Pa + \
            ( -0.00164119440 ) * Ta*Ta*va*Pa + \
            ( -5.16670694*(10**(-6)) ) * Ta*Ta*Ta*va*Pa + \
            ( 9.52692432*(10**(-7)) ) * Ta*Ta*Ta*Ta*va*Pa + \
            ( -0.0429223622 ) * va*va*Pa + \
            ( 0.00500845667 ) * Ta*va*va*Pa + \
            ( 1.00601257*(10**(-6)) ) * Ta*Ta*va*va*Pa + \
            ( -1.81748644*(10**(-6)) ) * Ta*Ta*Ta*va*va*Pa + \
            ( -1.25813502*(10**(-3)) ) * va*va*va*Pa + \
            ( -1.79330391*(10**(-4)) ) * Ta*va*va*va*Pa + \
            ( 2.34994441*(10**(-6)) ) * Ta*Ta*va*va*va*Pa + \
            ( 1.29735808*(10**(-4)) ) * va*va*va*va*Pa + \
            ( 1.29064870*(10**(-6)) ) * Ta*va*va*va*va*Pa + \
            ( -2.28558686*(10**(-6)) ) * va*va*va*va*va*Pa + \
            ( -0.0369476348 ) * D_Tmrt*Pa + \
            ( 0.00162325322 ) * Ta*D_Tmrt*Pa + \
            ( -3.14279680*(10**(-5)) ) * Ta*Ta*D_Tmrt*Pa + \
            ( 2.59835559*(10**(-6)) ) * Ta*Ta*Ta*D_Tmrt*Pa + \
            ( -4.77136523*(10**(-8)) ) * Ta*Ta*Ta*Ta*D_Tmrt*Pa + \
            ( 8.64203390*(10**(-3)) ) * va*D_Tmrt*Pa + \
            ( -6.87405181*(10**(-4)) ) * Ta*va*D_Tmrt*Pa + \
            ( -9.13863872*(10**(-6)) ) * Ta*Ta*va*D_Tmrt*Pa + \
            ( 5.15916806*(10**(-7)) ) * Ta*Ta*Ta*va*D_Tmrt*Pa + \
            ( -3.59217476*(10**(-5)) ) * va*va*D_Tmrt*Pa + \
            ( 3.28696511*(10**(-5)) ) * Ta*va*va*D_Tmrt*Pa + \
            ( -7.10542454*(10**(-7)) ) * Ta*Ta*va*va*D_Tmrt*Pa + \
            ( -1.24382300*(10**(-5)) ) * va*va*va*D_Tmrt*Pa + \
            ( -7.38584400*(10**(-9)) ) * Ta*va*va*va*D_Tmrt*Pa + \
            ( 2.20609296*(10**(-7)) ) * va*va*va*va*D_Tmrt*Pa + \
            ( -7.32469180*(10**(-4)) ) * D_Tmrt*D_Tmrt*Pa + \
            ( -1.87381964*(10**(-5)) ) * Ta*D_Tmrt*D_Tmrt*Pa + \
            ( 4.80925239*(10**(-6)) ) * Ta*Ta*D_Tmrt*D_Tmrt*Pa + \
            ( -8.75492040*(10**(-8)) ) * Ta*Ta*Ta*D_Tmrt*D_Tmrt*Pa + \
            ( 2.77862930*(10**(-5)) ) * va*D_Tmrt*D_Tmrt*Pa + \
            ( -5.06004592*(10**(-6)) ) * Ta*va*D_Tmrt*D_Tmrt*Pa + \
            ( 1.14325367*(10**(-7)) ) * Ta*Ta*va*D_Tmrt*D_Tmrt*Pa + \
            ( 2.53016723*(10**(-6)) ) * va*va*D_Tmrt*D_Tmrt*Pa + \
            ( -1.72857035*(10**(-8)) ) * Ta*va*va*D_Tmrt*D_Tmrt*Pa + \
            ( -3.95079398*(10**(-8)) ) * va*va*va*D_Tmrt*D_Tmrt*Pa + \
            ( -3.59413173*(10**(-7)) ) * D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( 7.04388046*(10**(-7)) ) * Ta*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( -1.89309167*(10**(-8)) ) * Ta*Ta*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( -4.79768731*(10**(-7)) ) * va*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( 7.96079978*(10**(-9)) ) * Ta*va*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( 1.62897058*(10**(-9)) ) * va*va*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( 3.94367674*(10**(-8)) ) * D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( -1.18566247*(10**(-9)) ) * Ta*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( 3.34678041*(10**(-10)) ) * va*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( -1.15606447*(10**(-10)) ) * D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*Pa + \
            ( -2.80626406 ) * Pa*Pa + \
            ( 0.548712484 ) * Ta*Pa*Pa + \
            ( -0.00399428410 ) * Ta*Ta*Pa*Pa + \
            ( -9.54009191*(10**(-4)) ) * Ta*Ta*Ta*Pa*Pa + \
            ( 1.93090978*(10**(-5)) ) * Ta*Ta*Ta*Ta*Pa*Pa + \
            ( -0.308806365 ) * va*Pa*Pa + \
            ( 0.0116952364 ) * Ta*va*Pa*Pa + \
            ( 4.95271903*(10**(-4)) ) * Ta*Ta*va*Pa*Pa + \
            ( -1.90710882*(10**(-5)) ) * Ta*Ta*Ta*va*Pa*Pa + \
            ( 0.00210787756 ) * va*va*Pa*Pa + \
            ( -6.98445738*(10**(-4)) ) * Ta*va*va*Pa*Pa + \
            ( 2.30109073*(10**(-5)) ) * Ta*Ta*va*va*Pa*Pa + \
            ( 4.17856590*(10**(-4)) ) * va*va*va*Pa*Pa + \
            ( -1.27043871*(10**(-5)) ) * Ta*va*va*va*Pa*Pa + \
            ( -3.04620472*(10**(-6)) ) * va*va*va*va*Pa*Pa + \
            ( 0.0514507424 ) * D_Tmrt*Pa*Pa + \
            ( -0.00432510997 ) * Ta*D_Tmrt*Pa*Pa + \
            ( 8.99281156*(10**(-5)) ) * Ta*Ta*D_Tmrt*Pa*Pa + \
            ( -7.14663943*(10**(-7)) ) * Ta*Ta*Ta*D_Tmrt*Pa*Pa + \
            ( -2.66016305*(10**(-4)) ) * va*D_Tmrt*Pa*Pa + \
            ( 2.63789586*(10**(-4)) ) * Ta*va*D_Tmrt*Pa*Pa + \
            ( -7.01199003*(10**(-6)) ) * Ta*Ta*va*D_Tmrt*Pa*Pa + \
            ( -1.06823306*(10**(-4)) ) * va*va*D_Tmrt*Pa*Pa + \
            ( 3.61341136*(10**(-6)) ) * Ta*va*va*D_Tmrt*Pa*Pa + \
            ( 2.29748967*(10**(-7)) ) * va*va*va*D_Tmrt*Pa*Pa + \
            ( 3.04788893*(10**(-4)) ) * D_Tmrt*D_Tmrt*Pa*Pa + \
            ( -6.42070836*(10**(-5)) ) * Ta*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( 1.16257971*(10**(-6)) ) * Ta*Ta*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( 7.68023384*(10**(-6)) ) * va*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( -5.47446896*(10**(-7)) ) * Ta*va*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( -3.59937910*(10**(-8)) ) * va*va*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( -4.36497725*(10**(-6)) ) * D_Tmrt*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( 1.68737969*(10**(-7)) ) * Ta*D_Tmrt*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( 2.67489271*(10**(-8)) ) * va*D_Tmrt*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( 3.23926897*(10**(-9)) ) * D_Tmrt*D_Tmrt*D_Tmrt*D_Tmrt*Pa*Pa + \
            ( -0.0353874123 ) * Pa*Pa*Pa + \
            ( -0.221201190 ) * Ta*Pa*Pa*Pa + \
            ( 0.0155126038 ) * Ta*Ta*Pa*Pa*Pa + \
            ( -2.63917279*(10**(-4)) ) * Ta*Ta*Ta*Pa*Pa*Pa + \
            ( 0.0453433455 ) * va*Pa*Pa*Pa + \
            ( -0.00432943862 ) * Ta*va*Pa*Pa*Pa + \
            ( 1.45389826*(10**(-4)) ) * Ta*Ta*va*Pa*Pa*Pa + \
            ( 2.17508610*(10**(-4)) ) * va*va*Pa*Pa*Pa + \
            ( -6.66724702*(10**(-5)) ) * Ta*va*va*Pa*Pa*Pa + \
            ( 3.33217140*(10**(-5)) ) * va*va*va*Pa*Pa*Pa + \
            ( -0.00226921615 ) * D_Tmrt*Pa*Pa*Pa + \
            ( 3.80261982*(10**(-4)) ) * Ta*D_Tmrt*Pa*Pa*Pa + \
            ( -5.45314314*(10**(-9)) ) * Ta*Ta*D_Tmrt*Pa*Pa*Pa + \
            ( -7.96355448*(10**(-4)) ) * va*D_Tmrt*Pa*Pa*Pa + \
            ( 2.53458034*(10**(-5)) ) * Ta*va*D_Tmrt*Pa*Pa*Pa + \
            ( -6.31223658*(10**(-6)) ) * va*va*D_Tmrt*Pa*Pa*Pa + \
            ( 3.02122035*(10**(-4)) ) * D_Tmrt*D_Tmrt*Pa*Pa*Pa + \
            ( -4.77403547*(10**(-6)) ) * Ta*D_Tmrt*D_Tmrt*Pa*Pa*Pa + \
            ( 1.73825715*(10**(-6)) ) * va*D_Tmrt*D_Tmrt*Pa*Pa*Pa + \
            ( -4.09087898*(10**(-7)) ) * D_Tmrt*D_Tmrt*D_Tmrt*Pa*Pa*Pa + \
            ( 0.614155345 ) * Pa*Pa*Pa*Pa + \
            ( -0.0616755931 ) * Ta*Pa*Pa*Pa*Pa + \
            ( 0.00133374846 ) * Ta*Ta*Pa*Pa*Pa*Pa + \
            ( 0.00355375387 ) * va*Pa*Pa*Pa*Pa + \
            ( -5.13027851*(10**(-4)) ) * Ta*va*Pa*Pa*Pa*Pa + \
            ( 1.02449757*(10**(-4)) ) * va*va*Pa*Pa*Pa*Pa + \
            ( -0.00148526421 ) * D_Tmrt*Pa*Pa*Pa*Pa + \
            ( -4.11469183*(10**(-5)) ) * Ta*D_Tmrt*Pa*Pa*Pa*Pa + \
            ( -6.80434415*(10**(-6)) ) * va*D_Tmrt*Pa*Pa*Pa*Pa + \
            ( -9.77675906*(10**(-6)) ) * D_Tmrt*D_Tmrt*Pa*Pa*Pa*Pa + \
            ( 0.0882773108 ) * Pa*Pa*Pa*Pa*Pa + \
            ( -0.00301859306 ) * Ta*Pa*Pa*Pa*Pa*Pa + \
            ( 0.00104452989 ) * va*Pa*Pa*Pa*Pa*Pa + \
            ( 2.47090539*(10**(-4)) ) * D_Tmrt*Pa*Pa*Pa*Pa*Pa + \
            ( 0.00148348065 ) * Pa*Pa*Pa*Pa*Pa*Pa
            
            if UTCI_approx > 9 and UTCI_approx < 26: comfortable = 1
            else: comfortable = 0
            
            if UTCI_approx < -14.0: stressRange = -2
            elif UTCI_approx > -14.0 and UTCI_approx < 9.0: stressRange = -1
            elif UTCI_approx > 9.0 and UTCI_approx < 26.0: stressRange = 0
            elif UTCI_approx > 26.0 and UTCI_approx < 32.0: stressRange = 1
            else: stressRange = 2
            
        else:
            UTCI_approx = None
            comfortable = None
            stressRange = None
        
        return UTCI_approx, comfortable, stressRange
    
    
    def calcHumidRatio(self, airTemp, relHumid, barPress):
        #Convert Temperature to Kelvin
        TKelvin = []
        for item in airTemp:
            TKelvin.append(item+273)
        
        #Calculate saturation vapor pressure above freezing
        Sigma = []
        for item in TKelvin:
            if item >= 273:
                Sigma.append(1-(item/647.096))
            else:
                Sigma.append(0)
        
        ExpressResult = []
        for item in Sigma:
            ExpressResult.append(((item)*(-7.85951783))+((item**1.5)*1.84408259)+((item**3)*(-11.7866487))+((item**3.5)*22.6807411)+((item**4)*(-15.9618719))+((item**7.5)*1.80122502))
        
        CritTemp = []
        for item in TKelvin:
            CritTemp.append(647.096/item)
        
        Exponent = [a*b for a,b in zip(CritTemp,ExpressResult)]
        
        Power = []
        for item in Exponent:
            Power.append(math.exp(item))
        
        SatPress1 = []
        for item in Power:
            if item != 1:
                SatPress1.append(item*22064000)
            else:
                SatPress1.append(0)
        
        #Calculate saturation vapor pressure below freezing
        Theta = []
        for item in TKelvin:
            if item < 273:
                Theta.append(item/273.16)
            else:
                Theta.append(1)
        
        Exponent2 = []
        for x in Theta:
            Exponent2.append(((1-(x**(-1.5)))*(-13.928169))+((1-(x**(-1.25)))*34.707823))
        
        Power = []
        for item in Exponent2:
            Power.append(math.exp(item))
        
        SatPress2 = []
        for item in Power:
            if item != 1:
                SatPress2.append(item*611.657)
            else:
                SatPress2.append(0)
        
        #Combine into final saturation vapor pressure
        saturationPressure = [a+b for a,b in zip(SatPress1,SatPress2)]
        
        #Calculate hourly water vapor pressure
        DecRH = []
        for item in relHumid:
            DecRH.append(item*0.01)
        
        partialPressure = [a*b for a,b in zip(DecRH,saturationPressure)]
        
        #Calculate hourly humidity ratio
        PressDiffer = [a-b for a,b in zip(barPress,partialPressure)]
        
        Constant = []
        for item in partialPressure:
            Constant.append(item*0.621991)
        
        humidityRatio = [a/b for a,b in zip(Constant,PressDiffer)]
        
        #Calculate hourly enthalpy
        EnVariable1 = []
        for item in humidityRatio:
            EnVariable1.append(1.01+(1.89*item))
        
        EnVariable2 = [a*b for a,b in zip(EnVariable1,airTemp)]
        
        EnVariable3 = []
        for item in humidityRatio:
            EnVariable3.append(2500*item)
        
        EnVariable4 = [a+b for a,b in zip(EnVariable2,EnVariable3)]
        
        enthalpy = []
        for x in EnVariable4:
            if x >= 0:
                enthalpy.append(x)
            else:
                enthalpy.append(0)
        
        #Return all of the results
        return humidityRatio, enthalpy, partialPressure, saturationPressure
    
    def outlineCurve(self, curve):
        solidBrep = rc.Geometry.Brep.CreatePlanarBreps([curve])[0]
        try:
            offsetCrv = curve.OffsetOnSurface(solidBrep.Faces[0], 0.25, sc.doc.ModelAbsoluteTolerance)[0]
            finalBrep = (rc.Geometry.Brep.CreatePlanarBreps([curve, offsetCrv])[0])
        except:
            finalBrep = solidBrep
            warning = "Creating an outline of one of the comfort or strategy curves failed.  Component will return a solid brep."
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
        return finalBrep
    
    
    def getSeatedMannequinData(self):
        seatedData = [[(-0.0495296, 0.284129, 0.450062), (-0.0495296, 0.284129, 0.973663), (-0.175068, 0.166825, 0.973663), (-0.175068, 0.166825, 0.38225)],
        [(0.0495296, 0.284129, 0.450062), (0.0495296, 0.284129, 0.973663), (-0.0495296, 0.284129, 0.973663), (-0.0495296, 0.284129, 0.450062)],
        [(0.0495296, 0.284129, 0.973663), (0.0495296, 0.284129, 0.450062), (0.175068, 0.166825, 0.38225), (0.175068, 0.166825, 0.973663)],
        [(-0.165339, 0.096853, 0.60115), (-0.120896, -0.222765, 0.60115), (-0.120896, -0.222765, 0.38225), (-0.175068, 0.166825, 0.38225)],
        [(-0.165339, 0.096853, 0.789205), (-0.165339, 0.096853, 0.60115), (-0.175068, 0.166825, 0.902163)],
        [(-0.175068, 0.166825, 0.38225), (-0.175068, 0.166825, 0.902163), (-0.165339, 0.096853, 0.60115)],
        [(0.165339, 0.096853, 0.60115), (0.120896, -0.222765, 0.60115), (0.120896, -0.222765, 0.38225), (0.175068, 0.166825, 0.38225)],
        [(0.165339, 0.096853, 0.789205), (0.165339, 0.096853, 0.60115), (0.175068, 0.166825, 0.902163)],
        [(0.175068, 0.166825, 0.38225), (0.175068, 0.166825, 0.902163), (0.165339, 0.096853, 0.60115)],
        [(0.120896, -0.222765, 0.60115), (0.120896, -0.222765, 0.0715), (0.0223678, -0.222765, 0.0715), (0.0223678, -0.222765, 0.60115)],
        [(-0.120896, -0.222765, 0.60115), (-0.0223678, -0.222765, 0.60115), (-0.0223678, -0.222765, 0.0715), (-0.120896, -0.222765, 0.0715)],
        [(0.0223678, -0.132523, 0.38225), (0.0223678, -0.222765, 0.0715), (0.0223678, -0.222765, 0.60115)],
        [(0.0223678, -0.222765, 0.0715), (0.0223678, -0.382764, -4.51028e-17), (0.0223678, -0.382764, 0.0715)],
        [(0.0223678, -0.382764, -4.51028e-17), (0.0223678, -0.222765, 0.0715), (0.0223678, -0.132523, -4.51028e-17)],
        [(0.0223678, -0.132523, 0.38225), (0.0223678, 0.0529662, 0.60115), (0.0223678, 0.0529662, 0.38225)],
        [(0.0223678, -0.222765, 0.0715), (0.0223678, -0.132523, 0.38225), (0.0223678, -0.132523, -4.51028e-17)],
        [(0.0223678, -0.222765, 0.60115), (0.0223678, 0.0529662, 0.60115), (0.0223678, -0.132523, 0.38225)],
        [(-0.0223678, -0.222765, 0.0715), (-0.0223678, -0.382764, 0.0715), (-0.0223678, -0.382764, -3.1225e-17)],
        [(-0.0223678, -0.132523, 0.38225), (-0.0223678, -0.222765, 0.60115), (-0.0223678, -0.222765, 0.0715)],
        [(-0.0223678, -0.222765, 0.0715), (-0.0223678, -0.382764, -3.1225e-17), (-0.0223678, -0.132523, -3.1225e-17)],
        [(-0.0223678, -0.222765, 0.0715), (-0.0223678, -0.132523, -3.1225e-17), (-0.0223678, -0.132523, 0.38225)],
        [(-0.0223678, -0.132523, 0.38225), (-0.0223678, 0.0529662, 0.38225), (-0.0223678, 0.0529662, 0.60115)],
        [(-0.0223678, -0.222765, 0.60115), (-0.0223678, -0.132523, 0.38225), (-0.0223678, 0.0529662, 0.60115)],
        [(-0.120896, -0.382764, 0.0715), (-0.120896, -0.382764, -3.29597e-17), (-0.120896, -0.222765, 0.0715)],
        [(-0.120896, -0.132523, -3.29597e-17), (-0.120896, -0.222765, 0.0715), (-0.120896, -0.382764, -3.29597e-17)],
        [(-0.120896, -0.222765, 0.38225), (-0.120896, -0.222765, 0.0715), (-0.120896, -0.132523, -3.29597e-17), (-0.120896, -0.132523, 0.38225)],
        [(0.120896, -0.382764, 0.0715), (0.120896, -0.382764, -4.51028e-17), (0.120896, -0.222765, 0.0715)],
        [(0.120896, -0.132523, -4.51028e-17), (0.120896, -0.222765, 0.0715), (0.120896, -0.382764, -4.51028e-17)],
        [(0.120896, -0.222765, 0.38225), (0.120896, -0.222765, 0.0715), (0.120896, -0.132523, -4.51028e-17), (0.120896, -0.132523, 0.38225)],
        [(0.0223678, 0.0529662, 0.38225), (0.0223678, 0.0529662, 0.973663), (-0.0223678, 0.0529662, 0.973663), (-0.0223678, 0.0529662, 0.38225)],
        [(-0.0495296, 0.284129, 0.450062), (0.0495296, 0.284129, 0.450062), (0.175068, 0.166825, 0.38225), (-0.175068, 0.166825, 0.38225)],
        [(-0.0223678, -0.132523, 0.38225), (-0.0223678, -0.132523, 0.0715), (-0.120896, -0.132523, 0.0715), (-0.120896, -0.132523, 0.38225)],
        [(-0.120896, -0.222765, 0.0715), (-0.120896, -0.382764, 0.0715), (-0.0223678, -0.382764, 0.0715), (-0.0223678, -0.222765, 0.0715)],
        [(-0.0223678, -0.382764, -3.1225e-17), (-0.120896, -0.382764, -3.29597e-17), (-0.120896, -0.132523, -3.29597e-17), (-0.0223678, -0.132523, -3.1225e-17)],
        [(-0.0223678, -0.132523, 0.0715), (-0.0223678, -0.132523, -3.1225e-17), (-0.120896, -0.132523, -3.29597e-17), (-0.120896, -0.132523, 0.0715)],
        [(-0.0223678, -0.382764, 0.0715), (-0.120896, -0.382764, 0.0715), (-0.120896, -0.382764, -3.29597e-17), (-0.0223678, -0.382764, -3.1225e-17)],
        [(0.0223678, -0.132523, 0.0715), (0.0223678, -0.132523, 0.38225), (0.120896, -0.132523, 0.38225), (0.120896, -0.132523, 0.0715)],
        [(-0.175068, 0.166825, 0.38225), (-0.120896, -0.222765, 0.38225), (-0.120896, -0.132523, 0.38225)],
        [(-0.175068, 0.166825, 0.38225), (-0.120896, -0.132523, 0.38225), (-0.0223678, 0.0529662, 0.38225)],
        [(-0.0223678, -0.132523, 0.38225), (-0.0223678, 0.0529662, 0.38225), (-0.120896, -0.132523, 0.38225)],
        [(0.175068, 0.166825, 0.38225), (-0.175068, 0.166825, 0.38225), (-0.0223678, 0.0529662, 0.38225), (0.0223678, 0.0529662, 0.38225)],
        [(0.175068, 0.166825, 0.38225), (0.0223678, 0.0529662, 0.38225), (0.120896, -0.132523, 0.38225)],
        [(0.0223678, -0.132523, 0.38225), (0.120896, -0.132523, 0.38225), (0.0223678, 0.0529662, 0.38225)],
        [(0.120896, -0.222765, 0.38225), (0.175068, 0.166825, 0.38225), (0.120896, -0.132523, 0.38225)],
        [(0.165339, 0.096853, 0.60115), (0.0223678, 0.0529662, 0.60115), (0.0223678, -0.222765, 0.60115), (0.120896, -0.222765, 0.60115)],
        [(-0.120896, -0.222765, 0.60115), (-0.0223678, -0.222765, 0.60115), (-0.0223678, 0.0529662, 0.60115), (-0.165339, 0.096853, 0.60115)],
        [(0.165339, 0.096853, 0.60115), (0.165339, 0.096853, 0.973663), (0.0223678, 0.0529662, 0.973663), (0.0223678, 0.0529662, 0.60115)],
        [(0.232207, 0.15888, 0.902163), (0.175068, 0.166825, 0.902163), (0.175068, 0.166825, 0.973663), (0.232207, 0.15888, 0.973663)],
        [(0.232207, 0.15888, 0.973663), (0.222478, 0.0889078, 0.973663), (0.165339, 0.096853, 0.973663), (0.175068, 0.166825, 0.973663)],
        [(0.206606, -0.025235, 0.728104), (0.206606, -0.180522, 0.728104), (0.209127, -0.180873, 0.694807), (0.211569, 0.0104553, 0.662556)],
        [(0.153842, 0.0141721, 0.655729), (0.151455, -0.172853, 0.687256), (0.148959, -0.172506, 0.720232), (0.148959, -0.0209489, 0.720232)],
        [(0.206606, -0.025235, 0.728104), (0.148959, -0.0209489, 0.720232), (0.148959, -0.172506, 0.720232), (0.206606, -0.180522, 0.728104)],
        [(0.153842, 0.0141721, 0.655729), (0.151455, -0.172853, 0.687256), (0.209127, -0.180873, 0.694807), (0.211569, 0.0104553, 0.662556)],
        [(0.209127, -0.180873, 0.694807), (0.151455, -0.172853, 0.687256), (0.139503, -0.258806, 0.687256), (0.197175, -0.266825, 0.694807)],
        [(0.151455, -0.172853, 0.687256), (0.148959, -0.172506, 0.720232), (0.137007, -0.258459, 0.720232), (0.139503, -0.258806, 0.687256)],
        [(0.148959, -0.172506, 0.720232), (0.206606, -0.180522, 0.728104), (0.194654, -0.266475, 0.728104), (0.137007, -0.258459, 0.720232)],
        [(0.197175, -0.266825, 0.694807), (0.194654, -0.266475, 0.728104), (0.206606, -0.180522, 0.728104), (0.209127, -0.180873, 0.694807)],
        [(0.197175, -0.266825, 0.694807), (0.194654, -0.266475, 0.728104), (0.137007, -0.258459, 0.720232), (0.139503, -0.258806, 0.687256)],
        [(0.232207, 0.15888, 0.902163), (0.211569, 0.0104553, 0.662556), (0.153842, 0.0141721, 0.655729), (0.175068, 0.166825, 0.902163)],
        [(0.222478, 0.0889078, 0.973663), (0.206606, -0.025235, 0.728104), (0.211569, 0.0104553, 0.662556)],
        [(0.232207, 0.15888, 0.973663), (0.222478, 0.0889078, 0.973663), (0.232207, 0.15888, 0.902163)],
        [(0.211569, 0.0104553, 0.662556), (0.232207, 0.15888, 0.902163), (0.222478, 0.0889078, 0.973663)],
        [(0.165339, 0.096853, 0.973663), (0.148959, -0.0209489, 0.720232), (0.153842, 0.0141721, 0.655729), (0.165339, 0.096853, 0.789205)],
        [(0.165339, 0.096853, 0.973663), (0.148959, -0.0209489, 0.720232), (0.206606, -0.025235, 0.728104), (0.222478, 0.0889078, 0.973663)],
        [(-0.232207, 0.15888, 0.902163), (-0.175068, 0.166825, 0.902163), (-0.175068, 0.166825, 0.973663), (-0.232207, 0.15888, 0.973663)],
        [(-0.175068, 0.166825, 0.973663), (-0.165339, 0.096853, 0.973663), (-0.222478, 0.0889078, 0.973663), (-0.232207, 0.15888, 0.973663)],
        [(-0.206606, -0.025235, 0.728104), (-0.206606, -0.180522, 0.728104), (-0.209127, -0.180873, 0.694807), (-0.211569, 0.0104553, 0.662556)],
        [(-0.153842, 0.0141721, 0.655729), (-0.151455, -0.172853, 0.687256), (-0.148959, -0.172506, 0.720232), (-0.148959, -0.0209489, 0.720232)],
        [(-0.206606, -0.025235, 0.728104), (-0.148959, -0.0209489, 0.720232), (-0.148959, -0.172506, 0.720232), (-0.206606, -0.180522, 0.728104)],
        [(-0.153842, 0.0141721, 0.655729), (-0.151455, -0.172853, 0.687256), (-0.209127, -0.180873, 0.694807), (-0.211569, 0.0104553, 0.662556)],
        [(-0.209127, -0.180873, 0.694807), (-0.151455, -0.172853, 0.687256), (-0.139503, -0.258806, 0.687256), (-0.197175, -0.266825, 0.694807)],
        [(-0.151455, -0.172853, 0.687256), (-0.148959, -0.172506, 0.720232), (-0.137007, -0.258459, 0.720232), (-0.139503, -0.258806, 0.687256)],
        [(-0.148959, -0.172506, 0.720232), (-0.206606, -0.180522, 0.728104), (-0.194654, -0.266475, 0.728104), (-0.137007, -0.258459, 0.720232)],
        [(-0.197175, -0.266825, 0.694807), (-0.194654, -0.266475, 0.728104), (-0.206606, -0.180522, 0.728104), (-0.209127, -0.180873, 0.694807)],
        [(-0.197175, -0.266825, 0.694807), (-0.194654, -0.266475, 0.728104), (-0.137007, -0.258459, 0.720232), (-0.139503, -0.258806, 0.687256)],
        [(-0.232207, 0.15888, 0.902163), (-0.211569, 0.0104553, 0.662556), (-0.153842, 0.0141721, 0.655729), (-0.175068, 0.166825, 0.902163)],
        [(-0.222478, 0.0889078, 0.973663), (-0.206606, -0.025235, 0.728104), (-0.211569, 0.0104553, 0.662556)],
        [(-0.232207, 0.15888, 0.973663), (-0.222478, 0.0889078, 0.973663), (-0.232207, 0.15888, 0.902163)],
        [(-0.211569, 0.0104553, 0.662556), (-0.232207, 0.15888, 0.902163), (-0.222478, 0.0889078, 0.973663)],
        [(-0.153842, 0.0141721, 0.655729), (-0.165339, 0.096853, 0.789205), (-0.165339, 0.096853, 0.973663), (-0.148959, -0.0209489, 0.720232)],
        [(-0.165339, 0.096853, 0.973663), (-0.148959, -0.0209489, 0.720232), (-0.206606, -0.025235, 0.728104), (-0.222478, 0.0889078, 0.973663)],
        [(-0.0495296, 0.284129, 0.973663), (-0.0369027, 0.229597, 1.00290), (0.0369027, 0.229597, 1.00290), (0.0495296, 0.284129, 0.973663)],
        [(0.0564241, 0.229597, 0.994861), (0.0564241, 0.166825, 1.02253), (0.175068, 0.166825, 0.973663)],
        [(0.0369027, 0.229597, 1.00290), (0.0564241, 0.229597, 0.994861), (0.0495296, 0.284129, 0.973663)],
        [(0.175068, 0.166825, 0.973663), (0.0495296, 0.284129, 0.973663), (0.0564241, 0.229597, 0.994861)],
        [(0.175068, 0.166825, 0.973663), (0.0564241, 0.166825, 1.02253), (0.0564241, 0.131926, 1.02053), (0.165339, 0.096853, 0.973663)],
        [(0.0564241, 0.118717, 1.01150), (0.0223678, 0.118717, 1.01865), (0.0223678, 0.0529662, 0.973663)],
        [(0.0564241, 0.131926, 1.02053), (0.0564241, 0.118717, 1.01150), (0.165339, 0.096853, 0.973663)],
        [(0.0223678, 0.0529662, 0.973663), (0.165339, 0.096853, 0.973663), (0.0564241, 0.118717, 1.01150)],
        [(0.0223678, 0.0529662, 0.973663), (0.0223678, 0.118717, 1.01865), (-0.0223678, 0.118717, 1.01865), (-0.0223678, 0.0529662, 0.973663)],
        [(-0.165339, 0.096853, 0.60115), (-0.0223678, 0.0529662, 0.60115), (-0.0223678, 0.0529662, 0.973663), (-0.165339, 0.096853, 0.973663)],
        [(-0.0564241, 0.118717, 1.01150), (-0.0564241, 0.131926, 1.02053), (-0.165339, 0.096853, 0.973663)],
        [(-0.0223678, 0.118717, 1.01865), (-0.0564241, 0.118717, 1.01150), (-0.0223678, 0.0529662, 0.973663)],
        [(-0.165339, 0.096853, 0.973663), (-0.0223678, 0.0529662, 0.973663), (-0.0564241, 0.118717, 1.01150)],
        [(-0.175068, 0.166825, 0.973663), (-0.0564241, 0.166825, 1.02253), (-0.0564241, 0.131926, 1.02053), (-0.165339, 0.096853, 0.973663)],
        [(-0.0564241, 0.229597, 0.994861), (-0.0564241, 0.166825, 1.02253), (-0.175068, 0.166825, 0.973663)],
        [(-0.0369027, 0.229597, 1.00290), (-0.0564241, 0.229597, 0.994861), (-0.0495296, 0.284129, 0.973663)],
        [(-0.175068, 0.166825, 0.973663), (-0.0495296, 0.284129, 0.973663), (-0.0564241, 0.229597, 0.994861)],
        [(0.0223678, -0.222765, 0.0715), (0.0223678, -0.382764, 0.0715), (0.120896, -0.382764, 0.0715), (0.120896, -0.222765, 0.0715)],
        [(0.0223678, -0.132523, -4.51028e-17), (0.120896, -0.132523, -4.51028e-17), (0.120896, -0.382764, -4.51028e-17), (0.0223678, -0.382764, -4.51028e-17)],
        [(0.120896, -0.132523, 0.0715), (0.120896, -0.132523, -4.51028e-17), (0.0223678, -0.132523, -4.51028e-17), (0.0223678, -0.132523, 0.0715)],
        [(0.0223678, -0.382764, -4.51028e-17), (0.120896, -0.382764, -4.51028e-17), (0.120896, -0.382764, 0.0715), (0.0223678, -0.382764, 0.0715)],
        [(-0.0564241, 0.118717, 1.01150), (-0.0564241, 0.118717, 1.0945), (-0.0223678, 0.118717, 1.01865)],
        [(-0.0564241, 0.118717, 1.0945), (0.0564241, 0.118717, 1.0945), (0.0223678, 0.118717, 1.01865), (-0.0223678, 0.118717, 1.01865)],
        [(0.0564241, 0.118717, 1.01150), (0.0223678, 0.118717, 1.01865), (0.0564241, 0.118717, 1.0945)],
        [(0.0564241, 0.118717, 1.01150), (0.0564241, 0.118717, 1.0945), (0.0564241, 0.131926, 1.02053)],
        [(0.0564241, 0.166825, 1.02253), (0.0564241, 0.131926, 1.02053), (0.0564241, 0.118717, 1.0945)],
        [(0.0564241, 0.229597, 0.994861), (0.0564241, 0.166825, 1.02253), (0.0564241, 0.229597, 1.0945)],
        [(0.0564241, 0.118717, 1.0945), (0.0564241, 0.229597, 1.0945), (0.0564241, 0.166825, 1.02253)],
        [(-0.0564241, 0.229597, 1.0945), (-0.0564241, 0.229597, 0.994861), (-0.0369027, 0.229597, 1.00290)],
        [(-0.0369027, 0.229597, 1.00290), (0.0369027, 0.229597, 1.00290), (0.0564241, 0.229597, 1.0945), (-0.0564241, 0.229597, 1.0945)],
        [(0.0564241, 0.229597, 1.0945), (0.0369027, 0.229597, 1.00290), (0.0564241, 0.229597, 0.994861)],
        [(-0.0709703, 0.229597, 1.0945), (0.0709703, 0.229597, 1.0945), (0.0709703, 0.264736, 1.23032), (-0.0709703, 0.264736, 1.23032)],
        [(-0.0709703, 0.264736, 1.23032), (-0.0709703, 0.229597, 1.3112), (0.0709703, 0.229597, 1.3112), (0.0709703, 0.264736, 1.23032)],
        [(0.0709703, 0.264736, 1.23032), (0.0709703, 0.107585, 1.0945), (0.0709703, 0.107585, 1.3112)],
        [(0.0709703, 0.107585, 1.0945), (0.0709703, 0.264736, 1.23032), (0.0709703, 0.229597, 1.0945)],
        [(0.0709703, 0.229597, 1.3112), (0.0709703, 0.264736, 1.23032), (0.0709703, 0.107585, 1.3112)],
        [(-0.0709703, 0.264736, 1.23032), (-0.0709703, 0.107585, 1.0945), (-0.0709703, 0.107585, 1.3112)],
        [(-0.0709703, 0.107585, 1.0945), (-0.0709703, 0.264736, 1.23032), (-0.0709703, 0.229597, 1.0945)],
        [(-0.0709703, 0.229597, 1.3112), (-0.0709703, 0.264736, 1.23032), (-0.0709703, 0.107585, 1.3112)],
        [(-0.0709703, 0.107585, 1.3112), (-0.0394345, 0.0843967, 1.24231), (0.0394345, 0.0843967, 1.24231), (0.0709703, 0.107585, 1.3112)],
        [(0.0394345, 0.0843967, 1.24231), (0.0394345, 0.0843967, 1.0945), (-0.0394345, 0.0843967, 1.0945), (-0.0394345, 0.0843967, 1.24231)],
        [(0.0709703, 0.229597, 1.3112), (0.0709703, 0.107585, 1.3112), (-0.0709703, 0.107585, 1.3112), (-0.0709703, 0.229597, 1.3112)],
        [(-0.0709703, 0.107585, 1.3112), (-0.0394345, 0.0843967, 1.24231), (-0.0394345, 0.0843967, 1.0945), (-0.0709703, 0.107585, 1.0945)],
        [(0.0709703, 0.107585, 1.0945), (0.0394345, 0.0843967, 1.0945), (0.0394345, 0.0843967, 1.24231), (0.0709703, 0.107585, 1.3112)],
        [(-0.0564241, 0.229597, 1.0945), (-0.0564241, 0.118717, 1.0945), (-0.0709703, 0.107585, 1.0945), (-0.0709703, 0.229597, 1.0945)],
        [(-0.0394345, 0.0843967, 1.0945), (-0.0709703, 0.107585, 1.0945), (-0.0564241, 0.118717, 1.0945)],
        [(-0.0564241, 0.118717, 1.0945), (0.0564241, 0.118717, 1.0945), (0.0394345, 0.0843967, 1.0945), (-0.0394345, 0.0843967, 1.0945)],
        [(0.0564241, 0.118717, 1.0945), (0.0564241, 0.229597, 1.0945), (0.0709703, 0.229597, 1.0945), (0.0709703, 0.107585, 1.0945)],
        [(0.0709703, 0.107585, 1.0945), (0.0394345, 0.0843967, 1.0945), (0.0564241, 0.118717, 1.0945)],
        [(-0.0564241, 0.118717, 1.0945), (-0.0564241, 0.118717, 1.01150), (-0.0564241, 0.131926, 1.02053)],
        [(-0.0564241, 0.166825, 1.02253), (-0.0564241, 0.118717, 1.0945), (-0.0564241, 0.131926, 1.02053)],
        [(-0.0564241, 0.229597, 1.0945), (-0.0564241, 0.166825, 1.02253), (-0.0564241, 0.229597, 0.994861)],
        [(-0.0564241, 0.118717, 1.0945), (-0.0564241, 0.166825, 1.02253), (-0.0564241, 0.229597, 1.0945)]]
        
        return seatedData
    
    def getStandingMannequinData(self):
        standingData = [[(0.171916, -0.047394, 1.00065), (0.171916, -0.047394, 1.36994), (0.172486, -0.0875496, 1.06244)],
        [(0.228398, -0.0483948, 1.00065), (0.196123, -0.118413, 0.759271), (0.228968, -0.0885504, 1.06244)],
        [(0.228968, -0.0885504, 1.06244), (0.196885, -0.172085, 0.783852), (0.196123, -0.118413, 0.759271)],
        [(0.197285, -0.200214, 0.687691), (0.174081, -0.199803, 0.687691), (0.173681, -0.171674, 0.783852), (0.196885, -0.172085, 0.783852)],
        [(0.196522, -0.146542, 0.66311), (0.196123, -0.118413, 0.759271), (0.172919, -0.118002, 0.759271), (0.173318, -0.146131, 0.66311)],
        [(0.173681, -0.171674, 0.783852), (0.172919, -0.118002, 0.759271), (0.173318, -0.146131, 0.66311), (0.174081, -0.199803, 0.687691)],
        [(0.174081, -0.199803, 0.687691), (0.173318, -0.146131, 0.66311), (0.196522, -0.146542, 0.66311), (0.197285, -0.200214, 0.687691)],
        [(0.196123, -0.118413, 0.759271), (0.196522, -0.146542, 0.66311), (0.197285, -0.200214, 0.687691), (0.196885, -0.172085, 0.783852)],
        [(0.196123, -0.118413, 0.759271), (0.228398, -0.0483948, 1.00065), (0.171916, -0.047394, 1.00065), (0.172919, -0.118002, 0.759271)],
        [(0.228968, -0.0885504, 1.06244), (0.172486, -0.0875496, 1.06244), (0.173681, -0.171674, 0.783852), (0.196885, -0.172085, 0.783852)],
        [(0.171916, -0.047394, 1.00065), (0.172919, -0.118002, 0.759271), (0.173681, -0.171674, 0.783852), (0.172486, -0.0875496, 1.06244)],
        [(0.228398, -0.0483948, 1.00065), (0.228398, -0.0483948, 1.36994), (0.228968, -0.0885504, 1.06244)],
        [(0.227417, 0.0206151, 1.36994), (0.228398, -0.0483948, 1.36994), (0.227417, 0.0206151, 1.30002)],
        [(0.228398, -0.0483948, 1.36994), (0.227417, 0.0206151, 1.30002), (0.228398, -0.0483948, 1.00065)],
        [(0.171916, -0.047394, 1.36994), (0.228398, -0.0483948, 1.36994), (0.228968, -0.0885504, 1.06244), (0.172486, -0.0875496, 1.06244)],
        [(0.171916, -0.047394, 1.00065), (0.170935, 0.0216159, 1.30002), (0.227417, 0.0206151, 1.30002), (0.228398, -0.0483948, 1.00065)],
        [(0.227417, 0.0206151, 1.36994), (0.170935, 0.0216159, 1.36994), (0.170935, 0.0216159, 1.30002), (0.227417, 0.0206151, 1.30002)],
        [(0.227417, 0.0206151, 1.36994), (0.170935, 0.0216159, 1.36994), (0.171916, -0.047394, 1.36994), (0.228398, -0.0483948, 1.36994)],
        [(0.170935, 0.0216159, 1.36994), (0.170935, 0.0216159, 0.791631), (0.0198005, 0.138854, 0.791631), (0.0198005, 0.138854, 1.36994)],
        [(0.171916, -0.047394, 1.36994), (0.0230087, -0.0869583, 1.36994), (0.0230087, -0.0869583, 0.791631), (0.171916, -0.047394, 0.791631)],
        [(0.170935, 0.0216159, 1.30002), (0.170935, 0.0216159, 0.791631), (0.171916, -0.047394, 0.791631), (0.171916, -0.047394, 1.00065)],
        [(-0.227379, -0.0403189, 1.00065), (-0.193098, -0.111516, 0.759271), (-0.226809, -0.0804746, 1.06244)],
        [(-0.226809, -0.0804746, 1.06244), (-0.192336, -0.165189, 0.783852), (-0.193098, -0.111516, 0.759271)],
        [(-0.191936, -0.193318, 0.687691), (-0.168732, -0.193729, 0.687691), (-0.169132, -0.1656, 0.783852), (-0.192336, -0.165189, 0.783852)],
        [(-0.193098, -0.111516, 0.759271), (-0.169894, -0.111928, 0.759271), (-0.169495, -0.140056, 0.66311), (-0.192698, -0.139645, 0.66311)],
        [(-0.169132, -0.1656, 0.783852), (-0.169894, -0.111928, 0.759271), (-0.169495, -0.140056, 0.66311), (-0.168732, -0.193729, 0.687691)],
        [(-0.168732, -0.193729, 0.687691), (-0.169495, -0.140056, 0.66311), (-0.192698, -0.139645, 0.66311), (-0.191936, -0.193318, 0.687691)],
        [(-0.193098, -0.111516, 0.759271), (-0.192698, -0.139645, 0.66311), (-0.191936, -0.193318, 0.687691), (-0.192336, -0.165189, 0.783852)],
        [(-0.169894, -0.111928, 0.759271), (-0.170897, -0.0413197, 1.00065), (-0.227379, -0.0403189, 1.00065), (-0.193098, -0.111516, 0.759271)],
        [(-0.226809, -0.0804746, 1.06244), (-0.170327, -0.0814754, 1.06244), (-0.169132, -0.1656, 0.783852), (-0.192336, -0.165189, 0.783852)],
        [(-0.169894, -0.111928, 0.759271), (-0.170897, -0.0413197, 1.00065), (-0.170327, -0.0814754, 1.06244), (-0.169132, -0.1656, 0.783852)],
        [(-0.227379, -0.0403189, 1.00065), (-0.227379, -0.0403189, 1.36994), (-0.226809, -0.0804746, 1.06244)],
        [(-0.22836, 0.028691, 1.36994), (-0.227379, -0.0403189, 1.36994), (-0.22836, 0.028691, 1.30002)],
        [(-0.227379, -0.0403189, 1.36994), (-0.22836, 0.028691, 1.30002), (-0.227379, -0.0403189, 1.00065)],
        [(-0.170327, -0.0814754, 1.06244), (-0.170897, -0.0413197, 1.36994), (-0.227379, -0.0403189, 1.36994), (-0.226809, -0.0804746, 1.06244)],
        [(-0.170897, -0.0413197, 1.00065), (-0.171878, 0.0276902, 1.30002), (-0.22836, 0.028691, 1.30002), (-0.227379, -0.0403189, 1.00065)],
        [(-0.22836, 0.028691, 1.36994), (-0.171878, 0.0276902, 1.36994), (-0.171878, 0.0276902, 1.30002), (-0.22836, 0.028691, 1.30002)],
        [(-0.22836, 0.028691, 1.36994), (-0.171878, 0.0276902, 1.36994), (-0.170897, -0.0413197, 1.36994), (-0.227379, -0.0403189, 1.36994)],
        [(-0.170327, -0.0814754, 1.06244), (-0.170897, -0.0413197, 1.36994), (-0.170897, -0.0413197, 1.00065)],
        [(-0.171878, 0.0276902, 1.30002), (-0.171878, 0.0276902, 0.791631), (-0.170897, -0.0413197, 0.791631), (-0.170897, -0.0413197, 1.00065)],
        [(-0.11609, -0.166736, 0.069916), (-0.11831, -0.0104408, 0.069916), (-0.11609, -0.166736, -1.43982e-16)],
        [(-0.11831, -0.0104408, 0.069916), (-0.119563, 0.0777126, -1.43982e-16), (-0.11609, -0.166736, -1.43982e-16)],
        [(-0.11831, -0.0104408, 0.069916), (-0.119563, 0.0777126, 0.373781), (-0.119563, 0.0777126, -1.43982e-16)],
        [(-0.119563, 0.0777126, 0.373781), (-0.11831, -0.0104408, 0.373781), (-0.11831, -0.0104408, 0.069916)],
        [(0.120645, -0.170931, -1.5786e-16), (0.118424, -0.0146354, 0.069916), (0.120645, -0.170931, 0.069916)],
        [(0.120645, -0.170931, -1.5786e-16), (0.117172, 0.073518, -1.5786e-16), (0.118424, -0.0146354, 0.069916)],
        [(0.118424, -0.0146354, 0.373781), (0.117172, 0.073518, 0.373781), (0.118424, -0.0146354, 0.069916)],
        [(0.118424, -0.0146354, 0.069916), (0.117172, 0.073518, 0.373781), (0.117172, 0.073518, -1.5786e-16)],
        [(-0.119563, 0.0777126, 0.373781), (-0.0230953, 0.0760034, 0.373781), (-0.0230953, 0.0760034, 0.069916), (-0.119563, 0.0777126, 0.069916)],
        [(-0.11831, -0.0104408, 0.069916), (-0.0218429, -0.0121501, 0.069916), (-0.0196224, -0.168445, 0.069916), (-0.11609, -0.166736, 0.069916)],
        [(-0.119563, 0.0777126, -1.43982e-16), (-0.0230953, 0.0760034, -1.43982e-16), (-0.0196224, -0.168445, -1.43982e-16), (-0.11609, -0.166736, -1.43982e-16)],
        [(-0.119563, 0.0777126, -1.43982e-16), (-0.0230953, 0.0760034, -1.43982e-16), (-0.0230953, 0.0760034, 0.069916), (-0.119563, 0.0777126, 0.069916)],
        [(-0.11609, -0.166736, 0.069916), (-0.0196224, -0.168445, 0.069916), (-0.0196224, -0.168445, -1.43982e-16), (-0.11609, -0.166736, -1.43982e-16)],
        [(0.117172, 0.073518, 0.069916), (0.0207045, 0.0752273, 0.069916), (0.0207045, 0.0752273, 0.373781), (0.117172, 0.073518, 0.373781)],
        [(0.118424, -0.0146354, 0.069916), (0.0219569, -0.0129262, 0.069916), (0.0241775, -0.169221, 0.069916), (0.120645, -0.170931, 0.069916)],
        [(0.120645, -0.170931, -1.5786e-16), (0.0241775, -0.169221, -1.5786e-16), (0.0207045, 0.0752273, -1.5786e-16), (0.117172, 0.073518, -1.5786e-16)],
        [(0.117172, 0.073518, 0.069916), (0.0207045, 0.0752273, 0.069916), (0.0207045, 0.0752273, -1.5786e-16), (0.117172, 0.073518, -1.5786e-16)],
        [(0.120645, -0.170931, -1.5786e-16), (0.0241775, -0.169221, -1.5786e-16), (0.0241775, -0.169221, 0.069916), (0.120645, -0.170931, 0.069916)],
        [(-0.0196224, -0.168445, 0.069916), (-0.0218429, -0.0121501, 0.069916), (-0.0196224, -0.168445, -1.43982e-16)],
        [(-0.0218429, -0.0121501, 0.069916), (-0.0230953, 0.0760034, -1.43982e-16), (-0.0196224, -0.168445, -1.43982e-16)],
        [(-0.0218429, -0.0121501, 0.373781), (-0.0230953, 0.0760034, 0.373781), (-0.0218429, -0.0121501, 0.069916)],
        [(-0.0230953, 0.0760034, 0.373781), (-0.0230953, 0.0760034, -1.43982e-16), (-0.0218429, -0.0121501, 0.069916)],
        [(0.0241775, -0.169221, -1.5786e-16), (0.0219569, -0.0129262, 0.069916), (0.0241775, -0.169221, 0.069916)],
        [(0.0241775, -0.169221, -1.5786e-16), (0.0207045, 0.0752273, -1.5786e-16), (0.0219569, -0.0129262, 0.069916)],
        [(0.0207045, 0.0752273, 0.373781), (0.0219569, -0.0129262, 0.069916), (0.0207045, 0.0752273, -1.5786e-16)],
        [(0.0207045, 0.0752273, 0.373781), (0.0219569, -0.0129262, 0.373781), (0.0219569, -0.0129262, 0.069916)],
        [(-0.11831, -0.0104408, 0.069916), (-0.0218429, -0.0121501, 0.069916), (-0.0218429, -0.0121501, 0.373781), (-0.11831, -0.0104408, 0.373781)],
        [(0.118424, -0.0146354, 0.373781), (0.0219569, -0.0129262, 0.373781), (0.0219569, -0.0129262, 0.069916), (0.118424, -0.0146354, 0.069916)],
        [(-0.037937, -0.0551831, 1.4881), (-0.0550476, -0.0213627, 1.4881), (-0.069135, -0.0319849, 1.4881)],
        [(-0.0708283, 0.0872035, 1.4881), (-0.0550476, -0.0213627, 1.4881), (-0.0565864, 0.0869511, 1.4881)],
        [(-0.069135, -0.0319849, 1.4881), (-0.0708283, 0.0872035, 1.4881), (-0.0550476, -0.0213627, 1.4881)],
        [(-0.037937, -0.0551831, 1.4881), (0.0554401, -0.0233204, 1.4881), (-0.0550476, -0.0213627, 1.4881)],
        [(0.0698365, -0.0344473, 1.4881), (0.0554401, -0.0233204, 1.4881), (0.0392822, -0.0565513, 1.4881)],
        [(0.0539013, 0.0849934, 1.4881), (0.0554401, -0.0233204, 1.4881), (0.0681432, 0.084741, 1.4881)],
        [(0.0554401, -0.0233204, 1.4881), (0.0681432, 0.084741, 1.4881), (0.0698365, -0.0344473, 1.4881)],
        [(0.0392822, -0.0565513, 1.4881), (-0.037937, -0.0551831, 1.4881), (0.0554401, -0.0233204, 1.4881)],
        [(0.0698365, -0.0344473, 1.4881), (0.0698365, -0.0344473, 1.7), (0.0392822, -0.0565513, 1.63263), (0.0392822, -0.0565513, 1.4881)],
        [(-0.037937, -0.0551831, 1.4881), (-0.037937, -0.0551831, 1.63263), (-0.069135, -0.0319849, 1.7), (-0.069135, -0.0319849, 1.4881)],
        [(-0.0708283, 0.0872035, 1.7), (-0.069135, -0.0319849, 1.7), (0.0698365, -0.0344473, 1.7), (0.0681432, 0.084741, 1.7)],
        [(0.0392822, -0.0565513, 1.63263), (-0.037937, -0.0551831, 1.63263), (-0.037937, -0.0551831, 1.4881), (0.0392822, -0.0565513, 1.4881)],
        [(0.0392822, -0.0565513, 1.63263), (-0.037937, -0.0551831, 1.63263), (-0.069135, -0.0319849, 1.7), (0.0698365, -0.0344473, 1.7)],
        [(-0.069135, -0.0319849, 1.7), (-0.071316, 0.12153, 1.62091), (-0.069135, -0.0319849, 1.4881)],
        [(-0.069135, -0.0319849, 1.4881), (-0.0708283, 0.0872035, 1.4881), (-0.071316, 0.12153, 1.62091)],
        [(-0.071316, 0.12153, 1.62091), (-0.0708283, 0.0872035, 1.7), (-0.069135, -0.0319849, 1.7)],
        [(0.0698365, -0.0344473, 1.7), (0.0676555, 0.119067, 1.62091), (0.0698365, -0.0344473, 1.4881)],
        [(0.0698365, -0.0344473, 1.4881), (0.0681432, 0.084741, 1.4881), (0.0676555, 0.119067, 1.62091)],
        [(0.0676555, 0.119067, 1.62091), (0.0681432, 0.084741, 1.7), (0.0698365, -0.0344473, 1.7)],
        [(-0.0708283, 0.0872035, 1.7), (-0.071316, 0.12153, 1.62091), (0.0676555, 0.119067, 1.62091), (0.0681432, 0.084741, 1.7)],
        [(-0.0708283, 0.0872035, 1.4881), (-0.071316, 0.12153, 1.62091), (0.0676555, 0.119067, 1.62091), (0.0681432, 0.084741, 1.4881)],
        [(-0.0550476, -0.0213627, 1.4881), (-0.0217036, -0.0219535, 1.41393), (-0.0550476, -0.0213627, 1.40694)],
        [(-0.0217036, -0.0219535, 1.41393), (0.0220962, -0.0227296, 1.41393), (-0.0550476, -0.0213627, 1.4881)],
        [(0.0554401, -0.0233204, 1.40694), (0.0220962, -0.0227296, 1.41393), (0.0554401, -0.0233204, 1.4881)],
        [(-0.0550476, -0.0213627, 1.4881), (0.0220962, -0.0227296, 1.41393), (0.0554401, -0.0233204, 1.4881)],
        [(0.0220962, -0.0227296, 1.41393), (0.0230087, -0.0869583, 1.36994), (-0.0207911, -0.0861823, 1.36994), (-0.0217036, -0.0219535, 1.41393)],
        [(0.0230087, -0.0869583, 1.36994), (-0.0207911, -0.0861823, 1.36994), (-0.0207911, -0.0861823, 0.791631), (0.0230087, -0.0869583, 0.791631)],
        [(-0.170897, -0.0413197, 1.36994), (-0.0207911, -0.0861823, 1.36994), (-0.0207911, -0.0861823, 0.791631), (-0.170897, -0.0413197, 0.791631)],
        [(-0.0550476, -0.0213627, 1.40694), (-0.0207911, -0.0861823, 1.36994), (-0.0217036, -0.0219535, 1.41393)],
        [(-0.0550476, -0.0213627, 1.40694), (-0.170897, -0.0413197, 1.36994), (-0.0552309, -0.00845877, 1.41577)],
        [(-0.0207911, -0.0861823, 1.36994), (-0.0550476, -0.0213627, 1.40694), (-0.170897, -0.0413197, 1.36994)],
        [(0.0554401, -0.0233204, 1.40694), (0.0230087, -0.0869583, 1.36994), (0.0220962, -0.0227296, 1.41393)],
        [(0.0552568, -0.0104165, 1.41577), (0.0554401, -0.0233204, 1.40694), (0.171916, -0.047394, 1.36994)],
        [(0.0230087, -0.0869583, 1.36994), (0.0554401, -0.0233204, 1.40694), (0.171916, -0.047394, 1.36994)],
        [(0.0198005, 0.138854, 1.36994), (-0.0239993, 0.13963, 1.36994), (-0.0239993, 0.13963, 0.791631), (0.0198005, 0.138854, 0.791631)],
        [(-0.171878, 0.0276902, 1.36994), (-0.171878, 0.0276902, 0.791631), (-0.0239993, 0.13963, 0.791631), (-0.0239993, 0.13963, 1.36994)],
        [(-0.0565864, 0.0869511, 1.4881), (-0.0565864, 0.0869511, 1.39853), (0.0539013, 0.0849934, 1.39853), (0.0539013, 0.0849934, 1.4881)],
        [(-0.0550476, -0.0213627, 1.4881), (-0.0552309, -0.00845877, 1.41577), (-0.0550476, -0.0213627, 1.40694)],
        [(-0.0550476, -0.0213627, 1.4881), (-0.0557152, 0.0256319, 1.41773), (-0.0552309, -0.00845877, 1.41577)],
        [(-0.0565864, 0.0869511, 1.39853), (-0.0557152, 0.0256319, 1.41773), (-0.0565864, 0.0869511, 1.4881)],
        [(-0.0550476, -0.0213627, 1.4881), (-0.0565864, 0.0869511, 1.4881), (-0.0557152, 0.0256319, 1.41773)],
        [(-0.0239993, 0.13963, 1.36994), (-0.0565864, 0.0869511, 1.39853), (0.0539013, 0.0849934, 1.39853), (0.0198005, 0.138854, 1.36994)],
        [(-0.170897, -0.0413197, 0.791631), (-0.11831, -0.0104408, 0.373781), (-0.119563, 0.0777126, 0.373781), (-0.171878, 0.0276902, 0.791631)],
        [(-0.170897, -0.0413197, 0.791631), (-0.11831, -0.0104408, 0.373781), (-0.0207911, -0.0861823, 0.791631)],
        [(-0.11831, -0.0104408, 0.373781), (-0.0207911, -0.0861823, 0.791631), (-0.0218429, -0.0121501, 0.373781)],
        [(-0.0230953, 0.0760034, 0.373781), (-0.0239993, 0.13963, 0.791631), (-0.119563, 0.0777126, 0.373781)],
        [(-0.0239993, 0.13963, 0.791631), (-0.119563, 0.0777126, 0.373781), (-0.171878, 0.0276902, 0.791631)],
        [(-0.0230953, 0.0760034, 0.373781), (-0.0239993, 0.13963, 0.791631), (-0.0207911, -0.0861823, 0.791631), (-0.0218429, -0.0121501, 0.373781)],
        [(0.171916, -0.047394, 0.791631), (0.118424, -0.0146354, 0.373781), (0.117172, 0.073518, 0.373781), (0.170935, 0.0216159, 0.791631)],
        [(0.171916, -0.047394, 0.791631), (0.118424, -0.0146354, 0.373781), (0.0230087, -0.0869583, 0.791631)],
        [(0.118424, -0.0146354, 0.373781), (0.0230087, -0.0869583, 0.791631), (0.0219569, -0.0129262, 0.373781)],
        [(0.0207045, 0.0752273, 0.373781), (0.0198005, 0.138854, 0.791631), (0.117172, 0.073518, 0.373781)],
        [(0.0198005, 0.138854, 0.791631), (0.117172, 0.073518, 0.373781), (0.170935, 0.0216159, 0.791631)],
        [(0.0207045, 0.0752273, 0.373781), (0.0198005, 0.138854, 0.791631), (0.0230087, -0.0869583, 0.791631), (0.0219569, -0.0129262, 0.373781)],
        [(0.0230087, -0.0869583, 0.791631), (0.0198005, 0.138854, 0.791631), (-0.0239993, 0.13963, 0.791631), (-0.0207911, -0.0861823, 0.791631)],
        [(-0.0565864, 0.0869511, 1.39853), (-0.171878, 0.0276902, 1.36994), (-0.0557152, 0.0256319, 1.41773)],
        [(-0.0239993, 0.13963, 1.36994), (-0.0565864, 0.0869511, 1.39853), (-0.171878, 0.0276902, 1.36994)],
        [(0.0539013, 0.0849934, 1.39853), (0.170935, 0.0216159, 1.36994), (0.0547724, 0.0236742, 1.41773)],
        [(0.0198005, 0.138854, 1.36994), (0.0539013, 0.0849934, 1.39853), (0.170935, 0.0216159, 1.36994)],
        [(0.0554401, -0.0233204, 1.40694), (0.0552568, -0.0104165, 1.41577), (0.0554401, -0.0233204, 1.4881)],
        [(0.0552568, -0.0104165, 1.41577), (0.0547724, 0.0236742, 1.41773), (0.0554401, -0.0233204, 1.4881)],
        [(0.0539013, 0.0849934, 1.4881), (0.0547724, 0.0236742, 1.41773), (0.0539013, 0.0849934, 1.39853)],
        [(0.0547724, 0.0236742, 1.41773), (0.0539013, 0.0849934, 1.4881), (0.0554401, -0.0233204, 1.4881)],
        [(-0.170897, -0.0413197, 1.36994), (-0.0557152, 0.0256319, 1.41773), (-0.0552309, -0.00845877, 1.41577)],
        [(-0.171878, 0.0276902, 1.36994), (-0.0557152, 0.0256319, 1.41773), (-0.170897, -0.0413197, 1.36994)],
        [(0.0552568, -0.0104165, 1.41577), (0.0547724, 0.0236742, 1.41773), (0.171916, -0.047394, 1.36994)],
        [(0.170935, 0.0216159, 1.36994), (0.0547724, 0.0236742, 1.41773), (0.171916, -0.047394, 1.36994)]]
        
        return standingData

class WindSpeed(object):
    
    def readTerrainType(self, terrainType):
        checkData = True
        roughLength = None
        
        if round(terrainType, 1) == 3.0 or terrainType == "water":
            print "Terrain set to water."
            d = 210
            a = 0.10
        elif round(terrainType, 1) == 2.0 or terrainType == "country":
            print "Terrain set to country."
            d = 270
            a = 0.14
        elif round(terrainType, 1) == 1.0 or terrainType == "suburban":
            print "Terrain set to suburban."
            d = 370
            a = 0.22
        elif round(terrainType, 1) == 0.0 or terrainType == "urban":
            print "Terrain set to urban."
            d = 460
            a = 0.33
        else:
            d = None
            a = None
            checkData = False
        
        return checkData, d, a
    
    def calcWindSpeedBasedOnHeight(self, vMet, height, d, a):
        #Calculate the wind speed.
        vHeight = ((height / d) ** a) * (vMet * (270 / 10) ** 0.14)
        
        return vHeight


try:
    checkIn.checkForUpdates(LB= True, HB= False, OpenStudio = False, template = False)
except:
    # no internet connection
    pass

now = datetime.datetime.now()

def checkGHPythonVersion(target = "0.6.0.3"):
    
    currentVersion = int(ghenv.Version.ToString().replace(".", ""))
    targetVersion = int(target.replace(".", ""))
    
    if targetVersion > currentVersion: return False
    else: return True

GHPythonTargetVersion = "0.6.0.3"

if not checkGHPythonVersion(GHPythonTargetVersion):
    msg =  "Ladybug failed to fly! :(\n" + \
           "You are using an old version of GHPython. " +\
           "Please update to version: " + GHPythonTargetVersion
    print msg
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    letItFly = False
    sc.sticky["ladybug_release"] = False

if letItFly:
    # let's just overwrite it every time
    #if not sc.sticky.has_key("ladybug_release"):
    sc.sticky["ladybug_release"] = versionCheck()       
    sc.sticky["ladybug_Preparation"] = Preparation
    sc.sticky["ladybug_Mesh"] = MeshPreparation
    sc.sticky["ladybug_RunAnalysis"] = RunAnalysisInsideGH
    sc.sticky["ladybug_Export2Radiance"] = ExportAnalysis2Radiance
    sc.sticky["ladybug_ResultVisualization"] = ResultVisualization
    sc.sticky["ladybug_SunPath"] = Sunpath
    sc.sticky["ladybug_SkyColor"] = Sky
    sc.sticky["ladybug_Vector"] = Vector
    sc.sticky["ladybug_ComfortModels"] = ComfortModels
    sc.sticky["ladybug_WindSpeed"] = WindSpeed
        
if sc.sticky.has_key("ladybug_release") and sc.sticky["ladybug_release"]:
    print "Hi " + os.getenv("USERNAME")+ "!\n" + \
          "Ladybug is Flying! Vviiiiiiizzz...\n\n" + \
          "Default path is set to: " + sc.sticky["Ladybug_DefaultFolder"]
