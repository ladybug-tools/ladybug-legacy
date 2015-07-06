# Adaptive Comfort Chart
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2015, Chris Mackey <Chris@MackeyArchitecture.com> 
# Ladybug is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Ladybug is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to calculate the adaptive comfort for a given set of input conditions.
This component will output a stream of 0's and 1's indicating whether certain conditions are comfortable given the prevailing mean monthly temperature that ocuppants tend to adapt themselves to.
This component will also output a series of interger numbers that indicate the following: -1 = The average monthly temperature is too extreme for the adaptive model. 0 = The input conditions are too cold for occupants. 1 = The input conditions are comfortable for occupants. 2 = The input conditions are too hot for occupants.
Lastly, this component outputs the percent of time comfortable, hot, cold and monthly extreme as well as a lit of numbers indicating the upper temperature of comfort and lower temperature of comfort.
_
The adaptive comfort model was created in response to the shortcomings of the PMV model that became apparent when it was applied to buildings without air conditioning.  Namely, the PMV model was over-estimating the discomfort of occupants in warm conditions of nautrally ventilated buildings.
Accordingly, the adaptive comfort model was built on the work of hundreds of field studies in which people in naturally ventilated buildings were asked asked about how comfortable they were.
Results showed that users tended to adapt themselves to the monthly mean temperature and would be comfortable in buildings so long as the building temperature remained around a value close to that monthly mean.  This situation held true so long as the monthly mean temperature remained above 10 C and below 33.5 C.
_
The comfort models that make this component possible were translated to python from a series of validated javascript comfort models coded at the Berkely Center for the Built Environment (CBE).  The Adaptive model used by both the CBE Tool and this component was originally published in ASHARAE 55.
Special thanks goes to the authors of the online CBE Thermal Comfort Tool who first coded the javascript: Hoyt Tyler, Schiavon Stefano, Piccioli Alberto, Moon Dustin, and Steinfeld Kyle. http://cbe.berkeley.edu/comforttool/
-
Provided by Ladybug 0.0.60
    
    Args:
        _dryBulbTemperature: A number representing the dry bulb temperature of the air in degrees Celcius.  This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the Import EPW component.
        meanRadiantTemperature_: A number representing the mean radiant temperature of the surrounding surfaces in degrees Celcius.  If no value is plugged in here, this component will assume that the mean radiant temperature is equal to air temperature value above.  This input can also accept a list of temperatures representing conditions at different times or the direct output of dryBulbTemperature from the Import EPW component.
        _prevailingOutdoorTemp: A number representing the average monthly outdoor temperature in degrees Celcius.  This average monthly outdoor temperature is the temperature that occupants in naturally ventilated buildings tend to adapt themselves to. For this reason, this input can also accept the direct output of dryBulbTemperature from the Import EPW component if houlry values for the full year are connected for the other inputs of this component.
        windSpeed_: A number representing the wind speed of the air in meters per second.  If no value is plugged in here, this component will assume a very low wind speed of 0.3 m/s, characteristic of most naturally ventilated buildings.  This input can also accept a list of wind speeds representing conditions at different times or the direct output of windSpeed from of the Import EPW component.
        ------------------------------: ...
        eightyPercentComfortable: Set to "True" to have the comfort standard be 80 percent of occupants comfortable and set to "False" to have the comfort standard be 90 percent of all occupants comfortable.  The default is set to "True" for 80 percent, which is what most members of the building industry aim for.  However some projects will occasionally use 90%.
        analysisPeriod_: An optional analysis period from the Analysis Period component.  If no Analysis period is given and epw data from the ImportEPW component has been connected, the analysis will be run for the enitre year.
        _runIt: Set to "True" to run the component and calculate the adaptive comfort metrics.
    Returns:
        readMe!: ...
        --------------------------: ...
        comfortableOrNot: A stream of 0's and 1's (or "False" and "True" values) indicating whether occupants are comfortable under the input conditions given the fact that these occupants tend to adapt themselves to the prevailing mean monthly temperature. 0 indicates that a person is not comfortable while 1 indicates that a person is comfortable.
        degreesFromTarget: A stream of temperature values in degrees Celcius indicating how far from the target temperature the conditions of the people are.  Positive values indicate conditions hotter than the target temperature while negative values indicate degrees below the target temperture.
        comfPercentOfTime: The percent of the input data for which the occupants are comfortable.  Comfortable conditions are when the indoor temperature is within the comfort range determined by the prevailing outdoor temperature.
        --------------------------: ...
        chartCurvesAndTxt: The chart curves and text labels of the adaptive chart.
        adaptiveChartMesh: A colored mesh showing the number of input hours happen in each part of the adaptive chart.
        legend: A colored legend showing the number of hours that correspond to each color.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the chart with the grasshopper "move" component.
        comfortPolygons: A brep representing the range of comfort for.
        --------------------------: ...
        chartHourPoints: Points representing each of the hours of input temperature and opTemperity ratio.  By default, this ouput is hidden and, to see it, you should connect it to a Grasshopper preview component.

"""
ghenv.Component.Name = "Ladybug_Adaptive Comfort Chart"
ghenv.Component.NickName = 'AdaptiveChart'
ghenv.Component.Message = 'VER 0.0.60\nJUL_06_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | WIP"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Grasshopper.Kernel as gh
import math
import scriptcontext as sc
import Rhino as rc
import System

w = gh.GH_RuntimeMessageLevel.Warning
tol = sc.doc.ModelAbsoluteTolerance


def checkTheInputs():
    #Define a value that will indicate whether someone has hooked up epw data.
    epwData = False
    epwStr = []
    
    #Define a function to duplicate data
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
    
    #Check lenth of the _dryBulbTemperature list and evaluate the contents.
    checkData1 = False
    airTemp = []
    airMultVal = False
    if len(_dryBulbTemperature) != 0:
        try:
            if "Temperature" in _dryBulbTemperature[2]:
                airTemp = _dryBulbTemperature[7:]
                checkData1 = True
                epwData = True
                epwStr = _dryBulbTemperature[0:7]
        except: pass
        if checkData1 == False:
            for item in _dryBulbTemperature:
                try:
                    airTemp.append(float(item))
                    checkData1 = True
                except: checkData1 = False
        if len(airTemp) > 1: airMultVal = True
        if checkData1 == False:
            warning = '_dryBulbTemperature input does not contain valid temperature values in degrees Celcius.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        print 'Connect a temperature in degrees celcius for _dryBulbTemperature'
    
    #Check lenth of the meanRadiantTemperature_ list and evaluate the contents.
    checkData2 = False
    radTemp = []
    radMultVal = False
    if len(meanRadiantTemperature_) != 0:
        try:
            if "Temperature" in meanRadiantTemperature_[2]:
                radTemp = meanRadiantTemperature_[7:]
                checkData2 = True
                epwData = True
                epwStr = meanRadiantTemperature_[0:7]
        except: pass
        if checkData2 == False:
            for item in meanRadiantTemperature_:
                try:
                    radTemp.append(float(item))
                    checkData2 = True
                except: checkData2 = False
        if len(radTemp) > 1: radMultVal = True
        if checkData2 == False:
            warning = 'meanRadiantTemperature_ input does not contain valid temperature values in degrees Celcius.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData2 = True
        radTemp = airTemp
        if len (radTemp) > 1: radMultVal = True
        print 'No value connected for meanRadiantTemperature_.  It will be assumed that the radiant temperature is the same as the air temperature.'
    
    #Check lenth of the _prevailingOutdoorTemp list and evaluate the contents.
    checkData3 = False
    prevailTemp = []
    prevailMultVal = False
    if len(_prevailingOutdoorTemp) != 0:
        if monthlyOrWeekly_ == False:
            try:
                if _prevailingOutdoorTemp[2] == 'Dry Bulb Temperature' and (len(airTemp) == 8760 or len(airTemp) == 1):
                    #Bin the temperature values by week.
                    prevailList = []
                    prevailWeek = []
                    weekCounter = 0
                    weekLength = 168
                    for hour in _prevailingOutdoorTemp[7:]:
                        if weekCounter < weekLength:
                            prevailWeek.append(hour)
                            weekCounter += 1
                        else:
                            weekCounter = 0
                            prevailList.append(prevailWeek)
                            prevailWeek = []
                    
                    #Average the weekly Temperatures.
                    for tempList in prevailList:
                        prevailTemp.extend(duplicateData([float(sum(tempList)/weekLength)], weekLength))
                    prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[8568:])/192)], 192))
                    
                    checkData3 = True
                    epwData = True
                    if epwStr == []:
                        epwStr = _prevailingOutdoorTemp[0:7]
            except: pass
            if checkData3 == False:
                for item in _prevailingOutdoorTemp:
                    try:
                        prevailTemp.append(float(item))
                        checkData3 = True
                    except: checkData3 = False
        else:
            try:
                if _prevailingOutdoorTemp[2] == 'Dry Bulb Temperature' and (len(airTemp) == 8760 or len(airTemp) == 1):
                    prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[7:751])/744)], 744))
                    prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[751:1423])/672)], 672))
                    prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[1423:2167])/744)], 744))
                    prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[2167:2887])/720)], 720))
                    prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[2887:3631])/744)], 744))
                    prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[3631:4351])/720)], 720))
                    prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[4351:5095])/744)], 744))
                    prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[5095:5839])/744)], 744))
                    prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[5839:6559])/720)], 720))
                    prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[6559:7303])/744)], 744))
                    prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[7303:8023])/720)], 720))
                    prevailTemp.extend(duplicateData([float(sum(_prevailingOutdoorTemp[8023:])/744)], 744))
                    checkData3 = True
                    epwData = True
                    if epwStr == []:
                        epwStr = _prevailingOutdoorTemp[0:7]
            except: pass
            if checkData3 == False:
                for item in _prevailingOutdoorTemp:
                    try:
                        prevailTemp.append(float(item))
                        checkData3 = True
                    except: checkData3 = False
        if len(prevailTemp) > 1: prevailMultVal = True
        if checkData3 == False:
            warning = '_prevailingOutdoorTemp input does not contain valid temperature values in degrees Celcius.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        print 'Connect a temperature in degrees celcius for _prevailingOutdoorTemp'
    
    #Check lenth of the windSpeed_ list and evaluate the contents.
    checkData4 = False
    windSpeed = []
    windMultVal = False
    nonPositive = True
    if len(windSpeed_) != 0:
        try:
            if windSpeed_[2] == 'Wind Speed':
                windSpeed = windSpeed_[7:]
                checkData4 = True
                epwData = True
                if epwStr == []:
                    epwStr = windSpeed_[0:7]
        except: pass
        if checkData4 == False:
            for item in windSpeed_:
                try:
                    if float(item) >= 0:
                        windSpeed.append(float(item))
                        checkData4 = True
                    else: nonPositive = False
                except: checkData4 = False
        if nonPositive == False: checkData4 = False
        if len(windSpeed) > 1: windMultVal = True
        if checkData4 == False:
            warning = 'windSpeed_ input does not contain valid wind speed in meters per second.  Note that wind speed must be positive.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData4 = True
        windSpeed = [0.05]
        print 'No value connected for windSpeed_.  It will be assumed that the wind speed is a low 0.05 m/s.'
    
    #Finally, for those lists of length greater than 1, check to make sure that they are all the same length.
    checkData5 = False
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True:
        if airMultVal == True or radMultVal == True or prevailMultVal == True or windMultVal == True:
            listLenCheck = []
            if airMultVal == True: listLenCheck.append(len(airTemp))
            if radMultVal == True: listLenCheck.append(len(radTemp))
            if prevailMultVal == True: listLenCheck.append(len(prevailTemp))
            if windMultVal == True: listLenCheck.append(len(windSpeed))
            
            if all(x == listLenCheck[0] for x in listLenCheck) == True:
                checkData5 = True
                calcLength = listLenCheck[0]
                
                if airMultVal == False: airTemp = duplicateData(airTemp, calcLength)
                if radMultVal == False: radTemp = duplicateData(radTemp, calcLength)
                if prevailMultVal == False: prevailTemp = duplicateData(prevailTemp, calcLength)
                if windMultVal == False: windSpeed = duplicateData(windSpeed, calcLength)
                
            else:
                calcLength = None
                warning = 'If you have put in lists with multiple values, the lengths of these lists must match across the parameters or you have a single value for a given parameter to be applied to all values in the list.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData5 = True
            calcLength = 1
    else:
        calcLength = 0
    
    #If all of the checkDatas have been good to go, let's give a final go ahead.
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True:
        checkData = True
    else:
        checkData = False
    
    #Let's return everything we need.
    return checkData, epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed

def outlineCurve(curve):
    try:
        offsetCrv = curve.Offset(rc.Geometry.Plane.WorldXY, 0.15, sc.doc.ModelAbsoluteTolerance, rc.Geometry.CurveOffsetCornerStyle.Sharp)[0]
        finalBrep = (rc.Geometry.Brep.CreatePlanarBreps([curve, offsetCrv])[0])
        if finalBrep.Edges.Count < 3:
            finalBrep = curve
    except:
        finalBrep = curve
        warning = "Creating an outline of one of the comfort or strategy curves failed.  Component will return a solid brep."
        print warning
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    return finalBrep


def drawAdaptChart(prevailTemp, legendFont, legendFontSize, legendBold, epwData, epwStr, lb_visualization, lb_comfortModels):
    #Define lists to be filled.
    chartCrvAndText = []
    comfortPolygons = []
    
    #Set a default Offset.
    if eightyPercentComfortable_: offset = 3.5
    else: offset = 2.5
    
    #Set a default text height if the user has not provided one.
    if legendFontSize == None:
        legendFontSize = 0.6
    
    #Check to see if any of the prevailing outdoor temperatures are below 10 C.
    belowTen = False
    for number in prevailTemp:
        if number < 10: belowTen = True
    
    #Generate a list of temperatures that will be used to make the chart lines.
    if belowTen == False:
        tempNum = range(10, 40, 2)
        prevailTempNum = range(10, 33, 2)
        boundRect = rc.Geometry.Rectangle3d(rc.Geometry.Plane(rc.Geometry.Point3d(10, 10, 0), rc.Geometry.Vector3d.ZAxis), 23, 30)
    else:
        tempNum = range(0, 40, 2)
        prevailTempNum = range(-20, 33, 2)
        boundRect = rc.Geometry.Rectangle3d(rc.Geometry.Plane(rc.Geometry.Point3d(-20, 0, 0), rc.Geometry.Vector3d.ZAxis), 53, 40)
    boundRect = boundRect.ToPolyline()
    chartCrvAndText.append(boundRect)
    
    #Use the dry bulb temperatures to create coordinates for the operative temp lines.
    tempNumLines = []
    tempLabelBasePts = []
    tempText = []
    for count in tempNum:
        if belowTen == False:
            point1 = rc.Geometry.Point3d(10, count, 0)
            tempLabelBasePts.append(rc.Geometry.Point3d(8.5, count-0.25, 0))
        else:
            point1 = rc.Geometry.Point3d(-20, count, 0)
            tempLabelBasePts.append(rc.Geometry.Point3d(-21.5, count-0.25, 0))
        point2 = rc.Geometry.Point3d(33, count, 0)
        
        tempLine = rc.Geometry.LineCurve(point1, point2)
        tempNumLines.append(tempLine)
        tempText.append(str(count))
    if belowTen == False: tempLabelBasePts.append(rc.Geometry.Point3d(8.5, 40, 0))
    else: tempLabelBasePts.append(rc.Geometry.Point3d(-21.5, 40, 0))
    tempText.append("40")
    
    #Use the dry bulb temperatures to create coordinates for the operative temp lines.
    prevailTempNumLines = []
    prevailLabelBasePts = []
    prevailText = []
    for count in prevailTempNum:
        if belowTen == False: point1 = rc.Geometry.Point3d(count, 10, 0)
        else: point1 = rc.Geometry.Point3d(count, 0, 0)
        point2 = rc.Geometry.Point3d(count, 40, 0)
        
        tempLine = rc.Geometry.LineCurve(point1, point2)
        prevailTempNumLines.append(tempLine)
        
        prevailLabelBasePts.append(rc.Geometry.Point3d(point1.X-(legendFontSize*.75), point1.Y-(legendFontSize*2), 0))
        prevailText.append(str(count))
    
    #Get the values to draw the adaptive comfort polygon.
    prevailOutBases = [10, 33]
    opTempBases = []
    opTempMax = []
    opTempMin = []
    for startTemp in prevailOutBases:
        comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortASH55(20, 20, startTemp, 0.0, eightyPercentComfortable_)
        
        if levelOfConditioning_ and levelOfConditioning_ != 0 and levelOfConditioning_ > 0 and levelOfConditioning_ <= 1:
            comfTemp2 = 0.09*startTemp + 22.6
            lowTemp2 = comfTemp2 - offset
            upTemp2 = comfTemp2 + offset
            comfTemp = comfTemp*(1-levelOfConditioning_) + comfTemp2*(levelOfConditioning_)
            lowTemp = lowTemp*(1-levelOfConditioning_) + lowTemp2*(levelOfConditioning_)
            upTemp = upTemp*(1-levelOfConditioning_) + upTemp2*(levelOfConditioning_)
        
        opTempBases.append(comfTemp)
        opTempMax.append(upTemp)
        opTempMin.append(lowTemp)
    
    #Draw the middle line of the comfort polygon.
    point1 = rc.Geometry.Point3d(prevailOutBases[0], opTempBases[0], 0)
    point2 = rc.Geometry.Point3d(prevailOutBases[1], opTempBases[1], 0)
    centerLine = rc.Geometry.LineCurve(point1, point2)
    comfortPolygons.append(centerLine)
    
    #Draw the comfort polygon.
    point1 = rc.Geometry.Point3d(prevailOutBases[0], opTempMin[0], 0)
    point2 = rc.Geometry.Point3d(prevailOutBases[0], opTempMax[0], 0)
    point3 = rc.Geometry.Point3d(prevailOutBases[1], opTempMax[1], 0)
    point4 = rc.Geometry.Point3d(prevailOutBases[1], opTempMin[1], 0)
    polygon = rc.Geometry.PolylineCurve([point1, point2, point3, point4, point1])
    finalComfBrep = outlineCurve(polygon)
    comfortPolygons.append(finalComfBrep)
    
    #If the temperatures are below 10C, draw the heated comfort polygon.
    if belowTen == True:
        if levelOfConditioning_ and levelOfConditioning_ != 0 and levelOfConditioning_ > 0 and levelOfConditioning_ <= 1:
            point1 = rc.Geometry.Point3d(prevailOutBases[0], opTempBases[0], 0)
            point2 = rc.Geometry.Point3d(-20, opTempBases[0], 0)
            centerLine = rc.Geometry.LineCurve(point1, point2)
            comfortPolygons.append(centerLine)
            
            point1 = rc.Geometry.Point3d(10, opTempMin[0], 0)
            point2 = rc.Geometry.Point3d(10, opTempMax[0], 0)
            point3 = rc.Geometry.Point3d(-20, opTempMax[0], 0)
            point4 = rc.Geometry.Point3d(-20, opTempMin[0], 0)
            polygon = rc.Geometry.PolylineCurve([point1, point4, point3, point2, point1])
            finalComfBrep = outlineCurve(polygon)
            comfortPolygons.append(finalComfBrep)
        else:
            coldPrevailTempVals = range(-20, 12, 2)
            coldNeutralTempPts = []
            coldUpTempPts = []
            coldLowTempPts = []
            
            for val in coldPrevailTempVals:
                Tn = 24.024 + (0.295*(val - 22.0)) * math.exp((-1)*(((val-22)/(33.941125))*((val-22)/(33.941125))))
                TnUp = Tn + offset
                TnLow = Tn - offset
                coldNeutralTempPts.append(rc.Geometry.Point3d(val, Tn, 0))
                coldUpTempPts.append(rc.Geometry.Point3d(val, TnUp, 0))
                coldLowTempPts.append(rc.Geometry.Point3d(val, TnLow, 0))
            
            neurtalCold = rc.Geometry.Curve.CreateInterpolatedCurve(coldNeutralTempPts, 3)
            comfortPolygons.append(neurtalCold)
            
            upCold = rc.Geometry.Curve.CreateInterpolatedCurve(coldUpTempPts, 3)
            downCold = rc.Geometry.Curve.CreateInterpolatedCurve(coldLowTempPts, 3)
            lineRight = rc.Geometry.LineCurve(upCold.PointAtEnd, downCold.PointAtEnd)
            lineLeft = rc.Geometry.LineCurve(upCold.PointAtStart, downCold.PointAtStart)
            coldComfortPolygon = rc.Geometry.Curve.JoinCurves([upCold, lineRight, downCold, lineLeft], tol)[0]
            finalComfBrep = outlineCurve(coldComfortPolygon)
            comfortPolygons.append(finalComfBrep)
    
    # Make the temperature value text for the chart.
    tempLabels = []
    for count, text in enumerate(tempText):
        tempLabels.extend(lb_visualization.text2srf([text], [tempLabelBasePts[count]], legendFont, legendFontSize, legendBold)[0])
    prevailLabels = []
    for count, text in enumerate(prevailText):
        tempLabels.extend(lb_visualization.text2srf([text], [prevailLabelBasePts[count]], legendFont, legendFontSize, legendBold)[0])
    
    #Make axis labels for the chart.
    xAxisLabels = []
    xAxisTxt = ["Prevailing Outdoor Temperature (C)"]
    if belowTen == False: xAxisPt = [rc.Geometry.Point3d(12, 10 -(5*legendFontSize), 0)]
    else: xAxisPt = [rc.Geometry.Point3d(-3, -(5*legendFontSize), 0)]
    tempLabels.extend(lb_visualization.text2srf(xAxisTxt, xAxisPt, legendFont, legendFontSize*1.25, legendBold)[0])
    
    yAxisLabels = []
    yAxisTxt = ["Desired Indoor Operative Temperature (C)"]
    if belowTen == False:  yAxisPt = [rc.Geometry.Point3d(7, 14, 0)]
    else: yAxisPt = [rc.Geometry.Point3d(-23, 9, 0)]
    yAxisLabels.extend(lb_visualization.text2srf(yAxisTxt, yAxisPt, legendFont, legendFontSize*1.25, legendBold)[0])
    rotateTransf = rc.Geometry.Transform.Rotation(1.57079633, yAxisPt[0])
    for geo in yAxisLabels:
        geo.Transform(rotateTransf)
    tempLabels.extend(yAxisLabels)
    
    #Make the chart title.
    def getDateStr(start, end):
        stMonth, stDay, stHour, endMonth, endDay, endHour = lb_visualization.readRunPeriod((start, end), False)
        period = `stDay`+ ' ' + lb_visualization.monthList[stMonth-1] + ' ' + `stHour` + ':00' + \
                 " - " + `endDay`+ ' ' + lb_visualization.monthList[endMonth-1] + ' ' + `endHour` + ':00'
        return period
    
    titleLabels = []
    if epwData == True:
        titleTxt = ["Adaptive Chart", epwStr[1]]
        if analysisPeriod_ == []:
            titleTxt.append(getDateStr(epwStr[5], epwStr[6]))
        else:
            titleTxt.append(getDateStr(analysisPeriod_[0], analysisPeriod_[1]))
    else: titleTxt = ["Adaptive Chart", "Unkown Location", "Unknown Time Period"]
    if belowTen == False: titlePt = [rc.Geometry.Point3d(10, 4, 0), rc.Geometry.Point3d(10, (4)-(legendFontSize*2.5), 0),  rc.Geometry.Point3d(10, (4)-(legendFontSize*5), 0)]
    else: titlePt = [rc.Geometry.Point3d(-20, -6, 0), rc.Geometry.Point3d(-20, (-6)-(legendFontSize*2.5), 0),  rc.Geometry.Point3d(-20, (-6)-(legendFontSize*5), 0)]
    for count, text in enumerate(titleTxt):
        titleLabels.extend(lb_visualization.text2srf([text], [titlePt[count]], legendFont, legendFontSize*1.5, legendBold)[0])
    
    #Make sure that there is a good surface to use to make the legend.
    
    #Bring all text and curves together in one list.
    for item in tempNumLines:
        chartCrvAndText.append(item)
    for item in prevailTempNumLines:
        chartCrvAndText.append(item)
    for item in tempLabels:
        chartCrvAndText.append(item)
    for item in titleLabels:
        chartCrvAndText.append(item)
    
    
    return chartCrvAndText, comfortPolygons, belowTen, tempNumLines[0:8]


def colorMesh(airTemp, radTemp, prevailTemp, lb_preparation, lb_comfortModels, lb_visualization, lowB, highB, customColors, belowTen):
    # Make the full chart mesh
    #Generate a list of temperatures that will be used to make the mesh.
    if belowTen == False:
        tempNumMesh = range(10, 41, 1)
        prevailNumMesh = range(10, 34, 1)
    else:
        tempNumMesh = range(0, 41, 1)
        prevailNumMesh = range(-20, 34, 1)
    
    #Make a matrix
    tempNumMeshFinal =[]
    for temp in tempNumMesh:
        tempNumMeshInit = []
        for item in prevailNumMesh:
            tempNumMeshInit.append(temp)
        tempNumMeshFinal.append(tempNumMeshInit)
    
    #Make the mesh faces.
    chartMesh = rc.Geometry.Mesh()
    meshFacePts = []
    
    for listCount, list in enumerate(tempNumMeshFinal[:-1]):
        for tempCount, temp in enumerate(prevailNumMesh[:-1]):
            facePt1 = rc.Geometry.Point3d(temp, list[tempCount], 0)
            facePt2 = rc.Geometry.Point3d(temp, tempNumMeshFinal[listCount+1][tempCount], 0)
            facePt3 = rc.Geometry.Point3d(prevailNumMesh[tempCount+1], tempNumMeshFinal[listCount+1][tempCount+1], 0)
            facePt4 = rc.Geometry.Point3d(prevailNumMesh[tempCount+1], list[tempCount+1], 0)
            
            meshFacePts.append([facePt1, facePt2, facePt3, facePt4])
    
    for list in  meshFacePts:
        mesh = rc.Geometry.Mesh()
        for point in list:
            mesh.Vertices.Add(point)
        
        mesh.Faces.AddFace(0, 1, 2, 3)
        chartMesh.Append(mesh)
    uncoloredMesh = chartMesh
    
    #Calculate the opTemper for each of the hours of the year and use this to make points for the chart.
    hourPts = []
    operativeTemps = []
    for count, temp in enumerate(prevailTemp):
        operTemp = (airTemp[count]+radTemp[count])/2
        hourPts.append(rc.Geometry.Point3d(temp, operTemp, 0))
        operativeTemps.append(operTemp)
    
    #Make a list to hold values for all of the mesh faces.
    meshFrequency = []
    for count, value in enumerate(tempNumMesh[:-1]):
        meshFrequency.append([])
        for face in prevailNumMesh[:-1]:
            meshFrequency[count].append([])
    
    #Bin the input prevail and temperatures into categories that correspond to the mesh faces.
    def getTempIndex(hour):
        if belowTen == False:
            if prevailTemp[hour] > 10 and prevailTemp[hour] < 33.5:
                index  = int(round(prevailTemp[hour]-10.5))
            else: index = -1
        else:
            if prevailTemp[hour] > -20 and prevailTemp[hour] < 33.5:
                index  = int(round(prevailTemp[hour]+19.5))
            else: index = -1
        
        return index
    
    for hour, opTemper in enumerate(operativeTemps):
        tempIndex = getTempIndex(hour)
        
        if tempIndex != -1:
            if belowTen == False:
                if opTemper < 10: pass
                elif opTemper < 11: meshFrequency[0][tempIndex].append(1)
                elif opTemper < 12: meshFrequency[1][tempIndex].append(1)
                elif opTemper < 13:meshFrequency[2][tempIndex].append(1)
                elif opTemper < 14:meshFrequency[3][tempIndex].append(1)
                elif opTemper < 15:meshFrequency[4][tempIndex].append(1)
                elif opTemper < 16:meshFrequency[5][tempIndex].append(1)
                elif opTemper < 17:meshFrequency[6][tempIndex].append(1)
                elif opTemper < 18:meshFrequency[7][tempIndex].append(1)
                elif opTemper < 19:meshFrequency[8][tempIndex].append(1)
                elif opTemper < 20:meshFrequency[9][tempIndex].append(1)
                elif opTemper < 21:meshFrequency[10][tempIndex].append(1)
                elif opTemper < 22:meshFrequency[11][tempIndex].append(1)
                elif opTemper < 23:meshFrequency[12][tempIndex].append(1)
                elif opTemper < 24:meshFrequency[13][tempIndex].append(1)
                elif opTemper < 25:meshFrequency[14][tempIndex].append(1)
                elif opTemper < 26:meshFrequency[15][tempIndex].append(1)
                elif opTemper < 27:meshFrequency[16][tempIndex].append(1)
                elif opTemper < 28:meshFrequency[17][tempIndex].append(1)
                elif opTemper < 29:meshFrequency[18][tempIndex].append(1)
                elif opTemper < 30:meshFrequency[19][tempIndex].append(1)
                elif opTemper < 31:meshFrequency[20][tempIndex].append(1)
                elif opTemper < 32:meshFrequency[21][tempIndex].append(1)
                elif opTemper < 33:meshFrequency[22][tempIndex].append(1)
                elif opTemper < 34:meshFrequency[23][tempIndex].append(1)
                elif opTemper < 35:meshFrequency[24][tempIndex].append(1)
                elif opTemper < 36:meshFrequency[25][tempIndex].append(1)
                elif opTemper < 37:meshFrequency[26][tempIndex].append(1)
                elif opTemper < 38:meshFrequency[27][tempIndex].append(1)
                elif opTemper < 39:meshFrequency[28][tempIndex].append(1)
                else: meshFrequency[29][tempIndex].append(1)
            else:
                if opTemper < 0: pass
                elif opTemper < 1: meshFrequency[0][tempIndex].append(1)
                elif opTemper < 2: meshFrequency[1][tempIndex].append(1)
                elif opTemper < 3:meshFrequency[2][tempIndex].append(1)
                elif opTemper < 4:meshFrequency[3][tempIndex].append(1)
                elif opTemper < 5:meshFrequency[4][tempIndex].append(1)
                elif opTemper < 6:meshFrequency[5][tempIndex].append(1)
                elif opTemper < 7:meshFrequency[6][tempIndex].append(1)
                elif opTemper < 8:meshFrequency[7][tempIndex].append(1)
                elif opTemper < 9:meshFrequency[8][tempIndex].append(1)
                elif opTemper < 10:meshFrequency[9][tempIndex].append(1)
                elif opTemper < 11:meshFrequency[10][tempIndex].append(1)
                elif opTemper < 12:meshFrequency[11][tempIndex].append(1)
                elif opTemper < 13:meshFrequency[12][tempIndex].append(1)
                elif opTemper < 14:meshFrequency[13][tempIndex].append(1)
                elif opTemper < 15:meshFrequency[14][tempIndex].append(1)
                elif opTemper < 16:meshFrequency[15][tempIndex].append(1)
                elif opTemper < 17:meshFrequency[16][tempIndex].append(1)
                elif opTemper < 18:meshFrequency[17][tempIndex].append(1)
                elif opTemper < 19:meshFrequency[18][tempIndex].append(1)
                elif opTemper < 20:meshFrequency[19][tempIndex].append(1)
                elif opTemper < 21:meshFrequency[20][tempIndex].append(1)
                elif opTemper < 22:meshFrequency[21][tempIndex].append(1)
                elif opTemper < 23:meshFrequency[22][tempIndex].append(1)
                elif opTemper < 24:meshFrequency[23][tempIndex].append(1)
                elif opTemper < 25:meshFrequency[24][tempIndex].append(1)
                elif opTemper < 26:meshFrequency[25][tempIndex].append(1)
                elif opTemper < 27:meshFrequency[26][tempIndex].append(1)
                elif opTemper < 28:meshFrequency[27][tempIndex].append(1)
                elif opTemper < 29:meshFrequency[28][tempIndex].append(1)
                elif opTemper < 30:meshFrequency[29][tempIndex].append(1)
                elif opTemper < 31:meshFrequency[30][tempIndex].append(1)
                elif opTemper < 32:meshFrequency[31][tempIndex].append(1)
                elif opTemper < 33:meshFrequency[32][tempIndex].append(1)
                elif opTemper < 34:meshFrequency[33][tempIndex].append(1)
                elif opTemper < 35:meshFrequency[34][tempIndex].append(1)
                elif opTemper < 36:meshFrequency[35][tempIndex].append(1)
                elif opTemper < 37:meshFrequency[36][tempIndex].append(1)
                elif opTemper < 38:meshFrequency[37][tempIndex].append(1)
                elif opTemper < 39:meshFrequency[38][tempIndex].append(1)
                else: meshFrequency[39][tempIndex].append(1)
    
    #Sum all of the lists together to get the frequency.
    finalMeshFrequency = []
    for opTemperlist in meshFrequency:
        for prevailTemplist in opTemperlist:
            finalMeshFrequency.append(sum(prevailTemplist))
    
    #Get a list of colors
    colors = lb_visualization.gradientColor(finalMeshFrequency, lowB, highB, customColors)
    
    # color the mesh faces.
    uncoloredMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Gray)
    
    for srfNum in range (uncoloredMesh.Faces.Count):
        uncoloredMesh.VertexColors[4 * srfNum + 0] = colors[srfNum]
        uncoloredMesh.VertexColors[4 * srfNum + 1] = colors[srfNum]
        uncoloredMesh.VertexColors[4 * srfNum + 3] = colors[srfNum]
        uncoloredMesh.VertexColors[4 * srfNum + 2] = colors[srfNum]
    
    # Remove the mesh faces that do not have any hour associated with them.
    cullFaceIndices = []
    for count, freq in enumerate(finalMeshFrequency):
        if freq == 0:
            cullFaceIndices.append(count)
    uncoloredMesh.Faces.DeleteFaces(cullFaceIndices)
    
    #Flip the mesh to be sure that it always displays correctly.
    uncoloredMesh.Flip(True, True, True)
    
    
    #Return everything that's useful.
    return hourPts, uncoloredMesh, finalMeshFrequency


def main(epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed, lb_preparation, lb_comfortModels, lb_visualization):
    #Create lists to be filled.
    comfortableOrNot = []
    degreesFromTarget = []
    comfPercentOfTime = None
    legend = []
    legendBasePt = None
    strategyPolygons = []
    
    # Read the legend parameters.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar_, False)
    
    # Generate the chart curves.
    chartCurvesAndTxt, comfortPolygons, belowTen, bound = drawAdaptChart(prevailTemp, legendFont, legendFontSize, legendBold, epwData, epwStr, lb_visualization, lb_comfortModels)
    
    #Generate the colored mesh.
    #As long as the calculation length is more than 1, make a colored mesh and get chart points for the input data.
    legend = []
    if calcLength > 1:
        chartHourPoints, adaptiveChartMesh, meshFaceValues = colorMesh(airTemp, radTemp, prevailTemp, lb_preparation, lb_comfortModels, lb_visualization, lowB, highB, customColors, belowTen)
        legendTitle = "Hours"
        lb_visualization.calculateBB(bound, True)
        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(meshFaceValues, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold)
        legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
        legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
        legend.append(legendSrfs)
        for list in legendTextCrv:
            for item in list:
                legend.append(item)
        if legendBasePoint == None:
            legendBasePoint = lb_visualization.BoundingBoxPar[0]
    else:
        chartHourPoints = [rc.Geometry.Point3d((airTemp[0]+radTemp[0])/2, prevailTemp[0], 0)]
        adaptiveChartMesh = None
        meshFaceValues = []
        legendBasePoint = None
    
    
    
    return comfortableOrNot, degreesFromTarget, comfPercentOfTime, chartCurvesAndTxt, adaptiveChartMesh, legend, legendBasePt, comfortPolygons, chartHourPoints




#Check to be sure Ladybug is flying.
initCheck = False
if sc.sticky.has_key('ladybug_release'):
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): pass
        initCheck = True
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    if initCheck == True:
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
else:
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")




#Check the inputs and organize the incoming data into streams that can be run throught the comfort model.
if initCheck == True:
    checkData = False
    checkData, epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed = checkTheInputs()


if checkData == True and _runIt == True:
    results = main(epwData, epwStr, calcLength, airTemp, radTemp, prevailTemp, windSpeed, lb_preparation, lb_comfortModels, lb_visualization)
    if results != -1:
        comfortableOrNot, degreesFromTarget, comfPercentOfTime, chartCurvesAndTxt, adaptiveChartMesh, legend, legendBasePt, comfortPolygons, chartHourPoints = results

ghenv.Component.Params.Output[11].Hidden = True