# this script is based on RADIANCE sun.c script
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to make a 3D sun-path (aka. sun plot) in the Rhino scene.  The component also outputs sun vectors that can be used for sunlight hours analysis or shading design with the other Ladybug components.
The sun-path function used here is a Python version of the RADIANCE sun-path script by Greg Ward. The RADIANCE source code can be accessed at:
http://www.radiance-online.org/download-install/CVS%20source%20code

-
Provided by Ladybug 0.0.59
    
    Args:
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _location: The output from the importEPW or constructLocation component.  This is essentially a list of text summarizing a location on the earth.
        ---------------- : ...
        _hour_: A number between 1 and 24 (or a list of numbers) that represent hour(s) of the day to position sun sphere(s) on the sun path.  The default is 12, which signifies 12:00 PM.
        _day_: A number between 1 and 31 (or a list of numbers) that represent days(s) of the month to position sun sphere(s) on the sun path.  The default is 21, which signifies the 21st of the month (when solstices and equinoxes occur).
        _month_: A number between 1 and 12 (or a list of numbers) that represent months(s) of the year to position sun sphere(s) on the sun path.  The default is 12, which signifies December.
        _timeStep_: The number of timesteps per hour in the sun path. This number should be smaller than 60 and divisible by 60. The default is set to 1 such that one sun sphere and one sun vector is generated for each hour.
                  Note that a linear interpolation will be used to generate curves and suns for timeSteps greater than 1.
        analysisPeriod_: An optional analysis period from the Analysis Period component.  Inputs here will override the hour, day, and month inputs above.
        ---------------- : ...
        _centerPt_: Input a point here to change the location of the sun path in the Rhino scene.  The default is set to the Rhino model origin (0,0,0).
        _sunPathScale_: Input a number here to change the scale of the sun path.  The default is set to 1.
        _sunScale_: Input a number here to change the scale of the sun spheres located along the sun path.  The default is set to 1.
        ---------------- : ...
        annualHourlyData_: An optional list of hourly data from the Import epw component, which will be used to color the sun spheres of the sun path (e.g. dryBulbTemperature).
        conditionalStatement_: This input allows users to remove data that does not fit specific conditions or criteria from the sun path. To use this input correctly, hourly data, such as temperature or humidity, must be plugged into the annualHourlyData_ input. The conditional statement input here should be a valid condition statement in Python, such as "a>25" or "b<80" (without quotation marks).
                              The current version of this component accepts "and" and "or" operators. To visualize the hourly data, only lowercase English letters should be used as variables, and each letter alphabetically corresponds to each of the lists (in their respective order): "a" always represents the 1st list, "b" always represents the 2nd list, etc.
                              For example, if you have hourly dry bulb temperature connected as the first list, and relative humidity connected as the second list (both to the annualHourlyData_ input), and you want to plot the data for the time period when temperature is between 18C and 23C, and humidity is less than 80%, the conditional statement should be written as 18<a<23 and b<80 (without quotation marks).
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        ---------------- : ...
        _dailyOrAnnualSunPath_: By default, this value is set to "True" (or 1), which will produce a sun path for the whole year.  Set this input to "False" (or 0) to generate a sun path for just one day of the year (or several days if multiple days are included in the analysis period).
        solarOrStandardTime_: Set to 'True' to have the sunPath display in solar time and set to 'False' to have it display in standard time.  The default is set to 'False.'  Note that this input only changes the way in which the supath curves are drawn currently and does not yet change the position of the sun based on the input hour.
        bakeIt_: Set to True to bake the sunpath into the Rhino scene.
    Returns:
        readMe!: ...
        sunVectors: Vector(s) indicating the direction of sunlight for each sun position on the sun path. 
        sunAltitudes: Number(s) indicating the sun altitude(s) in degrees for each sun position on the sun path.
        sunAzimuths: Number(s) indicating the sun azimuths in degrees for each sun position on the sun path.
        --------------: ...
        sunSpheresMesh: A colored mesh of spheres representing sun positions.  Colors indicate annualHourlyData_ and will be yellow if no data is hooked up to annualHourlyData_.
        sunPathCrvs:  A set of guide curves that mark the path of the sun across the sky dome.
        legend: A legend for the sun path. Connect this output to a grasshopper "Geo" component in order to preview the legend separately in the Rhino scene.  
        legendBasePts: The legend base point(s), which can be used to move the legend(s) in relation to the sun path with the grasshopper "move" component.
        --------------: ...
        sunPathCenPts: The center point of the sun path (or sun paths if multiple annualHourlyData_ streams are connected).  Use this to move sun paths around in the Rhino scene with the grasshopper "move" component.
        sunPositions: Point(s) idicating the location on the sun path of each sun position.
        sunPositionsInfo: Detailied information for each sun position on the sun path including date and time.
        sunPositionsHOY: The hour of the year for each sun position on the sun path.
        selHourlyData: The annualHourlyData_ for each sun position on the sun path. Note that this data has the following removed from it: 1) Any parts of the annualHourlyData_ that happen when the sun is down, 2) annualHourlyData_ that is not apart of the analysisPeriod_ and, 3) annualHourlyData_ that does not fit the conditional statement.
"""

ghenv.Component.Name = "Ladybug_SunPath"
ghenv.Component.NickName = 'sunPath'
ghenv.Component.Message = 'VER 0.0.59\nJUN_24_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import math
import System
import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
from clr import AddReference
AddReference ('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

def checkConditionalStatement(annualHourlyData, conditionalStatement):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        indexList, listInfo = lb_preparation.separateList(annualHourlyData, lb_preparation.strToBeFound)
        
        letters = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
        # remove 'and' and 'or' from conditional statements
        csCleaned = conditionalStatement.replace('and', '',20000)
        csCleaned = csCleaned.replace('or', '',20000)
        
        # find the number of the lists that have assigned conditional statements
        listNum = []
        for count, let in enumerate(letters):
            if csCleaned.find(let)!= -1: listNum.append(count)
        
        # check if all the conditions are actually applicable
        for num in listNum:
            if num>len(listInfo) - 1:
                warning = 'A conditional statement is assigned for list number ' + `num + 1` + '  which is not existed!\n' + \
                          'Please remove the letter "' + letters[num] + '" from the statements to solve this problem!\n' + \
                          'Number of lists are ' + `len(listInfo)` + '. Please fix this issue and try again.'
                          
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1, -1
        
        selList = []
        [selList.append([]) for i in range(len(listInfo))]
        for i in range(len(listInfo)):
            selList[i] = annualHourlyData[indexList[i]+7:indexList[i+1]]
            if listInfo[i][4]!='Hourly' or listInfo[i][5]!=(1,1,1) or  listInfo[i][6]!=(12,31,24) or len(selList[i])!=8760:
                warning = 'At least one of the input data lists is not a valid ladybug hourly data! Please fix this issue and try again!\n List number = '+ `i+1`
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1, -1
        
        # replace the right list in the conditional statement
        statement = conditionalStatement.split(' ')
        finalStatement = 'pattern = '
        titleStatement = '...                         ...                         ...\n' +\
                         'Conditional Selection Applied:\n'
        
        for statemntPart in statement:
            statementCopy = str.Copy(statemntPart) # a copy to make a meaningful string
            
            if statemntPart!='and' and statemntPart!='or':
                for num in listNum:
                    toBeReplacedWith = 'selList[this][HOY]'.replace('this', `num`)
                    titleToBeReplacedWith = listInfo[num][2]
                    
                    statemntPart = statemntPart.replace(letters[num], toBeReplacedWith, 20000)
                    statementCopy = statementCopy.replace(letters[num], titleToBeReplacedWith, 20000)
                    if statementCopy.find(letters[num])!=-1: break
                    
                titleStatement = titleStatement + ' ' + statementCopy
            else:
                
                titleStatement = titleStatement + '\n' + statementCopy
            finalStatement = finalStatement + ' ' + statemntPart
        print titleStatement
        
        # check for the pattern
        patternList = []
        try:
            for HOY in range(8760):
                exec(finalStatement)
                patternList.append(pattern)
        except Exception,e:
            warning = 'There is an error in the conditional statement:\n' + `e`
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1, -1
        
        return titleStatement, patternList


def readLocation(location):
    solarTimeZonesPos = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180]
    locationStr = location.split('\n')
    newLocStr = ""
    #clean the idf file
    for line in locationStr:
        if '!' in line:
            line = line.split('!')[0]
            newLocStr  = newLocStr + line.replace(" ", "")
        else:
            newLocStr  = newLocStr + line
    
    newLocStr = newLocStr.replace(';', "")
    
    site, locationName, latitude, longitude, timeZone, elevation = newLocStr.split(',')
    
    
    if solarOrStandardTime_:
        if int(float(timeZone)) == 0: longitude = 0.0
        elif int(float(timeZone)) > 0: longitude = solarTimeZonesPos[int(float(timeZone))]
        elif int(float(timeZone)) < 0: longitude = -solarTimeZonesPos[-int(float(timeZone))]
    
    return float(latitude), float(longitude), float(timeZone), float(elevation)



def getHOYs(hours, days, months, timeStep, lb_preparation, method = 0):
    
    if method == 1: stDay, endDay = days
        
    numberOfDaysEachMonth = lb_preparation.numOfDaysEachMonth
    
    numOfHours = timeStep * len(hours) 
    
    if timeStep != 1:
        step = 1/timeStep
        hours = rs.frange(hours[0], hours[-1] + 1, step)
        
        # make sure hours are generated correctly
        if len(hours) > numOfHours:
            hours = hours[:numOfHours]
        elif len(hours) < numOfHours:
            newHour = hours[-1] + step
    
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
                days = range(1, lb_preparation.checkDay(endDay, m) + 1)
            else:
                #rest of the months
                days = range(1, numberOfDaysEachMonth[monthCount] + 1)
        
        for d in days:
            for h in hours:
                h = lb_preparation.checkHour(float(h))
                m  = lb_preparation.checkMonth(int(m))
                d = lb_preparation.checkDay(int(d), m)
                HOY = lb_preparation.date2Hour(m, d, h)
                if HOY not in HOYS: HOYS.append(HOY)
    
    return HOYS


def getHOYsBasedOnPeriod(analysisPeriod, timeStep, lb_preparation):
    
    stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, True, False)
    
    # print stMonth, stDay, stHour, endMonth, endDay, endHour
    
    if stMonth > endMonth:
        months = range(stMonth, 13) + range(1, endMonth + 1)
    else:
        months = range(stMonth, endMonth + 1)
    
    # end hour shouldn't be included
    hours  = range(stHour, endHour)
    
    days = stDay, endDay
    
    HOYS = getHOYs(hours, days, months, timeStep, lb_preparation, method = 1)
    
    return HOYS, months, days
    
    
def main(latitude, longitude, timeZone, elevation, north, hour, day, month, timeStep, analysisPeriod, centerPt, sunPathScale, sunScale, annualHourlyData, conditionalStatement, legendPar, dailyOrAnnualSunPath, bakeIt):
    if solarOrStandardTime_: solarOrStandardTime = solarOrStandardTime_
    else: solarOrStandardTime = False
    
    if dailyOrAnnualSunPath:
        dailySunPath, annualSunPath = False, True
    else:
        dailySunPath, annualSunPath = True, False
        
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        lb_sunpath = sc.sticky["ladybug_SunPath"]()
        
        conversionFac = lb_preparation.checkUnits()
        
        def colorSun(spheres, colors):
            sunS = rc.Geometry.Mesh()
            repeatedColors = []
            for j, sun in enumerate(spheres):
                for face in range(sun.Faces.Count):repeatedColors.append(colors[j])
                sunS.Append(sun)
            return lb_visualization.colorMesh(repeatedColors, sunS)

        def bakePlease(listInfo, sunsJoined, legendSrfs, legendText, textPt, legendFont, textSize, sunPathCrvs):
            # legendText = legendText + ('\n\n' + customHeading)
            studyLayerName = 'SUNPATH'
            try:
                layerName = listInfo[1]
                dataType = 'Hourly Data:' + listInfo[2]
            
            except:
                layerName = 'Latitude=' +`latitude`
                dataType = 'No Hourly Data'
            
            # check the study type
            newLayerIndex, l = lb_visualization.setupLayers(dataType, 'LADYBUG', layerName, studyLayerName)
            lb_visualization.bakeObjects(newLayerIndex, sunsJoined, legendSrfs, legendText, textPt, textSize, legendFont, sunPathCrvs)
        
        def movePointList(textPt, movingVector):
            for ptCount, pt in enumerate(textPt):
                ptLocation = rc.Geometry.Point(pt)
                ptLocation.Translate(movingVector) # move it to the right place
                textPt[ptCount] = rc.Geometry.Point3d(ptLocation.Location)
            return textPt

        def getAzimuth(sunVector, northVector):
            # this function is a temporary fix and should be removed
            # calculate azimuth based on sun vector
            newSunVector = rc.Geometry.Vector3d(sunVector)
            newSunVector.Reverse()
            
            return 360 - math.degrees(rc.Geometry.Vector3d.VectorAngle(northVector, newSunVector, rc.Geometry.Plane.WorldXY))
            
        # define sun positions based on altitude and azimuth [this one should have a bug]
        sunPositions = []; sunVectors = []; sunUpHours = []; sunSpheres = []
        sunAlt = []; sunAzm = []; sunPosInfo = []
        PI = math.pi;

        northAngle, northVector = lb_preparation.angle2north(north)
        
        cenPt = lb_preparation.getCenPt(centerPt)
        scale = lb_preparation.setScale(sunPathScale, conversionFac) * 200
        sunSc = lb_preparation.setScale(sunScale, conversionFac)* scale * conversionFac * 0.007
        
        try:
            timeStep = int(timeStep)
            if 60%timeStep!=0:
                validTimeSteps = [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60]
                stepDifference = []
                [stepDifference.append(abs(validTimeStep - timeStep)) for validTimeStep in validTimeSteps]
                timeStep = validTimeSteps[stepDifference.index(min(stepDifference))]
                print 'Time-step is set to ' + `timeStep`
        except: timeStep = 1; print 'Time-step is set to 1'
        
        if longitude!=None and timeZone != None:
            try: longitude = float(longitude); timeZone = float(timeZone)
            except: longitude = 0; timeZone = 0
        else: longitude = 0; timeZone = 0
        
        # check for analysisPeriod
        if len(analysisPeriod)!=0 and analysisPeriod[0]!=None:
            
            HOYs, months, days = getHOYsBasedOnPeriod(analysisPeriod, timeStep, lb_preparation)
            
        else:
            days = day
            months = month
            hours = hour
            
            HOYs = getHOYs(hours, days, months, timeStep, lb_preparation)
        
        if latitude!=None:
            # check conditional statement for the whole year
            titleStatement = -1
            if conditionalStatement and len(annualHourlyData)!=0 and annualHourlyData[0]!=None:
                print 'Checking conditional statements...'
                # send all data and statement to a function and return back
                # True, False Pattern and condition statement
                titleStatement, patternList = checkConditionalStatement(annualHourlyData, conditionalStatement)
                
            if titleStatement == -1:
                patternList = [[True]] * 8760
                titleStatement = False

            printWarning = False
            if float(latitude) > 90: latitude = 90; printWarning = True
            elif float(latitude) < -90: latitude = -90; printWarning = True
                
            if printWarning == True:
                print 'Latitude should be between -90 and 90'
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, 'Latitude should be between -90 and 90')
            
            
            lb_sunpath.initTheClass(float(latitude), northAngle, cenPt, scale, longitude, timeZone)
            # count total sun up hours
            SUH = 0
            
            for HOY in HOYs:
                d, m, h = lb_preparation.hour2Date(HOY, True)
                m += 1
                lb_sunpath.solInitOutput(m, d, h, solarOrStandardTime)
                
                if lb_sunpath.solAlt >= 0: SUH += 1
                if lb_sunpath.solAlt >= 0 and patternList[int(round(lb_preparation.date2Hour(m, d, h)))]:
                    sunSphere, sunVector, sunPoint = lb_sunpath.sunPosPt(sunSc)
                    # find the hour of the year
                    sunUpHours.append(lb_preparation.date2Hour(m, d, h))
                    sunPosInfo.append(lb_preparation.hour2Date(lb_preparation.date2Hour(m, d, h)))
                    sunPositions.append(sunPoint)
                    sunSpheres.append(sunSphere)
                    sunVectors.append(sunVector)
                    sunAlt.append(math.degrees(lb_sunpath.solAlt))
                    #print math.degrees(lb_sunpath.angle2North)
                    solAz = getAzimuth(sunVector, northVector)
                    sunAzm.append(solAz)
            
            if len(sunVectors)== 0:
                if conditionalStatement!=None:
                    warning = 'None of the hours meet the conditional statement'
                else:
                    warning = 'Night time!'
                    
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            
            dailySunPathCrvs = []
            annualSunPathCrvs = []
            baseCrvs = []
            if annualSunPath!=False:
                annualSunPathCrvs = [item.ToNurbsCurve() for i,sublist in enumerate(lb_sunpath.drawSunPath(solarOrStandardTime)) for item in sublist if i < 2]
            if dailySunPath:
                dailySunPathCrvs = []
                for HOY in HOYs:
                    d, m, h = lb_preparation.hour2Date(HOY, True)
                    m += 1
                    dailySunPathCrvs.append(lb_sunpath.drawDailyPath(m, d).ToNurbsCurve())
            if annualSunPath or dailySunPath: baseCrvs = [rc.Geometry.Circle(cenPt, 1.08*scale).ToNurbsCurve()] #lb_sunpath.drawBaseLines()
        
            sunPathCrvs = []
            if annualSunPathCrvs: sunPathCrvs = sunPathCrvs + annualSunPathCrvs
            if dailySunPathCrvs: sunPathCrvs = sunPathCrvs + dailySunPathCrvs
            if baseCrvs: sunPathCrvs = sunPathCrvs + baseCrvs
            if sunPathCrvs!=[]: lb_visualization.calculateBB(sunPathCrvs, True)
            # sunPathCrvs = sunPathCrvs - baseCrvs
            overwriteScale = False
            if legendPar == []: overwriteScale = True
            elif legendPar[-1] == []: overwriteScale = True
            lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar, False)
            
            if overwriteScale: legendScale = 0.9
            
            
            
            legend = []; legendText = []; textPt = []; legendSrfs = None
            customHeading = '\n\n\n\nSun-Path Diagram - Latitude: ' + `latitude` + '\n'
            colors = [System.Drawing.Color.Yellow] * len(sunPositions)
            
            allSunPositions = []; allSunsJoined = []; allSunVectors = []
            allSunPathCrvs = []; allLegend = []; allValues = []
            allSunAlt = []; allSunAzm = []; cenPts = []; allSunPosInfo = []
            legendBasePoints = []
            
            # hourly data
            if len(annualHourlyData)!=0 and annualHourlyData[0]!=None:
                try: movingDist = 1.5 * lb_visualization.BoundingBoxPar[1] # moving distance for sky domes
                except: movingDist = 0
                
                #separate data
                indexList, listInfo = lb_preparation.separateList(annualHourlyData, lb_preparation.strToBeFound)
                
                for i in range(len(listInfo)):
                    movingVector = rc.Geometry.Vector3d(i * movingDist, 0, 0)
                    values= []
                    selList = [];
                    modifiedsunPosInfo = []
                    [selList.append(float(x)) for x in annualHourlyData[indexList[i]+7:indexList[i+1]]]
                    if listInfo[i][4]!='Hourly' or str(listInfo[i][5])!="(1, 1, 1)" or  str(listInfo[i][6])!="(12, 31, 24)" or len(selList)!=8760:
                        warning = 'At least one of the input data lists is not a valid ladybug hourly data! Please fix this issue and try again!\n List number = '+ `i+1`
                        print warning
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                        return -1
                    else:
                        listInfo[i][5] = (1,1,1)
                        listInfo[i][6] = (12,31,24)
                        #find the numbers
                        for h, hr in enumerate(sunUpHours):
                            value = selList[int(math.floor(hr))] + (selList[int(math.ceil(hr))] - selList[int(math.floor(hr))])* (hr - math.floor(hr))
                            values.append(value)
                            modifiedsunPosInfo.append(sunPosInfo[h] + '\n' + ("%.2f" % value) + ' ' + listInfo[i][3])
                    
                    if values!=[] and sunPathCrvs!=[]:
                        # mesh colors
                        colors = lb_visualization.gradientColor(values, lowB, highB, customColors)
                        
                        customHeading = '\n\n\n\nSun-Path Diagram - Latitude: ' + `latitude` + '\n'
                        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(values
                                , lowB, highB, numSeg, listInfo[i][3], lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold)
                        
                        # generate legend colors
                        legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
                        
                        # color legend surfaces
                        legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
                        
                        # list info should be provided in case there is no hourly input data
                        
                        if len(sunSpheres) == 1:
                            d, m, h = lb_preparation.hour2Date(HOYs[0], True)
                            m += 1
                            customHeading = customHeading + '\n' + lb_preparation.hour2Date(lb_preparation.date2Hour(m, d, h)) + \
                                           ', ALT = ' + ("%.2f" % sunAlt[0]) + ', AZM = ' + ("%.2f" % sunAzm[0]) + '\n'
                        elif len(months) == 1 and len(days) == 1:
                            customHeading = customHeading + '\n' + `days[0]` + ' ' + lb_preparation.monthList[months[0] -1] + '\n'
                        
                        customHeading = customHeading + 'Hourly Data: ' + listInfo[i][2] + ' (' + listInfo[i][3] + ')\n' + listInfo[i][1]
                        
                        if titleStatement:
                            resultStr = ("%.1f" % (len(values)/timeStep)) + ' hours of total ' + ("%.1f" % (SUH/timeStep)) + ' sun up hours' + \
                                        '(' + ("%.2f" % ((len(values)/timeStep)/(SUH/timeStep) * 100)) + '%).'
                            # print resultStr
                            customHeading = customHeading + '\n' + titleStatement + '\n' + resultStr
                        
                        titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo[i]], lb_visualization.BoundingBoxPar, legendScale, customHeading, True, legendFont, legendFontSize, legendBold)
                        
                        
                        legend = lb_visualization.openLegend([legendSrfs, [lb_preparation.flattenList(legendTextCrv + titleTextCurve)]])
                        
                        legendText.append(titleStr)
                        textPt.append(titlebasePt)
                        
                        sunsJoined = colorSun(sunSpheres, colors)
                        
                        ##
                        compassCrvs, compassTextPts, compassText = lb_visualization. compassCircle(cenPt, northVector, scale, range(0, 360, 30), 1.5*textSize)
                        numberCrvs = lb_visualization.text2srf(compassText, compassTextPts, 'Times New Romans', textSize/1.5, legendBold)
                        compassCrvs = compassCrvs + lb_preparation.flattenList(numberCrvs)
                    

                        # let's move it move it move it!
                        if legendScale>1: movingVector = legendScale * movingVector
                        sunsJoined.Translate(movingVector); allSunsJoined.append(sunsJoined)
                        
                        textPt = movePointList(textPt, movingVector)
                        
                        sunPosDup = []
                        [sunPosDup.append(pt) for pt in sunPositions]
                        allSunPositions.append(movePointList(sunPosDup, movingVector))
                        
                        newCenPt = movePointList([cenPt], movingVector)[0];
                        cenPts.append(newCenPt)
                        
                        if legendBasePoint == None:
                            nlegendBasePoint = lb_visualization.BoundingBoxPar[0]
                            movedLegendBasePoint = rc.Geometry.Point3d.Add(nlegendBasePoint, movingVector);
                        else:
                            movedLegendBasePoint = rc.Geometry.Point3d.Add(legendBasePoint, movingVector);
                            
                        legendBasePoints.append(movedLegendBasePoint)
                        
                        for crv in legendTextCrv:
                            for c in crv: c.Translate(movingVector)
                        for crv in titleTextCurve:
                            for c in crv: c.Translate(movingVector)
                        crvsTemp = []
                        for c in sunPathCrvs + compassCrvs:
                            cDuplicate = c.Duplicate()
                            cDuplicate.Translate(movingVector)
                            crvsTemp.append(cDuplicate)
                        allSunPathCrvs.append(crvsTemp)
                        
                        legendSrfs.Translate(movingVector)
                        allLegend.append(lb_visualization.openLegend([legendSrfs, [lb_preparation.flattenList(legendTextCrv + titleTextCurve)]]))
                        
                        allSunPosInfo.append(modifiedsunPosInfo)
                        allValues.append(values)
                        
                        if bakeIt: bakePlease(listInfo[i], sunsJoined, legendSrfs, legendText, textPt, legendFont, textSize, crvsTemp)
            
                return allSunPositions, allSunsJoined, sunVectors, allSunPathCrvs, allLegend, allValues, sunAlt, sunAzm, cenPts, allSunPosInfo, legendBasePoints, [sunUpHours]
            
            # no hourly data tp overlay
            elif dailySunPath or annualSunPath:
                values = []
                if len(sunSpheres) == 1:
                    d, m, h = lb_preparation.hour2Date(HOYs[0], True)
                    m += 1
                    
                    customHeading = customHeading + '\n' + lb_preparation.hour2Date(lb_preparation.date2Hour(m, d, h)) + \
                                   ', ALT = ' + ("%.2f" % sunAlt[0]) + ', AZM = ' + ("%.2f" % sunAzm[0]) + '\n'
                elif len(months) == 1 and len(days) == 1:
                    #h = lb_preparation.checkHour(float(h))
                    m  = lb_preparation.checkMonth(int(months[0]))
                    d = lb_preparation.checkDay(int(days[0]), m)
                    customHeading = customHeading + '\n' + `d` + ' ' + lb_preparation.monthList[ m -1]
                    
                textSize = legendScale * 0.5 * lb_visualization.BoundingBoxPar[2]/20
                titlebasePt = lb_visualization.BoundingBoxPar[-2]
                titleTextCurve = lb_visualization.text2srf(['\n\n' + customHeading], [titlebasePt], 'Veranda', textSize, legendBold)
                legend = None, lb_preparation.flattenList(titleTextCurve)
                
                legendText.append('\n\n' + customHeading)
                textPt.append(titlebasePt)
                sunsJoined = colorSun(sunSpheres, colors)
                
                compassCrvs, compassTextPts, compassText = lb_visualization. compassCircle(cenPt, northVector, scale, range(0, 360, 30), 1.5*textSize)
                numberCrvs = lb_visualization.text2srf(compassText, compassTextPts, 'Times New Romans', textSize/1.5, legendBold)
                compassCrvs = compassCrvs + lb_preparation.flattenList(numberCrvs)
                
                if bakeIt: bakePlease(None, sunsJoined, legendSrfs, legendText, textPt, legendFont, textSize, sunPathCrvs + compassCrvs)
                
            else: return -1
                
            return [sunPositions], [sunsJoined], sunVectors, [sunPathCrvs + compassCrvs], [legend], [values], sunAlt, sunAzm, [cenPt], [sunPosInfo], [titlebasePt], [sunUpHours]
        
        else:
            print 'Please input a number for Latitude'
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Please input a number for Latitude")
            return -1
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1
        

if _location:
    latitude, longitude, timeZone, elevation = readLocation(_location)
    result = main(latitude, longitude, timeZone, elevation, north_, _hour_, _day_,
                  _month_, _timeStep_, analysisPeriod_, _centerPt_, _sunPathScale_,
                  _sunScale_, annualHourlyData_, conditionalStatement_, legendPar_,
                  _dailyOrAnnualSunPath_, bakeIt_)

    if result!= -1:
        sunPositionsList, sunSpheres, sunVectors, sunPathCrvsList, legendCrvs, selHourlyDataList, sunAltitudes, sunAzimuths, centerPoints, sunPosInfoList,  legendBasePtList, sunPosHOY = result
        
        # graft the data
        # I added this at the last minute! There should be a cleaner way
        legend = DataTree[System.Object]()
        sunSpheresMesh = DataTree[System.Object]()
        sunPathCrvs = DataTree[System.Object]()
        selHourlyData = DataTree[System.Object]()
        sunPositions = DataTree[System.Object]()
        sunPathCenPts = DataTree[System.Object]()
        sunPositionsInfo = DataTree[System.Object]()
        sunPositionsHOY = DataTree[System.Object]()
        legendBasePts = DataTree[System.Object]()
        for i, leg in enumerate(legendCrvs):
            p = GH_Path(i)
            legend.Add(leg[0], p)
            legend.AddRange(leg[1], p)
            sunSpheresMesh.Add(sunSpheres[i],p)
            sunPathCrvs.AddRange(sunPathCrvsList[i],p)
            selHourlyData.AddRange(selHourlyDataList[i],p)
            sunPositions.AddRange(sunPositionsList[i],p)
            sunPathCenPts.Add(centerPoints[i],p)
            sunPositionsInfo.AddRange(sunPosInfoList[i], p)
            sunPositionsHOY.AddRange(sunPosHOY[0], p)
            legendBasePts.Add(legendBasePtList[i],p)
        
        # hide preview of sunCnterpoints and legendBasePts
        ghenv.Component.Params.Output[8].Hidden = True      #legend base point
        ghenv.Component.Params.Output[10].Hidden = True     #sunPath center
        ghenv.Component.Params.Output[11].Hidden = True     #sun position
    else:
        pass
else:
    print "You need to provide the location data."
