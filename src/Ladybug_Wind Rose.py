# Wind Rose
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Draws windRose

-
Provided by Ladybug 0.0.54
    
    Args:
        _north_: Input a number or a vector to set north; default is set to the Y-axis
        _hourlyWindDirection: A list of hourly wind direction data
        _hourlyWindSpeed: A list of hourly wind speed data
        annualHourlyData_: Connect a list of annual hourly data to be overlaid on sunpath
        _analysisPeriod_: Analysis period from Analysis Period component; may be used to override hour of  the year
        conditionalStatement_: The Conditional Statement Input allows users to filter data for specific conditions. Specific hourly data, such as temperature or humidity, can be filtered and overlaid with the Sun Path. The conditional statement should be a valid condition statement in Python such as a>25 and b<80.
                              The current version accepts "and" and "or" operators. To visualize the hourly data, only lowercase English letters should be used as variables, and each letter corresponds to each of the lists (in their respective order): "a" always represents the 1st list, "b" represents the 2nd list, etc.
                              For example, if you have hourly dry bulb temperature connected as the first list, and relative humidity connected as the second list, and you want to plot the data for the time period when temperature is between 18 and 23, and humidity is less than 80%, the statement should be written as 18<a<23 and b<80 (without quotation marks)
                              In windRose component "a" always represents windSpeed as the first list.
        _numOfDirections_: Input a number to set the number of directions for wind rose. Minimum is 4
        _centerPoint_: Input a point to locate the center point of the wind rose 
        _scale_: Input a number to set the scale of the radiation rose
        legendPar_: Input legend parameters from the Ladybug Legend Parameters component
        _runIt: Set Boolean to True to run the component 
        bakeIt_: Set Boolean to True to bake the radiation rose
    
    Returns:
        readMe!: ...
        calmRoseMesh: Frequency during the calm hours as a joined mesh
        windRoseMesh: Wind rose as a joined mesh
        windRoseCrvs: Wind rose guide curves
        windRoseCenPts: Center point(s) of wind rose
        legend: Legend(s) of the chart(s). Connect to Geo for preview
        legendBasePts: Legend base point, mainly for presentation purposes
"""

ghenv.Component.Name = "Ladybug_Wind Rose"
ghenv.Component.NickName = 'windRose'
ghenv.Component.Message = 'VER 0.0.54\nFEB_16_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

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
                         'Conditiontional Selection Applied:\n'
        
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


def main(north, hourlyWindDirection, hourlyWindSpeed, annualHourlyData,
                  analysisPeriod, conditionalStatement, numOfDirections, centerPoint,
                  scale, legendPar, bakeIt):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_runStudy_GH = sc.sticky["ladybug_RunAnalysis"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        conversionFac = lb_preparation.checkUnits()
        
        def bakePlease(listInfo, meshJoined, legendSrfs, legendText, textPt, textSize, windRoseCrvs):
            # legendText = legendText + ('\n\n' + customHeading)
            studyLayerName = 'WINDROSE'
            try:
                layerName = listInfo[1]
                dataType = 'Hourly Data:' + listInfo[2]
            
            except:
                layerName = 'Latitude=' +`latitude`
                dataType = 'No Hourly Data'
            
            # check the study type
            newLayerIndex, l = lb_visualization.setupLayers(dataType, 'LADYBUG', layerName, studyLayerName)
            lb_visualization.bakeObjects(newLayerIndex, meshJoined, legendSrfs, legendText, textPt, textSize, 'Verdana', windRoseCrvs)
        
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
            
            if titleStatement != -1 and True not in patternList:
                warning = 'No hour meets the conditional statement.' 
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1
            
            if titleStatement == -1:
                patternList = [[True]] * 8760
                titleStatement = False
            
           # check the scale
            try:
                if float(scale)!=0:
                    try:scale = 10*float(scale)/conversionFac
                    except: scale = 10/conversionFac
                else: scale = 10/conversionFac
            except: scale = 10/conversionFac
            
            cenPt = lb_preparation.getCenPt(centerPoint)
            
            if not numOfDirections or int(numOfDirections) < 4: numOfDirections = 24
            elif int(numOfDirections)> 360: numOfDirections = 360
            else:
                try: numOfDirections = int(numOfDirections)
                except: numOfDirections = 24
            
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
            
            
            selectedWindDir = lb_preparation.selectHourlyData(windDir, analysisPeriod)[7:]
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
                            if roseAngles[angleCount]<= windDirection <= roseAngles[angleCount + 1]:
                                separatedBasedOnAngle[angleCount].append(h)
                                break
                            elif roseAngles[-1]<= windDirection:
                                separatedBasedOnAngle[-1].append(h)
                                break
            
            # calculate the frequency
            calmFreq = 100*len(calmHour)/len(studyHours)
            comment1 = 'Calm for ' + '%.2f'%calmFreq + '% of the time = ' + `len(calmHour)` + ' hours.'
            print comment1
            windFreq = []
            for angle in separatedBasedOnAngle:
                windFreq.append(100*len(angle)/len(studyHours))
            
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
            maxFreq = max(windFreq) + calmFreq
            
            step = (maxFreq-minFreq)/10
            comment2 = 'Each closed polyline shows frequency of ' + "%.1f"%step + '%. = ' + `int(step * len(studyHours)/100)` + ' hours.'
            print comment2
            for freq in rs.frange(minFreq, maxFreq + step, step):
                freqCrvs.append(freqPolyline(cenPt, freq, sideVectors, scale))
            
            # initial compass for BB
            textSize = 10
            compassCrvs, compassTextPts, compassText = lb_visualization. compassCircle(cenPt, northVector, 1.07 *maxFreq * scale, roseAngles, 1.5*textSize)
            numberCrvs = lb_visualization.text2crv(compassText, compassTextPts, 'Times New Romans', textSize/1.5)
            compassCrvs = compassCrvs + lb_preparation.flattenList(numberCrvs)
            lb_visualization.calculateBB(compassCrvs, True)
            
            # initiate legend parameters
            overwriteScale = False
            if legendPar == []: overwriteScale = True
            elif legendPar[-1] == None: overwriteScale = True
            lowB, highB, numSeg, customColors, legendBasePoint, legendScale = lb_preparation.readLegendParameters(legendPar, False)
            
            if overwriteScale: legendScale = 0.9
            legend = []; legendText = []; textPt = []; legendSrfs = None
            
            allWindRoseMesh = []; allWindCenMesh = []; cenPts = []
            legendBasePoints = []; allWindRoseCrvs = []; allLegend = []
            
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
                                , lowB, highB, numSeg, listInfo[i][3], lb_visualization.BoundingBoxPar, legendBasePoint, legendScale)
                        
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
                            # print resultStr
                            customHeading = customHeading + '\n' + titleStatement + '\n' + resultStr
                        
                        titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo[i]], lb_visualization.BoundingBoxPar, legendScale, customHeading, True)
                        
                        
                        # find the freq of the numbers in each segment
                        numRanges = legendText[:-1]
                        
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
                                
                    segments = lb_visualization.colorMesh(segmentsColors, segments)
                    centerMesh = lb_visualization.colorMesh(cenMeshColors, centerMesh)
                    
                    legendText.append(titleStr)
                    textPt.append(titlebasePt)
                    
                    compassCrvs, compassTextPts, compassText = lb_visualization. compassCircle(cenPt, northVector, 1.07 *maxFreq * scale, roseAngles, 1.5*textSize)
                    numberCrvs = lb_visualization.text2crv(compassText, compassTextPts, 'Times New Romans', textSize/1.5)
                    compassCrvs = compassCrvs + lb_preparation.flattenList(numberCrvs)
                    
                    
                    
                    # let's move it move it move it!
                    if legendScale > 1: movingVector = legendScale * movingVector
                    crvsTemp = []
                    try:
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
                        allLegend.append(lb_visualization.openLegend([legendSrfs, [lb_preparation.flattenList(legendTextCrv + titleTextCurve)]]))
                        
                        #allSunPosInfo.append(modifiedsunPosInfo)
                        #allValues.append(values)
                    except Exception, e:
                        print `e`
                        
                    if bakeIt:
                        try:
                            bakePlease(listInfo[i], [segments, centerMesh], legendSrfs, legendText, textPt, textSize, crvsTemp)
                        except Exception, e:
                            print `e`
                            
        
            return allWindRoseMesh, allWindCenMesh, cenPts, legendBasePoints, allWindRoseCrvs, allLegend, legendBasePoints

    else:
        warning =  "You should first let the Ladybug fly..."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1


if _runIt:
    result = main(_north_, _hourlyWindDirection, _hourlyWindSpeed, annualHourlyData_,
                  _analysisPeriod_, conditionalStatement_, _numOfDirections_, _centerPoint_,
                  _scale_, legendPar_, bakeIt_)
    
    if result!= -1:
        allWindRoseMesh, allWindCenMesh, cenPts, legendBasePoints, allWindRoseCrvs, allLegend, legendBasePoints = result
        
        legend = DataTree[Object]()
        calmRoseMesh = DataTree[Object]()
        windRoseMesh = DataTree[Object]()
        windRoseCrvs = DataTree[Object]()
        legend = DataTree[Object]()
        windRoseCenPts = DataTree[Object]()
        sunPositionsInfo = DataTree[Object]()
        legendBasePts = DataTree[Object]()
        for i, leg in enumerate(allLegend):
            p = GH_Path(i)
            legend.Add(leg[0], p)
            legend.AddRange(leg[1], p)
            if allWindCenMesh!=[]: calmRoseMesh.Add(allWindCenMesh[i],p)
            windRoseMesh.Add(allWindRoseMesh[i],p)
            windRoseCrvs.AddRange(allWindRoseCrvs[i],p)
            #selHourlyData.AddRange(selHourlyDataList[i],p)
            #sunPositions.AddRange(sunPositionsList[i],p)
            windRoseCenPts.Add(cenPts[i],p)
            #sunPositionsInfo.AddRange(sunPosInfoList[i], p)
            legendBasePts.Add(legendBasePoints[i],p)
        
        ghenv.Component.Params.Output[4].Hidden = True
        ghenv.Component.Params.Output[6].Hidden = True
else:
    print 'Set runIt to True!'
