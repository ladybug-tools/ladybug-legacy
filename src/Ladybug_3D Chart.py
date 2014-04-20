# This component separates numbers and strings from an input list
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to make a 3D chart of any climate data in the Rhino scene.
-
Provided by Ladybug 0.0.57
    
    Args:
        _inputData: A list of input data to plot.
        _xScale_: The scale of the X axis of the graph. The default will plot the X axis with a length of 365 Rhino model units (for 365 days of the year). Connect a list of values for multiple graphs.
        _yScale_: The scale of the Y axis of the graph. The default will plot the Y axis with a length of 24 Rhino model units (for 24 hours of the day). Connect a list of values for multiple graphs.
        _zScale_: The scale of the Z axis of the graph. The default will plot the Z axis with a number of Rhino model units corresponding to the input data values.  Connect a list of values for multiple graphs.
        _yCount_: The number of segments on your y-axis.  The default is set to 24 for 24 hours of the day. This variable is particularly useful for input data that is not for each hour of the year.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        _basePoint_: An optional point with which to locate the 3D chart in the Rhino Model.  The default is set to the Rhino origin at (0,0,0).
        condStatement_ : An optional conditional statement, which will remove data from the chart that does not fit the conditions. The input must be a valid python conditional statement (e.g. a > 25).
        cullVertices_: If set to True, the vertices that do not satisfy the conditional statement will be removed from the plotted mesh.
        bakeIt_ : If set to True, the chart will be Baked into the Rhino scene as a colored mesh.
    Returns:
        readMe!: ...
        graphMesh: A 3D plot of the input data as a colored mesh.  Multiple meshes will be output for several input data streams or graph scales.
        legend: A legend of the chart. Connect this output to a grasshopper "Geo" component in order to preview the legend in the Rhino scene.  
        legendBasePts: The legend base point, which can be used to move the legend in relation to the chart with the grasshopper "move" component.
        conditionalPts: A list of points that represent the values of the mesh data on the chart.
        HOY: The input data for the hours of the year that pass the conditional statement.
"""

ghenv.Component.Name = "Ladybug_3D Chart"
ghenv.Component.NickName = '3DChart'
ghenv.Component.Message = 'VER 0.0.57\nAPR_20_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


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
        csCleaned = conditionalStatement.Replace('and', '')
        csCleaned = csCleaned.Replace('or', '')
        
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
        startHour = listInfo[0][5]
        endHour = listInfo[0][6]
        
        for i in range(len(listInfo)):
            selList[i] = annualHourlyData[indexList[i]+7:indexList[i+1]]
            if listInfo[i][5]!= startHour or  listInfo[i][6]!=endHour :
                warning = 'Length of all the lists should be the same to apply conditional statemnets.' + \
                          ' Please fix this issue and try again!\nList number '+ `i+1` + ' is the one that causes the issue.'
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
       
        for HOY in range(8760):
            try:
                exec(finalStatement)
                patternList.append(pattern)
            except:
                pass
                
        return titleStatement, patternList


def main(inputData, basePoint, xScale, yScale, zScale, yCount, legendPar, condStatement, bakeIt, cullVertices):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        conversionFac = lb_preparation.checkUnits()
        # copy the custom code here
        
        if len(inputData)!=0 and inputData[0]!=None and str(inputData[0]) != "Connect input data here":
            
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
            
            hoursOfYear = []
            for hoy, pattern in enumerate(patternList):
                if pattern: hoursOfYear.append(hoy + 1)
                
            
            
            # separate the data
            indexList, listInfo = lb_preparation.separateList(inputData, lb_preparation.strToBeFound)
        
            #separate total, diffuse and direct radiations
            separatedLists = []
            for i in range(len(indexList)-1):
                selList = []
                [selList.append(float(x)) for x in inputData[indexList[i]+7:indexList[i+1]]]
                separatedLists.append(selList)
            
            
            res = [[],[], [], [], []]
            # legendBasePoints = []
            for i, results in enumerate(separatedLists):
                
                if 'Month' in listInfo[i][4]:
                    # scale for the monthly data
                    xExtraFactor = 10
                else:
                    xExtraFactor = 1
                
                    
                try:
                    # assuming there is a scale for this chart
                    xSCC = 10 * float(xScale[i]) * xExtraFactor /conversionFac
                except:
                    try:
                        # try the first item
                        xSCC = 10 * float(xScale[0]) * xExtraFactor /conversionFac
                    except:
                        xSCC = 10 * xExtraFactor/conversionFac
                
                # make sure the scale is not 0
                if xSCC == 0: xSCC = 10 * xExtraFactor/conversionFac
                
                # this is because I rotate the geometry 90 degrees!
                ySC = abs(xSCC)
                
                try:
                    ySCC = 10 * float(yScale[i])/conversionFac
                except:
                    try:
                        ySCC = 10 * float(yScale[0])/conversionFac
                    except:
                        ySCC = 10/conversionFac
                
                if ySCC==0: ySCC = 10/conversionFac
                
                xSC = abs(ySCC)
                
                # read running period
                stMonth, stDay, stHour, endMonth, endDay, endHour = lb_visualization.readRunPeriod((listInfo[i][5], listInfo[i][6]), False)
                
                
                try:
                    xC = float(yCount[i])
                except:
                    try:
                        xC = float(yCount[0])
                    except:
                        xC = abs(endHour - stHour) + 1
                        
                if xC == 0: xC = abs(endHour - stHour) + 1
                xC = int(xC)
                
                dataType = listInfo[i][2]
                
                if ('Rad' in dataType): extraFactor = 100
                elif ('Hum' in dataType): extraFactor = 5
                elif ('Illuminance' in dataType): extraFactor = 5000
                elif ('Wind Direction' in dataType): extraFactor = 30
                else: extraFactor = 1
                #if xExtraFactor !=1: extraFactor = extraFactor/3
                
                try:
                    zSC = 10 * float(zScale[i])/(conversionFac*extraFactor)
                except:
                    try:
                        zSC = 10 * float(zScale[0])/(conversionFac*extraFactor)
                    except:
                        zSC = 10/(conversionFac*extraFactor)
                
                
                print 'zScale is set to ' +  ("%.2f" % (1/extraFactor)) + ' for ' + dataType
                    
                zSC = abs(zSC)
                
                # read legend parameters
                lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize = lb_preparation.readLegendParameters(legendPar, False)
                
                # print lowB, highB, numSeg, legendBasePoint, legendScale
                # draw the graph
                mesh, conditionalPoints, duplicatedMeshPattern = lb_visualization.chartGeometry(results, xC, xSC, ySC, zSC, patternList, lb_preparation.getCenPt(basePoint))
                
                # print len(duplicatedMeshPattern)
                
                colors = lb_visualization.gradientColor(results, lowB, highB, customColors)
                    
                coloredChart = lb_visualization.colorMeshChart(mesh, xC, colors, lb_preparation.getCenPt(basePoint))
                
                lb_visualization.calculateBB([coloredChart], True)
                
                # cull mesh vertices
                # There should be a better way to do this. I should be able to generate the mesh in a smarter way
                # and then the process of coloring will be more clear
                if condStatement and cullVertices:
                    culledMesh = rc.Geometry.Mesh()
                    for faceCount in range (coloredChart.Faces.Count):
                        # Find the vertices
                        selVertices = []
                        verCount = range(4 * faceCount, 4 * faceCount + 4) 
                        for id in verCount:
                            if duplicatedMeshPattern[id]: selVertices.append(id)
                        
                        if len(selVertices)>2:
                            mesh = rc.Geometry.Mesh()
                            for id in selVertices:
                                mesh.Vertices.Add(coloredChart.Vertices[id])
                        
                            if len(selVertices) == 3:
                                mesh.Faces.AddFace(0, 1, 2)
                            else:
                                mesh.Faces.AddFace(0, 1, 2, 3)
                            
                            mesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.White)
                            # apply the colors
                            for verCount in range(mesh.Vertices.Count):
                                mesh.VertexColors[verCount] = coloredChart.VertexColors[selVertices[verCount]]
                            
                            # add to culledMesh
                            culledMesh.Append(mesh)
                    
                    coloredChart = culledMesh
                
                
                try: movingDist = -1.5 * lb_visualization.BoundingBoxPar[2] # moving distance for sky domes
                except: movingDist = 0
                
                movingVector = rc.Geometry.Vector3d(0, i * movingDist,0)
                coloredChart.Translate(movingVector)
                titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo[i]],lb_visualization.BoundingBoxPar, legendScale, None, False, legendFont, legendFontSize)
                
                legendTitle = listInfo[i][3]
                placeName = listInfo[i][1]
                dataType = listInfo[i][2]
                
                # create legend geometries
                legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(results
                    , lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize)
                
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
                try: legendSrfs.Translate(movingVector) # move it to the right place
                except:
                    msg = "0 hour meets the conditional statemnet."
                    print msg
                    w = gh.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(w, msg)
                    return -1
                
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
                    lb_visualization.bakeObjects(newLayerIndex, coloredChart, legendSrfs, legendText, textPt, textSize, legendFont)
                
                res[0].append(coloredChart)
                res[1].append([legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)])
                res[2].append(movedLegendBasePoint)
                res[3].append(conditionalPoints)
                res[4].append(hoursOfYear)
            return res
        elif str(inputData[0]) == "Connect input data here":
            print 'Connect inputData!'
            return -1
        else:
            warning = 'Please ensure that the connected inputData is valid!'
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



result = main(_inputData, _basePoint_, _xScale_, _yScale_, _zScale_, _yCount_, legendPar_, condStatement_, bakeIt_, cullVertices_)
if result!= -1:
    legend = DataTree[System.Object]()
    graphMesh = DataTree[System.Object]()
    legendBasePts = DataTree[System.Object]()
    conditionalPts = DataTree[System.Object]()
    HOY = DataTree[System.Object]()
    
    for i, leg in enumerate(result[1]):
        p = GH_Path(i)
        graphMesh.Add(result[0][i], p)
        legend.Add(leg[0], p)
        legend.AddRange(leg[1], p)
        legendBasePts.Add(result[2][i], p)
        conditionalPts.AddRange(result[3][i], p)
        HOY.AddRange(result[4][i], p)
    ghenv.Component.Params.Output[3].Hidden = True
    ghenv.Component.Params.Output[4].Hidden = True
