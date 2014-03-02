# This is a component for visualizing the desirability of shading over a window by using the outdoor dry bulb temperature and an assumed building balance point.
# By Chris Mackey and Mostapha Sadeghipour Roudsari
# Chris@MackeyArchitecture.com; Sadeghipour@gmail.com
# HoneyBee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This is a component for visualizing the desirability of shading over a window by using solar vectors, the outdoor dry bulb temperature, and an assumed building balance temperature.

Solar vectors for hours when the temperature is above the balance point contribute positively to shade desirability while solar vectors for hours when the temperature is below the balance point contribute negatively.

The component outputs a colored mesh of the shade illistrating the net effect of shading each mesh face.  A higher saturation of blue indicates that shading the cell is very desirable.  A higher saturation of red indicates that shading the cell is harmful (blocking more winter sun than summer sun). Desaturated cells indicate that shading the cell will have relatively little effect on building performance. 

The method used by this component is based off of the Shaderade method developed by Christoph Reinhart, Jon Sargent, Jeffrey Niemasz.  A special thanks goes to them and their research.  A paper detailing the shaderade method is available at:
http://www.gsd.harvard.edu/research/gsdsquare/Publications/Shaderade_BS2011.pdf

-
Provided by Ladybug 0.0.55
    
    Args:
        _sunVectors: The sunVectors output from the Ladybug_SunPath component.  Note that, for accurate use of this component, you should usually connect all sun vectors for the entire year (or perhaps all sun vectors above a certain radiation threshold).
        _dryBulbTempForVec: The selHourlyData output of the Ladybug_SunPath component when dryBulbTemperature is connected to the annualHourlyData_ input.
        bldgBalanceTemp_: An estimated building balance temperature (or the outside temperature at which the energy passively flowing into the building is equal to that flowing out).  Outdoor temperatures above this will contribute to shade benefit while those below it will contribute to shade harm.  Default is set to 18 C, which is sutiable for the case of an passive enclosed but uninsulated space with minimal heat gain.  A thickly-insulated passivhaus with 18" of insulation can have a very low balance point around 8 C. A mildly insulated residence (~4" of insulation) with a window to wall ratio of 0.4 might have a balance point around 12 C. A residence with an uninsulated stud wall house might be around 16 C.  A stud wall shack with single pane windows and no internal heat gain from appliances or lights might have a balance point around 20C.  An open air structure should be evaluated using an outdoor temperature around which people start to desire shade(24C).
        ============: ...
        _testShade: A brep or list of breps representing shading to be evaluated in terms of its benefit. Note that, in the case that multiple shading breps are connected, this component does not account for the interaction between the different shading surfaces.
        _testWindow: A brep representing the window affected by the shade.
        gridSize_: The length of each of the cells to be evaluated in model units.  Please note that, as this value gets lower, simulation times will increase exponentially even though this will give a higher resolution of shade benefit.
        ============: ...
        parallel_: Set to "True" to run the simulation with multiple cores.  This can increase the speed of the calculation substantially.
        _runIt: Set to 'True' to run the simulation.
    Returns:
        readMe!: ...
        ==========: ...
        windowTestPts: Points across the window surface from which sun vectors will be projected
        shadeMesh: A colored mesh of the _testShades showing where shading is helpful (in satuated blue), harmful (in saturated red), or does not make much of a difference (white or desaturated colors).
        legend: Legend showing the numeric values of degree-days that correspond to the colors in the shade mesh.
        ==========: ...
        shadeHelpfulness: The cumulative cooling degree-days/square Rhino model unit eased by shading the given cell. (C-day/m2)*if your model units are meters.
        shadeHarmfulness: The cumulative heating degree-days/square Rhino model unit intensified by shading the given cell. (C-day/m2)*if your model units are meters. Note that these values are all negative due to the fact that the shade is harmful. 
        netEffect: The sum of the helpfulness and harmfullness for each cell.  This will be negative if the cell is harmful and positive if the shade is helpful.
"""

ghenv.Component.Name = "Ladybug_Shade Benefit Evaluator"
ghenv.Component.NickName = 'ShadeBenefit'
ghenv.Component.Message = 'VER 0.0.55\nMAR_02_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass

import rhinoscriptsyntax as rs
import Rhino as rc
import collections
import System.Threading.Tasks as tasks
import System
import scriptcontext as sc
import math

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh


def checkTheInputs():
    #Check the lists of data to ensure that they are all the same length and all for sun-up hours
    if len(_sunVectors) == len(_dryBulbTempForVec) and len(_sunVectors) > 0:
        checkData1 = True
    else:
        checkData1 = False
        print 'Connect sunVectors and selHourlyData from a sun path component that has the dry bulb temperature plugged in as the annualHourlyData_.'
    
    #Check that both a window brep and test shade brep are connected.
    if _testShades and _testWindow:
        checkData2 = True
    else:
        checkData2 = False
        print 'Connect a brep for both the _testWindow and the _testShade.'
    
    #Check to make see if users have connected a grid size and building balance point.  If not, assign a grid size based on a bounding box around the test shade and assign a default balance point of 24 C.
    if gridSize_ and gridSize_ > 0:
        gridSize = gridSize_
    else:
        try:
            boundBox = _testShades.GetBoundingBox(False)
            box = rc.Geometry.Box(boundBox)
            if box.X[1] - box.X[0] < box.Y[1] - box.Y[0]:
                gridSize = (box.X[1] - box.X[0])/5
            else:
                gridSize = (box.Y[1] - box.Y[0])/5
        except: gridSize = 0
        print 'There is no positive value connected for gridSize_. A default value will be used based on the dimensions of the _testShades.'
    
    if bldgBalanceTemp_:
        balanceTemp = bldgBalanceTemp_
    else:
        balanceTemp = 18
        print 'No value is connected for bldgBalanceTemp_. A default value of 18 C will be used, which should be applicable to an enclosed but uninulated building.'
    
    # If the user has connected an absurd balance temperature, give them a warning.
    if balanceTemp > 30:
        print "WARNING: The balance temperatureis very high.  It is strongly recommended that you lower it if you want your shade evaluation to be in terms of human comfort. Wouldn't you want shade if the air temperature is greater than 30C?"
    else: pass
    if balanceTemp < 0:
        print "WARNING: The balance temperatureis very low.  Unless you are modelling a space ship with vacum sealed insulation, a building with several feet of inulation, or a building with a very high internal heat gain, it is strongly recommended that you raise it.  You are essentially saying that your unheated space is comfortable when the outside air is below freezing."
    else: pass
    
    #Check if runIt is set to true.
    if _runIt == True:
        checkData3 = True
    else:
        checkData3 = False
        print 'Set _runIt to True to perform the shade benefil calculation.'
    
    #Check if all of the above Checks are True
    if checkData1 == True and checkData2 == True and checkData3 == True:
        checkData = True
    else:
        checkData = False
    
    return checkData, gridSize, balanceTemp


def meshTheShade(gridSize, testShade):
    #Generate Meshes for the Shade
    meshPar = rc.Geometry.MeshingParameters.Default
    meshPar.GridAspectRatio = 1
    meshPar.MinimumEdgeLength = gridSize
    meshPar.MaximumEdgeLength = gridSize
    
    analysisMesh = rc.Geometry.Mesh.CreateFromBrep(testShade, meshPar)[0]
    
    #Generate breps of the mesh faces so that users can see how the shade will be divided before they run the analysis
    analysisBreps = []
    for face in analysisMesh.Faces:
        if face.IsQuad:
            analysisBreps.append(rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(analysisMesh.Vertices[face.A]), rc.Geometry.Point3d(analysisMesh.Vertices[face.B]), rc.Geometry.Point3d(analysisMesh.Vertices[face.C]), rc.Geometry.Point3d(analysisMesh.Vertices[face.D]), sc.doc.ModelAbsoluteTolerance))
        if face.IsTriangle:
            analysisBreps.append(rc.Geometry.Brep.CreateFromCornerPoints(rc.Geometry.Point3d(analysisMesh.Vertices[face.A]), rc.Geometry.Point3d(analysisMesh.Vertices[face.B]), rc.Geometry.Point3d(analysisMesh.Vertices[face.C]), sc.doc.ModelAbsoluteTolerance))
    
    #Calculate the areas of the breps for later use in the normalization of shade benefit values.
    analysisAreas = []
    for brep in analysisBreps:
        area = rc.Geometry.AreaMassProperties.Compute(brep).Area
        analysisAreas.append(area)
    
    return analysisMesh, analysisBreps, analysisAreas


def generateTestPoints(gridSize, testWindow):
    #Generate a Grid of Points Along the Window
    winMeshPar = rc.Geometry.MeshingParameters.Default
    winMeshPar.GridAspectRatio = 1
    winMeshPar.MinimumEdgeLength = (gridSize/1.75)
    winMeshPar.MaximumEdgeLength = (gridSize/1.75)
    windowMesh = rc.Geometry.Mesh.CreateFromBrep(testWindow, winMeshPar)[0]
    
    vertices = windowMesh.Vertices
    
    # Convert window Point3f to Point3d
    windowTestPts = []
    for item in vertices:
        windowTestPts.append(rc.Geometry.Point3d(item))
    
    return windowTestPts, windowMesh


def nonparallel_projection(analysisMesh, sunLines):
    #Intersect the sun lines with the test mesh
    faceInt = []
    for face in range(analysisMesh.Faces.Count): faceInt.append([])
    
    for ptCount, pt in enumerate(windowTestPts):
        try:
            for hour, sunLine in enumerate(sunLines[ptCount]):
                intPt, i = rc.Geometry.Intersect.Intersection.MeshLine(analysisMesh, sunLine)
                if len(intPt)!=0: faceInt[i[0]].append(hour)
        except Exception, e:
            print `e`
    
    return faceInt


def parallel_projection(analysisMesh, sunLines):
    #Intersect the sun lines with the test mesh using parallel processing
    faceInt = []
    for face in range(analysisMesh.Faces.Count): faceInt.append([]) #place holder for result
    
    def intersect(i):
        try:
            for hour, sunLine in enumerate(sunLines[i]):
                intPt, indx = rc.Geometry.Intersect.Intersection.MeshLine(analysisMesh, sunLine)
                if len(intPt)!=0: faceInt[indx[0]].append(hour)
        except Exception, e:
            print `e`
    
    tasks.Parallel.ForEach(range(len(windowTestPts)), intersect)
    
    return faceInt


def valCalc(percentBlocked, deltaBal, cellArea):
    #Multiply the percentBlocked by the deltaBal to get a measure of how helpful or harmful the shade is in each hour of the year
    hourlyEffect = [a*b for a,b in zip(percentBlocked,deltaBal)]
    
    #Sum up all of resulting hourly effects depending on whether the effect is negative or positive to get the effect of the cell on the total heating, cooling degree days felt by the window.
    coolEffectList = []
    heatEffectList = []
    for effect in hourlyEffect:
        if effect > 0:
            coolEffectList.append(effect)
        elif effect < 0:
            heatEffectList.append(effect)
        else: pass
    
    coolEffectInit = sum(coolEffectList)
    heatEffectInit = sum(heatEffectList)
    netEffectInit = coolEffectInit + heatEffectInit
    
    #Normalize the effects by the area of the cell such that there is a consistent metric between cells of different areas.  Also, divide the value by 24 such that the final unit is in degree-days/model unit instead of degree-hours/model unit.
    coolEffect = (coolEffectInit/cellArea)/24
    heatEffect = (heatEffectInit/cellArea)/24
    netEffect = (netEffectInit/cellArea)/24
    
    return coolEffect, heatEffect, netEffect


def main(gridSize, balanceTemp, analysisMesh, analysisAreas, windowMesh, windowTestPts, legendPar):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        #Reverse the sun vectors to ensure that they are facing the right direction
        for vec in _sunVectors:
            vec.Unitize()
            vec.Reverse()
        
        #Determine the length to make the sun lines based on the scale of the bounding box around the input geometry.
        def joinMesh(meshList):
            joinedMesh = rc.Geometry.Mesh()
            for m in meshList: joinedMesh.Append(m)
            return joinedMesh
        
        joinedMesh = joinMesh([analysisMesh, windowMesh])
        
        boundBox = rc.Geometry.Mesh.GetBoundingBox(joinedMesh, rc.Geometry.Plane.WorldXY)
        
        #Multiply the largest dimension of the bounding box by 2 to ensure that the lines are definitely long enough to intersect the shade.
        lineLength = (max(boundBox.Max - boundBox.Min)) * 2
        
        #Generate the sun lines for intersection.
        sunLines = []
        for pt in windowTestPts: sunLines.append([]) 
        
        for ptCount, pt in enumerate(windowTestPts):
            for vec in _sunVectors:
                sunLines[ptCount].append(rc.Geometry.Line(pt, lineLength * vec))
                
        
        #If parallel is true, then run the intersection through the parallel function.  If not, run it through the normal function.
        if parallel_ == True:
            faceInt = parallel_projection(analysisMesh, sunLines)
        else:
            faceInt = nonparallel_projection(analysisMesh, sunLines)
        
        #Convert the Number Of Intersections for Each Mesh Face into a Percent of Sun Blocked by Each Mesh Face for Each Hour of the Year.
        percentBlocked = []
        for face in range(analysisMesh.Faces.Count):
            percentBlocked.append(len(_sunVectors) *[0])
        
        testPtsCount = len(windowTestPts) 
        # for each mesh surface,
        for faceCount, faceData in enumerate(faceInt):
            # check the number of intersections for each hour
            counter= collections.Counter(faceData)
            
            for hour in counter.keys():
                 # store the result in the new percentBlocked list
                 percentBlocked[faceCount][hour] = counter[hour]/testPtsCount
        
        #Calculate how far the hourly temperatures are from the balance point, allowing for a range of +/- 2C in which people will be comfortable.
        comfortRange = 2
        deltaBal = []
        for temp in _dryBulbTempForVec:
            if temp > (balanceTemp + comfortRange):
                deltaBal.append(temp - (balanceTemp + comfortRange))
            elif temp < (balanceTemp - comfortRange):
                deltaBal.append(temp - (balanceTemp - comfortRange))
            else:
                deltaBal.append(0)
        
        #Compare the percent blocked for each hour with the temperatre at that hour in relation to the balance point in order to determine the net value of shading.
        shadeHelpfulness = []
        shadeHarmfulness = []
        shadeNetEffect = []
        for cellCount, cell in enumerate(percentBlocked):
            shadeHelp, shadeHarm, shadeNet = valCalc(cell, deltaBal, analysisAreas[cellCount])
            shadeHelpfulness.append(shadeHelp)
            shadeHarmfulness.append(shadeHarm)
            shadeNetEffect.append(shadeNet)
        
        #Sort the net effects to find the highest and lowest values which will be used to generate colors and a legend for the mesh.
        shadeNetSorted = []
        for value in shadeNetEffect:
            shadeNetSorted.append(value)
        shadeNetSorted.sort()
        mostHelp = shadeNetSorted[-1]
        mostHarm = shadeNetSorted[0]
        if abs(mostHelp) > abs(mostHarm): legendVal = abs(mostHelp)
        else: legendVal = abs(mostHarm)
        
        #Color the analysis mesh based on the calculated benefit values unless a user has connected specific legendPar.
        if legendPar:
            lowB, highB, numSeg, customColors, legendBasePoint, legendScale = lb_preparation.readLegendParameters(legendPar, False)
        else:
            lowB = -1 * legendVal
            highB = legendVal
            numSeg = 10
            customColors = [System.Drawing.Color.FromArgb(255,0,0), System.Drawing.Color.FromArgb(255,24,24), System.Drawing.Color.FromArgb(255,88,88), System.Drawing.Color.FromArgb(255,167,167), System.Drawing.Color.FromArgb(255,231,231), System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(231,239,255), System.Drawing.Color.FromArgb(167,198,255), System.Drawing.Color.FromArgb(88,146,255), System.Drawing.Color.FromArgb(24,105,255)]
            legendBasePoint = None
            legendScale = 1
        
        colors = lb_visualization.gradientColor(shadeNetEffect, lowB, highB, customColors)
        shadeMesh = lb_visualization.colorMesh(colors, analysisMesh)
        
        
        #Generate a legend for the mesh.
        lb_visualization.calculateBB([shadeMesh], True)
        
        units = sc.doc.ModelUnitSystem
        legendTitle = 'Degree-Day/(' + str(units) + ')2'
        analysisTitle = '\nShade Benefit Analysis'
        if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
        
        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(shadeNetEffect, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale)
        legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
        legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
        
        titlebasePt = lb_visualization.BoundingBoxPar[-2]
        titleTextCurve = lb_visualization.text2crv([analysisTitle], [titlebasePt], 'Veranda', legendScale * (lb_visualization.BoundingBoxPar[2]/20))
        
        #Package the final legend together.
        legend = [legendSrfs, [lb_preparation.flattenList(legendTextCrv + titleTextCurve)]]
        
        #If we have got all of the outputs, let the user know that the calculation has been successful.
        if shadeHelpfulness and shadeHarmfulness and shadeNetEffect and shadeMesh and legend and legendBasePoint:
            print 'Shade benefit caclculation successful!'
        else: pass
        
        return shadeHelpfulness, shadeHarmfulness, shadeNetEffect, shadeMesh, legend, legendBasePoint
    
    
    else:
        print "You should let the Ladybug fly first..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let the Ladybug fly first...")
        return -1


def openLegend(legendRes):
    if len(legendRes)!=0:
        meshAndCrv = []
        meshAndCrv.append(legendRes[0])
        [meshAndCrv.append(curve) for curveList in legendRes[1] for curve in curveList]
        return meshAndCrv
    else: return



#Check the inputs and generate default values for grid size and balance temp if the user has given none.
checkData, gridSize, balanceTemp = checkTheInputs()

#If the user has connected any breps to _testShades or _testWindow, output the window test points and an initial uncolored shadeMesh such that users can get a sense of what to expect before running the whole simulation.
if gridSize > 0 and _testShades:
    analysisMesh, shadeMesh, analysisAreas = meshTheShade(gridSize, _testShades)
else: pass

if gridSize > 0 and shadeMesh and _testWindow:
    windowTestPts, windowMesh = generateTestPoints(gridSize, _testWindow)
else: pass

#If all of the data is good, run the shade benefit calculation to generate all results.
if checkData == True:
    result = main(gridSize, balanceTemp, analysisMesh, analysisAreas, windowMesh, windowTestPts, legendPar_)
    if result != -1:
        shadeHelpfulness = result[0]
        shadeHarmfulness = result[1]
        shadeNetEffect = result[2]
        shadeMesh = result[3]
        legendBasePoint = result[5]
        legend = []
        [legend.append(item) for item in openLegend(result[4])]