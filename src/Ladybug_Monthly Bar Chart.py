# This component creates a bar chart of monthly or avrMonthlyPerHour data.
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Chris Mackey and Mostapha Sadeghipour Roudsari <Chris@MackeyArchitecture.com and Sadeghipour@gmail.com> 
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
Use this component to make a bar chart in the Rhino scene of any monhtly or avrMonthyPerHour climate data or simulation data.
_
This component can also plot daily or hourly data but, for visualizing this type of data, it is recommended that you use the "Ladybug_3D Chart" component.
-
Provided by Ladybug 0.0.62
    
    Args:
        _inputData: A list of input data to plot.  This should usually be data out of the "Ladybug_Average Data" component or monthly data from an energy simulation but can also be hourly or daily data from the "Ladybug_Import EPW."  However, it is recommended that you use the "Ladybug_3D Chart" component for daily or hourly data as this is usually a bit clearer.
        comfortModel_: An optional interger to draw the comfort model on the chart.  Choose from the following:
                        0 - No comfort range
                        1 - PMV comfort range (indoor)
                        2 - Adaptive confort range (naturally ventilated)
                        3 - UTCI Comfort (outdoor)
                        Note that this option is only available when temperature is connected so, by default, it is set to 0 for no comfort range.
        bldgBalancePt_: An optional float value to represent the outdoor temperature at which the energy passively flowing into a building is equal to that flowing out of the building.  This is usually a number that is well below the comfort temperture (~ 12C - 18C) since the internal heat of a building and its insulation keep the interior warmer then the exterior.  However, by default, this is set to 23.5C for fully outdoor conditions.
        stackValues_: Set to 'True' if you have multiple connected monthly or daily _inputData with the same units and want them to be drawn as bars stacked on top of each other.  Otherwise, all bars for monthly/daily data will be placed next to each other.  The default is set to 'False' to have these bars placed next to each other.
        plotFromZero_: Set to 'True' to have the component plot all bar values starting from zero (as opposed from the bottom of the chart, which might be a negative number).  This is useful when you are plotting the terms of an energy balance where you want gains to be above zero and losses to be below.  It can be detrimental if you are plotting temperatures in degrees celcius and do not want negative values to go below zero.  As such, the default is set to 'False' to not plot from zero.
        altTitle_: An optional text string to replace the default title of the chart of the chart.  The default is set to pick out the location of the data connected to 'inputData.'
        altYAxisTitle_: An optional text string to replace the default Y-Axis label of the chart.  This can also be a list of 2 y-axis titles if there are two different types of data connected to _inputData.  The default is set to pick out the names of the first (and possibly the second) list connected to the 'inputData.'
        _basePoint_: An optional point with which to locate the 3D chart in the Rhino Model.  The default is set to the Rhino origin at (0,0,0).
        _xScale_: The scale of the X axis of the graph. The default is set to 1 and this will plot the X axis with a length of 120 Rhino model units (for 12 months of the year).
        _yScale_: The scale of the Y axis of the graph. The default is set to 1 and this will plot the Y axis with a length of 50 Rhino model units.
        _labelPtsOffset_: A number in Rhino model units that represents the distance between the top of bars on the chart and the location where the dataLabelPts are. If you set this value to 0, you can use the dataLabelPts to create a polyline of monthly values.  The default is autocalculated based on the scale of the chart.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        bakeIt_ : An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options:
            0 (or False) - No geometry will be baked into the Rhino scene (this is the default).
            1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. 
            2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry.
    Returns:
        readMe!: ...
        dataMesh: A series of meshes that represent the different monthly (or daily) input data.  Multiple lists of meshes will be output for several input data streams.
        dataCurves: A list of curves that represent the different avrMonthyPerHour and hourly input data. Multiple lists of curves will be output for several input data streams.
        dataCrvColors: A list of colors that correspond to the dataCurves above.  Hook this up to the 'swatch' input of the native Grasshopper 'Preview' component and the curves above up to the 'geometry input to preview the curves with their repective color.
        graphAxes: A list of curves representing the axes of the chart.
        graphLabels: A list of text meshes representing the time periods corresponding to the input data
        title: A title for the chart.  By default, this is just the location of the data but you can input a custom title with the altTitle_ input.
        titleBasePt: The title base point, which can be used to move the title in relation to the chart with the grasshopper "move" component.
        legend: A legend of the chart that tells what each connected data stram's color is. Connect this output to a grasshopper "Geo" component in order to preview the legend in the Rhino scene.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the chart with the grasshopper "move" component.
        dataLabelPts: A series of points that mark where each of the bars or lines of the chart lie.  You can use this to label the bars or lines with numerical values using a native grasshopper "text tag" component and the data that you have connected to the _inputData of this component.
        comfortBand: A series of meshes that represent the comfort range in each month according to the input comfortModel_.
"""

ghenv.Component.Name = "Ladybug_Monthly Bar Chart"
ghenv.Component.NickName = 'BarChart'
ghenv.Component.Message = 'VER 0.0.62\nAUG_01_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.59\nJAN_24_2016
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
2: ["bldgBalancePt_", "An optional float value to represent the outdoor temperature at which the energy passively flowing into a building is equal to that flowing out of the building.  This is usually a number that is well below the comfort temperture (~ 12C - 18C) since the internal heat of a building and its insulation keep the interior warmer then the exterior.  However, by default, this is set to 23.5C for fully outdoor conditions."]
}



def checkTheInputs():
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
                if list[4] == 'Monthly' or list[4] == 'Monthly-> averaged' or list[4] == 'Monthly-> total' or list[4] == 'Monthly-> averaged for each day': methodsList.append(0)
                elif list[4] == 'Monthly-> averaged for each hour' or list[4] == 'Monthly-> total for each hour': methodsList.append(1)
                elif list[4] == 'Hourly': methodsList.append(2)
                elif list[4] == 'Daily' or list[4] == 'Daily-> averaged' or list[4] == 'Daily-> total': methodsList.append(3)
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
                    if list[4] == 'Hourly' or list[4] == 'Monthly-> averaged for each hour' or list[4] == 'Monthly-> total for each hour': hourCheckList.append(1)
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
                                if 'Dry Bulb Temperature' in list[2]:
                                    outdoorDryBlubTest = True
                            if outdoorDryBlubTest == True: comfortModel = comfortModel_
                            else:
                                checkData2 = False
                                warning = 'To use the adaptive comfortModel_, one of the connected _inputData must be a temperature value.'
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
            
            #Set a default for plotFromZero_.
            if plotFromZero_ != None: plotFromZero = plotFromZero_
            else: plotFromZero = False
            
            #Set defaults for xScale and yScale.
            if _xScale_ != None: xS = _xScale_
            else: xS = 1
            if _yScale_ != None: yS = _yScale_
            else: yS = 1
            
            #Check the altYAxisTitle_ input.
            checkData3 = True
            if len(altYAxisTitle_) <=2: pass
            else:
                checkData3 = False
                warning = 'altYAxisTitle_ cannot be more than 2 values (one for each side of the chart).'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            
            # Organize the data tree of legend parameters.
            legendPs = []
            for i in range(legendPar_.BranchCount):
                legendPs.append(legendPar_.Branch(i))
            if len(legendPs) == 0: legendPs.append([])
            
            #Put everything into a final check.
            if checkData1 == True and checkData2 == True and checkData3 == True: checkData = True
            else: checkData = False
            
            return checkData, separatedLists, listInfo, methodsList, hourCheckList, comfortModel, bldgBalPt, stackValues, plotFromZero, tempInList, farenheitCheck, xS, yS, conversionFac, legendPs, lb_preparation, lb_visualization, lb_comfortModels
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1


def manageInput():
    #If some of the component inputs and outputs are not right, blot them out or change them.
    for input in range(3):
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
    for input in range(3):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]


def makeChartCrvs(separatedLists, listInfo, methodsList, stackValues, plotFromZero, xS, yS, legendPs, lb_preparation, lb_visualization):
    #Read legend parameters
    lowBNotImp, highBNotImp, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPs[0], False)
    numSeg = int(numSeg)
    
    #Set some defaults.
    if legendFontSize == None: legendFontSize = 1
    allText = []
    allTextPt = []
    
    ### ANALYZE THE INPUT DATA TO SEE WHAT WE HAVE.
    daysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    #Organize the data into lists of relevant info for the chart axes.
    unitsList = []
    dataTypeList = []
    unitsFormatList = []
    newDataMethodsList = []
    futureColorsList = []
    dataList = []
    lowBList = []
    highBList = []
    
    for listCount, lst in enumerate(separatedLists):
        #Read the legendPar for the data set.
        try:
            lowBInit, highBInit, numSegNotImportant, customColorsNotImportant, legendBasePointNotImportant, legendScaleNotImportant, legendFontNotImportant, legendFontSizeNotImportant, legendBoldNotImportant, decimalPlacesNotImportant, removeLessThanNotImportant = lb_preparation.readLegendParameters(legendPs[listCount], False)
            lowBList.append(lowBInit)
            highBList.append(highBInit)
        except:
            lowBList.append('min')
            highBList.append('max')
        
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
    
    ### DRAW AN INITIAL BOUNDARY AROUND THE CHART AND DRAW MONTH LABELS.
    def areAllListsEmpty(masterList):
        return all(i == [] for i in masterList)
    
    monthsWeNeed = []
    for dat in dataList:
        for count, mon in enumerate(dat):
            if mon != [] and not areAllListsEmpty(mon) and count not in monthsWeNeed:
                monthsWeNeed.append(count)
    monthsWeNeed.sort()
    startMon = monthsWeNeed[0]
    endMon = monthsWeNeed[-1]
    totMons = range(startMon, endMon+1)
    
    #Make a chart boundary.
    chartAxes = []
    width = xS*10*len(totMons)
    height = yS*50
    chartAxes.append(rc.Geometry.Rectangle3d(rc.Geometry.Plane.WorldXY, width, height).ToNurbsCurve())
    
    #Add in the segments for each month.
    monthLines = []
    textBasePts = []
    segWidth = 0
    for segmentNum in range(len(totMons)):
        planeRec = rc.Geometry.Plane.WorldXY
        startPt = rc.Geometry.Point3d(segWidth, 0, 0)
        textBasePts.append(rc.Geometry.Point3d(segWidth + width/(len(totMons)*2) - legendFontSize*2, -legendFontSize*2, 0))
        planeRec.Origin = startPt
        monthLine = rc.Geometry.Rectangle3d(planeRec, width/len(totMons), height).ToNurbsCurve()
        monthLines.append(monthLine)
        segWidth = segWidth + (width/len(totMons))
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
    monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    textSrfs = []
    for count, monthInt in enumerate(totMons):
        textSrf = lb_visualization.text2srf([monthNames[monthInt]], [textBasePts[count]], legendFont, legendFontSize, legendBold)
        textSrfs.extend(textSrf[0])
    allText.extend(monthNames)
    allTextPt.extend(textBasePts)
    
    # Remove unneeded months from the data list.
    if len(totMons) != 12:
        newDataList = []
        for datCount, dat in enumerate(dataList):
            newDataList.append([])
            for count, mon in enumerate(dat):
                if count in totMons:
                    newDataList[datCount].append(mon)
        dataList = newDataList
    
    ### Correctly Label the Y-Values.
    #Have a value that tracks whether we have a stacked value graph with negative values.
    if plotFromZero: negativeTrigger = True
    else: negativeTrigger = False
    
    #Make a function that checks the range of the data and comes up with a scaling factor for the data.
    def makeNumberLabels(valueList, leftOrRight, lowB, highB, method):
        newNegativeTrigger = negativeTrigger
        cumulative = False
        if method == 0:
            valList = []
            negValList= []
            for item in valueList:
                if len(item) > 1:
                    cumulative = True
                    posVals = []
                    negVals = []
                    for val in item:
                        if val > 0: posVals.append(val)
                        else: negVals.append(val)
                    valList.append(sum(posVals))
                    negValList.append(sum(negVals))
                else:
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
            negValList= []
            for monthList in valueList:
                for item in monthList:
                    if len(item) > 1:
                        cumulative = True
                        posVals = []
                        negVals = []
                        for val in item:
                            if val > 0: posVals.append(val)
                            else: negVals.append(val)
                        valList.append(sum(posVals))
                        negValList.append(sum(negVals))
                    else:
                        valList.append(sum(item))
                    valList.append(sum(item))
        
        valList.sort()
        if lowB == 'min': lowB = valList[0]
        if highB == 'max': highB = valList[-1]
        if cumulative == True:
            if sum(negValList) < 0:
                lowB = negValList[0]
                newNegativeTrigger = True
                if -lowB < highB: lowB = -highB
                else:
                    highB = -lowB
            else: lowB = 0
        
        if plotFromZero and not lowB < 0:
            lowB = 0
        
        valRange = highB - lowB
        valStep = valRange/(numSeg-1)
        
        finalValues = []
        for num in range(numSeg):
            finalValues.append(str(round(lowB + num*valStep, 2)))
        
        return lowB, valRange, finalValues, newNegativeTrigger
    
    #Make lists of start values and scale factors for each of the data types.
    startVals = []
    scaleFacs = []
    tempVals = []
    tempScale = []
    avgMonthTemp = []
    
    #Put in right Y axis labels.
    basePt = rc.Geometry.Point3d(-9*legendFontSize, 0,0)
    allTextPt.append(basePt)
    if len(altYAxisTitle_) == 0:
        yAxisSrf = lb_visualization.text2srf([dataTypeList[0][0] + ' (' + unitsList[0] + ')'], [basePt], legendFont, legendFontSize*1.5, legendBold)
        allText.append(dataTypeList[0][0] + ' (' + unitsList[0] + ')')
    else:
        yAxisSrf = lb_visualization.text2srf([altYAxisTitle_[0]], [basePt], legendFont, legendFontSize*1.5, legendBold)
        allText.append(altYAxisTitle_[0])
    rotation = rc.Geometry.Transform.Rotation(math.pi/2, basePt)
    for srf in yAxisSrf[0]:
        srf.Transform(rotation)
    textSrfs.extend(yAxisSrf[0])
    lowVal1, valRange1, finalValues, negativeTrigger = makeNumberLabels(dataList[0], True, lowBList[0], highBList[0], newDataMethodsList[0])
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
        if 'Temperature' in dataTypeList[0][0] or 'Universal Thermal Climate Index' in dataTypeList[0][0]:
            avgMonthTemp = dataList[0]
    for count, valText in enumerate(finalValues):
        textSrf = lb_visualization.text2srf([valText], [yAxisLeftPts[count]], legendFont, legendFontSize, legendBold)
        textSrfs.extend(textSrf[0])
    allTextPt.extend(yAxisLeftPts)
    allText.extend(finalValues)
    
    #Put in left Y axis label and get scales for the rest of the data.
    unit1 = unitsList[0]
    unit2 = None
    lowVal2 = None
    valRange2 = None
    axesTextSrf = []
    done = False
    for uCount, unit in enumerate(unitsList[1:]):
        if unit.strip('') != unit1.strip('') and done == False:
            unit2 = unitsList[uCount+1]
            basePt = rc.Geometry.Point3d(9*legendFontSize+width, 0,0)
            allTextPt.append(basePt)
            if len(altYAxisTitle_) !=2:
                yAxisSrf = lb_visualization.text2srf([dataTypeList[uCount+1][0] + ' (' + unitsList[uCount+1] + ')'], [basePt], legendFont, legendFontSize*1.5, legendBold)
                allText.append(dataTypeList[uCount+1][0] + ' (' + unitsList[uCount+1] + ')')
            else:
                yAxisSrf = lb_visualization.text2srf([altYAxisTitle_[1]], [basePt], legendFont, legendFontSize*1.5, legendBold)
                allText.append(altYAxisTitle_[1])
            rotation = rc.Geometry.Transform.Rotation(math.pi/2, basePt)
            for srf in yAxisSrf[0]:
                srf.Transform(rotation)
            textSrfs.extend(yAxisSrf[0])
            lowVal2, valRange2, finalValues, negativeTrigger = makeNumberLabels(dataList[uCount+1], False, lowBList[uCount+1], highBList[uCount+1], newDataMethodsList[uCount+1])
            startVals.append(lowVal2)
            scaleFacs.append(valRange2/height)
            if unit2 == 'C' or unit2 == 'C' or unit2 == 'F' or unit2 == 'F':
                tempVals.append(lowVal2)
                tempScale.append(valRange2)
                if 'Temperature' in dataTypeList[uCount+1][0] or 'Universal Thermal Climate Index' in dataTypeList[uCount+1][0]: avgMonthTemp = dataList[uCount+1]
            for count, valText in enumerate(finalValues):
                axesTextSrf = lb_visualization.text2srf([valText], [yAxisRightPts[count]], legendFont, legendFontSize, legendBold)
                textSrfs.extend(axesTextSrf[0])
            allTextPt.extend(yAxisRightPts)
            allText.extend(finalValues)
            done = True
        elif unit.strip('') == unit1.strip(''):
            startVals.append(lowVal1)
            scaleFacs.append(valRange1/height)
            if unit1 == 'C' or unit1 == 'C' or unit1 == 'F' or unit1 == 'F':
                tempVals.append(lowVal1)
                tempScale.append(valRange1)
                if 'Temperature' in dataTypeList[uCount+1][0] or 'Universal Thermal Climate Index' in dataTypeList[uCount+1][0]: avgMonthTemp = dataList[uCount+1]
        elif unit.strip('') == unit2.strip(''):
            startVals.append(lowVal2)
            scaleFacs.append(valRange2/height)
        else:
            lowVal, valRange, finalValues, negativeTrigger = makeNumberLabels(dataList[uCount+1], False, lowBList[uCount+1], highBList[uCount+1], newDataMethodsList[uCount+1])
            startVals.append(lowVal)
            scaleFacs.append(valRange/height)
            if unitsList[uCount+1] == 'C' or unitsList[uCount+1] == 'C' or unitsList[uCount+1] == 'F' or unitsList[uCount+1] == 'F':
                tempVals.append(lowVal1)
                tempScale.append(valRange1)
                if 'Temperature' in dataTypeList[uCount+1][0] or 'Universal Thermal Climate Index' in dataTypeList[uCount+1][0]: avgMonthTemp = dataList[uCount+1]
    
    #Create a title.
    if altTitle_ == None: newlistInfo = str(listInfo[0][1])
    else: newlistInfo = altTitle_
    titleTxtPt = rc.Geometry.Point3d(-10*legendFontSize, -7*legendFontSize, 0)
    titleTextSrfs = lb_visualization.text2srf([newlistInfo], [titleTxtPt], legendFont, legendFontSize*1.5, legendBold)
    titleTextSrfs = lb_preparation.flattenList(titleTextSrfs)
    allTextPt.append(titleTxtPt)
    allText.append(newlistInfo)
    
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
        basePt = rc.Geometry.Point3d(lb_visualization.BoundingBoxPar[0].X+(legendFontSize*2), lb_visualization.BoundingBoxPar[0].Y, lb_visualization.BoundingBoxPar[0].Z)
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
    allTextPt.extend(textPt)
    allText.extend(dataTypeListFlat)
    
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
    
    return chartAxes, textSrfs, titleTextSrfs, titleTxtPt, legend, basePt, dataList, totMons, newDataMethodsList, startVals, scaleFacs, newColors, width/(len(totMons)), tempVals, tempScale, avgMonthTemp, negativeTrigger, allText, allTextPt, legendFontSize, legendFont, decimalPlaces


def plotData(dataList, dataMethodsList, startVals, scaleFacs, colors, xWidth, yS, conversionFac, negativeTrigger, dataPtOffset):
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
    dataLabelPts = []
    
    #Plot the data in each list.
    for dataCount, dataMethod in enumerate(dataMethodsList):
        dataLabelPtsInit = []
        
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
                negativeStackBotom = 0
                
                for stackCount, stack in enumerate(month):
                    #Calculate the height of the bar
                    if negativeTrigger: barHeight = (stack)/scaleFacs[dataCount]
                    else: barHeight = (stack-startVals[dataCount])/scaleFacs[dataCount]
                    
                    #Generate the points that make the face of the mesh
                    if barHeight > 0:
                        facePt1 = rc.Geometry.Point3d((monthWidth*monthCt)+xWidth*monthCount, stackBottom, 0)
                        facePt2 = rc.Geometry.Point3d((monthWidth*monthCt+monthWidth)+xWidth*monthCount, stackBottom, 0)
                        facePt3 = rc.Geometry.Point3d((monthWidth*monthCt+monthWidth)+xWidth*monthCount, stackBottom+barHeight, 0)
                        facePt4 = rc.Geometry.Point3d((monthWidth*monthCt)+xWidth*monthCount, stackBottom+barHeight, 0)
                    else:
                        facePt1 = rc.Geometry.Point3d((monthWidth*monthCt)+xWidth*monthCount, negativeStackBotom, 0)
                        facePt2 = rc.Geometry.Point3d((monthWidth*monthCt+monthWidth)+xWidth*monthCount, negativeStackBotom, 0)
                        facePt3 = rc.Geometry.Point3d((monthWidth*monthCt+monthWidth)+xWidth*monthCount, negativeStackBotom+barHeight, 0)
                        facePt4 = rc.Geometry.Point3d((monthWidth*monthCt)+xWidth*monthCount, negativeStackBotom+barHeight, 0)
                    
                    #Create the mesh
                    barMesh = rc.Geometry.Mesh()
                    for point in [facePt1, facePt2, facePt3, facePt4]:
                        barMesh.Vertices.Add(point)
                    barMesh.Faces.AddFace(0, 1, 2, 3)
                    # color the mesh faces.
                    barMesh.VertexColors.CreateMonotoneMesh(colors[dataCount][stackCount])
                    
                    #Append a point for text labels to the list.
                    if stackCount == len(month)-1:
                        if dataPtOffset == None:
                            dataLabelPoint = rc.Geometry.Point3d((monthWidth*monthCt+(monthWidth/2))+xWidth*monthCount, stackBottom+barHeight+(yS/conversionFac), 0)
                        else:
                            dataLabelPoint = rc.Geometry.Point3d((monthWidth*monthCt+(monthWidth/2))+xWidth*monthCount, stackBottom+barHeight+dataPtOffset, 0)
                        dataLabelPtsInit.append(dataLabelPoint)
                    
                    #Add the mesh to the list and increase the bar height for the next item in the stack.
                    stackList[stackCount].append(barMesh)
                    if barHeight > 0: stackBottom += barHeight
                    else: negativeStackBotom += barHeight
            
            #If the negative trigger is true, move the values to the zero position.
            if negativeTrigger:
                zeroingTransform = rc.Geometry.Transform.Translation(0,-startVals[dataCount]/scaleFacs[dataCount], 0)
                for monthMeshList in stackList:
                    for monthMesh in monthMeshList: monthMesh.Transform(zeroingTransform)
            
            dataLabelPts.append(dataLabelPtsInit)
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
                #Append a point for text labels to the list.
                if dataPtOffset == None:
                    dataLabelPtsInit.extend(pLinePts)
                else:
                    for pt in pLinePts:
                        dataLabelPtsInit.append(rc.Geometry.Point3d(pt.X, pt.Y+dataPtOffset, pt.Z))
            
            dataLabelPts.append(dataLabelPtsInit)
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
                    #Append a point for text labels to the list.
                    if dataPtOffset == None:
                        dataLabelPtsInit.extend(pLinePts)
                    else:
                        for pt in pLinePts:
                            dataLabelPtsInit.append(rc.Geometry.Point3d(pt.X, pt.Y+dataPtOffset, pt.Z))
            
            dataLabelPts.append(dataLabelPtsInit)
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
                    negativeStackBotom = 0
                    
                    for stackCount, stack in enumerate(day):
                        #Calculate the height of the bar
                        if negativeTrigger: barHeight = (stack)/scaleFacs[dataCount]
                        else: barHeight = (stack-startVals[dataCount])/scaleFacs[dataCount]
                        
                        #Generate the points that make the face of the mesh
                        if barHeight > 0:
                            facePt1 = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt)+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, stackBottom, 0)
                            facePt2 = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt+dayWidth[monthCount])+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, stackBottom, 0)
                            facePt3 = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt+dayWidth[monthCount])+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, stackBottom+barHeight, 0)
                            facePt4 = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt)+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, stackBottom+barHeight, 0)
                        else:
                            facePt1 = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt)+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, negativeStackBotom, 0)
                            facePt2 = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt+dayWidth[monthCount])+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, negativeStackBotom, 0)
                            facePt3 = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt+dayWidth[monthCount])+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, negativeStackBotom+barHeight, 0)
                            facePt4 = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt)+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, negativeStackBotom+barHeight, 0)
                        
                        #Create the mesh
                        barMesh = rc.Geometry.Mesh()
                        for point in [facePt1, facePt2, facePt3, facePt4]:
                            barMesh.Vertices.Add(point)
                        barMesh.Faces.AddFace(0, 1, 2, 3)
                        # color the mesh faces.
                        barMesh.VertexColors.CreateMonotoneMesh(colors[dataCount][stackCount])
                        
                        #Append a point for text labels to the list.
                        if stackCount == len(day)-1:
                            if dataPtOffset == None:
                                dataLabelPoint = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt+(dayWidth[monthCount]/2))+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, stackBottom+barHeight+(yS/(conversionFac*4)), 0)
                            else:
                                dataLabelPoint = rc.Geometry.Point3d((dayWidth[monthCount]*dayCt+(dayWidth[monthCount]/2))+(dayWidth[monthCount]*(dayCt+dayStackCt)*(numOfMethod[3]-1))+xWidth*monthCount, stackBottom+barHeight+dataPtOffset, 0)
                            dataLabelPtsInit.append(dataLabelPoint)
                        
                        #Add the mesh to the list and increase the bar height for the next item in the stack.
                        stackList[stackCount].append(barMesh)
                        if barHeight > 0: stackBottom += barHeight
                        else: negativeStackBotom += barHeight
                    dayCt +=1
            
            #If the negative trigger is true, move the values to the zero position.
            if negativeTrigger:
                zeroingTransform = rc.Geometry.Transform.Translation(0,-startVals[dataCount]/scaleFacs[dataCount], 0)
                for monthMeshList in stackList:
                    for monthMesh in monthMeshList: monthMesh.Transform(zeroingTransform)
            
            dataLabelPts.append(dataLabelPtsInit)
            dataMeshes.extend(stackList)
            dayStackCt += 1
    
    
    return dataMeshes, dataCurves, crvColors, dataLabelPts


def drawComfRange(comfortModel, bldgBalPt, farenheitCheck, xWidth, monthsInChart, tempVals, tempScale, avgMonthTemp, yS, lb_comfortModels):
    comfortBand = []
    
    #Create the comfort bands for the PMV model.
    if comfortModel == 1:
        if farenheitCheck == False: offsetDist = 3.2
        else: offsetDist = 5.76
        
        lowB = bldgBalPt - offsetDist
        highB = bldgBalPt + offsetDist
        
        monthCt = 0
        for month in range(len(monthsInChart)):
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
                #if avgTemp > 10:
                comfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortASH55(avgTemp, avgTemp, avgTemp, 0, None)
                avgTemps.append(comfTemp+distToShift)
                #else: avgTemps.append(None)
            else:
                #if avgTemp > 50:
                cTemp = (float(avgTemp)-32) * 5 / 9
                cComfTemp, distFromTarget, lowTemp, upTemp, comf, condition = lb_comfortModels.comfAdaptiveComfortASH55(cTemp, cTemp, cTemp, 0, None)
                comfTemp = (float(cComfTemp)-32) * 5 / 9
                avgTemps.append(comfTemp+distToShift)
                #else: avgTemps.append(None)
        
        monthCt = 0
        for month in range(len(monthsInChart)):
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
        for month in range(len(monthsInChart)):
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


def main(separatedLists, listInfo, methodsList, hourCheckList, comfortModel, bldgBalPt, stackValues, plotFromZero, tempInList, farenheitCheck, xS, yS, dataPtOffset, conversionFac, legendPs, lb_preparation, lb_visualization, lb_comfortModels):
    #Make the chart curves.
    graphAxes, graphLabels, titleTxt, titleTxtPt, legend, legendBasePt, dataList, monthsInChart, newDataMethodsList, startVals, scaleFacs, colors, xWidth, tempVals, tempScale, avgMonthTemp, negativeTrigger, allText, allTextPt, textSize, legendFont, decimalPlaces = makeChartCrvs(separatedLists, listInfo, methodsList, stackValues, plotFromZero, xS, yS, legendPs, lb_preparation, lb_visualization)
    
    #Plot the data on the chart.
    try:
        dataMesh, dataCurves, curveColors, dataLabelPts = plotData(dataList, newDataMethodsList, startVals, scaleFacs, colors, xWidth, yS, conversionFac, negativeTrigger, dataPtOffset)
    except ArithmeticError:
        warning = "All values are zero.  Chart cannot be created."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    
    #If the user has requested a comfort range, then draw it.
    comfortBand = None
    if tempInList == True and comfortModel != 0:
        comfortBand = drawComfRange(comfortModel, bldgBalPt, farenheitCheck, xWidth, monthsInChart, tempVals, (tempScale[0]/50), avgMonthTemp, yS, lb_comfortModels)
    
    #If the basePoint is specified and it's different than the origin, move everything.
    if _basePoint_ != None and _basePoint_ != rc.Geometry.Point3d.Origin:
        moveTransform = rc.Geometry.Transform.Translation(_basePoint_.X, _basePoint_.Y, _basePoint_.Z)
        
        for geo in graphAxes: geo.Transform(moveTransform)
        for geo in graphLabels: geo.Transform(moveTransform)
        for geo in legend: geo.Transform(moveTransform)
        try:
            for geo in comfortBand: geo.Transform(moveTransform)
        except: pass
        legendBasePt.Transform(moveTransform)
        for geo in titleTxt:geo.Transform(moveTransform)
        titleTxtPt.Transform(moveTransform)
        for lst in dataMesh:
            for geo in lst: geo.Transform(moveTransform)
        for lst in dataCurves:
            for geo in lst: geo.Transform(moveTransform)
        for lst in dataLabelPts:
            for geo in lst: geo.Transform(moveTransform)
    
    if bakeIt_ > 0:
        #Make a single mesh for all data.
        finalJoinedMesh = rc.Geometry.Mesh()
        for meshList in dataMesh:
            for mesh in meshList: finalJoinedMesh.Append(mesh)
        #Make a single list of curves for all data.
        allDataCurves = []
        for crvList in dataCurves:
            for crv in crvList: allDataCurves.append(crv)
        studyLayerName = 'MONTHLY_CHARTS'
        # check the study type
        try:
            if 'key:location/dataType/units/frequency/startsAt/endsAt' in _inputData[0]: placeName = _inputData[1]
            else: placeName = 'alternateLayerName'
        except: placeName = 'alternateLayerName'
        newLayerIndex, l = lb_visualization.setupLayers(None, 'LADYBUG', placeName, studyLayerName, False, False, 0, 0)
        if bakeIt_ == 1: lb_visualization.bakeObjects(newLayerIndex, finalJoinedMesh, legend[-1], allText, allTextPt, textSize, legendFont, graphAxes+allDataCurves, decimalPlaces, 2)
        else: lb_visualization.bakeObjects(newLayerIndex, finalJoinedMesh, legend[-1], allText, allTextPt, textSize, legendFont, graphAxes+allDataCurves, decimalPlaces, 2, False)
    
    return dataMesh, dataCurves, curveColors, graphAxes, graphLabels, titleTxt, titleTxtPt, legend, legendBasePt, dataLabelPts, comfortBand


#Check the inputs.
checkData = False
tempInList = True
initCheck = checkTheInputs()
if initCheck != -1:
    checkData, separatedLists, listInfo, methodsList, hourCheckList, comfortModel, bldgBalPt, stackValues, plotFromZero, tempInList, farenheitCheck, xS, yS, conversionFac, legendPs, lb_preparation, lb_visualization, lb_comfortModels = initCheck

#Manage the input.
if checkData == True and tempInList == False: manageInput()
else: restoreInput()

#Run the main function if all is good.
if checkData == True:
    result = main(separatedLists, listInfo, methodsList, hourCheckList, comfortModel, bldgBalPt, stackValues, plotFromZero, tempInList, farenheitCheck, xS, yS, _labelPtsOffset_, conversionFac, legendPs, lb_preparation, lb_visualization, lb_comfortModels)
    if result != -1:
        dataMeshInit, dataCurvesInit, dataCrvColorsInit, graphAxes, graphLabels, title, titleBasePt, legend, legendBasePt, dataLabelPtsPy, comfortBand = result
        
        dataMesh = DataTree[Object]()
        dataCurves = DataTree[Object]()
        dataCrvColors = DataTree[Object]()
        dataLabelPts = DataTree[Object]()
        
        for listCount, lst in enumerate(dataMeshInit):
            for item in lst:
                dataMesh.Add(item, GH_Path(listCount))
        
        for listCount, lst in enumerate(dataCurvesInit):
            for item in lst:
                dataCurves.Add(item, GH_Path(listCount))
        
        for listCount, lst in enumerate(dataCrvColorsInit):
            for item in lst:
                dataCrvColors.Add(item, GH_Path(listCount))
        
        for listCount, lst in enumerate(dataLabelPtsPy):
            for item in lst:
                dataLabelPts.Add(item, GH_Path(listCount))


ghenv.Component.Params.Output[7].Hidden = True
ghenv.Component.Params.Output[9].Hidden = True
ghenv.Component.Params.Output[10].Hidden = True