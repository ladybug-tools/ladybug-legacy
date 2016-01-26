# This script used to be ladybug all in one
# I separated them into three parts before distribution which made it such a mess
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
Use this component to evaluate the visibility of input _geometry from a set of key viewing points.
For example, this component can be used to evaluate the visibility of an 3D architectural feature from a set of key viewing points along a nearby street or park where people congregate.
Another example would be evaluating the visibility of park vegetation geometry from a set of key sun position points from the sunPath component.
Yet another example would be evaluating the "visibility" of an outdoor overhead radiative heater from a set of key "viewing" points located over a human body standing beneath it.
This component outputs a percentage of viewpoints seen by the input _geometry.  In the three examples here, this would be the percentage of the 3D architectural feature seen from the street, the percentage of sunlit hours received by the vegetation, or the percentage of the human body warmed by the heater.
This component will evaluate view from the test points objectively in all directions. 

-
Provided by Ladybug 0.0.62
    
    Args:
        _geometry: Geometry for which visibility analysis will be conducted.  Geometry must be either a Brep, a Mesh, or a list of Breps or Meshes.
        context_: Context geometry that could block the view from the _viewTypeOrPoints to the test _geometry.  Conext geometry must be either a Brep, a Mesh, or a list of Breps or Meshes.
        _gridSize_: A number in Rhino model units that represents the average size of a grid cell for visibility analysis on the test _geometry.  This value should be smaller than the smallest dimension of the test _geometry for meaningful results.  Note that, the smaller the grid size, the higher the resolution of the analysis and the longer the calculation will take.
        _disFromBase: A number in Rhino model units that represents the offset distance of the test point grid from the input test _geometry.  Usually, the test point grid is offset by a small amount from the test _geometry in order to ensure that visibility analysis is done for the correct side of the test _geometry.  If the resulting mesh of this component is offset to the wrong side of test _geometry, you should use the "Flip" Rhino command on the test _geometry before inputting it to this component.
        orientationStudyP_: Optional output from the "Orientation Study Parameter" component.  You can use an Orientation Study input here to answer questions like "What orientation of my building will give me the highest or lowest visibility from the street?"  An Orientation Study will automatically rotate your input _geometry around several times and record the visibility results each time in order to output a list of values for averageView and a grafted data stream for viewStudyResult.
        _viewTypeOrPoints: An integer representing the type of view analysis that you would like to conduct or a list of points to which you would like to test the view.  For integer options, choose from the following options:
            0 - Horizontal Radial - The percentage of the 360 horizontal view band visible from each test point. Use this to study horizontal views from interior spaces to the outdoors.
            1 - Horizontal 60 Degree Cone of Vision - The percentage of the 360 horizontal view band bounded on top and bottom by a 30 degree offset from the horizontal (derived from the human cone of vision). Use this to study views from interior spaces to the outdoors.  Note that this will discount the _geometry from the calculation and only look at _context that blocks the scene.
            2 - Spherical - The percentage of the sphere surrounding each of the test points that is not blocked by context geometry. Note that this will discount the _geometry from the calculation and only look at _context that blocks the scene.
            3 - Skyview - The percentage of the sky that is visible from the input _geometry.
        viewPtsWeights_: A list of numbers that align with the test points to assign weights of importance to the several _viewTypeOrPoints that have been connected.  Weighted values should be between 0 and 1 and should be closer to 1 if a certain point is more important. The default value for all points is 0, which means they all have an equal importance. This input could be useful in cases such as the radiative heater example where points on the human body with exposed skin could be weighted at a higher value.
        _____________________: ...
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        parallel_: Set to "True" to run the visibility analysis using multiple CPUs.  This can dramatically decrease calculation time but can interfere with other intense computational processes that might be running on your machine.
        _runIt: Set to "True" to run the component and perform visibility analysis of the input _geometry.
        bakeIt_ : An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options:
            0 (or False) - No geometry will be baked into the Rhino scene (this is the default).
            1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. 
            2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry.
    Returns:
        readMe!: ...
        contextMesh: An uncolored mesh representing the context_ geometry that was input to this component. Connect this output to a "Mesh" grasshopper component to preview this output seperately from the others of this component. Note that this mesh is generated before the analysis is run, allowing you to be sure that the right geometry will be run through the analysis before running this component.
        analysisMesh: An uncolored mesh representing the test _geometry that will be analyzed.  Connect this output to a "Mesh" grasshopper component to preview this output seperately from the others of this component. Note that this mesh is generated before the analysis is run, allowing you to be sure that the right geometry will be run through the analysis before running this component.
        testPts: The grid of test points on the test _geometry that will be used to perform the visibility analysis.  Note that these points are generated before the analysis is run, allowing you to preview the resolution of the result before you run the component.
        testVec: Vectors for each of the test points on the test _geometry, which indicate the direction for which visibility analysis is performed.  Hook this and the test points up to a Grasshopper "Vector Display" component to see how analysis is performed on the test _geometry.
        _____________________: ...
        viewStudyResult: The percentage of _viewTypeOrPoints visible from each of the test points of the input test _geometry.
        viewStudyMesh: A colored mesh of the test _geometry representing the percentage of _viewTypeOrPoints visible by each part of the input _geometry.
        viewStudyLegend: A legend for the visibility analysis showing the percentage of visible points that correspond to the colors of the viewStudyMesh. Connect this output to a grasshopper "Geo" component in order to preview the legend separately in the Rhino scene.  
        legendBasePt: The legend base point, which can be used to move the legend in relation to the view study mesh with the grasshopper "move" component.
        averageView: The average percentage of the _viewTypeOrPoints seen by all of the test _geometry.
        ptIsVisible: A grafted data stream for each _geometry test point with a "1" for each _viewPoint that is visible by the test point and a "0" for each _viewPoint that is blocked.
"""

ghenv.Component.Name = "Ladybug_View Analysis"
ghenv.Component.NickName = 'viewAnalysis'
ghenv.Component.Message = 'VER 0.0.62\nJAN_25_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nJAN_24_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass



import rhinoscriptsyntax as rs
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import math
import Rhino as rc
import sys
import scriptcontext as sc
import System.Threading.Tasks as tasks
import System
import time
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


w = gh.GH_RuntimeMessageLevel.Warning
e = gh.GH_RuntimeMessageLevel.Error

inputsDict = {
0: ["_geometry", "Geometry for which visibility analysis will be conducted.  Geometry must be either a Brep, a Mesh, or a list of Breps or Meshes."],
1: ["context_", "Context geometry that could block the view from the _viewTypeOrPoints to the test _geometry.  Conext geometry must be either a Brep, a Mesh, or a list of Breps or Meshes."],
2: ["_gridSize_", "A number in Rhino model units that represents the average size of a grid cell for visibility analysis on the test _geometry.  This value should be smaller than the smallest dimension of the test _geometry for meaningful results.  Note that, the smaller the grid size, the higher the resolution of the analysis and the longer the calculation will take."],
3: ["_disFromBase", "A number in Rhino model units that represents the offset distance of the test point grid from the input test _geometry.  Usually, the test point grid is offset by a small amount from the test _geometry in order to ensure that visibility analysis is done for the correct side of the test _geometry.  If the resulting mesh of this component is offset to the wrong side of test _geometry, you should use the 'Flip' Rhino command on the test _geometry before inputting it to this component."],
4: ["orientationStudyP_", "Optional output from the 'Orientation Study Parameter' component.  You can use an Orientation Study input here to answer questions like 'What orientation of my building will give me the highest or lowest visibility from the street?'  An Orientation Study will automatically rotate your input _geometry around several times and record the visibility results each time in order to output a list of values for averageView and a grafted data stream for viewStudyResult."],
5: ["_viewTypeOrPoints", "An integer representing the type of view analysis that you would like to conduct or a list of points to which you would like to test the view.  For integer options, choose from the following options: \n0 - Horizontal Radial - The percentage of the 360 horizontal view band visible from each test point. Use this to study horizontal views from interior spaces to the outdoors. \n 1 - Horizontal 60 Degree Cone of Vision - The percentage of the 360 horizontal view band bounded on top and bottom by a 30 degree offset from the horizontal (derived from the human cone of vision). Use this to study views from interior spaces to the outdoors. Note that this will discount the _geometry from the calculation and only look at _context that blocks the scene. \n2 - Spherical - The percentage of the sphere surrounding each of the test points that is not blocked by context geometry. Note that this will discount the _geometry from the calculation and only look at _context that blocks the scene. \n3 - Skyview - The percentage of the sky that is visible from the input _geometry."],
6: ["viewPtsWeights_", "A list of numbers that align with the test points to assign weights of importance to the several _viewTypeOrPoints that have been connected.  Weighted values should be between 0 and 1 and should be closer to 1 if a certain point is more important. The default value for all points is 0, which means they all have an equal importance. This input could be useful in cases such as the radiative heater example where points on the human body with exposed skin could be weighted at a higher value."],
7: ["_____________________", "..."],
8: ["legendPar_", "Optional legend parameters from the Ladybug Legend Parameters component."],
9: ["parallel_", "Set to 'True' to run the visibility analysis using multiple CPUs.  This can dramatically decrease calculation time but can interfere with other intense computational processes that might be running on your machine."],
10: ["_runIt", "Set to 'True' to run the component and perform visibility analysis of the input _geometry."],
11: ["bakeIt_", "An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options: \n     0 (or False) - No geometry will be baked into the Rhino scene (this is the default). \n     1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. \n     2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry."]
}


def setComponentInputs():
    for input in range(12):
        if input == 6:
            ghenv.Component.Params.Input[input].NickName = 'viewResolution_'
            ghenv.Component.Params.Input[input].Name = 'viewResolution_'
            ghenv.Component.Params.Input[input].Description = 'An interger between 0 and 4 to set the number of times that the tergenza skyview patches are split.  A higher number will ensure a greater accuracy but will take longer.  The default is set to 0 for a quick calculation.' 
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]

def restoreComponentInputs():
    for input in range(12):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]

def checkViewType(lb_preparation):
    viewVecs, viewType = [], -1
    try:
        viewType = int(_viewTypeOrPoints[0])
        if viewType >= 0 and viewType <= 3: pass
        else:
            warning = "_viewTypeOrPoints must be between 0 and 3."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
        
        viewRes = 0
        if viewResolution_ != []:
            try: viewRes = int(viewResolution_[0])
            except:
                warning = "viewResolution_ must be an integer."
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                return -1
        viewVecs = checkViewResolution(viewRes, viewType, lb_preparation)
    except:
        try:
            for val in _viewTypeOrPoints:
                vSplit = val.split(',')
                vect = rc.Geometry.Point3d(float(vSplit[0]), float(vSplit[1]), float(vSplit[2]))
                viewVecs.append(vect)
        except:
            warning = "Input for _viewTypeOrPoints not recognized."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
    
    return viewVecs, viewType

def checkViewResolution(viewResolution, viewType, lb_preparation):
    newVecs = []
    
    if viewType != 0:
        skyPatches = lb_preparation.generateSkyGeo(rc.Geometry.Point3d.Origin, viewResolution, 1)
        for patch in skyPatches:
            patchPt = rc.Geometry.AreaMassProperties.Compute(patch).Centroid
            Vec = None
            if viewType == 2 or viewType == 3: Vec = rc.Geometry.Vector3d(patchPt.X, patchPt.Y, patchPt.Z)
            elif viewType == 1 and patchPt.Z < 0.5: Vec = rc.Geometry.Vector3d(patchPt.X, patchPt.Y, patchPt.Z)
            
            if Vec != None:
                newVecs.append(Vec)
                if viewType == 1 or viewType == 2:
                    revVec = rc.Geometry.Vector3d(-patchPt.X, -patchPt.Y, -patchPt.Z)
                    newVecs.append(revVec)
    else:
        numberDivisions = (viewResolution+1) * 20
        initAngle = 0
        divisionAngleDeg = 360/numberDivisions
        divisionAngle = math.radians(divisionAngleDeg)
        for count in range(numberDivisions):
            viewVecInit = rc.Geometry.Vector3d.YAxis
            viewVecInit.Rotate(initAngle, rc.Geometry.Vector3d.ZAxis)
            newVecs.append(viewVecInit)
            initAngle += divisionAngle
    
    return newVecs


def openLegend(legendRes):
    if len(legendRes)!=0:
        meshAndCrv = []
        meshAndCrv.append(legendRes[0])
        [meshAndCrv.append(c) for c in legendRes[1]]
        return meshAndCrv
    else: return


def runAnalyses(testPoints, ptsNormals, meshSrfAreas, analysisSrfs, contextSrfs, parallel, viewPoints_viewStudy, viewPtsWeights, conversionFac, viewType, lb_mesh, lb_runStudy_GH):
    listInfo = ['key:location/dataType/units/frequency/startsAt/endsAt', 'City/Latitude', 'View Analysis', '%', 'NA', (1, 1, 1), (12, 31, 24)]
    if parallel:
        try:
            for geo in analysisSrfs + contextSrfs: geo.EnsurePrivateCopy()
        except: pass
    
    # join the meshes
    joinedAnalysisMesh = lb_mesh.joinMesh(analysisSrfs)
    if contextSrfs: joinedContext = lb_mesh.joinMesh(contextSrfs)
    else: joinedContext = None
    
    viewResults, averageViewResults, ptVisibility = lb_runStudy_GH.parallel_viewCalculator(testPoints, ptsNormals, meshSrfAreas, joinedAnalysisMesh, joinedContext, parallel, viewPoints_viewStudy, viewPtsWeights, conversionFac, viewType)
    
    return [viewResults], [averageViewResults], listInfo, ptVisibility


def resultVisualization(contextSrfs, analysisSrfs, results, totalResults, legendPar, legendTitle, studyLayerName, bakeIt, checkTheName, l, angle, listInfo, runOrientation, lb_visualization, lb_preparation):
    #Check the analysis Type.
    projectName = 'ViewToPoints'
    
    #Read Legend Parameters.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    if len(legendPar_) == 0: customColors = lb_visualization.gradientLibrary[3]
    elif legendPar_[3] == []: customColors = lb_visualization.gradientLibrary[3]
    
    colors = lb_visualization.gradientColor(results, lowB, highB, customColors)
    
    # color mesh surfaces
    analysisSrfs = lb_visualization.colorMesh(colors, analysisSrfs)
    
    ## generate legend
    # calculate the boundingbox to find the legendPosition
    if not (runOrientation and legendBasePoint==None):
        lb_visualization.calculateBB([analysisSrfs, contextSrfs])
    # legend geometry
    legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(results, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
    
    # legend colors
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    # color legend surfaces
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    
    customHeading = '\n\nView Analysis' + '\n#View Points = ' + `len(_viewTypeOrPoints)`
    if runOrientation:
        try: customHeading = customHeading + '\nRotation Angle: ' + `angle` + ' Degrees'
        except: pass
    titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo], lb_visualization.BoundingBoxPar, legendScale, customHeading, True, legendFont, legendFontSize, legendBold)
    
    if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
    
    if bakeIt > 0:
        legendText.append(titleStr)
        textPt.append(titlebasePt)
        # check the study type
        newLayerIndex, l = lb_visualization.setupLayers(totalResults, 'LADYBUG', projectName,
                                                        studyLayerName, checkTheName,
                                                        runOrientation, angle, l)
        if bakeIt == 1: lb_visualization.bakeObjects(newLayerIndex, analysisSrfs, legendSrfs, legendText, textPt, textSize, legendFont, None, decimalPlaces, True)
        else: lb_visualization.bakeObjects(newLayerIndex, analysisSrfs, legendSrfs, legendText, textPt, textSize, legendFont, None, decimalPlaces, False)
    
    return analysisSrfs, [legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)], l, legendBasePoint



def main(geometry, context, gridSize, disFromBase, orientationStudyP, viewPoints_viewStudy, viewPtsWeights, legendPar, parallel, bakeIt):
    # import the classes
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_mesh = sc.sticky["ladybug_Mesh"]()
    lb_runStudy_GH = sc.sticky["ladybug_RunAnalysis"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    
    conversionFac = lb_preparation.checkUnits()
    
    #Check the view type.
    viewType = -1
    viewCheck = checkViewType(lb_preparation)
    if viewCheck != -1:
        viewPoints_viewStudy, viewType = viewCheck
    else: return -1
    
    # read orientation study parameters
    runOrientation, rotateContext, rotationBasePt, angles = lb_preparation.readOrientationParameters(orientationStudyP)
    
    # mesh the test buildings
    ## clean the geometry and bring them to rhinoCommon separated as mesh and Brep
    analysisMesh, analysisBrep = lb_preparation.cleanAndCoerceList(geometry)
    
    originalTestPoints = []
    if gridSize == None:
        gridSize = 4/conversionFac
    
    ## mesh Brep
    analysisMeshedBrep = lb_mesh.parallel_makeSurfaceMesh(analysisBrep, float(gridSize))
    
    ## Flatten the list of surfaces
    analysisMeshedBrep = lb_preparation.flattenList(analysisMeshedBrep)
    analysisSrfs = analysisMesh + analysisMeshedBrep
    
    ## extract test points
    testPoints, ptsNormals, meshSrfAreas = lb_mesh.parallel_testPointCalculator(analysisSrfs, float(disFromBase), parallel)
    originalTestPoints = testPoints
    testPoints = lb_preparation.flattenList(testPoints)
    ptsNormals = lb_preparation.flattenList(ptsNormals)
    meshSrfAreas = lb_preparation.flattenList(meshSrfAreas)
    
    ## mesh context
    if len(context)!=0 and gridSize and disFromBase:
        ## clean the geometry and bring them to rhinoCommon separated as mesh and Brep
        contextMesh, contextBrep = lb_preparation.cleanAndCoerceList(context)
        
        ## mesh Brep
        contextMeshedBrep = lb_mesh.parallel_makeContextMesh(contextBrep)
        
        ## Flatten the list of surfaces
        contextMeshedBrep = lb_preparation.flattenList(contextMeshedBrep)
        contextSrfs = contextMesh + contextMeshedBrep
    else: contextSrfs = []
    
    
    ## data for visualization
    CheckTheName = True
    resV = 0 # Result visualization
    l = [0, 0, 0] # layer name indicator
    
    ## check for orientation Study
    if runOrientation and (len(viewPoints_viewStudy)!= 0 and viewPoints_viewStudy!=[]):
        if not isinstance(rotateContext, System.Boolean):
            #inputs are geometries and should be set as the context to be rotated
            rContextMesh, rContextBrep = rotateContext
            
            ## mesh Brep
            rContextMeshedBrep = lb_mesh.parallel_makeContextMesh(rContextBrep)
            
            ## Flatten the list of surfaces
            rContextMeshedBrep = lb_preparation.flattenList(rContextMeshedBrep)
            rContextSrfs = rContextMesh + rContextMeshedBrep
            rotateContext = "Partial"
        elif rotateContext == True:
            rContextSrfs = contextSrfs
        else:
            rContextSrfs = None
            
        # create rotation base point
        if rotationBasePt == 'set2center'and rotateContext=="Partial":
            # find the bounding box for the test geometry and context
            lb_visualization.calculateBB([analysisSrfs, rContextSrfs])
            rotationBasePt = rc.Geometry.Point3d(lb_visualization.BoundingBoxPar[4])
        elif rotationBasePt == 'set2center'and rotateContext:
            # find the bounding box for the test geometry and context
            lb_visualization.calculateBB([analysisSrfs, rContextSrfs])
            rotationBasePt = rc.Geometry.Point3d(lb_visualization.BoundingBoxPar[4])
        elif rotationBasePt == 'set2center'and not rotateContext:
            lb_visualization.calculateBB(analysisSrfs)
            rotationBasePt = rc.Geometry.Point3d(lb_visualization.BoundingBoxPar[4])
            # this is stupid and should be fixed later but for now I let it be!
            lb_visualization.calculateBB([analysisSrfs, contextSrfs])
            
        # total result is a list of lists
        orirntationStudyRes = {}
        totalResults = []
        angleCount = 0
        for angle in range(len(angles) - 1):
            rotationT = (rc.Geometry.Transform.Rotation(math.radians(angles[angle + 1] - angles[angle]) , rc.Geometry.Vector3d.ZAxis, rotationBasePt))
            # rotate the geometry, and points (and maybe the context)
            # print angles[angle + 1] - angles[angle] # there is a bug here!
            [srf.Transform(rotationT) for srf in analysisSrfs]
            [p.Transform(rotationT) for p in testPoints]
            [n.Transform(rotationT) for n in  ptsNormals]
            if rotateContext == "Partial":
                [msh.Transform(rotationT) for msh in rContextSrfs]
                # put the rotated mesh next to the rest of the context
                mergedContextSrfs = rContextSrfs + contextSrfs
            elif rotateContext:
                [msh.Transform(rotationT) for msh in rContextSrfs]
                mergedContextSrfs = rContextSrfs
            else:
                mergedContextSrfs = contextSrfs
                        
            ## run the analysis
            cumSky_radiationStudy = []
            sunVectors_sunlightHour = []
            
            results, eachTotalResult, listInfo, pointVisiblity = runAnalyses(testPoints, ptsNormals, meshSrfAreas,
                                        analysisSrfs, mergedContextSrfs, parallel, viewPoints_viewStudy, viewPtsWeights, conversionFac, viewType, lb_mesh, lb_runStudy_GH)
            
            #collect surfaces, results, and values
            orirntationStudyRes[angle] = {"angle" : angle,
                                          "totalResult": eachTotalResult,
                                          "results": results,
                                          "listInfo": listInfo,
                                          "contextSrf" : lb_mesh.joinMesh(mergedContextSrfs),
                                          "analysisSrf": lb_mesh.joinMesh(analysisSrfs)
                                          }
            
            # print
            totalResults.append(eachTotalResult)
            angleCount += 1
            
        if legendPar== [] or (legendPar[0] == None and legendPar[1] == None):
            # find max and min for the legend
            minValue = float("inf") 
            maxValue = 0
            allBuildingsAndContext = []
            for key in orirntationStudyRes.keys():
                # results is a nested list because the component used to be all in one
                # I should re-write this component at some point
                listMin = min(orirntationStudyRes[key]["results"][0])
                listMax = max(orirntationStudyRes[key]["results"][0])
                if  listMin < minValue: minValue = listMin
                if  listMax > maxValue: maxValue = listMax
                
                if legendPar== [] or legendPar[4] == None:
                    allBuildingsAndContext.extend([orirntationStudyRes[key]["analysisSrf"], orirntationStudyRes[key]["contextSrf"]])
            
            # find the collective bounding box
            if legendPar== [] or legendPar[4] == None:
                lb_visualization.calculateBB(allBuildingsAndContext)
            
            # preset the legend parameters if it is not set by the user
            if legendPar== []:
                legendPar = [minValue, maxValue, None, [], lb_visualization.BoundingBoxPar, 1, 'Verdana', None, False, 2, False]
            else:
                if legendPar[0] == None: legendPar[0] = minValue
                if legendPar[1] == None: legendPar[1] = maxValue
                if legendPar[4] == None: legendPar[4] = lb_visualization.BoundingBoxPar
                if legendPar[5] == None or float(legendPar[5])==0: legendPar[5] = 1
                if legendPar[6] == None: legendPar[6] = 'Verdana'
                if legendPar[7] == None: legendPar[7] = None
                if legendPar[8] == None: legendPar[8] = False
                if legendPar[9] == None: legendPar[9] = 2
                if legendPar[10] == None: legendPar[10] = False
        
        for angleCount, angle in enumerate(range(len(angles) - 1)):
            if (bakeIt or angles[angle + 1] == angles[-1]) and results!=-1:
                
                # read the values for each angle from the dictionary
                eachTotalResult = orirntationStudyRes[angle]["totalResult"]
                mergedContextSrfs = orirntationStudyRes[angle]["contextSrf"]
                analysisSrfs = orirntationStudyRes[angle]["analysisSrf"]
                listInfo = orirntationStudyRes[angle]["listInfo"]
                results = orirntationStudyRes[angle]["results"]
                
                
                resultColored = [[] for x in range(len(results))]
                legendColored = [[] for x in range(len(results))]
                if angleCount > 0: CheckTheName = False
                
                for i in range(len(results)):
                    if results[0]!=[] and results[i]!= None:
                        # Add an option for orientation study
                        # The i is a reminder from the time that all the analysis components was a single component
                        # so confusing!
                        #eachTotalResult = [[],[],[]]
                        resultColored[i], legendColored[i], l[i], legendBasePoint = resultVisualization(mergedContextSrfs, analysisSrfs,
                                          results[0], eachTotalResult[0], legendPar, '%',
                                          'VIEW_STUDIES', bakeIt, CheckTheName, l[i], angles[angle + 1], listInfo, runOrientation, lb_visualization, lb_preparation)
                        resV += 1
    else:
        # no orientation study
        angle = 0; l = [0]
        results, totalResults, listInfo, pointVisiblity = runAnalyses(testPoints, ptsNormals, meshSrfAreas,
                                analysisSrfs, contextSrfs, parallel, viewPoints_viewStudy, viewPtsWeights, conversionFac, viewType, lb_mesh, lb_runStudy_GH)
    
    #Returen view vectors is the vector method is specified.
    viewVecs = []
    if viewType != -1: viewVecs = viewPoints_viewStudy
    
    #Return the results
    if results!=-1 and viewPoints_viewStudy == []:
        #No view type or points have been selected.  We're just showing the gridsize.
        #contextSrfs, analysisSrfs, testPoints, ptsNormals = results
        return contextSrfs, analysisSrfs, testPoints, ptsNormals, originalTestPoints, viewVecs
    elif results != -1:
        #A view study has been run.
        if not runOrientation:
            totalResults = [totalResults] # make a list of the list so the same process can be applied to orientation study and normal run
        else:
            bakeIt = False
        
        resultColored = []
        legendColored = []
        [resultColored.append([]) for x in range(len(results))]
        [legendColored.append([]) for x in range(len(results))]
        
        for i in range(len(results)):
            if results[i]!= None:
                # Add an option for orientation study
                resultColored[i], legendColored[i], l[i], legendBasePoint = resultVisualization(contextSrfs, analysisSrfs,
                                  results[i], totalResults[0][i], legendPar, '%',
                                  'VIEW_STUDIES', bakeIt, CheckTheName, 0, angles[-1], listInfo, runOrientation, lb_visualization, lb_preparation)
                resV += 1
        
        # return outputs
        if runOrientation: contextSrfs = mergedContextSrfs
        if resV != 0: return contextSrfs, analysisSrfs, testPoints, ptsNormals, viewVecs, results, resultColored, legendColored, totalResults, legendBasePoint, originalTestPoints, pointVisiblity
        else: return -1
    else:
        return -1





initCheck = True
#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): pass
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)

#Set the Inputs.
try:
    viewType = int(_viewTypeOrPoints[0])
    setComponentInputs()
except:
    restoreComponentInputs()

#Run the component.
if _runIt and len(_geometry)!=0 and _geometry[0] != None and _disFromBase and initCheck == True:
    result = main(_geometry, context_, _gridSize_, _disFromBase, orientationStudyP_, _viewTypeOrPoints, viewPtsWeights_, legendPar_, parallel_, bakeIt_)
    
    if result!= -1:
        if len(result) == 6:
            contextMesh, analysisMesh, testPts_flatten, testVec_flatten, originalTestPoints, viewVec = result
            viewStudyMesh, viewStudyLegend = None, None
        elif len(result) > 6:
            # Assign the result to GH component outputs
            contextMesh, analysisMesh, testPts_flatten, testVec_flatten, viewVec = result[0], result[1], result[2], result[3], result[4]
            
            viewStudyResult_flatten = result[5][0]
            viewStudyMesh = result[6][0]
            viewStudyLegend = openLegend(result[7][0])
            
            # total results
            averageView = []
            for res in result[8]:
                averageView.append(res[0])
            
            legendBasePt = result[-3]
            originalTestPoints = result[-2]
            pointsVisibility = result[-1]
        
        testPts = DataTree[System.Object]()
        testVec = DataTree[System.Object]() 
        ptIsVisible = DataTree[System.Object]()
        viewStudyResult = DataTree[System.Object]()
        
        # graft test points
        ptCount = 0
        for i, ptList in enumerate(originalTestPoints):
            p = GH_Path(i)
            for pCount, pt in enumerate(ptList):
                testPts.Add(pt, p)
                testVec.Add(testVec_flatten[ptCount], p)
                if result!= -1 and len(result) != 5:
                    #try:
                    q = GH_Path(i, pCount)
                    viewStudyResult.Add(viewStudyResult_flatten[ptCount], p)
                    ptIsVisible.AddRange(pointsVisibility[ptCount], q)
                    #except: pass
                ptCount += 1
    else: print "Canceled by user!"


ghenv.Component.Params.Output[1].Hidden = True
ghenv.Component.Params.Output[2].Hidden = True
ghenv.Component.Params.Output[3].Hidden = True
ghenv.Component.Params.Output[10].Hidden = True