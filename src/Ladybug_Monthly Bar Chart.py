# This component creates a bar chart of monthly or avrMonthlyPerHour data.
# By Chris Mackey and Mostapha Sadeghipour Roudsari
# Chris@MackeyArchitecture.com and Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to make a bar chart in the Rhino scene of any monhtly or avrMonthyPerHour climate data or simulation data.
_
This component can also plot daily or hourly data but, for visualizing this type of data, it is recommended that you use the "Ladybug_3D Chart" component.
-
Provided by Ladybug 0.0.58
    
    Args:
        _inputData: A list of input data to plot.  This should usually be data out of the "Ladybug_Average Data" component or monthly data from an energy simulation but can also be hourly or daily data from the "Ladybug_Import EPW."  However, it is recommended that you use the "Ladybug_3D Chart" component for daily or hourly data as this is usually a bit clearer.
        comfortModel_: An optional interger to draw the comfort model on the chart.  Choose from the following:
                        0 - No comfort range
                        1 - PMV comfort range (indoor)
                        2 - Adaptive confort range (naturally ventilated)
                        3 - UTCI Comfort (outdoor)
                        Note that this option is only available when temperature is connected so, by default, it is set to 0 for no comfort range.
        bldgBalancePt_: An optional float value to represent the outdoor temperature at which the energy passively flowing into a building is equal to that flowing out of the building.  This is usually a number that is well below the comfort temperture (~ 12C - 18C) since the internal heat of a building and its insulation keep the interior warmer then the exterior.  However, by default, this is set to 23.5C for fully outdoor conditions.
        _______________: ...
        stackValues_: Set to 'True' if you have multiple connected monthly or daily _inputData with the same units and want them to be drawn as bars stacked on top of each other.  Otherwise, all bars for monthly/daily data will be placed next to each other.  The default is set to 'False' to have these bars placed next to each other.
        _basePoint_: An optional point with which to locate the 3D chart in the Rhino Model.  The default is set to the Rhino origin at (0,0,0).
        _xScale_: The scale of the X axis of the graph. The default is set to 1 and this will plot the X axis with a length of 120 Rhino model units (for 12 months of the year).
        _yScale_: The scale of the Y axis of the graph. The default is set to 1 and this will plot the Y axis with a length of 50 Rhino model units.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
    Returns:
        readMe!: ...
        dataMesh: A series of meshes that represent the different monthly input data.  Multiple lists of meshes will be output for several input data streams.
        dataCurves: A list of curves that represent the different avrMonthyPerHour and hourly input data. Multiple lists of curves will be output for several input data streams.
        dataCrvColors: A list of colors that correspond to the dataCurves above.  Hook this up to the 'swatch' input of the native Grasshopper 'Preview' component and the curves above up to the 'geometry input to preview the curves with their repective color.
        graphAxes: A list of curves representing the axes of the chart.  Note that if the time period of the input data is not clear, no curves will be generated here.
        graphLabels: A list of text surfaces representing the time periods corresponding to the input data
        legend: A legend of the chart. Connect this output to a grasshopper "Geo" component in order to preview the legend in the Rhino scene.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the chart with the grasshopper "move" component.
        comfortBand: A series of meshes that represent the comfort range in each month according to the input comfortModel_.
        hrsInComfRange: The number of hours in the comfort range for each month.  If avrMonthyPerHour temperature data is connected, this is the number of average hours in the range and, if hourly temperature data is provided, this is the actual number of hours.  Other data types will cause this output to be null.
"""

ghenv.Component.Name = "Ladybug_Monthly Bar Chart"
ghenv.Component.NickName = 'BarChart'
ghenv.Component.Message = 'VER 0.0.58\nNOV_16_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Rhino as rc
from System import Object
import System
from math import pi as PI

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import math


inputsDict = {
    
0: ["_inputData", "A list of input data to plot.  This should usually be data out of the 'Ladybug_Average Data' component or monthly data from an energy simulation but can also be hourly or daily data from the 'Ladybug_Import EPW.'  However, it is recommended that you use the 'Ladybug_3D Chart' component for daily or hourly data as this is usually a bit clearer."],
1: ["comfortModel_", "An optional interger to draw the comfort model on the chart.  Choose from the following: \n 0 - No comfort range \n 1 - PMV comfort range (indoor) \n 2 - Adaptive confort range (naturally ventilated) \n 3 - UTCI Comfort (outdoor) \n Note that this option is only available when temperature is connected so, by default, it is set to 0 for no comfort range."],
2: ["bldgBalancePt_", "An optional float value to represent the outdoor temperature at which the energy passively flowing into a building is equal to that flowing out of the building.  This is usually a number that is well below the comfort temperture (~ 12C - 18C) since the internal heat of a building and its insulation keep the interior warmer then the exterior.  However, by default, this is set to 23.5C for fully outdoor conditions."],
3: ["_______________", "..."],
4: ["stackValues_", "Set to 'True' if you have multiple connected monthly or daily _inputData with the same units and want them to be drawn as bars stacked on top of each other.  Otherwise, all bars for monthly/daily data will be placed next to each other.  The default is set to 'False' to have these bars placed next to each other."],
5: ["_basePoint_", "An optional point with which to locate the 3D chart in the Rhino Model.  The default is set to the Rhino origin at (0,0,0)."],
6: ["_xScale_", "The scale of the X axis of the graph. The default is set to 1 and this will plot the X axis with a length of 120 Rhino model units (for 12 months of the year)."],
7: ["_yScale_", "The scale of the Y axis of the graph. The default is set to 1 and this will plot the Y axis with a length of 50 Rhino model units."],
8: ["legendPar_", "Optional legend parameters from the Ladybug Legend Parameters component."],
}



def checkTheInputs():
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
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
        
        conversionFac = lb_preparation.checkUnits()
        
        if len(_inputData)== 0:  return -1
        elif _inputData[0] == None: return -1
        else:
            # separate the data
            indexList, listInfo = lb_preparation.separateList(_inputData, lb_preparation.strToBeFound)
            
            #separate the lists of data
            separatedLists = []
            for i in range(len(indexList)-1):
                selList = []
                [selList.append(float(x)) for x in _inputData[indexList[i]+7:indexList[i+1]]]
                separatedLists.append(selList)
            
            #Check to see the type of data in each list and make a key of methods for how to plot the data.
            #0 = Monthly, 1 = avrMonthlyPerHour, 2 = Hourly, 3 = Daily, 4 = Unknown timestep
            checkData1 = True
            methodsList = []
            for list in listInfo:
                if list[4] == 'Monthly' or list[4] == 'Monthly-> averaged': methodsList.append(0)
                elif list[4] == 'Monthly-> averaged for each hour': methodsList.append(1)
                elif list[4] == 'Hourly': methodsList.append(2)
                elif list[4] == 'Daily' or list[4] == 'Daily-> averaged': methodsList.append(3)
                else:
                    checkData1 = False
                    warning = 'The timestep of the inputData is not recognized. Data must have a Ladybug header with a recognizable timestep.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            
            #Check to see if the input is temperature.
            tempInList = False
            farenheitCheck = False
            hourCheckList = []
            for list in listInfo:
                if 'Temperature' in list[2] or 'Universal Thermal Climate Index' in list[2]:
                    tempInList = True
                    if list[3] == 'F' or list[3] == 'F': farenheitCheck = True
                    if list[4] == 'Hourly' or list[4] == 'Monthly-> averaged for each hour': hourCheckList.append(1)
                    else: hourCheckList.append(0)
                else: hourCheckList.append(0)
            
            #Set defaults for bldgBalancePt_ and comfortModel.
            if farenheitCheck == False: bldgBalPt = 23.5
            else: bldgBalPt = 74.3
            comfortModel = 0
            
            #Check to see if the user has connected something for comfortModel.
            checkData2 = True
            try:
                if comfortModel_ != None:
                    if comfortModel_ >= 0 and comfortModel_ <= 3:
                        if comfortModel_ == 2:
                            outdoorDryBlubTest = False
                            for list in listInfo:
                                if 'Dry Bulb Temperature' in list[2] or 'Effective Temperature' in list[2]:
                                    if list[5] == (1,1,1) and list[6] == (12,31,24): outdoorDryBlubTest = True
                            if outdoorDryBlubTest == True: comfortModel = comfortModel_
                            else:
                                checkData2 = False
                                warning = 'To use the adaptive comfortModel_, one of the connected _inputData must be annual Outdoor Dry Bulb Temperature or Effective Temperature.'
                                print warning
                                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                        else: comfortModel = comfortModel_
                    else:
                        checkData2 = False
                        warning = 'comfortModel_ must be an integer from 0 to 3.'
                        print warning
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            except: pass
            
            #Check to see if the user has connected something for bldgBalancePt_.
            try:
                if bldgBalancePt_ != None: bldgBalPt = bldgBalancePt_
            except: pass
            
            #Set a default for stackValues_.
            if stackValues_ != None: stackValues = stackValues_
            else: stackValues = False
            
            #Set defaults for xScale and yScale.
            if _xScale_ != None: xS = _xScale_
            else: xS = 1
            if _yScale_ != None: yS = _yScale_
            else: yS = 1
            
            #Put everything into a final check.
            if checkData1 == True and checkData2 == True: checkData = True
            else: checkData = False
            
            return checkData, separatedLists, listInfo, methodsList, hourCheckList, comfortModel, bldgBalPt, stackValues, tempInList, farenheitCheck, xS, yS, conversionFac, lb_preparation, lb_visualization, lb_comfortModels
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1


def manageInput():
    #If some of the component inputs and outputs are not right, blot them out or change them.
    for input in range(9):
        if input == 1:
            ghenv.Component.Params.Input[input].NickName = "."
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        elif input == 2:
            ghenv.Component.Params.Input[input].NickName = "."
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]

def restoreInput():
    for input in range(9):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]


def makeChartCrvs(separatedLists, listInfo, methodsList, stackValues, xS, yS, lb_preparation, lb_visualization):
    #Read legend parameters
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar_, False)
    numSeg = int(numSeg)
    
    #Set some defaults.
    if legendFontSize == None: legendFontSize = 1
    
    #Make a chart boundary.
    chartAxes = []
    width = xS*120
    height = yS*50
    chartAxes.append(rc.Geometry.Rectangle3d(rc.Geometry.Plane.WorldXY, width, height).ToNurbsCurve())
    
    #Add in the segments for each month.
    monthLines = []
    textBasePts = []
    segWidth = 0
    for segmentNum in range(12):
        planeRec = rc.Geometry.Plane.WorldXY
        startPt = rc.Geometry.Point3d(segWidth, 0, 0)
        textBasePts.append(rc.Geometry.Point3d(segWidth + width/24 - legendFontSize*2, -legendFontSize*2, 0))
        planeRec.Origin = startPt
        monthLine = rc.Geometry.Rectangle3d(planeRec, width/12, height).ToNurbsCurve()
        monthLines.append(monthLine)
        segWidth = segWidth + (width/(12))
    chartAxes.extend(monthLines)
    
    #Make a chart with the number of y segments from the legendPar.
    gridLines = []
    yAxisLeftPts = []
    yAxisRightPts = []
    segHeight = 0
    for segmentNum in range(numSeg):
        gridLine = rc.Geometry.Line(0,segHeight,0,width,segHeight,0).ToNurbsCurve()
        gridLines.append(gridLine)
        yAxisLeftPts.append(rc.Geometry.Point3d(-8*legendFontSize,segHeight,0))
        yAxisRightPts.append(rc.Geometry.Point3d(legendFontSize+width,segHeight,0))
        segHeight = segHeight + (height/(int(numSeg) - 1))
    chartAxes.extend(gridLines)
    
    #Put in month labels.
    daysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    textSrfs = []
    for count, monthText in enumerate(monthNames):
        textSrf = lb_visualization.text2srf([monthText], [textBasePts[count]], legendFont, legendFontSize, legendBold)
        textSrfs.extend(textSrf[0])
    
    
    #Organize the data into lists of relevant info for the chart axes.
    unitsList = []
    dataTypeList = []
    unitsFormatList = []
    newDataMethodsList = []
    futureColorsList = []
    dataList = []
    
    for listCount, lst in enumerate(separatedLists):
        #Make a list of lists to hold monthly data.
        startList = []
        for month in range(12): startList.append([])
        
        #Organize data for monthly values.
        if methodsList[listCount] == 0:
            startMonth = listInfo[listCount][5][0]
            for item in lst:
                startList[startMonth-1].append(item)
                startMonth +=1
            
            #Organize data for monthly per hour values.
        elif methodsList[listCount] == 1:
            startMonth = listInfo[listCount][5][0]
            hourRange = listInfo[listCount][6][2]-listInfo[listCount][5][2]+1
            hourCumulative = 0
            
            for count, item in enumerate(lst):
                if count < hourRange+hourCumulative:
                    startList[startMonth-1].append(item)
                else:
                    hourCumulative +=hourRange
                    startMonth +=1
                    startList[startMonth-1].append(item)
            
            #Organize data for hourly values.
        elif methodsList[listCount] == 2:
            startMonth = listInfo[listCount][5][0]
            startDay = listInfo[listCount][5][1]
            hourRange = listInfo[listCount][6][2]-listInfo[listCount][5][2]+1
            monthCumulative = (daysPerMonth[startMonth-1] - startDay + 1)*hourRange
            hourCumulative = monthCumulative
            totalHr = 0
            
            for month in range(12):
                for day in range(daysPerMonth[month]):
                    startList[month].append([])
            
            for count, item in enumerate(lst):
                if count < hourCumulative:
                    if totalHr < hourRange:
                        startList[startMonth-1][startDay-1].append(item)
                        totalHr += 1
                    else:
                        startDay +=1
                        totalHr = 1
                        startList[startMonth-1][startDay-1].append(item)
                else:
                    startMonth +=1
                    startDay = 1
                    totalHr = 1
                    monthCumulative = daysPerMonth[startMonth-1]*hourRange
                    hourCumulative = hourCumulative + monthCumulative
                    startList[startMonth-1][startDay-1].append(item)
            
            #Organize data for daily values.
        elif methodsList[listCount] == 3:
            startMonth = listInfo[listCount][5][0]
            startDay = listInfo[listCount][5][1]
            cumulativeDays = daysPerMonth[startMonth-1] - startDay
            
            for monthCount, dayNum in enumerate(daysPerMonth):
                for dayCount in range(dayNum):
                    startList[monthCount].append([])
            
            for count, item in enumerate(lst):
                if count < cumulativeDays:
                    startList[startMonth-1][count-cumulativeDays + daysPerMonth[startMonth-1]-1].append(item)
                else:
                    startList[startMonth-1][count-cumulativeDays + daysPerMonth[startMonth-1]-1].append(item)
                    startDay = 1
                    startMonth +=1
                    if startMonth-1 != 12:
                        cumulativeDays = cumulativeDays + daysPerMonth[startMonth-1]
        
        #Append everything to the full list of data.
        if methodsList[listCount] == 0 and listInfo[listCount][3]+str(methodsList[listCount]) in unitsFormatList and stackValues == True:
            for formatCount, formatList in enumerate(unitsFormatList):
                if listInfo[listCount][3]+str(methodsList[listCount]) == formatList:
                    dataTypeList[formatCount].append(listInfo[listCount][2])
                    futureColorsList[formatCount].append(1)
                    for monthCount, item in enumerate(startList):
                        dataList[formatCount][monthCount].extend(item)
        elif methodsList[listCount] == 3 and listInfo[listCount][3]+str(methodsList[listCount]) in unitsFormatList and stackValues == True:
            for formatCount, formatList in enumerate(unitsFormatList):
                if listInfo[listCount][3]+str(methodsList[listCount]) == formatList:
                    dataTypeList[formatCount].append(listInfo[listCount][2])
                    futureColorsList[formatCount].append(1)
                    for monthCount, dayList in enumerate(startList):
                        for dayCount, item in enumerate(dayList):
                            dataList[formatCount][monthCount][dayCount].extend(item)
        else:
            dataList.append(startList)
            unitsFormatList.append(listInfo[listCount][3]+str(methodsList[listCount]))
            #Keep a running list of the different units and data types.
            unitsList.append(listInfo[listCount][3])
            dataTypeList.append([listInfo[listCount][2]])
            newDataMethodsList.append(methodsList[listCount])
            futureColorsList.append([0])
    
    #Make a function that checks the range of the data and comes up with a scaling factor for the data.
    def makeNumberLabels(valueList, leftOrRight, lowB, highB, method):
        cumulative = False
        if method == 0:
            valList = []
            for item in valueList:
                if len(item) > 1: cumulative = True
                valList.append(sum(item))
        elif method == 1:
            valList = []
            for monthList in valueList:
                for item in monthList:
                    valList.append(item)
        elif method == 2:
            valList = []
            for monthList in valueList:
                for dayList in monthList:
                    for item in dayList:
                        valList.append(item)
        elif method == 3:
            valList = []
            for monthList in valueList:
                for item in monthList:
                    if len(item) > 1: cumulative = True
                    valList.append(sum(item))
        
        valList.sort()
        if leftOrRight == True:
            if lowB == 'min': lowB = valList[0]
            if highB == 'max': highB = valList[-1]
        else:
            lowB = valList[0]
            highB = valList[-1]
        if cumulative == True: lowB = 0
        
        valRange = highB - lowB
        valStep = valRange/(numSeg-1)
        
        finalValues = []
        for num in range(numSeg):
            finalValues.append(str(round(lowB + num*valStep, 2)))
        
        return lowB, valRange, finalValues
    
    #Make lists of start values and scale factors for each of the data types.
    startVals = []
    scaleFacs = []
    tempVals = []
    tempScale = []
    avgMonthTemp = []
    
    #Put in right Y axis labels.
    basePt = rc.Geometry.Point3d(-9*legendFontSize, 0,0)
    yAxisSrf = lb_visualization.text2srf([dataTypeList[0][0] + ' (' + unitsList[0] + ')'], [basePt], legendFont, legendFontSize*1.5, legendBold)
    rotation = rc.Geometry.Transform.Rotation(math.pi/2, basePt)
    for srf in yAxisSrf[0]:
        srf.Transform(rotation)
    textSrfs.extend(yAxisSrf[0])
    lowVal1, valRange1, finalValues = makeNumberLabels(dataList[0], True, lowB, highB, newDataMethodsList[0])
    startVals.append(lowVal1)
    scaleFacs.append(valRange1/height)
    #Move the text based on how long it is.
    for ptCount, point in enumerate(yAxisLeftPts):
        textLen = str(finalValues[ptCount])
        textLen = len(list(textLen))
        ptTransl = rc.Geometry.Transform.Translation(8-textLen, legendFontSize*(-0.5), 0)
        point.Transform(ptTransl)
    
    if unitsList[0] == 'C' or unitsList[0] == 'C' or unitsList[0] == 'F' or unitsList[0] == 'F':
        tempVals.append(lowVal1)
        tempScale.append(valRange1)
        if dataTypeList[0][0] == 'Dry Bulb Temperature' or dataTypeList[0][0] == 'Effective Temperature':
            avgMonthTemp = dataList[0]
    for count, valText in enumerate(finalValues):
        textSrf = lb_visualization.text2srf([valText], [yAxisLeftPts[count]], legendFont, legendFontSize, legendBold)
        textSrfs.extend(textSrf[0])
    
    #Put in left Y axis label and get scales for the rest of the data.
    unit1 = unitsList[0]
    unit2 = None
    lowVal2 = None
    valRange2 = None
    axesTextSrf = []
    done = False
    for uCount, unit in enumerate(unitsList[1:]):
        if unit != unit1 and done == False:
            unit2 = unitsList[uCount+1]
            basePt = rc.Geometry.Point3d(9*legendFontSize+width, 0,0)
            yAxisSrf = lb_visualization.text2srf([dataTypeList[uCount+1][0] + ' (' + unitsList[uCount+1] + ')'], [basePt], legendFont, legendFontSize*1.5, legendBold)
            rotation = rc.Geometry.Transform.Rotation(math.pi/2, basePt)
            for srf in yAxisSrf[0]:
                srf.Transform(rotation)
            textSrfs.extend(yAxisSrf[0])
            lowVal2, valRange2, finalValues = makeNumberLabels(dataList[uCount+1], False, lowB, highB, newDataMethodsList[uCount+1])
            startVals.append(lowVal2)
            scaleFacs.append(valRange2/height)
            if unit2 == 'C' or unit2 == 'C' or unit2 == 'F' or unit2 == 'F':
                tempVals.append(lowVal1)
                tempScale.append(valRange1)
                if dataTypeList[uCount+1][0] == 'Dry Bulb Temperature' or dataTypeList[uCount+1][0] == 'Effective Temperature': avgMonthTemp = dataList[uCount+1]
            for count, valText in enumerate(finalValues):
                axesTextSrf = lb_visualization.text2srf([valText], [yAxisRightPts[count]], legendFont, legendFontSize, legendBold)
                textSrfs.extend(axesTextSrf[0])
            done = True
        elif unit == unit1:
            startVals.append(lowVal1)
            scaleFacs.append(valRange1/height)
            if unit1 == 'C' or unit1 == 'C' or unit1 == 'F' or unit1 == 'F':
                tempVals.append(lowVal1)
                tempScale.append(valRange1)
                if dataTypeList[uCount+1][0] == 'Dry Bulb Temperature' or dataTypeList[uCount+1][0] == 'Effective Temperature': avgMonthTemp = dataList[uCount+1]
        elif unit == unit2:
            startVals.append(lowVal2)
            scaleFacs.append(valRange2/height)
        else:
            lowVal, valRange, finalValues = makeNumberLabels(dataList[uCount+1], False, lowB, highB, newDataMethodsList[uCount+1])
            startVals.append(lowVal)
            scaleFacs.append(valRange/height)
            if unitsList[uCount+1] == 'C' or unitsList[uCount+1] == 'C' or unitsList[uCount+1] == 'F' or unitsList[uCount+1] == 'F':
                tempVals.append(lowVal1)
                tempScale.append(valRange1)
                if dataTypeList[uCount+1][0] == 'Dry Bulb Temperature' or dataTypeList[uCount+1][0] == 'Effective Temperature': avgMonthTemp = dataList[uCount+1]
    
    #Create a title.
    newlistInfo = str(listInfo[0][1])
    txtPt = rc.Geometry.Point3d(-10*legendFontSize, -7*legendFontSize, 0)
    titleTextSrfs = lb_visualization.text2srf([newlistInfo], [txtPt], legendFont, legendFontSize*1.5, legendBold)
    for txt in titleTextSrfs:
        textSrfs.extend(txt)
    
    # Group eveything together to use it for the bounding box.
    allGeo = []
    allGeo.extend(chartAxes)
    allGeo.extend(axesTextSrf)
    
    #Calculate a bounding box around everything that will help place the legend ad title.
    lb_visualization.calculateBB(allGeo, True)
    
    # Get the graph colors
    colors = lb_visualization.gradientColor(range(len(separatedLists)), 0, len(separatedLists)-1, customColors)
    
    #Create a legend for the data types.
    if legendBasePoint == None:
        basePt = rc.Geometry.Point3d(lb_visualization.BoundingBoxPar[0].X+legendFontSize, lb_visualization.BoundingBoxPar[0].Y, lb_visualization.BoundingBoxPar[0].Z)
    else: basePt = legendBasePoint
    BBYlength = lb_visualization.BoundingBoxPar[2]
    legendHeight = legendWidth = (BBYlength/10) * legendScale
    
    def legend(basePt, legendHeight, legendWidth, numOfSeg):
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
            
            txtPt = meshVertices[segNum * 2 + 1]
            textPt.append(rc.Geometry.Point3d(txtPt.X+(legendFontSize), txtPt.Y+(legendFontSize/0.5), txtPt.Z))
        
        return legendSrf, textPt
    
    #Make Legend Text
    legendSrf, textPt = legend(basePt, legendHeight, legendWidth, len(separatedLists))
    dataTypeListFlat = []
    for lst in dataTypeList: dataTypeListFlat.extend(lst)
    
    for legCount, legItem in enumerate(dataTypeListFlat):
        if methodsList[legCount] == 0: dataTypeListFlat[legCount] = legItem + ' \n(Monthly)'
        if methodsList[legCount] == 1: dataTypeListFlat[legCount] = legItem + ' \n(Hourly Average)'
        if methodsList[legCount] == 2: dataTypeListFlat[legCount] = legItem + ' \n(Hourly)'
        if methodsList[legCount] == 3: dataTypeListFlat[legCount] = legItem + ' \n(Daily)'
    
    legendTextSrfs = lb_visualization.text2srf(dataTypeListFlat, textPt, legendFont, legendFontSize, legendBold)
    
    #Create legend.
    legend = []
    fullLegTxt = lb_preparation.flattenList(legendTextSrfs)
    legend.extend(fullLegTxt)
    #color legend surfaces
    legendSrf = lb_visualization.colorMesh(colors, legendSrf)
    legend.append(legendSrf)
    
    #Reorder the list of colors to align with the dataList.
    newColors = []
    colorCount = 0
    for listCount, lst in enumerate(futureColorsList):
        newColors.append([])
        for color in lst:
            newColors[listCount].append(colors[colorCount])
            colorCount += 1
    
    return chartAxes, textSrfs, legend, basePt, dataList, newDataMethodsList, startVals, scaleFacs, newColors, width/12, tempVals, tempScale, avgMonthTemp


def plotData(dataList, dataMethodsList, startVals, scaleFacs, colors, xWidth):
    #Perform an analysis of the number of each data type so that I know how to space out the bars.
    numOfMethod = [0,0,0,0]
    for dataMethod in dataMethodsList:
        if dataMethod == 0: numOfMethod[0] = numOfMethod[0]+1
        elif dataMethod == 1: numOfMethod[1] = numOfMethod[1]+1
        elif dataMethod == 2: numOfMethod[2] = numOfMethod[2]+1
        elif dataMethod == 3: numOfMethod[3] = numOfMethod[3]+1
    try: monthWidth = xWidth/(numOfMethod[0]+2)
    except: monthWidth = xWidth
    
    dayWidth = []
    daysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    try:
        for num in daysPerMonth:
            dayWidth.append(xWidth/(numOfMethod[3]*num))
    except: dayWidth = xWidth
    
    #Make numbers to keep track of the number of data types that I have gone through.
    monthCt = 1
    dayStackCt = 0
    
    #Make lists to collect everything.
    dataMeshes = []
    dataCurves = []
    crvColors = []
    
    #Plot the data in each list.
    for dataCount, dataMethod in enumerate(dataMethodsList):
        
        #Plot the monthly data
        if dataMethod == 0:
            #Analyze any stacking effects correctly.
            stackList = []
            numberStacks = []
            for month in dataList[dataCount]: numberStacks.append(len(month))
            numberStacks.sort()
            topLen = numberStacks[-1]
            for i in range(topLen): stackList.append([])
            
            for monthCount, month in enumerate(dataList[dataCount]):
                stackBottom = 0
                
                for stackCount, stack in enumerate(month):
                    #Calculate the height of the bar
                    barHeight = (stack-startVals[dataCount])/scaleFacs[dataCount]
                    
                    #Generate the points that make the face of the mesh
                    facePt1 = rc.Geometry.Point3d((monthWidth*monthCt)+xWidth*monthCount, stackBottom, 0)
                    facePt2 = rc.Geometry.Point3d((monthWidth*monthCt+monthWidth)+xWidth*monthCount, stackBottom, 0)
                    facePt3 = rc.Geometry.Point3d((monthWidth*monthCt+monthWidth)+xWidth*monthCount, stackBottom+barHeight, 0)
                    facePt4 = rc.Geometry.Point3d((monthWidth*monthCt)+xWidth*monthCount, stackBottom+barHeight, 0)
                    
                    #Create the mesh
                    barMesh = rc.Geometry.Mesh()
                    for point in [facePt1, facePt2, facePt3, facePt4]:
                        barMesh.Vertices.Add(point)
                    barMesh.Faces.AddFace(0, 1, 2, 3)
                    # color the mesh faces.
                    barMesh.VertexColors.CreateMonotoneMesh(colors[dataCount][stackCount])
                    
                    #Add the mesh to the list and increase the bar height for the next item in the stack.
                    stackList[stackCount].append(barMesh)
                    stackBottom += barHeight
            
            monthCt += 1
            dataMeshes.extend(stackList)
        
        #Plot the avgMonthlyPerHour data.
        if dataMethod == 1:
            curvesList = []
            
            for monthCount, month in enumerate(dataList[dataCount]):
                #Generate the polyline points for each month.
                pLinePts = []
                for datCount, datum in enumerate(month):
                    point = rc.Geometry.Point3d(monthCount*xWidth + ((xWidth/23)*datCount), (datum-startVals[dataCount])/scaleFacs[dataCount], 0)
                    pLinePts.append(point)
                #Create the Pline.
                monthPline = rc.Geometry.PolylineCurve(pLinePts)
                curvesList.append(monthPline)
            
            dataCurves.append(curvesList)
            crvColors.append(colors[dataCount])
        
        #Plot the hourly data.
        if dataMethod == 2:
            curvesList = []
            
            for monthCount, month in enumerate(dataList[dataCount]):
                for dayCount, day in enumerate(month):
                    #Generate the polyline points for each day.
                    pLinePts = []
                    for datCount, datum in enumerate(day):
                        point = rc.Geometry.Point3d(monthCount*xWidth + ((xWidth/23)*datCount), (datum-startVals[dataCount])/scaleFacs[dataCount], 0)
                        pLinePts.append(point)
                    #Create the Pline.
                    dayPline = rc.Geometry.PolylineCurve(pLinePts)
                    curvesList.append(dayPline)
            
            dataCurves.append(curvesList)
            crvColors.append(colors[dataCount])
        
        #Plot the daily data
        if dataMethod == 3:
            #Analyze any stacking effects correctly.
            stackList = []
            numberStacks = []
            for month in dataList[dataCount]:
                for day in month:
                    numberStacks.append(len(day))
            numberStacks.sort()
            topLen = numberStacks[-1]
            for i in range(topLen): stackList.append([])
            
            
            for monthCount, month in enumerate(dataList[dataCount]):
                dayCt = 0
                for dayCount, day in enumerate(month):
                    stackBottom = 0
                    
                    for stackCount, stack in enumerate(day):
                        #Calculate the height of the bar
                        barHeight = (stack-startVals[dataCount])/scaleFacs[dataCount]
                        
                        #Generate the points that make the face of the mesh
                        facePt1 = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt)+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, stackBottom, 0)
                        facePt2 = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt+dayWidth[monthCount])+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, stackBottom, 0)
                        facePt3 = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt+dayWidth[monthCount])+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, stackBottom+barHeight, 0)
                        facePt4 = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt)+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, stackBottom+barHeight, 0)
                        
                        #Create the mesh
                        barMesh = rc.Geometry.Mesh()
                        for point in [facePt1, facePt2, facePt3, facePt4]:
                            barMesh.Vertices.Add(point)
                        barMesh.Faces.AddFace(0, 1, 2, 3)
                        # color the mesh faces.
                        barMesh.VertexColors.CreateMonotoneMesh(colors[dataCount][stackCount])
                        
                        #Add the mesh to the list and increase the bar height for the next item in the stack.
                        stackList[stackCount].append(barMesh)
                        stackBottom += barHeight
                    dayCt +=1
            dataMeshes.extend(stackList)
            dayStackCt += 1
    
    
    return dataMeshes, dataCurves, crvColors


def drawComfRange(comfortModel, bldgBalPt, farenheitCheck, xWidth, tempVals, tempScale, avgMonthTemp, yS, lb_comfortModels):
    comfortBand = []
    
    #Create the comfort bands for the PMV model.
    if comfortModel == 1:
        if farenheitCheck == False: offsetDist = 3.2
        else: offsetDist = 5.76
        
        lowB = bldgBalPt - offsetDist
        highB = bldgBalPt + offsetDist
        
        monthCt = 0
        for month in range(12):
            #Calculate the height of the bar
            barTop = ((highB-tempVals[0])/tempScale)*yS
            barBottom = ((lowB-tempVals[0])/tempScale)*yS
            
            #Generate the points that make the face of the mesh
            facePt1 = rc.Geometry.Point3d((xWidth*monthCt), barBottom, -sc.doc.ModelAbsoluteTolerance)
            facePt2 = rc.Geometry.Point3d((xWidth*monthCt)+xWidth, barBottom, -sc.doc.ModelAbsoluteTolerance)
            facePt3 = rc.Geometry.Point3d((xWidth*monthCt)+xWidth, barTop, -sc.doc.ModelAbsoluteTolerance)
            facePt4 = rc.Geometry.Point3d((xWidth*monthCt), barTop, -sc.doc.ModelAbsoluteTolerance)
            
            #Create the comfort Brep
            barBrep = rc.Geometry.Brep.CreateFromCornerPoints(facePt1, facePt2, facePt3, facePt4, sc.doc.ModelAbsoluteTolerance)
            
            #Add the mesh to the list and increase the bar height for the next item in the stack.
            comfortBand.append(barBrep)
            monthCt +=1
    
    #Create the comfort bands for the Adaptive model.
    if comfortModel == 2:
        if farenheitCheck == False: offsetDist = 2
        else: offsetDist = 3.6
        
        if farenheitCheck == False: distToShift = bldgBalPt - 23.5
        else: distToShift = bldgBalPt - 74.3
        
        # Get the average monthly temperatures from the temperature data.
        avgTemps = []
        for month in avgMonthTemp:
            try: month = lb_preparation.flattenList(month)
            except: month[0]
            avgTemp = sum(month)/len(month)
            if farenheitCheck == False:
                if avgTemp > 10:
                    comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortASH55(avgTemp, avgTemp, avgTemp, 0, None)
                    avgTemps.append(comfTemp+distToShift)
                else: avgTemps.append(None)
            else:
                if avgTemp > 50:
                    cTemp = (float(avgTemp)-32) * 5 / 9
                    cComfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortASH55(cTemp, cTemp, cTemp, 0, None)
                    comfTemp = (float(cComfTemp)-32) * 5 / 9
                    avgTemps.append(comfTemp+distToShift)
                else: avgTemps.append(None)
        
        monthCt = 0
        for month in range(12):
            if avgTemps[month] != None:
                #Calculate the height of the bar
                barTop = ((avgTemps[month]+offsetDist-tempVals[0])/tempScale)*yS
                barBottom = ((avgTemps[month]-offsetDist-tempVals[0])/tempScale)*yS
                
                #Generate the points that make the face of the mesh
                facePt1 = rc.Geometry.Point3d((xWidth*monthCt), barBottom, -sc.doc.ModelAbsoluteTolerance)
                facePt2 = rc.Geometry.Point3d((xWidth*monthCt)+xWidth, barBottom, -sc.doc.ModelAbsoluteTolerance)
                facePt3 = rc.Geometry.Point3d((xWidth*monthCt)+xWidth, barTop, -sc.doc.ModelAbsoluteTolerance)
                facePt4 = rc.Geometry.Point3d((xWidth*monthCt), barTop, -sc.doc.ModelAbsoluteTolerance)
                
                #Create the comfort Brep
                barBrep = rc.Geometry.Brep.CreateFromCornerPoints(facePt1, facePt2, facePt3, facePt4, sc.doc.ModelAbsoluteTolerance)
                
                #Add the mesh to the list and increase the bar height for the next item in the stack.
                comfortBand.append(barBrep)
            monthCt +=1
    
    #Create the comfort bands for the UTCI model.
    if comfortModel == 3:
        if farenheitCheck == False:
            startPt = 17.5
            offsetDist = 8.5
        else:
            startPt = 63.5
            offsetDist = 15.3
        
        lowB = startPt - offsetDist
        highB = startPt + offsetDist
        
        monthCt = 0
        for month in range(12):
            #Calculate the height of the bar
            barTop = ((highB-tempVals[0])/tempScale)*yS
            barBottom = ((lowB-tempVals[0])/tempScale)*yS
            
            #Generate the points that make the face of the mesh
            facePt1 = rc.Geometry.Point3d((xWidth*monthCt), barBottom, -sc.doc.ModelAbsoluteTolerance)
            facePt2 = rc.Geometry.Point3d((xWidth*monthCt)+xWidth, barBottom, -sc.doc.ModelAbsoluteTolerance)
            facePt3 = rc.Geometry.Point3d((xWidth*monthCt)+xWidth, barTop, -sc.doc.ModelAbsoluteTolerance)
            facePt4 = rc.Geometry.Point3d((xWidth*monthCt), barTop, -sc.doc.ModelAbsoluteTolerance)
            
            #Create the comfort Brep
            barBrep = rc.Geometry.Brep.CreateFromCornerPoints(facePt1, facePt2, facePt3, facePt4, sc.doc.ModelAbsoluteTolerance)
            
            #Add the mesh to the list and increase the bar height for the next item in the stack.
            comfortBand.append(barBrep)
            monthCt +=1
    
    
    return comfortBand


def main(separatedLists, listInfo, methodsList, hourCheckList, comfortModel, bldgBalPt, stackValues, tempInList, farenheitCheck, xS, yS, conversionFac, lb_preparation, lb_visualization, lb_comfortModels):
    #Make the chart curves.
    graphAxes, graphLabels, legend, legendBasePt, dataList, newDataMethodsList, startVals, scaleFacs, colors, xWidth, tempVals, tempScale, avgMonthTemp = makeChartCrvs(separatedLists, listInfo, methodsList, stackValues, xS, yS, lb_preparation, lb_visualization)
    
    #Plot the data on the chart.
    dataMesh, dataCurves, curveColors = plotData(dataList, newDataMethodsList, startVals, scaleFacs, colors, xWidth)
    
    #If the user has requested a comfort range, then draw it.
    comfortBand = None
    if tempInList == True and comfortModel != 0:
        comfortBand = drawComfRange(comfortModel, bldgBalPt, farenheitCheck, xWidth, tempVals, (tempScale[0]/50), avgMonthTemp, yS, lb_comfortModels)
    
    #If the basePoint is specified and it's different than the origin, move everything.
    if _basePoint_ != None and _basePoint_ != rc.Geometry.Point3d.Origin:
        moveTransform = rc.Geometry.Transform.Translation(_basePoint_.X, _basePoint_.Y, _basePoint_.Z)
        
        for geo in graphAxes: geo.Transform(moveTransform)
        for geo in graphLabels: geo.Transform(moveTransform)
        for geo in legend: geo.Transform(moveTransform)
        for geo in comfortBand: geo.Transform(moveTransform)
        legendBasePt.Transform(moveTransform)
        for lst in dataMesh:
            for geo in lst: geo.Transform(moveTransform)
        for lst in dataCurves:
            for geo in lst: geo.Transform(moveTransform)
    
    
    return dataMesh, dataCurves, curveColors, graphAxes, graphLabels, legend, legendBasePt, comfortBand


#Check the inputs.
checkData = False
tempInList = True
initCheck = checkTheInputs()
if initCheck != -1:
    checkData, separatedLists, listInfo, methodsList, hourCheckList, comfortModel, bldgBalPt, stackValues, tempInList, farenheitCheck, xS, yS, conversionFac, lb_preparation, lb_visualization, lb_comfortModels = initCheck

#Manage the input.
if checkData == True and tempInList == False: manageInput()
else: restoreInput()

#Run the main function if all is good.
if checkData == True:
    result = main(separatedLists, listInfo, methodsList, hourCheckList, comfortModel, bldgBalPt, stackValues, tempInList, farenheitCheck, xS, yS, conversionFac, lb_preparation, lb_visualization, lb_comfortModels)
    if result != -1:
        dataMeshInit, dataCurvesInit, dataCrvColorsInit, graphAxes, graphLabels, legend, legendBasePt, comfortBand = result
        
        dataMesh = DataTree[Object]()
        dataCurves = DataTree[Object]()
        dataCrvColors = DataTree[Object]()
        
        for listCount, lst in enumerate(dataMeshInit):
            for item in lst:
                dataMesh.Add(item, GH_Path(listCount))
        
        for listCount, lst in enumerate(dataCurvesInit):
            for item in lst:
                dataCurves.Add(item, GH_Path(listCount))
        
        for listCount, lst in enumerate(dataCrvColorsInit):
            for item in lst:
                dataCrvColors.Add(item, GH_Path(listCount))


ghenv.Component.Params.Output[7].Hidden = True

