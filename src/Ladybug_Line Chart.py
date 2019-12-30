# This component creates a bar chart of monthly or avrMonthlyPerHour data.
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Chris Mackey <chris@ladybug.tools> 
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
Use this component to make a line chart in the Rhino scene of any data with a ladybug header on it.

-
Provided by Ladybug 0.0.68
    
    Args:
        _inputData: A list of input data to plot.  This should usually be data out of the "Ladybug_Average Data" component or monthly data from an energy simulation but can also be hourly or daily data from the "Ladybug_Import EPW."  However, it is recommended that you use the "Ladybug_3D Chart" component for daily or hourly data as this is usually a bit clearer.
        chartType_: An integer that sets the type of chart that will be drawn.  Choose from the following options:
            0 = Normal - Data will be plotted as polylines right next to each other.
            1 = Stacked - Data will be plotted as lines stacked on top of one another.
            2 = Stacked Area - Data will be plotted as filled areas stacked on top of one another.
        altTitle_: An optional text string to replace the default title of the chart of the chart.  The default is set to pick out the location of the data connected to 'inputData.'
        altYAxisTitle_: An optional text string to replace the default Y-Axis label of the chart.  This can also be a list of 2 y-axis titles if there are two different types of data connected to _inputData.  The default is set to pick out the names of the first (and possibly the second) list connected to the 'inputData.'
        _basePoint_: An optional point with which to locate the 3D chart in the Rhino Model.  The default is set to the Rhino origin at (0,0,0).
        _xScale_: The scale of the X axis of the graph. The default is set to 1 and this will plot the X axis with a length of 120 Rhino model units (for 12 months of the year).
        _yScale_: The scale of the Y axis of the graph. The default is set to 1 and this will plot the Y axis with a length of 50 Rhino model units.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        bakeIt_ : An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options:
            0 (or False) - No geometry will be baked into the Rhino scene (this is the default).
            1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. 
            2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry.
    Returns:
        readMe!: ...
        dataMesh: A list of meshes that represent the different input data.
        dataCurves: A list of curves that represent the different input data.
        dataCrvColors: A list of colors that correspond to the dataCurves above.  Hook this up to the 'swatch' input of the native Grasshopper 'Preview' component and the curves above up to the 'geometry input to preview the curves with their repective color.
        graphAxes: A list of curves representing the axes of the chart.
        graphLabels: A list of text meshes representing the time periods corresponding to the input data
        title: A title for the chart.  By default, this is just the location of the data but you can input a custom title with the altTitle_ input.
        titleBasePt: The title base point, which can be used to move the title in relation to the chart with the grasshopper "move" component.
        legend: A legend of the chart that tells what each connected data stram's color is. Connect this output to a grasshopper "Geo" component in order to preview the legend in the Rhino scene.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the chart with the grasshopper "move" component.
"""

ghenv.Component.Name = "Ladybug_Line Chart"
ghenv.Component.NickName = 'LineChart'
ghenv.Component.Message = 'VER 0.0.68\nJAN_01_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.59\nJAN_24_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh
import copy
import math

def checkTheInputs(lb_preparation, lb_visualization, lb_comfortModels):
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
        
        #Set a default for chartType_.
        if chartType_ != None:
            chartType = chartType_
        else: chartType = 0
        
        #Set defaults for xScale and yScale.
        if _xScale_ != None: xS = _xScale_
        else: xS = 1
        if _yScale_ != None: yS = _yScale_
        else: yS = 1
        
        #Check the altYAxisTitle_ input.
        checkData = True
        if len(altYAxisTitle_) <=2: pass
        else:
            checkData = False
            warning = 'altYAxisTitle_ cannot be more than 2 values (one for each side of the chart).'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        
        # Organize the data tree of legend parameters.
        legendPs = []
        for i in range(legendPar_.BranchCount):
            legendPs.append(legendPar_.Branch(i))
        if len(legendPs) == 0: legendPs.append([])
        
        return checkData, separatedLists, listInfo, chartType, xS, yS, legendPs

def makeChartCrvs(separatedLists, listInfo, chartType, xS, yS, legendPs, lb_preparation, lb_visualization):
    #Read legend parameters
    lowBNotImp, highBNotImp, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPs[0], False)
    numSeg = int(numSeg)
    
    #Set some defaults.
    if legendFontSize == None: legendFontSize = 1
    allText = []
    allTextPt = []
    
    unitsList = []
    dataTypeList = []
    futureColorsList = []
    dataList = []
    lowBList = []
    highBList = []
    dataLenList = []
    stackIndices = []
    
    ### ANALYZE THE INPUT DATA TO SEE WHAT WE HAVE ###
    for listCount, lst in enumerate(separatedLists):
        #Read the legendPar for the data set.
        try:
            lowBInit, highBInit, numSegNotImportant, customColorsNotImportant, legendBasePointNotImportant, legendScaleNotImportant, legendFontNotImportant, legendFontSizeNotImportant, legendBoldNotImportant, decimalPlacesNotImportant, removeLessThanNotImportant = lb_preparation.readLegendParameters(legendPs[listCount], False)
            lowBList.append(lowBInit)
            highBList.append(highBInit)
        except:
            lowBList.append('min')
            highBList.append('max')
        dataLenList.append(len(lst))
        
        #Append everything to the full list of data.
        if listInfo[listCount][3] in unitsList and chartType > 0:
            stackIndices.append([])
            for formatCount, formatList in enumerate(unitsList):
                if listInfo[listCount][3] == formatList:
                    stackIndices[listCount].append(formatCount)
        else:
            stackIndices.append(-1)
        
        dataList.append(lst)
        unitsList.append(listInfo[listCount][3])
        dataTypeList.append([listInfo[listCount][2]])
        futureColorsList.append([0])
    
    
    ### DRAW AN INITIAL BOUNDARY AROUND THE CHART ###
    chartAxes = []
    textSrfs = []
    
    #Make a chart boundary.
    dataLenList.sort()
    maxLen = dataLenList[-1]
    width = xS * 0.1 * (maxLen-1)
    height = yS * 50
    chartAxes.append(rc.Geometry.Rectangle3d(rc.Geometry.Plane.WorldXY, width, height).ToNurbsCurve())
    
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
    
    # Correctly Label the Y-Values.
    negativeTrigger = False
    
    # Make a function that checks the range of the data and comes up with a scaling factor for the data.
    def makeNumberLabels(valueList, leftOrRight, lowB, highB):
        newNegativeTrigger = negativeTrigger
        cumulative = False
        valList = copy.deepcopy(valueList)
        
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
        
        valRange = highB - lowB
        valStep = valRange/(numSeg-1)
        
        finalValues = []
        for num in range(numSeg):
            finalValues.append(str(round(lowB + num*valStep, 2)))
        
        return lowB, valRange, finalValues, newNegativeTrigger
    
    #Make lists of start values and scale factors for each of the data types.
    startVals = []
    scaleFacs = []
    
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
    lowVal1, valRange1, finalValues, negativeTrigger = makeNumberLabels(dataList[0], True, lowBList[0], highBList[0])
    if valRange1 == 0:
        valRange1 = 1
        finalValues = []
        valStep = valRange1/(numSeg-1)
        for num in range(numSeg):
            finalValues.append(str(round(lowVal1 + num*valStep, 2)))
        warning = "You have a list where all values are zero and this is would cause the Y-Axis to go from 0 to 0. \n" + \
        "As a result the Y-Axis has automatically beeen set to go from 0 to 1.  Use legendPar to change this."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    startVals.append(lowVal1)
    scaleFacs.append(valRange1/height)
    #Move the text based on how long it is.
    for ptCount, point in enumerate(yAxisLeftPts):
        textLen = str(finalValues[ptCount])
        textLen = len(list(textLen))
        ptTransl = rc.Geometry.Transform.Translation(8-textLen, legendFontSize*(-0.5), 0)
        point.Transform(ptTransl)
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
            lowVal2, valRange2, finalValues, negativeTrigger = makeNumberLabels(dataList[uCount+1], False, lowBList[uCount+1], highBList[uCount+1])
            startVals.append(lowVal2)
            scaleFacs.append(valRange2/height)
            for count, valText in enumerate(finalValues):
                axesTextSrf = lb_visualization.text2srf([valText], [yAxisRightPts[count]], legendFont, legendFontSize, legendBold)
                textSrfs.extend(axesTextSrf[0])
            allTextPt.extend(yAxisRightPts)
            allText.extend(finalValues)
            done = True
        elif unit.strip('') == unit1.strip(''):
            startVals.append(lowVal1)
            scaleFacs.append(valRange1/height)
        elif unit.strip('') == unit2.strip(''):
            startVals.append(lowVal2)
            scaleFacs.append(valRange2/height)
        else:
            lowVal, valRange, finalValues, negativeTrigger = makeNumberLabels(dataList[uCount+1], False, lowBList[uCount+1], highBList[uCount+1])
            startVals.append(lowVal)
            scaleFacs.append(valRange/height)
    
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
            #Generate the legend mesh for the _inputdata
            mesh = rc.Geometry.Mesh()
            mesh.Vertices.Add(meshVertices[segNum * 2]) #0
            mesh.Vertices.Add(meshVertices[segNum * 2 + 1]) #1
            mesh.Vertices.Add(meshVertices[segNum * 2 + 2]) #2
            mesh.Vertices.Add(meshVertices[segNum * 2 + 3]) #3
            mesh.Faces.AddFace(0, 1, 3, 2)
            legendSrf.Append(mesh)
            # Text Points
            txtPt = meshVertices[segNum * 2 + 1]
            textPt.append(rc.Geometry.Point3d(txtPt.X+(legendFontSize), txtPt.Y+(legendFontSize/0.5), txtPt.Z))
        
        return legendSrf, textPt
    
    #Make Legend Text
    legendSrf, textPt = legend(basePt, legendHeight, legendWidth, len(separatedLists))
    dataTypeListFlat = []
    for lst in dataTypeList: dataTypeListFlat.extend(lst)
    
    legendTextSrfs = lb_visualization.text2srf(dataTypeListFlat, textPt, legendFont, legendFontSize, legendBold)
    allTextPt.extend(textPt)
    allText.extend(dataTypeListFlat)
    #Create legend.
    legend = []
    #color legend surfaces
    legendSrf = lb_visualization.colorMesh(colors, legendSrf)
    legend.append(legendSrf)
    fullLegTxt = lb_preparation.flattenList(legendTextSrfs)   
    legend.extend(fullLegTxt) 
    
    # set the width to be useful for the plotted data.
    dataWidth = width + (xS * 0.1)
    
    return chartAxes, textSrfs, titleTextSrfs, titleTxtPt, legend, basePt, dataList, dataWidth, width, startVals, scaleFacs, colors, stackIndices, negativeTrigger, allText, allTextPt, legendFontSize, legendFont, decimalPlaces


def plotData(dataLists, startVals, scaleFacs, dataWidth, width, colors, stackIndices, yS, chartType):
    # make lists to collect everything.
    dataMeshes = []
    dataCurves = []
    crvColors = []
    stackPositions = []
    
    # create the first curve.
    bottomLine = rc.Geometry.LineCurve(rc.Geometry.Point3d.Origin, rc.Geometry.Point3d(width,0,0))
    bottomLines = []
    
    # plot the data in each list.
    for dataCount, dataList in enumerate(dataLists):
        pLinePts = []
        interval = dataWidth / len(dataList)
        stackPositions.append([])
        
        for count, val in enumerate(dataList):
            # generate the polyline points for each day.
            yPos = (val - startVals[dataCount]) / scaleFacs[dataCount]
            
            if stackIndices[dataCount] != -1:
                #for c in stackIndices[dataCount]:
                yPos = yPos + stackPositions[stackIndices[dataCount][-1]][count]
            stackPositions[dataCount].append(yPos)
            point = rc.Geometry.Point3d(count * interval, yPos, 0)
            pLinePts.append(point)
        
        # create the Pline.
        pLine = rc.Geometry.PolylineCurve(pLinePts)
        dataCurves.append(pLine)
        
        if chartType == 2:
            # find the bottom line
            bottomLines.append(pLine)
            if stackIndices[dataCount] == -1:
                theBottom = bottomLine
            else:
                theBottom = bottomLines[stackIndices[dataCount][-1]]
            
            # make a list of curves surrounding the mesh
            leftSideLine = rc.Geometry.LineCurve(theBottom.PointAtStart, pLine.PointAtStart)
            rightSideLine = rc.Geometry.LineCurve(theBottom.PointAtEnd, pLine.PointAtEnd)
            crvsToJoin = [theBottom, rightSideLine, pLine, leftSideLine]
            
            # create the joined curve
            joinedLine = rc.Geometry.PolylineCurve.JoinCurves(crvsToJoin)[0]
            joinedBrep = rc.Geometry.Brep.CreatePlanarBreps(joinedLine)
            
            # create the mesh from the curve
            joinedMesh = rc.Geometry.Mesh()
            if joinedBrep is not None:
                for br in joinedBrep:
                    mesh = rc.Geometry.Mesh.CreateFromBrep(br)[0]
                    joinedMesh.Append(mesh)
                joinedMesh.VertexColors.CreateMonotoneMesh(colors[dataCount])
                dataMeshes.append(joinedMesh)
            else:
                dataMeshes.append(None)
    
    return dataMeshes, dataCurves

def moveGeo(graphAxes, graphLabels, title, titleBasePt, legend, legendBasePt, dataMesh, dataCurves, allTextPt):
    moveTransform = rc.Geometry.Transform.Translation(_basePoint_.X, _basePoint_.Y, _basePoint_.Z)
    
    for geo in graphAxes:
        geo.Transform(moveTransform)
    for geo in graphLabels:
        geo.Transform(moveTransform)
    for geo in legend:
        geo.Transform(moveTransform)
    for geo in title:
        geo.Transform(moveTransform)
    legendBasePt.Transform(moveTransform)
    for geo in dataMesh:
        geo.Transform(moveTransform)
    for geo in dataCurves:
        geo.Transform(moveTransform)
    for pt in allTextPt:
        pt.Transform(moveTransform)

def bakeGeo(dataMesh, dataCurves):
    #Make a single mesh for all data.
    finalJoinedMesh = rc.Geometry.Mesh()
    for mesh in dataMesh:
        finalJoinedMesh.Append(mesh)
    #Make a single list of curves for all data.
    allDataCurves = []
    for crv in dataCurves:
        allDataCurves.append(crv)
    studyLayerName = 'LINE_CHARTS'
    # check the study type
    try:
        if 'key:location/dataType/units/frequency/startsAt/endsAt' in _inputData[0]: placeName = _inputData[1]
        else: placeName = 'alternateLayerName'
    except: placeName = 'alternateLayerName'
    newLayerIndex, l = lb_visualization.setupLayers(None, 'LADYBUG', placeName, studyLayerName, False, False, 0, 0)
    if bakeIt_ == 1: lb_visualization.bakeObjects(newLayerIndex, finalJoinedMesh, legend[-1], allText, allTextPt, textSize, legendFont, graphAxes+allDataCurves, decimalPlaces, 2)
    else: lb_visualization.bakeObjects(newLayerIndex, finalJoinedMesh, legend[-1], allText, allTextPt, textSize, legendFont, graphAxes+allDataCurves, decimalPlaces, 2, False)


#If Ladybug is not flying or is an older version, give a warning.
initCheck = True

#Ladybug check.
w = gh.GH_RuntimeMessageLevel.Warning
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): initCheck = False
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


if initCheck == True:
    checkData, separatedLists, listInfo, chartType, xS, yS, legendPs = checkTheInputs(lb_preparation, lb_visualization, lb_comfortModels)
    if checkData == True:
        # make the chart curves.
        graphAxes, graphLabels, title, titleBasePt, legend, legendBasePt, dataList, dataWidth, xWidth, startVals, scaleFacs, dataCrvColors, stackIndices, negativeTrigger, allText, allTextPt, textSize, legendFont, decimalPlaces = makeChartCrvs(separatedLists, listInfo, chartType, xS, yS, legendPs, lb_preparation, lb_visualization)
        
        # plot the data on the chart.
        dataMesh, dataCurves = plotData(dataList, startVals, scaleFacs, dataWidth, xWidth, dataCrvColors, stackIndices, yS, chartType)
        
        # move the geometry if the basepoint is not the origin.
        if _basePoint_ != None and _basePoint_ != rc.Geometry.Point3d.Origin:
            moveGeo(graphAxes, graphLabels, title, titleBasePt, legend, legendBasePt, dataMesh, dataCurves, allTextPt)
        
        # bake geometry if need be.
        if bakeIt_ == True:
            bakeGeo(dataMesh, dataCurves)

ghenv.Component.Params.Output[7].Hidden = True
ghenv.Component.Params.Output[9].Hidden = True