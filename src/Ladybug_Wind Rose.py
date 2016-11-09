# Wind Rose
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Use this component to make a windRose in the Rhino scene.

-
Provided by Ladybug 0.0.63
    
    Args:
        _north_: Input a vector to be used as a true North direction for the wind rose or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _hourlyWindDirection: The list of hourly wind direction data from the Import epw component.
        _hourlyWindSpeed: The list of hourly wind speed data from the Import epw component.
        annualHourlyData_: An optional list of hourly data from the Import epw component, which will be overlaid on wind rose (e.g. dryBulbTemperature)
        _analysisPeriod_: An optional analysis period from the Analysis Period component.
        conditionalStatement_: This input allows users to remove data that does not fit specific conditions or criteria from the wind rose. To use this input correctly, hourly data, such as temperature or humidity, must be plugged into the annualHourlyData_ input. The conditional statement input here should be a valid condition statement in Python, such as "a>25" or "b<80" (without quotation marks).
                              The current version of this component accepts "and" and "or" operators. To visualize the hourly data, only lowercase English letters should be used as variables, and each letter alphabetically corresponds to each of the lists (in their respective order): "a" always represents the 1st list, "b" always represents the 2nd list, etc.
                              For the WindBoundaryProfile component, the variable "a" always represents windSpeed. For example, if you have hourly dry bulb temperature connected as the second list, and relative humidity connected as the third list (both to the annualHourlyData_ input), and you want to plot the data for the time period when temperature is between 18C and 23C, and humidity is less than 80%, the conditional statement should be written as 18<b<23 and c<80 (without quotation marks).
        _numOfDirections_: A number of cardinal directions with which to divide up the data in wind rose. Values must be greater than 4 since you can have no fewer than 4 cardinal directions.
        _centerPoint_: Input a point here to change the location of the wind rose in the Rhino scene.  The default is set to the Rhino model origin (0,0,0).
        _scale_: Input a number here to change the scale of the wind rose.  The default is set to 1.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        maxFrequency_: An optional number between 1 and 100 that represents the maximum percentage of hours that the outer-most ring of the wind rose represents.  By default, this value is set by the wind direction with the largest number of hours (the highest frequency) but you may want to change this if you have several wind roses that you want to compare to each other.  For example, if you have wind roses for different months or seasons, which each have different maximum frequencies.
        showFrequency_: Connect boolean and set it to True to display frequency of wind coming from each direction
        frequencyOffset_: The offset of frequecy display on wind rose. This input only accepts floats. The default offset is 1.12
        bakeIt_ : An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options:
            0 (or False) - No geometry will be baked into the Rhino scene (this is the default).
            1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. 
            2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry.
        _runIt: Set this value to "True" to run the component and generate a wind rose in the Rhino scene.
    Returns:
        readMe!: ...
        calmRoseMesh: A mesh in the center of the wind rose representing the relative number of hours where the wind speed is around 0 m/s.
        windRoseMesh: A mesh representing the wind speed from different directions for all hours analyzed.
        windRoseCrvs: A set of guide curves that mark the number of hours corresponding to the windRoseMesh.
        windRoseCenPts: The center point(s) of wind rose(s).  Use this to move the wind roses in relation to one another using the grasshopper "move" component.
        windSpeeds: Wind speed data for the wind rose displayed in the Rhino scene.
        windDirections: Wind direction data for the wind rose displayed in the Rhino scene.
        legend: A legend of the wind rose. Connect this output to a grasshopper "Geo" component in order to preview the legend separately in the Rhino scene.
        legendBasePts: The legend base point(s), which can be used to move the legend in relation to the rose with the grasshopper "move" component.
        title: The title for the wind rose. Connect this output to a grasshopper "Geo" component in order to preview the legend separately in the Rhino scene.  
"""

ghenv.Component.Name = "Ladybug_Wind Rose"
ghenv.Component.NickName = 'windRose'
ghenv.Component.Message = 'VER 0.0.63\nAUG_10_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.59\nJAN_24_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino as rc
from System import Object
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import math


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
        
        selList = [[]] * len(listInfo)
        for i in range(len(listInfo)):
            selList[i] = annualHourlyData[indexList[i]+7:indexList[i+1]]
            if listInfo[i][4]!='Hourly' or listInfo[i][5]!=(1,1,1) or  listInfo[i][6]!=(12,31,24) or len(selList[i])!=8760:
                warning = 'At least one of the input data lists is not a valis ladybug hourly data! Please fix this issue and try again!\n List number = '+ `i+1`
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1, -1
        
        # replace the right list in the conditional statement
        statement = conditionalStatement.split(' ')
        finalStatement = 'pattern = '
        titleStatement = '...                         ...                         ...\n' +\
                         'Conditional Selection Applied:\n'
        
        for statemntPart in statement:
            statementCopy = str.Copy(statemntPart)
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
        
        
def unpackPatternList(patternList, analysisPeriod, _hourlyWindSpeed, _hourlyWindDirection):
    """This is a helper function. It is mainly used to generate lists for windSpeeds and windDirections
       output of this component.
       input(patternList) = a list with True and False values based on conditional statement
       input (analysisPeriod) = Data from _analysisPeriod_ input of this component
       input (_hourlyWindSpeed) = Data from _hourlyWindSpeed input of this component
       input (_hourlyWindDirection) = Data from _hourlyWindDirection input of this component
       output(result) = a tuple of lists"""
    
    #Trimming headers from weather data input and making new lists out of them
    speedData = _hourlyWindSpeed[7:]
    directionData = _hourlyWindDirection[7:]
    
    # Simple unpacking of the list in a new local variable finalPattern.
    if type(patternList[0]) == list:
        finalPattern = [val for sublist in patternList for val in sublist]
    else:
        finalPattern = patternList
        
    # Getting total hours of the year from the analysis period
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)

    # Making a new list for windSpeeds output
    windSpeeds = []
    # Creating header for the list
    windSpeeds.extend(_hourlyWindSpeed[0:5])
    if len(_analysisPeriod_) == 0:
        windSpeeds.extend(_hourlyWindSpeed[5:7])
    else:
        windSpeeds.extend(_analysisPeriod_)
    # Adding data to the list
    for i in range(len(HOYS)):
        j = int(HOYS[i])-1 # Here, -1 is important. So that, counting starts from index 0.
        if finalPattern[j] == True:
            windSpeeds.append(speedData[j])
        else:
            pass
    
    # Making a new list for windDirections output
    windDirections = []
    # Creating header for the list
    windDirections.extend(_hourlyWindDirection[0:5])
    if len(_analysisPeriod_) == 0:
        windDirections.extend(_hourlyWindDirection[5:7])
    else:
        windDirections.extend(_analysisPeriod_)
    # Adding data to the list
    for i in range(len(HOYS)):
        j = int(HOYS[i])-1 # Here, -1 is important. So that, counting starts from index 0.
        if finalPattern[j] == True:
            windDirections.append(directionData[j])
        else:
            pass

    return windSpeeds, windDirections


def freqOffset(frequencyOffset_):
    """This function sets the offset value for frequency display on wind rose
    input(frequencyOffset_) = input from this component
    output(offset) = a float value"""
    if frequencyOffset_ == None:
        offset = 1.12
        return offset
    else:
        offset = frequencyOffset_
        return offset
                        
                        

def main(north, hourlyWindDirection, hourlyWindSpeed, annualHourlyData,
                  analysisPeriod, conditionalStatement, numOfDirections, centerPoint,
                  scale, legendPar, bakeIt, maxFrequency):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_runStudy_GH = sc.sticky["ladybug_RunAnalysis"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        conversionFac = lb_preparation.checkUnits()
        
        def movePointList(textPt, movingVector):
            for ptCount, pt in enumerate(textPt):
                ptLocation = rc.Geometry.Point(pt)
                ptLocation.Translate(movingVector) # move it to the right place
                textPt[ptCount] = rc.Geometry.Point3d(ptLocation.Location)
            return textPt
            
        # copy the custom code here
        # check the input data
        try:
            if hourlyWindDirection[2] == 'Wind Direction' and hourlyWindSpeed[2] == 'Wind Speed':
                checkData = True
                indexList, listInfo = lb_preparation.separateList(hourlyWindDirection + hourlyWindSpeed, lb_preparation.strToBeFound)
                # check that both data are horly and for same time range
                if listInfo[0][4] != 'Hourly' or listInfo[1][4] != 'Hourly':
                    checkData = False
                    warning = "At list one of the input lists for windSpeed or windDirection is not hourly."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, warning)
                    return -1
                elif listInfo[1][5]!=(1,1,1) or listInfo[1][6]!=(12,31,24):
                    checkData = False
                    warning = "hourlyWindSpeed data should be annual. Find annual wind data as an output of importEPW component."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, warning)
                    return -1
                # wind direction data
                windDir = hourlyWindDirection[7:]
                windSpeed = hourlyWindSpeed[7:]
            else:
                checkData = False
                warning = "Please provide valid lists of hourly wind direction and hourly wind speed!"
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1
        except Exception,e:
            checkData = False
            warning = "Please provide valid lists of hourly wind direction and hourly wind speed!"
            # print `e`
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
    
        if checkData:
            titleStatement = -1
            annualHourlyData = hourlyWindSpeed + annualHourlyData
            if conditionalStatement and len(annualHourlyData)!=0 and annualHourlyData[0]!=None:
                print 'Checking conditional statements...'
                # send all data and statement to a function and return back
                # True, False Pattern and condition statement
                titleStatement, patternList = checkConditionalStatement(annualHourlyData, conditionalStatement)
                # Unpacking the paternList for output of windSpeeds and windDirections
                unpackedList = unpackPatternList(patternList, _analysisPeriod_, _hourlyWindSpeed, _hourlyWindDirection)
                windSpeeds = unpackedList[0]
                windDirections = unpackedList[1]

                
            if titleStatement != -1 and True not in patternList:
                warning = 'No hour meets the conditional statement.' 
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1
            
            if titleStatement == -1:
                patternList = [[True]] * 8760
                # Unpacking the paternList for output of windSpeeds and windDirections
                unpackedList = unpackPatternList(patternList, _analysisPeriod_, _hourlyWindSpeed, _hourlyWindDirection)
                windSpeeds = unpackedList[0]
                windDirections = unpackedList[1]
                titleStatement = False

            
           # check the scale
            try:
                if float(scale)!=0:
                    try:scale = 10*float(scale)/conversionFac
                    except: scale = 10/conversionFac
                else: scale = 10/conversionFac
            except: scale = 10/conversionFac
            
            cenPt = lb_preparation.getCenPt(centerPoint)
            
            if not numOfDirections or int(numOfDirections) < 4: numOfDirections = 16
            elif int(numOfDirections)> 360: numOfDirections = 360
            else:
                try: numOfDirections = int(numOfDirections)
                except: numOfDirections = 16
            
            # define angles
            segAngle = 360/numOfDirections
            roseAngles = rs.frange(0,360,segAngle);
            if round(roseAngles[-1]) == 360: roseAngles.remove(roseAngles[-1])
            
            movingVectors = []; sideVectors = []
            northAngle, northVector = lb_preparation.angle2north(north)
            for i, angle in enumerate(roseAngles):
                northVector1 = rc.Geometry.Vector3d(northVector)
                northVector2 = rc.Geometry.Vector3d(northVector)
                northVector1.Rotate(-float(math.radians(angle)), rc.Geometry.Vector3d.ZAxis)
                movingVectors.append(northVector1)
                northVector2.Rotate(-float(math.radians(angle + (segAngle/2))), rc.Geometry.Vector3d.ZAxis)
                sideVectors.append(northVector2)
            
            HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
            selectedWindDir = []
            for count in HOYS:
                selectedWindDir.append(windDir[count-1])
            #selectedWindDir = lb_preparation.selectHourlyData(windDir, analysisPeriod)[7:]
            # read analysis period
            stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod, False)

            # find the study hours based on wind direction data
            startHour = lb_preparation.date2Hour(stMonth, stDay, stHour)
            endingHour =  lb_preparation.date2Hour(endMonth, endDay, endHour)
            if startHour <= endingHour: studyHours = range(startHour-1, endingHour)
            else: studyHours = range(startHour - 1, 8760) + range(0, endingHour)
            
            calmHour = [] # count hours with no wind
            separatedBasedOnAngle = []
            [separatedBasedOnAngle.append([]) for i in range(len(roseAngles))]
            #print len(studyHours)
            #print len(selectedWindDir)
            for hour, windDirection in enumerate(selectedWindDir):
                h = studyHours[hour]
                if patternList[h]: # if the hour pass the conditional statement
                    # check if windSpeed is 0 so collect it in center
                    if windSpeed[h] == 0: calmHour.append(h)
                    else:
                        for angleCount in range(len(roseAngles)-1):
                            # print roseAngles[angleCount], roseAngles[angleCount + 1]
                            #print windDirection
                            if windDirection == 360.0: windDirection = 0
                            
                            if roseAngles[angleCount]-(segAngle/2)<= windDirection < roseAngles[angleCount + 1]-(segAngle/2):
                                separatedBasedOnAngle[angleCount].append(h)
                                break
                            elif roseAngles[-1]<= windDirection:
                                separatedBasedOnAngle[-1].append(h)
                                break
            
            # calculate the frequency
            calmFreq = (100*len(calmHour)/len(studyHours))
            
            comment1 = 'Calm for ' + '%.2f'%calmFreq + '% of the time = ' + `len(calmHour)` + ' hours.'
            print comment1
            windFreq = []
            for angle in separatedBasedOnAngle:
                windFreq.append(100*len(angle)/len(studyHours))
            
            calmFreq = (100*len(calmHour)/len(studyHours))/numOfDirections
            
            
            # draw the basic geometry for windRose
            
            ## draw the first polygon for calm period of the year
            def freqPolyline(cenPt, freq, vectorList, scale, onlyPts = False):
                pts = []
                for vector in vectorList:
                    newPt = rc.Geometry.Point3d.Add(cenPt, freq * scale * vector)
                    pts.append(newPt)
                pts.append(pts[0]) # close the polyline
                if onlyPts: return pts
                return rc.Geometry.Polyline(pts).ToNurbsCurve()
            
            
            freqCrvs = []
            minFreq = calmFreq

            try:
                maxFreq = float(maxFrequency)%100
                if maxFreq ==0: maxFreq == 100
                
                # overwrite minimum so all the graphs will have similar curves
                # regardless of calm hours
                minFreq = 0
                
            except: maxFreq = max(windFreq) + calmFreq
            
            step = (maxFreq-minFreq)/10
            comment2 = 'Each closed polyline shows frequency of ' + "%.1f"%step + '%. = ' + `int(step * len(studyHours)/100)` + ' hours.'
            print comment2
            for freq in rs.frange(minFreq, maxFreq + step, step):
                freqCrvs.append(freqPolyline(cenPt, freq, sideVectors, scale))
            
            # initial compass for BB
            textSize = 10
            compassCrvs, compassTextPts, compassText = lb_visualization. compassCircle(cenPt, northVector, 1.11 *(maxFreq) * scale, roseAngles, 1.5*textSize)
            
            
            
            # initiate legend parameters
            overwriteScale = False
            if legendPar == []: overwriteScale = True
            elif legendPar[-1] == None: overwriteScale = True
            lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
            
            numberCrvs = lb_visualization.text2srf(compassText, compassTextPts, 'Times New Romans', textSize/1.5, legendBold)
            compassCrvs = compassCrvs + lb_preparation.flattenList(numberCrvs)
            lb_visualization.calculateBB(compassCrvs, True)
            
            if overwriteScale: legendScale = 0.9
            legend = []; legendText = []; textPt = []; legendSrfs = None
            
            allWindRoseMesh = []; allWindCenMesh = []; cenPts = []
            legendBasePoints = []; allWindRoseCrvs = []; allLegend = []
            titleTextCurveFinal = []
            
            # for each of the information in hourly data
            if len(annualHourlyData)!=0 and annualHourlyData[0]!=None:
                try: movingDist = 1.8 * lb_visualization.BoundingBoxPar[1] # moving distance for sky domes
                except: movingDist = 0
                
                #separate data
                indexList, listInfo = lb_preparation.separateList(annualHourlyData, lb_preparation.strToBeFound)
                
                for i in range(len(listInfo)):
                    customHeading = 'Wind-Rose\n'
                    movingVector = rc.Geometry.Vector3d(i * movingDist, 0, 0)
                    selList = [];
                    modifiedsunPosInfo = []
                    [selList.append(float(x)) for x in annualHourlyData[indexList[i]+7:indexList[i+1]]]
                    if listInfo[i][4]!='Hourly' or listInfo[i][5]!=(1,1,1) or  listInfo[i][6]!=(12,31,24) or len(selList)!=8760:
                        warning = 'At least one of the input data lists is not a valis ladybug hourly data! Please fix this issue and try again!\n List number = '+ `i+1`
                        print warning
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                        return -1
                    else:
                        values= []; allValues = []
                        [values.append([]) for v in range(len(separatedBasedOnAngle))]
                        #find the values based on the hours separated before
                        for segNum, eachSegment in enumerate(separatedBasedOnAngle):
                            for h in eachSegment:
                                values[segNum].append(selList[h])
                                allValues.append(selList[h])
                        
                        calmValues = []
                        for h in calmHour:
                            calmValues.append(selList[h])
                            allValues.append(selList[h])
                        
                        # get the legend done
                        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(allValues
                                , lowB, highB, numSeg, listInfo[i][3], lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
                        
                        # generate legend colors
                        legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
                        
                        # color legend surfaces
                        legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
                        
                        customHeading = customHeading + listInfo[i][1] + \
                                        '\n'+lb_preparation.hour2Date(lb_preparation.date2Hour(stMonth, stDay, stHour)) + ' - ' + \
                                        lb_preparation.hour2Date(lb_preparation.date2Hour(endMonth, endDay, endHour)) + \
                                        '\nHourly Data: ' + listInfo[i][2] + ' (' + listInfo[i][3] + ')\n'
                        
                        customHeading = customHeading + comment1 + '\n' + comment2 + '\n'
                        
                        if titleStatement:
                            resultStr = "%.1f" % (len(allValues)) + ' hours of total ' + ("%.1f" % len(windDir)) + ' hours' + \
                                        ' (' + ("%.2f" % (len(allValues)/len(windDir) * 100)) + '%).'
                            if analysisPeriod != [(1, 1, 1), (12, 31, 24)] and analysisPeriod != []:
                                additStr = "%.1f" % (len(allValues)) + ' hours of analysis period ' + ("%.1f" % len(HOYS)) + ' hours' + \
                                            ' (' + ("%.2f" % (len(allValues)/len(HOYS) * 100)) + '%).'
                                customHeading = customHeading + '\n' + titleStatement + '\n' + resultStr + '\n' + additStr
                            else:
                                customHeading = customHeading + '\n' + titleStatement + '\n' + resultStr
                        
                        titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo[i]], lb_visualization.BoundingBoxPar, legendScale, customHeading, True, legendFont, legendFontSize, legendBold)
                        
                        # find the freq of the numbers in each segment
                        numRanges = legendText[:-1]
                        if len(numRanges) == 1:
                            numRanges.insert(0, 0.0)

                        # do it for the calm period
                        # calculate the frequency for calm
                        freqInCenter = []
                        [freqInCenter.append([]) for v in range(len(numRanges))]
                        for v in calmValues:
                            for rangeCount in range(len(numRanges)):
                                if numRanges[rangeCount]<= v <= numRanges[rangeCount + 1]:
                                    freqInCenter[rangeCount].append(v)
                                    break
                                elif numRanges[-1]<= v:
                                    freqInCenter[-1].append(v)
                                    break
                        
                        centerFrqPts = []
                        cumFreq = 0
                        freqList = []
                        avrValues = []
                        for freq in freqInCenter:
                            if len(freq)!=0:
                                freqList.append(len(freq)/len(calmValues))
                                avrValues.append(sum(freq)/len(freq))
                                cumFreq = cumFreq + ((len(freq)/len(calmValues)) * calmFreq)
                                centerFrqPts.append(freqPolyline(cenPt, cumFreq , sideVectors, scale, True))
                                
                        centerMesh = rc.Geometry.Mesh()
                        cenMeshColors = []
                        
                        for crvNum in range(len(centerFrqPts)):
                            avr = avrValues[crvNum]
                            color = lb_visualization.gradientColor([avr], numRanges[0], numRanges[-1], customColors)
                            if crvNum==0:
                                for ptCount in range(len(centerFrqPts[crvNum])-1):
                                    try:
                                        singleMesh = rc.Geometry.Mesh()
                                        pt1 = cenPt
                                        pt2 = centerFrqPts[crvNum][ptCount]
                                        pt3 = centerFrqPts[crvNum][ptCount + 1]
                                        singleMesh.Vertices.Add(pt1)
                                        singleMesh.Vertices.Add(pt2)
                                        singleMesh.Vertices.Add(pt3)
                                        singleMesh.Faces.AddFace(0, 1, 2)
                                        cenMeshColors.append(color[0])
                                        centerMesh.Append(singleMesh)
                                    except Exception, e:
                                        print `e`
                            else:
                                for ptCount in range(len(centerFrqPts[crvNum])-1):
                                    try:
                                        singleMesh = rc.Geometry.Mesh()
                                        pt1 = centerFrqPts[crvNum-1][ptCount]
                                        pt2 = centerFrqPts[crvNum][ptCount]
                                        pt3 = centerFrqPts[crvNum-1][ptCount + 1]
                                        pt4 = centerFrqPts[crvNum][ptCount + 1]
                                        singleMesh.Vertices.Add(pt1)
                                        singleMesh.Vertices.Add(pt2)
                                        singleMesh.Vertices.Add(pt3)
                                        singleMesh.Vertices.Add(pt4)
                                        singleMesh.Faces.AddFace(0, 1, 3, 2)
                                        cenMeshColors.append(color[0])
                                        centerMesh.Append(singleMesh)
                                    except Exception, e:
                                        print `e`
                        
                        centerMesh.Flip(True, True, True)
                        
                        segments = rc.Geometry.Mesh()
                        segmentsColors = []
                        for direction, segmentValues in enumerate(values):
                            freqInEachSeg = []
                            [freqInEachSeg.append([]) for v in range(len(numRanges))]
                            
                            for v in segmentValues:
                                for rangeCount in range(len(numRanges)-1):
                                    if numRanges[rangeCount]<= v <= numRanges[rangeCount + 1]:
                                        freqInEachSeg[rangeCount].append(v)
                                        break
                                    elif numRanges[-1]<= v:
                                        freqInEachSeg[-1].append(v)
                                        break
                            totalFr = 0
                            
                            for rangeCount in range(len(numRanges)):
                                if len(segmentValues)!=0:
                                    fr = (len(freqInEachSeg[rangeCount])/len(segmentValues))
                                    if fr!=0:
                                        avr = [sum(freqInEachSeg[rangeCount])/len(freqInEachSeg[rangeCount])]
                                        color = lb_visualization.gradientColor(avr, numRanges[0], numRanges[-1], customColors)
                                        pt1 = rc.Geometry.Point3d.Add(cenPt, (calmFreq + (windFreq[direction] * totalFr)) * scale * sideVectors[direction-1])
                                        pt2 = rc.Geometry.Point3d.Add(cenPt, (calmFreq + (windFreq[direction] * (totalFr + fr)))* scale * sideVectors[direction-1])
                                        pt3 = rc.Geometry.Point3d.Add(cenPt, (calmFreq + (windFreq[direction] * totalFr)) * scale * sideVectors[direction])
                                        pt4 = rc.Geometry.Point3d.Add(cenPt, (calmFreq + (windFreq[direction] * (totalFr + fr)))* scale * sideVectors[direction])
                                        segment = rc.Geometry.Mesh()
                                        segment.Vertices.Add(pt1)
                                        segment.Vertices.Add(pt2)
                                        segment.Vertices.Add(pt3)
                                        segment.Vertices.Add(pt4)
                                        segment.Faces.AddFace(0, 1, 3, 2)
                                        segmentsColors.append(color[0])
                                        segments.Append(segment)
                                    totalFr = totalFr + fr
                    
                    segments.Flip(True, True, True)
                    segments = lb_visualization.colorMesh(segmentsColors, segments)
                    centerMesh = lb_visualization.colorMesh(cenMeshColors, centerMesh)
                    legendText.append(titleStr)
                    textPt.append(titlebasePt)
                    compassCrvs, compassTextPts, compassText = lb_visualization. compassCircle(cenPt, northVector, 1.11 *maxFreq * scale, roseAngles, 1.5*textSize)
                    
                    # Adding frequencies to the wind Rose
                    # Making a list of frequecies to display on wind rose and rounding them
                    freqTextList = []
                    for item in windFreq:
                        freqTextList.append(str(round(item, 2)))
                    # Measuring the distance between the north point and the center of the wind rose.
                    # This radial distance is crucial for position of frequencies
                    point01 = cenPt
                    point02 = compassTextPts[0]
                    distance = rc.Geometry.Point3d.DistanceTo(point02, point01)
                    offset = freqOffset(frequencyOffset_)
                    factor = offset * distance
                    # Making first point for frequency display. This is the first point
                    newPoint = rc.Geometry.Point3d.Add(point01, rc.Geometry.Vector3d(northVector)*factor)
                    # Point container for othe points
                    freqTextPts = [newPoint]
                    angleList = [x*22.5 for x in range(17)]
                    angleList = angleList[1:]
                    # Based on angles new points are created
                    for angle in angleList:
                        newVector = rc.Geometry.Vector3d(northVector)*factor #Factor is important here
                        newVector.Rotate(-math.radians(angle), rc.Geometry.Vector3d.ZAxis)
                        addPoint = rc.Geometry.Point3d.Add(point01, newVector)
                        freqTextPts.append(addPoint)
                        
                    if showFrequency_ == True:
                        freqTextCrvs = lb_visualization.text2srf(freqTextList, freqTextPts, 'Times New Romans', textSize/1.5, legendBold, plane = None, justificationIndex = 1 )
                    else:
                        freqTextCrvs = []
                        
                    numberCrvs = lb_visualization.text2srf(compassText, compassTextPts, 'Times New Romans', textSize/1.5, True)
                    numberCrvs = numberCrvs + freqTextCrvs
                    compassCrvs = compassCrvs + lb_preparation.flattenList(numberCrvs)
                    
                    # let's move it move it move it!
                    if legendScale > 1: movingVector = legendScale * movingVector
                    crvsTemp = []
                    try:
                        moveTransform = rc.Geometry.Transform.Translation(movingVector)
                        for pt in compassTextPts: pt.Transform(moveTransform)
                        
                        segments.Translate(movingVector); allWindRoseMesh.append(segments)
                        if centerMesh!=-1:
                            centerMesh.Translate(movingVector); allWindCenMesh.append(centerMesh)
                        
                        textPt = movePointList(textPt, movingVector)
                        
                        newCenPt = movePointList([cenPt], movingVector)[0];
                        cenPts.append(newCenPt)
                        
                        if legendBasePoint == None:
                            nlegendBasePoint = lb_visualization.BoundingBoxPar[0]
                            movedLegendBasePoint = movePointList([nlegendBasePoint], movingVector)[0];
                        else:
                            movedLegendBasePoint = movePointList([legendBasePoint], movingVector)[0];
                            
                        legendBasePoints.append(movedLegendBasePoint)
                        
                        for crv in legendTextCrv:
                            for c in crv: c.Translate(movingVector)
                        for crv in titleTextCurve:
                            for c in crv: c.Translate(movingVector)
                        
                        for c in freqCrvs + compassCrvs:
                            cDuplicate = c.Duplicate()
                            cDuplicate.Translate(movingVector)
                            crvsTemp.append(cDuplicate)
                        allWindRoseCrvs.append(crvsTemp)
                        
                        legendSrfs.Translate(movingVector)
                        allLegend.append(lb_visualization.openLegend([legendSrfs, [lb_preparation.flattenList(legendTextCrv)]]))
                        titleTextCurveFinal.append(titleTextCurve[0])
                        
                    except Exception, e:
                        print `e`
                        
                    if bakeIt > 0:
                        #Join everything into one mesh.
                        finalJoinedMesh = rc.Geometry.Mesh()
                        try: finalJoinedMesh.Append(segments)
                        except: pass
                        try: finalJoinedMesh.Append(centerMesh)
                        except: pass
                        #Put all of the curves into one list.
                        finalCrvs = []
                        for crv in crvsTemp:
                            try:
                                testPt = crv.PointAtEnd
                                finalCrvs.append(crv)
                            except: pass
                        #Put all of the text together.
                        legendText.extend(compassText)
                        textPt.extend(compassTextPts)
                        #Make labels for the layer.
                        studyLayerName = 'WINDROSE'
                        try:
                            layerName = listInfo[i][1]
                            dataType = 'Hourly Data:' + listInfo[i][2]
                        except:
                            layerName = 'Latitude=' +`latitude`
                            dataType = 'No Hourly Data'
                        
                        # check the study type
                        newLayerIndex, l = lb_visualization.setupLayers(dataType, 'LADYBUG', layerName, studyLayerName)
                        if bakeIt == 1: lb_visualization.bakeObjects(newLayerIndex, finalJoinedMesh, legendSrfs, legendText, textPt, textSize, legendFont, finalCrvs, decimalPlaces, True)
                        else: lb_visualization.bakeObjects(newLayerIndex, finalJoinedMesh, legendSrfs, legendText, textPt, textSize, legendFont, finalCrvs, decimalPlaces, False)
        
            return allWindRoseMesh, allWindCenMesh, cenPts, legendBasePoints, allWindRoseCrvs, windSpeeds, windDirections, allLegend, legendBasePoints, titleTextCurveFinal

    else:
        warning =  "You should first let the Ladybug fly..."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1


if _runIt:
    result = main(_north_, _hourlyWindDirection, _hourlyWindSpeed, annualHourlyData_,
                  _analysisPeriod_, conditionalStatement_, _numOfDirections_, _centerPoint_,
                  _scale_, legendPar_, bakeIt_, maxFrequency_)
    
    if result!= -1:
        allWindRoseMesh, allWindCenMesh, cenPts, legendBasePoints, allWindRoseCrvs, windSpeeds, windDirections, allLegend, legendBasePoints, titleTextCurve = result
        
        legend = DataTree[Object]()
        calmRoseMesh = DataTree[Object]()
        windRoseMesh = DataTree[Object]()
        windRoseCrvs = DataTree[Object]()
        legend = DataTree[Object]()
        windRoseCenPts = DataTree[Object]()
        sunPositionsInfo = DataTree[Object]()
        legendBasePts = DataTree[Object]()
        title = DataTree[Object]()
        for i, leg in enumerate(allLegend):
            p = GH_Path(i)
            legend.Add(leg[0], p)
            legend.AddRange(leg[1], p)
            if allWindCenMesh!=[]: calmRoseMesh.Add(allWindCenMesh[i],p)
            windRoseMesh.Add(allWindRoseMesh[i],p)
            windRoseCrvs.AddRange(allWindRoseCrvs[i],p)
            windRoseCenPts.Add(cenPts[i],p)
            legendBasePts.Add(legendBasePoints[i],p)
            title.AddRange(titleTextCurve[i],p)
        
        ghenv.Component.Params.Output[4].Hidden = True
        ghenv.Component.Params.Output[6].Hidden = True
else:
    print 'Set runIt to True!'
