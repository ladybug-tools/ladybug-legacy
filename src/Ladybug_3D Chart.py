# This component separates numbers and strings from an input list
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Draw 3D Charts
-
Provided by Ladybug 0.0.52
    
    Args:
        _inputData: List of input data for plot
        _xScale_: Scale of the X axis of the graph. Connect a list for multiple graphs
        _yScale_: Scale of the Y axis of the graph. Connect a list for multiple graphs
        _zScale_: Scale of the Z axis of the graph. Connect a list for multiple graphs
        _xCount_: Default is set to 24, as 24 hours. Change it in regard to your input data
        legendPar_: Input legend parameters from the Ladybug Legend Parameters component
        _basePoint_: Input a point to locate the 3D chart base point
        condStatement_ : Conditional statement (e.g. a > 25)
        bakeIt_ : Bake the chart as a colored mesh
    Returns:
        readMe!: ...
        graphMesh: 3D chart as a mesh
        legend: Legend(s) of the chart(s). Connect to Geo for preview
        legendBasePts: Legend base point, mainly for presentation purposes
        conditionalPts: A list of 3D points which represent the time steps that conditional statement is correct
"""

ghenv.Component.Name = "Ladybug_3D Chart"
ghenv.Component.NickName = '3DChart'
ghenv.Component.Message = 'VER 0.0.52\nNOV_01_2013'

import scriptcontext as sc
import Rhino as rc
import System
from math import pi as PI

from clr import AddReference
AddReference('Grasshopper')
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


def main(inputData, basePoint, xScale, yScale, zScale, xCount, legendPar, condStatement, bakeIt):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        conversionFac = lb_preparation.checkUnits()
        # copy the custom code here
        
        if len(inputData)!=0 and inputData[0]!=None:
            
            # check conditional statement for the whole year
            titleStatement = -1
            if condStatement:
                print 'Checking conditional statements...'
                # send all data and statement to a function and return back
                # True, False Pattern and condition statement
                titleStatement, patternList = checkConditionalStatement(inputData, condStatement)
            if titleStatement == -1:
                patternList = [False] * 8760
                titleStatement = False
            
            
            # separate the data
            indexList, listInfo = lb_preparation.separateList(inputData, lb_preparation.strToBeFound)
        
            #separate total, diffuse and direct radiations
            separatedLists = []
            for i in range(len(indexList)-1):
                selList = []
                [selList.append(float(x)) for x in inputData[indexList[i]+7:indexList[i+1]]]
                separatedLists.append(selList)
            
            
            res = [[],[], [], []]
            # legendBasePoints = []
            for i, results in enumerate(separatedLists):
                
                if 'Month' in listInfo[i][4]: xExtraFactor = 10
                else: xExtraFactor = 1
                try:
                    if float(xScale[i])!=0:
                        try:xSCC = 10 * float(xScale[i]) * xExtraFactor /conversionFac
                        except: xSCC = 10 * xExtraFactor/conversionFac
                    else: xSCC = 10 * xExtraFactor/conversionFac
                except: xSCC = 10 * xExtraFactor/conversionFac
                # this is because I rotate the geometry 90 degrees!
                ySC = abs(xSCC)
                
                try:
                    if float(yScale[i])!=0:
                        try:ySCC = 10 * float(yScale[i])/conversionFac
                        except: ySCC = 10/conversionFac
                    else: ySCC = 10/conversionFac
                except: ySCC = 10/conversionFac
                xSC = abs(ySCC)
                
                # read running period
                stMonth, stDay, stHour, endMonth, endDay, endHour = lb_visualization.readRunPeriod((listInfo[i][5], listInfo[i][6]), False)
                
                try:
                    if float(xCount[i])!=0:
                        try:xC = float(xCount[i])
                        except: xC = abs(endHour - stHour) + 1
                    else: xC = abs(endHour - stHour) + 1
                except: xC = abs(endHour - stHour) + 1
                xC = int(xC)
                
                dataType = listInfo[i][2]
                
                if ('Rad' in dataType): extraFactor = 100
                elif ('Hum' in dataType): extraFactor = 5
                elif ('Illuminance' in dataType): extraFactor = 5000
                elif ('Wind Direction' in dataType): extraFactor = 30
                else: extraFactor = 1
                #if xExtraFactor !=1: extraFactor = extraFactor/3
                
                try:
                    if float(zScale[i])>=0:
                        try:zSC = 10 * float(zScale[i])/(conversionFac*extraFactor)
                        except: zSC = 10/(conversionFac*extraFactor); print 'zScale is set to ' + ("%.2f" % (1/extraFactor)) + ' for ' + dataType
                    else: zSC = 10/(conversionFac*extraFactor); print 'zScale is set to ' + ("%.2f" % (1/extraFactor)) + ' for ' + dataType
                except: zSC = 10/(conversionFac*extraFactor); print 'zScale is set to ' +  ("%.2f" % (1/extraFactor)) + ' for ' + dataType
                zSC = abs(zSC)
                
                # read legend parameters
                lowB, highB, numSeg, customColors, legendBasePoint, legendScale = lb_preparation.readLegendParameters(legendPar, False)
                
                # draw the graph
                mesh, conditionalPoints = lb_visualization.chartGeometry(results, xC, xSC, ySC, zSC, patternList, lb_preparation.getCenPt(basePoint))
                colors = lb_visualization.gradientColor(results, lowB, highB, customColors)
                coloredChart = lb_visualization.colorMeshChart(mesh, xC, colors, lb_preparation.getCenPt(basePoint))
                
                lb_visualization.calculateBB([coloredChart], True)
                
                try: movingDist = -1.5 * lb_visualization.BoundingBoxPar[2] # moving distance for sky domes
                except: movingDist = 0
                
                movingVector = rc.Geometry.Vector3d(0, i * movingDist,0)
                coloredChart.Translate(movingVector)
                titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo[i]],lb_visualization.BoundingBoxPar, legendScale)
                
                legendTitle = listInfo[i][3]
                placeName = listInfo[i][1]
                dataType = listInfo[i][2]
                
                # create legend geometries
                legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(results
                    , lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale)
                
                textPt.append(titlebasePt)
                
                ptCount  = 0
                for pt in textPt:
                    ptLocation = rc.Geometry.Point(pt)
                    ptLocation.Translate(movingVector) # move it to the right place
                    textPt[ptCount] = rc.Geometry.Point3d(ptLocation.Location)
                    ptCount += 1
                
                cenPt = lb_preparation.getCenPt(basePoint)
                rotatoion = rc.Geometry.Transform.Rotation(rc.Geometry.Vector3d.YAxis, rc.Geometry.Vector3d.XAxis, cenPt)
                
                for ptCount, pt in enumerate(conditionalPoints):
                    pt.Transform(rotatoion)
                    ptLocation = rc.Geometry.Point(pt)
                    ptLocation.Translate(movingVector) # move it to the right place
                    conditionalPoints[ptCount] = rc.Geometry.Point3d(ptLocation.Location)
                    
                    
                for crv in legendTextCrv:
                    for c in crv: c.Translate(movingVector)
                for crv in titleTextCurve:
                    for c in crv: c.Translate(movingVector)
                
                # generate legend colors
                legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
                
                # color legend surfaces
                legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
                legendSrfs.Translate(movingVector) # move it to the right place
                
                if legendBasePoint == None:
                    nlegendBasePoint = lb_visualization.BoundingBoxPar[0]
                    movedLegendBasePoint = rc.Geometry.Point3d.Add(nlegendBasePoint, movingVector);
                else:
                    movedLegendBasePoint = rc.Geometry.Point3d.Add(legendBasePoint, movingVector);
                #legendBasePoints.append(movedLegendBasePoint)
        
                
                
                if bakeIt:
                    studyLayerName = '3D_CHARTS'
                    legendText.append(titleStr)
                    # check the study type
                    try:
                        newLayerIndex, l = lb_visualization.setupLayers(dataType, 'LADYBUG', placeName, studyLayerName, False, False, 0, 0)
                    except:
                        placeName = 'alternateLayerName'
                        newLayerIndex, l = lb_visualization.setupLayers(dataType, 'LADYBUG', placeName, studyLayerName, False, False, 0, 0)
                    lb_visualization.bakeObjects(newLayerIndex, coloredChart, legendSrfs, legendText, textPt, textSize, fontName = 'Verdana')
                
                res[0].append(coloredChart)
                res[1].append([legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)])
                res[2].append(movedLegendBasePoint)
                res[3].append(conditionalPoints)
            return res
        else:
            warning = 'Connect inputData!'
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1
    
    conversionFac = lb_preparation.checkUnits()



result = main(_inputData, _basePoint_, _xScale_, _yScale_, _zScale_, _xCount_, legendPar_, condStatement_, bakeIt_)
if result!= -1:
    legend = DataTree[System.Object]()
    graphMesh = DataTree[System.Object]()
    legendBasePts = DataTree[System.Object]()
    conditionalPts = DataTree[System.Object]()
    for i, leg in enumerate(result[1]):
        p = GH_Path(i)
        graphMesh.Add(result[0][i], p)
        legend.Add(leg[0], p)
        legend.AddRange(leg[1], p)
        legendBasePts.Add(result[2][i], p)
        conditionalPts.AddRange(result[3][i], p)
    ghenv.Component.Params.Output[3].Hidden = True