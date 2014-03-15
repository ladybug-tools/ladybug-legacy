# This is a component for visualizing the desirability of shading over a window by using the outdoor dry bulb temperature and an assumed building balance point.
# By Chris Mackey and Mostapha Sadeghipour Roudsari
# Chris@MackeyArchitecture.com; Sadeghipour@gmail.com
# HoneyBee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This is a component for visualizing the desirability of shade in terms of comfort temperature by using solar vectors, the outdoor temperature, and an assumed balance temperature.  The balance temperature represents either a median temperature of outdoor comfort if this component is being used to evaluate shade in an open space, or the outside temperature at which the energy passively flowing into a building is equal to that flowing out if the component is being used to evaluate shading over windows.

Solar vectors for hours when the temperature is above the balance point contribute positively to shade desirability while solar vectors for hours when the temperature is below the balance point contribute negatively.

The component outputs a colored mesh of the shade illustrating the net effect of shading each mesh face.  A higher saturation of blue indicates that shading the cell is very desirable.  A higher saturation of red indicates that shading the cell is harmful (blocking more winter sun than summer sun). Desaturated cells indicate that shading the cell will have relatively little effect on outdoor comfort or building performance.

The units for shade desirability are net cooling degree-days helped per unit area of shade if the test cell is blue.  If the test cell is red, the units are net heating degree-days harmed per unit area of shade.

The method used by this component is based off of the Shaderade method developed by Christoph Reinhart, Jon Sargent, Jeffrey Niemasz.  This component uses Shaderade's method for evaluating shade and window geometry in terms of solar vectors but substitutes Shaderade's energy simulation for an evaluation of heating and cooling degree-days about a balance temperature. 

A special thanks goes to them and their research.  A paper detailing the Shaderade method is available at:
http://www.gsd.harvard.edu/research/gsdsquare/Publications/Shaderade_BS2011.pdf

The heating/cooling degree-day calculation used here works by first getting the percentage of sun blocked by the test cell for each hour of the year using the Shaderade method.  Next, this percentage for each hour is multiplied by the temperature above or below the balance point for each hour to get a "degree-hour" for each hour of the year for a cell.  Then, all the cooling-degree hours (above the balance point) and heating degree-hours (below the balance point) are summed to give the total heating or cooling degree-hours helped or harmed respectively.  This number is divided by 24 hours of a day to give degree-days.  These degree days are normalized by the area of the cell to make the metric consistent across cells of different area.  Lastly, the negative heating degree-days are added to the positive cooling degree-days to give a net effect for the cell.

-
Provided by Ladybug 0.0.55
    
    Args:
        _sunVectors: The sunVectors output from the Ladybug_SunPath component.  Note that you can adjust the analysis period of the sun vectors to look at shade benefit over an entire year or just for a few months (for example, when you have an outdoor space that you know will only be occupied for a few months of the year or when the outside is above a certain temperature).
        _temperatureForVec: The selHourlyData output of the Ladybug_SunPath component when dryBulbTemperature is connected to the SunPath's annualHourlyData_ input.
        _balanceTemperature: An estimated balance temperature representing either the median outside temperature that people find comfortable (if being used to evaluate a shade in an outdoor space) or the outside temperature at which the energy passively flowing into a building is equal to that flowing out (if being used to evaluate a shade over a window).  Outdoor temperatures above this balance temperature will contribute to shade benefit while those below it will contribute to shade harm.  For shades in outdoor spaces, balance points will usually range from 20C (for people acclimated to a cold climate or for a cold analysis period) to 24C (for people acclimated to a warm climate or a warm analysis period).  Building balance points can be much more difficult to estimate and can range from 6C (for a thickly insulated passivhaus in a cold climate) to 22C (for an open-air enclosure in the tropics). To use this component correctly for buildings, you should calculate your building balance point by solving a simple energy balance that accounts for heat losses/gains through the envelope, ventilation and infiltration as well as gains from solar radiation through the windows and gains from people, lights and equipment.  Alternatively, you can be patient and wait for a version of this component that will be released with Honeybee energy components, which will essentially calculate this balance point for you.
        ============: ...
        _testShade: A brep or list of breps representing shading to be evaluated in terms of its benefit. Note that, in the case that multiple shading breps are connected, this component does not account for the interaction between the different shading surfaces. Note that only breps with a single surface are supported now and volumetric breps will be included at a later point.
        _testRegion: A brep representing an outdoor area for which shading is being considered or the window of a building that would be affected by the shade. Note that only breps with a single surface are supported now and volumetric breps will be included at a later point.
        gridSize_: The length of each of the shade's test cells in model units.  Please note that, as this value gets lower, simulation times will increase exponentially even though this will give a higher resolution of shade benefit.
        ============: ...
        delNonIntersect_: Set to "True" to delete mesh cells with no intersection with sun vectors.  Mesh cells where shading will have little effect because an equal amount of warm and cool temperature vectors will still be left in white.
        legendPar_: Legend parameters that can be used to re-color the shade, change the high and low boundary, or sync multiple evaluated shades with the same colors and legend parameters.
        parallel_: Set to "True" to run the simulation with multiple cores.  This can increase the speed of the calculation substantially and is recommended if you are not running other big or important processes.
        _runIt: Set to 'True' to run the simulation.
    Returns:
        readMe!: ...
        ==========: ...
        windowTestPts: Points across the window surface from which sun vectors will be projected
        shadeMesh: A colored mesh of the _testShades showing where shading is helpful (in satuated blue), harmful (in saturated red), or does not make much of a difference (white or desaturated colors).
        legend: Legend showing the numeric values of degree-days that correspond to the colors in the shade mesh.
        ==========: ...
        shadeHelpfulness: The cumulative cooling degree-days/square Rhino model unit helped by shading the given cell. (C-day/m2)*if your model units are meters.
        shadeHarmfulness: The cumulative heating degree-days/square Rhino model unit harmed by shading the given cell. (C-day/m2)*if your model units are meters. Note that these values are all negative due to the fact that the shade is harmful. 
        netEffect: The sum of the helpfulness and harmfulness for each cell.  This will be negative if shading the cell has a net harmful effect and positive if the shade has a net helpful effect.
"""

ghenv.Component.Name = "Ladybug_Shade Benefit Evaluator"
ghenv.Component.NickName = 'ShadeBenefit'
ghenv.Component.Message = 'VER 0.0.55\nMAR_15_2014'
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
    if len(_sunVectors) == len(_temperatureForVec) and len(_sunVectors) > 0:
        checkData1 = True
    else:
        checkData1 = False
        print 'Connect sunVectors and selHourlyData from a sun path component that has the dry bulb temperature plugged in as the annualHourlyData_.'
    
    #Check that both a window brep and test shade brep are connected and are a single surface.
    if _testShades and _testRegion:
        if _testShades.Faces.Count == 1:
            if _testRegion.Faces.Count == 1:
                checkData2 = True
            else:
                checkData2 = False
                print 'The _testRegion must be a brep with a single surface.  Polysurface or volumetric Breps are not supported at this time. Try breaking your Brep up into single surfaces.'
        else:
            checkData2 = False
            print 'The _testShades must each be a brep with a single surface.  Polysurface or volumetric Breps are not supported at this time. Try breaking your Brep up into single surfaces.'
    else:
        checkData2 = False
        print 'Connect a brep for both the _testRegion and the _testShade.'
    
    #Check to make see if users have connected a grid size and balance point.  If not, assign a grid size based on a bounding box around the test shade and altert the user that they should select a balance point.
    if gridSize_:
        try:
            if gridSize_ > 0:
                gridSize = float(gridSize_)
                checkData3 = True
            else:
                try:
                    boundBox = _testShades.GetBoundingBox(False)
                    box = rc.Geometry.Box(boundBox)
                    if box.X[1] - box.X[0] < box.Y[1] - box.Y[0]:
                        gridSize = (box.X[1] - box.X[0])/5
                    else:
                        gridSize = (box.Y[1] - box.Y[0])/5
                    checkData3 = True
                    print 'There is no positive value connected for gridSize_. A default value will be used based on the dimensions of the _testShades.'
                except:
                    gridSize = 0
                    checkData3 = False
                    print 'No value is connected for gridSize_.'
        except:
            gridSize = 0
            checkData3 = False
            print "An invalid value is connected for grid Size_.  The gridSize_ must be a number."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "An invalid value is connected for grid Size_.  The gridSize_ must be a number.")
    else:
        gridSize = 0
        checkData3 = False
        print 'No value is connected for gridSize_.'
    
    
    if _balanceTemperature == 0 and _runIt == True:
        checkData4 = False
        balanceTemp = 0
        print 'No value is connected for _balanceTemperature. You must specify a numeric value for _balanceTemperature.'
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "No value is connected for _balanceTemperature. You must specify a numeric value for _balanceTemperature.")
    
    elif _balanceTemperature == 0:
        checkData4 = False
        balanceTemp = 0
        print 'No value is connected for _balanceTemperature.'
        
    elif _balanceTemperature:
        balanceTemp = float(_balanceTemperature)
        checkData4 = True
    
    else:
        checkData4 = False
        balanceTemp = 0
        print 'No value is connected for _balanceTemperature. You must specify a numeric value for _balanceTemperature.'
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "No value is connected for _balanceTemperature. You must specify a numeric value for _balanceTemperature.")
    
    #Check if runIt is set to true.
    if _runIt == True:
        checkData5 = True
    else:
        checkData5 = False
        print 'Set _runIt to True to perform the shade benefit calculation.'
    
    #Check if all of the above Checks are True
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True:
        checkData = True
    else:
        checkData = False
    
    return checkData, gridSize, balanceTemp


def meshTheShade(gridSize, testShade):
    #Generate Meshes for the Shade
    meshPar = rc.Geometry.MeshingParameters.Default
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


def generateTestPoints(gridSize, testRegion):
    #Generate a Grid of Points Along the Window
    winMeshPar = rc.Geometry.MeshingParameters.Default
    winMeshPar.MinimumEdgeLength = (gridSize/1.75)
    winMeshPar.MaximumEdgeLength = (gridSize/1.75)
    windowMesh = rc.Geometry.Mesh.CreateFromBrep(testRegion, winMeshPar)[0]
    
    vertices = windowMesh.Vertices
    
    # Convert window Point3f to Point3d
    windowTestPtsInit = []
    for item in vertices:
        windowTestPtsInit.append(rc.Geometry.Point3d(item))
    
    #Get rid of the points that lie along the boundary of the shape.
    windowTestPts = []
    edges = testRegion.DuplicateEdgeCurves()
    boundary = rc.Geometry.Curve.JoinCurves(edges)
    for point in windowTestPtsInit:
        closestPtInit =  rc.Geometry.Curve.ClosestPoint(boundary[0], point)
        closestPt = boundary[0].PointAt(closestPtInit[1])
        if point.DistanceTo(closestPt) < sc.doc.ModelAbsoluteTolerance: pass
        else: windowTestPts.append(point)
    
    #If there is a dense collection of points that are too close to each other, get rid of it.
    windowTestPtsFinal = []
    for pointCount, point in enumerate(windowTestPts):
        pointOK = True
        testPtsWihtout = list(windowTestPts)
        del testPtsWihtout[pointCount]
        for othPt in testPtsWihtout:
            if point.DistanceTo(othPt) < (gridSize/4):
                pointOK = False
            else:pass
        if pointOK == True:
            windowTestPtsFinal.append(point)
    
    return windowTestPtsFinal, windowMesh


def nonparallel_projection(analysisMesh, sunLines):
    #Intersect the sun lines with the test mesh
    faceInt = []
    for face in range(analysisMesh.Faces.Count): faceInt.append([])
    
    for ptCount, pt in enumerate(windowTestPts):
        try:
            for hour, sunLine in enumerate(sunLines[ptCount]):
                if sunLine != 0:
                    intPt, i = rc.Geometry.Intersect.Intersection.MeshLine(analysisMesh, sunLine)
                    if len(intPt)!=0: faceInt[i[0]].append(hour)
                else: pass
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
                if sunLine != 0:
                    intPt, indx = rc.Geometry.Intersect.Intersection.MeshLine(analysisMesh, sunLine)
                    if len(intPt)!=0: faceInt[indx[0]].append(hour)
                else: pass
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
        
        #Generate the sun lines for intersection and discount the vector if it intersects a context.
        sunLines = []
        if context_:
            contextMeshes = []
            for brep in context_:
                contextMeshes.extend(rc.Geometry.Mesh.CreateFromBrep(brep, rc.Geometry.MeshingParameters.Default))
            contextMesh = joinMesh(contextMeshes)
        else: pass
        
        for pt in windowTestPts: sunLines.append([]) 
        
        for ptCount, pt in enumerate(windowTestPts):
            for vec in _sunVectors:
                if context_:
                    if rc.Geometry.Intersect.Intersection.MeshRay(contextMesh, rc.Geometry.Ray3d(pt, vec)) < 0:
                        sunLines[ptCount].append(rc.Geometry.Line(pt, lineLength * vec))
                    else: sunLines[ptCount].append(0)
                else:
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
        for temp in _temperatureForVec:
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
        
        #Get the colors for the analysis mesh based on the calculated benefit values unless a user has connected specific legendPar.
        if legendPar:
            lowB, highB, numSeg, customColors, legendBasePoint, legendScale = lb_preparation.readLegendParameters(legendPar, False)
        else:
            lowB = -1 * legendVal
            highB = legendVal
            numSeg = 11
            customColors = [System.Drawing.Color.FromArgb(255,0,0), System.Drawing.Color.FromArgb(255,51,51), System.Drawing.Color.FromArgb(255,102,102), System.Drawing.Color.FromArgb(255,153,153), System.Drawing.Color.FromArgb(255,204,204), System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(204,204,255), System.Drawing.Color.FromArgb(153,153,255), System.Drawing.Color.FromArgb(102,102,255), System.Drawing.Color.FromArgb(51,51,255), System.Drawing.Color.FromArgb(0,0,255)]
            legendBasePoint = None
            legendScale = 1
        
        colors = lb_visualization.gradientColor(shadeNetEffect, lowB, highB, customColors)
        
        #Color the shade mesh based on the colors.
        shadeMesh = lb_visualization.colorMesh(colors, analysisMesh)
        
        # If the user has set "delNonIntersect_" to True, delete those mesh values that do not have ny solar intersections.
        if delNonIntersect_ == True:
            deleteFaces = []
            newShadeHelpfulness = []
            newShadeHarmfulness = []
            newShadeNetEffect = []
            for cellCount, cell in enumerate(colors):
                if shadeHelpfulness[cellCount] == 0.0 and shadeHarmfulness[cellCount] == 0.0:
                    deleteFaces.append(cellCount)
                else:
                    newShadeHelpfulness.append(shadeHelpfulness[cellCount])
                    newShadeHarmfulness.append(shadeHarmfulness[cellCount])
                    newShadeNetEffect.append(shadeNetEffect[cellCount])
            shadeMesh.Faces.DeleteFaces(deleteFaces)
            shadeHelpfulness = newShadeHelpfulness
            shadeHarmfulness = newShadeHarmfulness
            shadeNetEffect = newShadeNetEffect
        else:
            pass
        
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

#If the user has connected any breps to _testShades or _testRegion, output the window test points and an initial uncolored shadeMesh such that users can get a sense of what to expect before running the whole simulation.
if gridSize > 0 and _testShades:
    analysisMesh, shadeMesh, analysisAreas = meshTheShade(gridSize, _testShades)
else: pass

if gridSize > 0 and shadeMesh and _testRegion:
    windowTestPts, windowMesh = generateTestPoints(gridSize, _testRegion)
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