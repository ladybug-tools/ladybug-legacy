# This is a component for visualizing the desirability of shading over a window by using the outdoor dry bulb temperature and an assumed building balance point.
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Chris Mackey and Mostapha Sadeghipour Roudsari <Chris@MackeyArchitecture.com; Sadeghipour@gmail.com> 
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
This is a component for visualizing the desirability of shade in terms of comfort temperature by using solar vectors, a series of hourly temperatures (usually outdoor temperatures), and an assumed balance temperature.  The balance temperature represents the median temperture that people find comfortable, which can vary from climate to climate but is usually somewhere around 20C.
_
Solar vectors for hours when the temperature is above the balance point contribute positively to shade desirability while solar vectors for hours when the temperature is below the balance point contribute negatively.
_
The component outputs a colored mesh of the shade illustrating the net effect of shading each mesh face.  A higher saturation of blue indicates that shading the cell is very desirable.  A higher saturation of red indicates that shading the cell is harmful (blocking more winter sun than summer sun). Desaturated cells indicate that shading the cell will have relatively little effect on outdoor comfort or building performance.
_
The units for shade desirability are net temperture degree-days helped per unit area of shade if the test cell is blue.  If the test cell is red, the units are net heating degree-days harmed per unit area of shade.
_
The method used by this component is based off of the Shaderade method developed by Christoph Reinhart, Jon Sargent, Jeffrey Niemasz.  This component uses Shaderade's method for evaluating shade and window geometry in terms of solar vectors but substitutes Shaderade's energy simulation for an evaluation of heating and temperture degree-days about a balance temperature. 
_
A special thanks goes to them and their research.  A paper detailing the Shaderade method is available at:
http://web.mit.edu/tito_/www/Publications/BS2011_Shaderade.pdf
_
The heating/temperture degree-day calculation used here works by first getting the percentage of sun blocked by the test cell for each hour of the year using the Shaderade method.  Next, this percentage for each hour is multiplied by the temperature above or below the balance point for each hour to get a "degree-hour" for each hour of the year for a cell.  Then, all the temperture-degree hours (above the balance point) and heating degree-hours (below the balance point) are summed to give the total heating or temperture degree-hours helped or harmed respectively.  This number is divided by 24 hours of a day to give degree-days.  These degree days are normalized by the area of the cell to make the metric consistent across cells of different area.  Lastly, the negative heating degree-days are added to the positive temperture degree-days to give a net effect for the cell.

-
Provided by Ladybug 0.0.63
    
    Args:
        _location: The location output from the importEPW or constructLocation component.  This is essentially a list of text summarizing a location on the earth.
        _temperatures: A stream of 8760 temperature values (including a header) representing the temperature at each hour of the year that will be used to evaluate shade benefit.  This can be the dryBulbTemperature from the 'Import EPW' component, the univeralThermalClimateIndex (UTCI) output from the 'Outdoor Comfort Calculator' component, or the standardEffectiveTemperature (SET) output from the 'PMV Comfort Calculator' component.  If you are using this component to evaluate shade for a passive building with no heating/cooling, this input can also be the indoor temperature of the zone to be shaded.
        balanceTemperature_: An estimated balance temperature representing median temperture that people find comfortable, which can vary from climate to climate. The default is set to 17.5C, which is the median outdoor comfort temperature (UTCI) that defines the conditions of no thermal stress (9 < UTCI <26).
        temperatureOffest_: An number represeting the offset from the balanceTemperature_ in degrees Celcius at which point the shade importance begins to have an effect.  The default is set to 8.5 C, which is the range of outdoor comfort temperature (UTCI) that defines the conditions of no thermal stress (9 < UTCI <26).
        ============: ...
        _testShade: A brep or list of breps representing shading to be evaluated in terms of its benefit. Note that, in the case that multiple shading breps are connected, this component does not account for the interaction between the different shading surfaces. Note that only breps with a single surface are supported now and volumetric breps will be included at a later point.
        _testRegion: A brep representing an outdoor area for which shading is being considered or the window of a building that would be affected by the shade. Note that only breps with a single surface are supported now and volumetric breps will be included at a later point.
        gridSize_: The length of each of the shade's test cells in model units.  Please note that, as this value gets lower, simulation times will increase exponentially even though this will give a higher resolution of shade benefit.
        ============: ...
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        skyResolution_: An interger equal to 0 or above to set the number of times that the tergenza sky patches are split.  A higher number will ensure a greater accuracy but will take longer.  At a sky resolution of 4, each hour's temperature is essentially matched with an individual sun vector for that hour.  At a resolution of 5, a sun vector is produced for every half-hour, at 6, every quarter hour, and so on. The default is set to 4, which should be high enough of a resolution to produce a meaningful reault in all cases.
        delNonIntersect_: Set to "True" to delete mesh cells with no intersection with sun vectors.  Mesh cells where shading will have little effect because an equal amount of warm and cool temperature vectors will still be left in white.
        legendPar_: Legend parameters that can be used to re-color the shade, change the high and low boundary, or sync multiple evaluated shades with the same colors and legend parameters.
        parallel_: Set to "True" to run the simulation with multiple cores.  This can increase the speed of the calculation substantially and is recommended if you are not running other big or important processes.
        bakeIt_ : An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options:
            0 (or False) - No geometry will be baked into the Rhino scene (this is the default).
            1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. 
            2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry. 
        _runIt: Set to 'True' to run the simulation.
    Returns:
        readMe!: ...
        ==========: ...
        sunVectors: The sun vectors that were used to evaluate the shade (note that these will increase as the sky desnity increases).
        regionTestPts: Points across the test region surface from which sun vectors will be projected
        shadeMesh: A colored mesh of the _testShades showing where shading is helpful (in satuated blue), harmful (in saturated red), or does not make much of a difference (white or desaturated colors).
        legend: Legend showing the numeric values of degree-days that correspond to the colors in the shade mesh.
        ==========: ...
        shadeHelpfulness: The cumulative temperture degree-days/square Rhino model unit helped by shading the given cell. (C-day/m2)*if your model units are meters.
        shadeHarmfulness: The cumulative heating degree-days/square Rhino model unit harmed by shading the given cell. (C-day/m2)*if your model units are meters. Note that these values are all negative due to the fact that the shade is harmful. 
        shadeNetEffect: The sum of the helpfulness and harmfulness for each cell.  This will be negative if shading the cell has a net harmful effect and positive if the shade has a net helpful effect.
"""

ghenv.Component.Name = "Ladybug_Comfort Shade Benefit Evaluator"
ghenv.Component.NickName = 'ComfortShadeBenefit'
ghenv.Component.Message = 'VER 0.0.63\nAUG_28_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nJAN_24_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
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

from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

w = gh.GH_RuntimeMessageLevel.Warning

def checkTheInputs():
    #Create a dictionary of all of the input temperatures and shades.
    checkData1 = True
    allDataDict = {}
    
    for i in range(_testRegion.BranchCount):
        path = []
        for index in _testRegion.Path(i):
            path.append(index)
        path = str(path)
        
        if not allDataDict.has_key(path):
            allDataDict[path] = {}
        
        allDataDict[path]["regionSrf"] = _testRegion.Branch(i)
        allDataDict[path]["shadeSrfs"] = _testShades.Branch(i)
        allDataDict[path]["temperatures"] = _temperatures.Branch(i)
    
    
    #Check that both a region brep and test shade brep have only one surface.
    checkData2 = True
    if _testShades.BranchCount != 0 and _testRegion.BranchCount != 0:
        for path in allDataDict:
            newRegionList = []
            for srf in allDataDict[path]["regionSrf"]:
                if srf.Faces.Count == 1: newRegionList.append(srf)
                else:
                    for subSrf in srf.Faces:
                        srfBrep = subSrf.ToBrep()
                        newRegionList.append(srfBrep)
            allDataDict[path]["regionSrf"] = newRegionList
            
            newShadesList = []
            for srf in allDataDict[path]["shadeSrfs"]:
                try:
                    newSrf = rs.coercebrep(srf)
                    if newSrf.Faces.Count == 1: newShadesList.append(newSrf)
                    else:
                        for subSrf in newSrf.Faces:
                            srfBrep = subSrf.ToBrep()
                            newShadesList.append(srfBrep)
                except:
                    newSrf = rs.coercemesh(srf)
                    newShadesList.append(newSrf)
            allDataDict[path]["shadeSrfs"] = newShadesList
    else:
        checkData2 = False
        print 'Connect a brep for both the _testRegion and the _testShade.'
    
    
    #Check to see if users have connected a grid size.  If not, assign a grid size based on a bounding box around the test shade.
    checkData3 = True
    if gridSize_:
            if gridSize_ > 0: gridSize = float(gridSize_)
            else:
                warning = 'Values for gridSize_ must be positive.'
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
                gridSize = 0
                checkData3 = False
    else:
        for branch in allDataDict:
            testKey = branch
        boundBox = allDataDict[testKey]["shadeSrfs"][0].GetBoundingBox(False)
        box = rc.Geometry.Box(boundBox)
        if box.X[1] - box.X[0] < box.Y[1] - box.Y[0]:
            gridSize = (box.X[1] - box.X[0])/10
        else:
            gridSize = (box.Y[1] - box.Y[0])/10
        print "A default coarse grid size was chosen for your shades since you did not input a grid size."
    
    
    #Test to be sure that each window has a respective shade, and set of temperatures. If not, take them out of the dictionary.
    newAllDataDict = {}
    for branch in allDataDict:
        if allDataDict[branch].has_key('regionSrf') and allDataDict[branch].has_key('shadeSrfs') and allDataDict[branch].has_key('temperatures'):
            if not newAllDataDict.has_key(branch):
                newAllDataDict[branch] = {}
                newAllDataDict[branch]["regionSrf"] = allDataDict[branch]["regionSrf"]
                newAllDataDict[branch]["shadeSrfs"] = allDataDict[branch]["shadeSrfs"]
                newAllDataDict[branch]["temperatures"] = allDataDict[branch]["temperatures"]
        else:
            print "One of the data tree branches of the input data does not have all 3 required inputs of window, shade, and temperatures and has thus been disconted from the shade benefit evaluation."
    
    #Test to be sure that the correct headers are on the temperatures and that the correct data type is referenced in these headers.  Also check to be sure that the data is hourly.
    checkData4 = True
    analysisPeriods = []
    locations = []
    
    def checkDataHeaders(dataBranch, dataType, dataType2, dataName, bCount, numKey):
        if str(dataBranch[0]) == "key:location/dataType/units/frequency/startsAt/endsAt":
            try:
                analysisStart = dataBranch[5].split(')')[0].split('(')[-1].split(',')
                analysisEnd = dataBranch[6].split(')')[0].split('(')[-1].split(',')
                anaS = []
                anaE = []
                for item in analysisStart:anaS.append(int(item))
                for item in analysisEnd:anaE.append(int(item))
                analysisPeriods.append([tuple(anaS), tuple(anaE)])
            except:
                analysisPeriods.append([dataBranch[5], dataBranch[6]])
            locations.append(dataBranch[1])
            if dataType in dataBranch[2] or dataType2 in dataBranch[2]:
                if dataBranch[4] == "Hourly":
                    newList = []
                    for itemCount, item in enumerate(dataBranch):
                        if itemCount > 6:
                            newList.append(item)
                    newAllDataDict[branch][numKey] = newList
                else:
                    checkData4 = False
                    warning = "Data in the " + dataName + " input is not the right type of data.  Data must be of the correct type."
                    print warning
                    ghenv.Component.AddRuntimeMessage(w, warning)
            else:
                checkData4 = False
                warning = "Data in the " + dataName + " input is not hourly.  Data must be hourly."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        else:
            warning = 'Data in the ' + dataName + ' input does not possess a valid Ladybug header.  Data must have a header to use this component.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    for branchCount, branch in enumerate(newAllDataDict):
        checkDataHeaders(newAllDataDict[branch]["temperatures"], "Temperature", "Universal Thermal Climate Index", "_temperatures", branchCount, "temperture")
    
    #Make sure that the analysis periods and locations are all the same.
    checkData5 = True
    checkData6 = True
    checkData7 = True
    analysisPeriod = None
    location = None
    
    if checkData4 == True:
        if len(analysisPeriods) != 0:
            analysisPeriod = analysisPeriods[0]
            for period in analysisPeriods:
                if period  == analysisPeriod: pass
                else: checkData5 = False
        if checkData5 == False:
            warning = 'All of the analysis periods on the connected data are not the same.  Data must all be from the same analysis period.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        if len(locations) != 0:
            location = locations[0]
            for loc in locations:
                if loc  == location: pass
                else: checkData6 = False
        if checkData6 == False:
            warning = 'All of the locations on the connected data are not the same.  Data must all be from the same location.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    if balanceTemperature_ == None:
        balanceTemp = 17.5
        print "A default balanceTemperature_ of 17.5 C has been set, which defines the range of outdoor comfort temperature (UTCI) of no thermal stress (9 < UTCI <26)."
    elif balanceTemperature_ >= 9 and balanceTemperature_ <= 26: balanceTemp = balanceTemperature_
    else:
        checkData7 = False
        balanceTemp = None
        print 'balanceTemperature_ must be between 9 C and 26 C. Anything else is frankly not human.'
        ghenv.Component.AddRuntimeMessage(w, "_balanceTemperature must be between 9 C and 26 C. Anything else is frankly not human.")
    
    checkData10 = True
    if temperatureOffest_ == None:
        temperatureOffest = 8.5
        print "A default temperatureOffest_ of 8.5 C has been set, which defines the range of outdoor comfort temperature (UTCI) of no thermal stress (9 < UTCI <26)."
    elif temperatureOffest_ >= 0: temperatureOffest = temperatureOffest_
    else:
        checkData10 = False
        temperatureOffest = None
        print 'temperatureOffest_ must be greater than zero.'
        ghenv.Component.AddRuntimeMessage(w, "temperatureOffest_ must be greater than zero.")
    
    
    #Check the sky resolution and set a default.
    checkData8 = True
    if skyResolution_ == None:
        skyResolution = 4
        print "Sky resolution has been set to 4, which should be a high enough resolution to deal with almost all cases.\n You may want to decrease it for a faster simulation or increase it for a smoother gradient."
    else:
        if skyResolution_ >= 0:
            skyResolution = skyResolution_
            print "Sky resolution set to " + str(skyResolution)
        else:
            checkData8 = False
            warning = 'Sky resolution must be greater than 0.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the location, make sure that it matches the location of the inputData, and get the latitude, longitude, and time zone.
    checkData9 = True
    latitude = None
    longitude = None
    timeZone = None
    
    if _location != None:
        try:
            locList = _location.split('\n')
            for line in locList:
                if "Latitude" in line: latitude = float(line.split(',')[0])
                elif "Longitude" in line: longitude = float(line.split(',')[0])
                elif "Time Zone" in line: timeZone = float(line.split(',')[0])
        except:
            checkData9 = False
            warning = 'The connected _location is not a valid location from the "Ladybug_Import EWP" component or the "Ladybug_Construct Location" component.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    else:
        checkData9 = False
        print 'Connect a _location from the "Ladybug_Import EWP" component or the "Ladybug_Construct Location" component.'
    
    #Check the north direction and, if none is given, set a default to the Y-Axis.
    if north_ == None: north = 0
    else:
        north, northVec = lb_preparation.angle2north(north_)
    
    #Check if all of the above Checks are True
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True and checkData8 == True and checkData9 == True and checkData10 == True:
        checkData = True
    else:
        checkData = False
    
    return checkData, gridSize, newAllDataDict, skyResolution, analysisPeriod, location, latitude, longitude, timeZone, north, balanceTemp, temperatureOffest


def meshTheShade(gridSize, testShades):
    #Set the paramters for meshing the shade
    meshPar = rc.Geometry.MeshingParameters.Default
    meshPar.MinimumEdgeLength = gridSize
    meshPar.MaximumEdgeLength = gridSize
    
    #Create the lists of variables to be meshed.
    analysisBreps = []
    analysisAreasList = []
    analysisMeshList = []
    
    for testShade in testShades:
        try:
            analysisMesh = rc.Geometry.Mesh.CreateFromBrep(testShade, meshPar)[0]
        except:
            analysisMesh = testShade
        
        #Generate breps of the mesh faces so that users can see how the shade will be divided before they run the analysis
        
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
        
        #Append the lists to the total list.
        analysisAreasList.append(analysisAreas)
        analysisMeshList.append(analysisMesh)
    
    return analysisMeshList, analysisBreps, analysisAreasList


def generateTestPoints(gridSize, testRegion):
    def getPts(gridSiz, region):
        #Generate a Grid of Points Along the Window
        regionMeshPar = rc.Geometry.MeshingParameters.Default
        regionMeshPar.MinimumEdgeLength = (gridSiz/1.75)
        regionMeshPar.MaximumEdgeLength = (gridSiz/1.75)
        regionMesh = rc.Geometry.Mesh.CreateFromBrep(region, regionMeshPar)[0]
        
        vertices = regionMesh.Vertices
        
        # Convert window Point3f to Point3d
        regionTestPtsInit = []
        for item in vertices:
            regionTestPtsInit.append(rc.Geometry.Point3d(item))
        
        return regionTestPtsInit
    
    regionTestPtsFin = []
    for brep in testRegion:
        regionTestPtsFin.extend(getPts(gridSize, brep))
    
    if len(regionTestPtsFin) < 10:
        regionVertices = []
        for regbrep in testRegion: regionVertices.extend(regbrep.DuplicateVertices())
        bbox = rc.Geometry.Box(rc.Geometry.BoundingBox())
        bboxDim = [(bbox.X[1] - bbox.X[0]), (bbox.Y[1] - bbox.Y[0]), (bbox.Z[1] - bbox.Z[0])]
        bboxDim.sort()
        if bboxDim[0] < sc.doc.ModelAbsoluteTolerance: smallestDim = bboxDim[1]
        else: smallestDim = bboxDim[0]
        newGridSize = smallestDim/10
        regionTestPtsFin = []
        for brep in testRegion: regionTestPtsFin.extend(getPts(newGridSize, brep))
    
    return regionTestPtsFin


def prepareGeometry(gridSize, allDataDict):
    #Things to generate: shadeFaceAreas, allShadeBreps, regionTestPts, shadeMesh, shadeMeshBreps
    #Create the lists that will be filled.
    regionTestPts = []
    shadeMeshBreps = []
    
    for branchCount, branch in enumerate(allDataDict):
        #Mesh the shade.
        shadeMesh, shadeMeshBrepList, shadeMeshAreas = meshTheShade(gridSize, allDataDict[branch]["shadeSrfs"])
        
        shadeMeshBreps.append(shadeMeshBrepList)
        allDataDict[branch]["shadeMesh"] = shadeMesh
        allDataDict[branch]["shadeMeshAreas"] = shadeMeshAreas
        
        #Generate window test points.
        regionPoints = generateTestPoints(gridSize, allDataDict[branch]["regionSrf"])
        regionTestPts.append(regionPoints)
        allDataDict[branch]["regionPts"] = regionPoints
    
    return regionTestPts, shadeMeshBreps, allDataDict


def checkSkyResolution(skyResolution, allDataDict, analysisPeriod, latitude, longitude, timeZone, north, lb_sunpath, lb_preparation):
    # Make lists for all of the sun up hours of the data dictionary.
    for path in allDataDict:
        allDataDict[path]["tempertureSun"] = []
    
    #Get all of the sun vectors for the analysis period.
    sunVectors = []
    sunUpHoys = []
    lb_sunpath.initTheClass(latitude, north, rc.Geometry.Point3d.Origin, 1, longitude, timeZone)
    if analysisPeriod != [(1,1,1), (12,31,24)]:
        HOYs, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
    else:
        HOYs = range(8760)
    HOYStart = HOYs[0]
    
    
    
    if skyResolution <= 4:
        for count, hoy in enumerate(HOYs):
            d, m, h = lb_preparation.hour2Date(hoy, True)
            m += 1
            lb_sunpath.solInitOutput(m, d, h)
            
            if lb_sunpath.solAlt >= 0:
                sunVec = lb_sunpath.sunReverseVectorCalc()
                sunVectors.append(sunVec)
                sunUpHoys.append(count)
                for path in allDataDict:
                    allDataDict[path]["tempertureSun"].append(float(allDataDict[path]["temperture"][count]))
    else:
        newHOYs = []
        hourDivisions = []
        dividend = 1/(math.pow(2, (skyResolution-4)))
        startVal = dividend
        while startVal < 1:
            hourDivisions.append(startVal)
            startVal += dividend
        for hoy in HOYs:
            for division in hourDivisions:
                newHOYs.append(hoy - 1 + division)
            newHOYs.append(hoy)
        for hoy in newHOYs:
            d, m, h = lb_preparation.hour2Date(hoy, True)
            m += 1
            lb_sunpath.solInitOutput(m, d, h)
            
            if lb_sunpath.solAlt >= 0:
                sunVec = lb_sunpath.sunReverseVectorCalc()
                sunVectors.append(sunVec)
                sunUpHoys.append(hoy)
                for path in allDataDict:
                    allDataDict[path]["tempertureSun"].append(float(allDataDict[path]["temperture"][int(hoy)]))
    
    #Check to see if the user has requested the highest resolution and, if not, consolidate the sun vectors into sky patches.
    finalSunVecs = []
    finalPatchHOYs = []
    for path in allDataDict:
        allDataDict[path]["tempertureFinal"] = []
        allDataDict[path]["divisor"] = []
    
    if skyResolution < 4:
        newVecs = []
        skyPatches = lb_preparation.generateSkyGeo(rc.Geometry.Point3d.Origin, skyResolution, .5)
        skyPatchMeshes = []
        for patch in skyPatches:
            verts = patch.DuplicateVertices()
            if len(verts) == 4:
                patchBrep = rc.Geometry.Brep.CreateFromCornerPoints(verts[0], verts[1], verts[2], verts[3], sc.doc.ModelAbsoluteTolerance)
            else: patchBrep = patch
            skyPatchMeshes.append(rc.Geometry.Mesh.CreateFromBrep(patchBrep, rc.Geometry.MeshingParameters.Coarse)[0])
            patchPt = rc.Geometry.AreaMassProperties.Compute(patch).Centroid
            newVec = rc.Geometry.Vector3d(patchPt)
            newVecs.append(newVec)
            finalPatchHOYs.append([])
        
        for vecCount, vector in enumerate(sunVectors):
            ray = rc.Geometry.Ray3d(rc.Geometry.Point3d.Origin, vector)
            for patchCount, patch in enumerate(skyPatchMeshes):
                if rc.Geometry.Intersect.Intersection.MeshRay(patch, ray) >= 0:
                    finalPatchHOYs[patchCount].append(sunUpHoys[vecCount])
        
        vecCount = -1
        for patchCount, hourList in enumerate(finalPatchHOYs):
            if hourList != []:
                vecCount += 1
                finalSunVecs.append(newVecs[patchCount])
                for path in allDataDict:
                    allDataDict[path]["tempertureFinal"].append(0)
                    allDataDict[path]["divisor"].append(0)
                
                for hour in hourList:
                    for path in allDataDict:
                        allDataDict[path]["tempertureFinal"][vecCount] = allDataDict[path]["tempertureFinal"][vecCount] + float(allDataDict[path]["temperture"][hour])
                        allDataDict[path]["divisor"][vecCount] += 1
        
        for path in allDataDict:
            for vecCount2, tempSum in enumerate(allDataDict[path]["tempertureFinal"]):
                allDataDict[path]["tempertureFinal"][vecCount2] = tempSum/allDataDict[path]["divisor"][vecCount2]
    elif skyResolution >= 4:
        finalSunVecs = sunVectors
        for path in allDataDict:
            allDataDict[path]["tempertureFinal"] = allDataDict[path]["tempertureSun"]
    
    return allDataDict, finalSunVecs


def nonparallel_projection(analysisMesh, sunLines, regionTestPts):
    #Intersect the sun lines with the test mesh
    faceInt = []
    for face in range(analysisMesh.Faces.Count): faceInt.append([])
    
    for ptCount, pt in enumerate(regionTestPts):
        try:
            for hour, sunLine in enumerate(sunLines[ptCount]):
                if sunLine != 0:
                    intPt, i = rc.Geometry.Intersect.Intersection.MeshLine(analysisMesh, sunLine)
                    if len(intPt)!=0: faceInt[i[0]].append(hour)
                else: pass
        except Exception, e:
            print `e`
    
    return faceInt


def parallel_projection(analysisMesh, sunLines, regionTestPts):
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
    
    tasks.Parallel.ForEach(range(len(regionTestPts)), intersect)
    
    return faceInt


def valCalc(percentBlocked, deltaBal, cellArea, numDaySteps):
    #Multiply the percentBlocked by the deltaBal to get a measure of how helpful or harmful the shade is in each hour of the year
    hourlyEffect = [a*b for a,b in zip(percentBlocked,deltaBal)]
    
    #Sum up all of resulting hourly effects depending on whether the effect is negative or positive to get the effect of the cell on the total heating, temperture degree days felt by the window.
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
    coolEffect = ((coolEffectInit)/cellArea)/numDaySteps
    heatEffect = ((heatEffectInit)/cellArea)/numDaySteps
    netEffect = ((netEffectInit)/cellArea)/numDaySteps
    
    return coolEffect, heatEffect, netEffect


def evaluateShade(temperatures, balanceTemp, temperatureOffest, numHrs, analysisMesh, analysisAreas, regionMesh, regionTestPts, sunVectors, skyResolution):
    #Determine the length to make the sun lines based on the scale of the bounding box around the input geometry.
    def joinMesh(meshList):
        joinedMesh = rc.Geometry.Mesh()
        for m in meshList: joinedMesh.Append(m)
        return joinedMesh
    
    joinedMesh = joinMesh([analysisMesh, regionMesh])
    
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
    
    for pt in regionTestPts: sunLines.append([]) 
    
    for ptCount, pt in enumerate(regionTestPts):
        for vec in sunVectors:
            if context_:
                if rc.Geometry.Intersect.Intersection.MeshRay(contextMesh, rc.Geometry.Ray3d(pt, vec)) < 0:
                    sunLines[ptCount].append(rc.Geometry.Line(pt, lineLength * vec))
                else: sunLines[ptCount].append(0)
            else:
                sunLines[ptCount].append(rc.Geometry.Line(pt, lineLength * vec))
            
    
    #If parallel is true, then run the intersection through the parallel function.  If not, run it through the normal function.
    if parallel_ == True:
        faceInt = parallel_projection(analysisMesh, sunLines, regionTestPts)
    else:
        faceInt = nonparallel_projection(analysisMesh, sunLines, regionTestPts)
    
    #Convert the Number Of Intersections for Each Mesh Face into a Percent of Sun Blocked by Each Mesh Face for Each Hour of the Year.
    percentBlocked = []
    for face in range(analysisMesh.Faces.Count):
        percentBlocked.append(len(sunVectors) *[0])
    
    testPtsCount = len(regionTestPts) 
    # for each mesh surface,
    for faceCount, faceData in enumerate(faceInt):
        # check the number of intersections for each hour
        counter= collections.Counter(faceData)
        
        for hour in counter.keys():
             # store the result in the new percentBlocked list
             percentBlocked[faceCount][hour] = counter[hour]/testPtsCount
    
    #Calculate how far the hourly temperatures are from the balance point, allowing for a range of +/- 2C in which people will be comfortable.
    comfortRange = temperatureOffest
    deltaBal = []
    if numHrs == []:
        for hrCount, temp in enumerate(temperatures):
            if temp > (balanceTemp + comfortRange):
                deltaBal.append(temp - (balanceTemp + comfortRange))
            elif temp < (balanceTemp - comfortRange):
                deltaBal.append(temp - (balanceTemp - comfortRange))
            else:
                deltaBal.append(0)
    else:
        for hrCount, temp in enumerate(temperatures):
            if temp > (balanceTemp + comfortRange):
                deltaBal.append((temp - (balanceTemp + comfortRange))*numHrs[hrCount])
            elif temp < (balanceTemp - comfortRange):
                deltaBal.append((temp - (balanceTemp - comfortRange))*numHrs[hrCount])
            else:
                deltaBal.append(0)
    
    #Compare the percent blocked for each hour with the temperatre at that hour in relation to the balance point in order to determine the net value of shading.
    if skyResolution == 4: numDaySteps = 24
    elif skyResolution == 0: numDaySteps = 8
    elif skyResolution == 1: numDaySteps = 10
    elif skyResolution == 2: numDaySteps = 13
    elif skyResolution == 3: numDaySteps = 17
    else: numDaySteps = (math.pow(2, (skyResolution-4)))*24
    shadeHelpfulness = []
    shadeHarmfulness = []
    shadeNetEffect = []
    for cellCount, cell in enumerate(percentBlocked):
        shadeHelp, shadeHarm, shadeNet = valCalc(cell, deltaBal, analysisAreas[cellCount], numDaySteps)
        shadeHelpfulness.append(shadeHelp)
        shadeHarmfulness.append(shadeHarm)
        shadeNetEffect.append(shadeNet)
    
    return shadeHelpfulness, shadeHarmfulness, shadeNetEffect



def main(allDataDict, balanceTemp, temperatureOffest, sunVectors, skyResolution, legendPar, lb_preparation, lb_visualization):
    #Create lists to be filled.
    totalNetEffect = []
    totalShadeGeo = []
    shadeHelpfulnessList = []
    shadeHarmfulnessList = []
    shadeNetEffectList = []
    shadeMeshListInit = []
    shadeMeshList = []
    calcSuccess = True
    
    try:
        #Evaluate each shade.
        for regionCount, path in enumerate(allDataDict):
            # let the user cancel the process
            if gh.GH_Document.IsEscapeKeyDown(): assert False
            
            shadeHelpfulnessList.append([])
            shadeHarmfulnessList.append([])
            shadeNetEffectList.append([])
            shadeMeshListInit.append([])
            shadeMeshList.append([])
            
            temperatures = allDataDict[path]["tempertureFinal"]
            numHrs = allDataDict[path]["divisor"]
            
            regionMesh = rc.Geometry.Mesh()
            for brep in allDataDict[path]["regionSrf"]:
                regionMesh.Append(rc.Geometry.Mesh.CreateFromBrep(brep)[0])
            regionPoints = allDataDict[path]["regionPts"]
            
            for shadeCount, shadeMesh in enumerate(allDataDict[path]["shadeMesh"]):
                totalShadeGeo.append(shadeMesh)
                shadeMeshListInit[regionCount].append(shadeMesh)
                shadeMeshAreas = allDataDict[path]["shadeMeshAreas"][shadeCount]
                shadeHelpfulness, shadeHarmfulness, shadeNetEffect = evaluateShade(temperatures, balanceTemp, temperatureOffest, numHrs, shadeMesh, shadeMeshAreas, regionMesh, regionPoints, sunVectors, skyResolution)
                
                
                for item in shadeNetEffect: totalNetEffect.append(item)
                shadeHelpfulnessList[regionCount].append(shadeHelpfulness)
                shadeHarmfulnessList[regionCount].append(shadeHarmfulness)
                shadeNetEffectList[regionCount].append(shadeNetEffect)
        
        #Sort the net effects to find the highest and lowest values which will be used to generate colors and a legend for the mesh.
        shadeNetSorted = totalNetEffect[:]
        shadeNetSorted.sort()
        mostHelp = shadeNetSorted[-1]
        mostHarm = shadeNetSorted[0]
        if abs(mostHelp) > abs(mostHarm): legendVal = abs(mostHelp)
        else: legendVal = abs(mostHarm)
        
        #Get the colors for the analysis mesh based on the calculated benefit values unless a user has connected specific legendPar.
        legendFont = 'Verdana'
        if legendPar:
            lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
            if legendPar[3] == []:
                customColors = lb_visualization.gradientLibrary[12]
                customColors.reverse()
        else:
            lowB = -1 * legendVal
            highB = legendVal
            numSeg = 11
            customColors = lb_visualization.gradientLibrary[12]
            customColors.reverse()
            legendBasePoint = None
            legendFontSize = None
            legendBold = False
            legendScale = 1
            decimalPlaces = 2
            removeLessThan = False
        
        #If the user has not input custom boundaries, automatically choose the boundaries for them.
        if lowB == "min": lowB = -1 * legendVal
        if highB == "max": highB = legendVal
        
        #Color each of the meshes with shade benefit.
        for regionCount, shadeMeshGroup in enumerate(shadeMeshListInit):
            for shadeCount, shadeMesh in enumerate(shadeMeshGroup):
                shadeMeshNetEffect = shadeNetEffectList[regionCount][shadeCount]
                colors = lb_visualization.gradientColor(shadeMeshNetEffect, lowB, highB, customColors)
                coloredShadeMesh = lb_visualization.colorMesh(colors, shadeMesh)
                shadeMeshList[regionCount].append(coloredShadeMesh)
        
        # If the user has set "delNonIntersect_" to True, delete those mesh values that do not have any solar intersections.
        if delNonIntersect_ == True:
            for regionCount, shadeMeshGroup in enumerate(shadeMeshList):
                for shadeCount, shadeMesh in enumerate(shadeMeshGroup):
                    deleteFaces = []
                    newShadeHelpfulness = []
                    newShadeHarmfulness = []
                    newShadeNetEffect = []
                    shadeMeshNetEffect = shadeNetEffectList[regionCount][shadeCount]
                    for cellCount, cell in enumerate(shadeMeshNetEffect):
                        if shadeHelpfulnessList[regionCount][shadeCount][cellCount] == 0.0 and shadeHarmfulnessList[regionCount][shadeCount][cellCount] == 0.0:
                            deleteFaces.append(cellCount)
                        else:
                            newShadeHelpfulness.append(shadeHelpfulnessList[regionCount][shadeCount][cellCount])
                            newShadeHarmfulness.append(shadeHarmfulnessList[regionCount][shadeCount][cellCount])
                            newShadeNetEffect.append(cell)
                    shadeMesh.Faces.DeleteFaces(deleteFaces)
                    shadeHelpfulnessList[regionCount][shadeCount] = newShadeHelpfulness
                    shadeHarmfulnessList[regionCount][shadeCount] = newShadeHarmfulness
                    shadeNetEffectList[regionCount][shadeCount] = newShadeNetEffect
    except:
        calcSuccess = False
        print "The calculation has been terminated by the user!"
        e = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(e, "The calculation has been terminated by the user!")
    
    if calcSuccess == True:
        #Generate a legend for all of the meshes.
        lb_visualization.calculateBB(totalShadeGeo, True)
        
        units = sc.doc.ModelUnitSystem
        legendTitle = 'Degree-Day/(' + str(units) + ')2'
        analysisTitle = '\nShade Benefit Analysis'
        if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
        
        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(shadeNetEffect, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
        legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
        legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
        
        titlebasePt = lb_visualization.BoundingBoxPar[-2]
        titleTextCurve = lb_visualization.text2srf([analysisTitle], [titlebasePt], legendFont, legendScale * (lb_visualization.BoundingBoxPar[2]/20), legendBold)
        
        #Package the final legend together.
        legend = []
        legend.append(legendSrfs)
        for item in lb_preparation.flattenList(legendTextCrv + titleTextCurve):
            legend.append(item)
        
        #If we have got all of the outputs, let the user know that the calculation has been successful.
        print 'Shade benefit caclculation successful!'
        
        if bakeIt_ > 0:
            #Bring all of the text together.
            legendText.append(analysisTitle)
            textPt.append(titlebasePt)
            #Join the shade mesh into one.
            analysisSrfs = rc.Geometry.Mesh()
            for meshList in shadeMeshList:
                for mesh in meshList: analysisSrfs.Append(mesh)
            #Bake the objects
            studyLayerName = 'SHADE_BENEFIT_ANALYSIS'
            placeName = _location.split('\n')[1]
            newLayerIndex, l = lb_visualization.setupLayers(None, 'LADYBUG', placeName, studyLayerName, False, False, 0, 0)
            if bakeIt_ == 1: lb_visualization.bakeObjects(newLayerIndex, analysisSrfs, legendSrfs, legendText, textPt, textSize, legendFont, None, decimalPlaces, True)
            else: lb_visualization.bakeObjects(newLayerIndex, analysisSrfs, legendSrfs, legendText, textPt, textSize, legendFont, None, decimalPlaces, False)
        
        return shadeHelpfulnessList, shadeHarmfulnessList, shadeNetEffectList, shadeMeshList, legend, legendBasePoint
    else:
        return -1





#Import the classes, check the inputs, and generate default values for grid size if the user has given none.
checkLB = True
if sc.sticky.has_key('ladybug_release'):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    lb_sunpath = sc.sticky["ladybug_SunPath"]()
else:
    checkLB = False
    print "You should let the Ladybug fly first..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should let the Ladybug fly first...")

#Check the inputs.
checkData = False
if _temperatures.BranchCount > 0 and _testShades.BranchCount > 0 and _testRegion.BranchCount > 0 and _location != None:
    if _temperatures.Branch(0)[0] != None and _testShades.Branch(0)[0] != None and _testRegion.Branch(0)[0] != None:
        checkData, gridSize, allDataDict, skyResolution, analysisPeriod, locationData, latitude, longitude, timeZone, north, balanceTemp, temperatureOffest = checkTheInputs()

#If everything passes above, prepare the geometry for analysis.
if checkLB == True and checkData == True:
    regionTestPtsInit, shadeMeshInit, geoAllDataDict = prepareGeometry(gridSize, allDataDict)
    
    #Unpack the data trees of test pts and shade mesh breps so that the user can see them and get a sense of what to expect from the evaluation.
    regionTestPts = DataTree[Object]()
    shadeMesh = DataTree[Object]()
    for brCount, branch in enumerate(regionTestPtsInit):
        for item in branch:
            regionTestPts.Add(item, GH_Path(brCount))
    for brCount, branch in enumerate(shadeMeshInit):
        for item in branch:
            shadeMesh.Add(item, GH_Path(brCount))


#If all of the data is good and the user has set "_runIt" to "True", run the shade benefit calculation to generate all results.
if checkLB == True and checkData == True and _runIt == True:
    finalAllDataDict, sunVectors = checkSkyResolution(skyResolution, geoAllDataDict, analysisPeriod, latitude, longitude, timeZone, north, lb_sunpath, lb_preparation)
    result = main(finalAllDataDict, balanceTemp, temperatureOffest, sunVectors, skyResolution, legendPar_, lb_preparation, lb_visualization)
    
    if result != -1:
        shadeHelpfulnessList, shadeHarmfulnessList, shadeNetEffectList, shadeMeshList, legend, legendBasePt = result
        
        shadeMesh = DataTree[Object]()
        shadeHelpfulness = DataTree[Object]()
        shadeHarmfulness = DataTree[Object]()
        shadeNetEffect = DataTree[Object]()
        
        for regionCount, path in enumerate(finalAllDataDict):
            for shadeCount, shade in enumerate(shadeMeshList[regionCount]):
                newPath = path.split(']')[0].split('[')[-1]
                finalPath = ()
                for item in newPath.split(','):
                    num = int(item)
                    finalPath = finalPath + (num,)
                b = shadeCount
                finalPath = finalPath + (b,)
                
                shadeMesh.Add(shade, GH_Path(finalPath))
                for item in shadeHelpfulnessList[regionCount][shadeCount]: shadeHelpfulness.Add(item, GH_Path(finalPath))
                for item in shadeHarmfulnessList[regionCount][shadeCount]: shadeHarmfulness.Add(item, GH_Path(finalPath))
                for item in shadeNetEffectList[regionCount][shadeCount]: shadeNetEffect.Add(item, GH_Path(finalPath))
        
        ghenv.Component.Params.Output[3].Hidden = True
        ghenv.Component.Params.Output[6].Hidden = True
else:
    ghenv.Component.Params.Output[3].Hidden = False
    ghenv.Component.Params.Output[6].Hidden = False


