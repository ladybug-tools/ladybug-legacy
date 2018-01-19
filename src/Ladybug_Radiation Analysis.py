# This script used to be ladybug all in one
# I separated them into three parts before distribution which made it such a mess
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
This component allows you to calculate the radiation fallin on input _geometry using a sky matrix from the selectSkyMxt component.
This type of radiation sutdy is useful for building surfaces such as windows, where you might be interested in solar heat gain, or solar panels, where you might be interested in the energy that can be collected.
This component is also good for surfaces representing outdoor spaces (such as parks or seating areas) where radiation could affect thermal comfort or vegetation growth.
No reflection of sunlight is included in the radiation analysis with this component and it should therefore be used
neither for interior daylight studies nor for complex geometries nor for surfaces with high a reflectivity.
For these situations where the relfection of light is important, the Honeybee daylight components should be used instead of this one.


-
Provided by Ladybug 0.0.66
    
    Args:
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _geometry: Geometry for which radiation analysis will be conducted.  Geometry must be either a Brep, a Mesh or a list of Breps or Meshes.
        context_: Context geometry that could block sunlight to the test _geometry.  Conext geometry must be either a Brep, a Mesh or a list of Breps or Meshes.
        _gridSize_: A number in Rhino model units that represents the average size of a grid cell for radiation analysis on the test surface(s).  This value should be smaller than the smallest dimension of the test geometry for meaningful results.  Note that, the smaller the grid size, the higher the resolution of the analysis and the longer the calculation will take.
        _disFromBase: A number in Rhino model units that represents the offset distance of the test point grid from the input test _geometry.  Usually, the test point grid is offset by a small amount from the test _geometry in order to ensure that radiation analysis is done for the correct side of the test _geometry.  If the resulting testPts of this component are offset to the wrong side of test _geometry, you should use the "Flip" Rhino command on the test _geometry before inputting it to this component.
        contextTransmit_: A number or list of numbers that corresponds to the number of input context surfaces to denote the transmittance of the context.  Note that this number must be between 0 and 1.  The default assumes all context is opaque with a transmittance of 0.
        orientationStudyP_: Optional output from the "Orientation Study Parameter" component.  You can use an Orientation Study input here to answer questions like "What orientation of my building will give me the highest or lowest radiation gain for my analysis period?"  An Orientation Study will automatically rotate your input _geometry around several times and record the radiation results each time in order to output a list of values for totalRadiation and a grafted data stream for radiationResult.
        _selectedSkyMtx: The output from the selectSkyMtx component.
        _____________________: ...
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        parallel_: Set to "True" to run the radiation analysis using multiple CPUs.  This can dramatically decrease calculation time but can interfere with other intense computational processes that might be running on your machine.
        _runIt: Set to "True" to run the component and perform radiation analysis on the input _geometry.
        bakeIt_ : An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options:
            0 (or False) - No geometry will be baked into the Rhino scene (this is the default).
            1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. 
            2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry.
        workingDir_: Use this input to change the working directory of the radiation analysis on your system. Input here must be a valid file path location on your computer.  The default is set to "C:\Ladybug" and it is from this file location that radiation results are loaded into grasshopper after the analysis is done.
        projectName_: Use this input to change the project name of the files generated in the working directory.  Input here must be a string without special characters.  If "bakeIt_" is set to "True", the result will be baked into a layer with this project name.
    Returns:
        readMe!: ...
        contextMesh: An uncolored mesh representing the context_ geometry that was input to this component. Connect this output to a "Mesh" grasshopper component to preview this output seperately from the others of this component. Note that this mesh is generated before the analysis is run, allowing you to be sure that the right geometry will be run through the analysis before running this component.
        analysisMesh: An uncolored mesh representing the test _geometry that will be analyzed.  Connect this output to a "Mesh" grasshopper component to preview this output seperately from the others of this component. Note that this mesh is generated before the analysis is run, allowing you to be sure that the right geometry will be run through the analysis before running this component.
        testPts: The grid of test points on the test _geometry that will be used to perform the radiation analysis.  Note that these points are generated before the analysis is run, allowing you to preview the resolution of the result before you run the component.
        testVec: Vectors for each of the test points on the test _geometry, which indicate the direction for which radiation analysis is performed.  Hook this and the test points up to a Grasshopper "Vector Display" component to see how analysis is performed on the test _geometry.
        _____________________: ...
        radiationResult: The amount of radiation in kWh/m2 falling on the input test _geometry at each of the test points.
        radiationMesh: A colored mesh of the test _geometry representing the radiation in kWh/m2 falling on this input _geometry for the selected sky.
        radiationLegend: A legend for the radiation study showing radiation values that correspond to the colors of the radiationMesh. Connect this output to a grasshopper "Geo" component in order to preview the legend separately in the Rhino scene.  
        legendBasePt: The legend base point, which can be used to move the legend in relation to the radiation mesh with the grasshopper "move" component.
        totalRadiation: The total radiation in kWh falling on the input test _geometry.  This is computed through a mass addition of results at each of the test points in kWh/m2 multiplied by the area of the face that the test point is representing.
        intersectionMtx: A python list that includes the relation between each test point and all the sky patchs on the sky dome.  After running a basic radiation study, you can connect this output to the Ladybug "Real Time Radiation Analysis" component to scroll through the radiation falling on your test geometry on an hour-by-hour, day-by-day, or month-by-month basis in real time.
"""

ghenv.Component.Name = "Ladybug_Radiation Analysis"
ghenv.Component.NickName = 'radiationAnalysis'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass



import rhinoscriptsyntax as rs
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

if len(_selectedSkyMtx)!=0: cumSky_radiationStudy = _selectedSkyMtx
else: cumSky_radiationStudy = []


def runAnalyses(testPoints, ptsNormals, meshSrfAreas, analysisSrfs, contextSrfs, contextTransmit, parallel, cumSky_radiationStudy, viewPoints_viewStudy, viewFields_Angles_D, sunVectors_sunlightHour, conversionFac, northVector, lb_preparation, lb_mesh, lb_runStudy_GH):
    RADIANCE_radiationStudy = []
    if len(RADIANCE_radiationStudy)!=0:
        pass
    elif cumSky_radiationStudy != None and (len(cumSky_radiationStudy) == 456 or len(cumSky_radiationStudy) == 1752) and analysisSrfs:
        indexList, listInfo = lb_preparation.separateList(cumSky_radiationStudy, lb_preparation.strToBeFound)
        selList = []
        for i in range(1):
            [selList.append(float(x)) for x in cumSky_radiationStudy[indexList[i]+7:indexList[i+1]]]
            
        cumSky_radiationStudy = selList
        if parallel:
            try:
                for geo in analysisSrfs + contextSrfs: geo.EnsurePrivateCopy()
            except:
                pass
        
        # join the meshes and group them by transmitance.
        joinedAnalysisMesh = lb_mesh.joinMesh(analysisSrfs)
        if contextTransmit != []:
            transmitGroup = []
            contextGroup = []
            for count, val in enumerate(contextTransmit):
                if not val in transmitGroup:
                    transmitGroup.append(val)
                    contextGroup.append(contextSrfs[count])
                else:
                    for mcount, trans in enumerate(transmitGroup):
                        if val == trans:
                            contextGroup[mcount].Append(contextSrfs[count])
            
            if len(cumSky_radiationStudy) == 145:
                radResults, totalRadResults, intersectionMtx = lb_runStudy_GH.parallel_radCalculator(testPoints, ptsNormals, meshSrfAreas, joinedAnalysisMesh, contextGroup,
                                        parallel, cumSky_radiationStudy, lb_preparation.TregenzaPatchesNormalVectors, conversionFac, 2200000000000000, northVector, transmitGroup)
            elif len(cumSky_radiationStudy) == 577:
                radResults, totalRadResults, intersectionMtx = lb_runStudy_GH.parallel_radCalculator(testPoints, ptsNormals, meshSrfAreas, joinedAnalysisMesh, contextGroup,
                                        parallel, cumSky_radiationStudy, lb_preparation.getReinhartPatchesNormalVectors(), conversionFac, 2200000000000000, northVector, transmitGroup)
        else:
            if contextSrfs: joinedContext = lb_mesh.joinMesh(contextSrfs)
            else: joinedContext = None
            
            if len(cumSky_radiationStudy) == 145:
                radResults, totalRadResults, intersectionMtx = lb_runStudy_GH.parallel_radCalculator(testPoints, ptsNormals, meshSrfAreas, joinedAnalysisMesh, joinedContext,
                                        parallel, cumSky_radiationStudy, lb_preparation.TregenzaPatchesNormalVectors, conversionFac, 2200000000000000, northVector)
            elif len(cumSky_radiationStudy) == 577:
                radResults, totalRadResults, intersectionMtx = lb_runStudy_GH.parallel_radCalculator(testPoints, ptsNormals, meshSrfAreas, joinedAnalysisMesh, joinedContext,
                                        parallel, cumSky_radiationStudy, lb_preparation.getReinhartPatchesNormalVectors(), conversionFac, 2200000000000000, northVector)
                                    
    else:
        print "selectedSkyMtx failed to collect data! Use selectSkyMtx component to generate the selectedSkyMtx."
        radResults = totalRadResults = None
        
        return [contextSrfs, analysisSrfs, testPoints, ptsNormals], -1, -1, -1
    
    results = radResults, None, None
    totalResults = totalRadResults, None, None
    
    return results, totalResults, listInfo, intersectionMtx

def resultVisualization(contextSrfs, analysisSrfs, results, totalResults, legendPar, legendTitle, studyLayerName, bakeIt, checkTheName, l, angle, listInfo, lb_preparation, lb_visualization, runOrientation):
    
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    
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
    
    customHeading = '\n\nRadiation Analysis'
    if runOrientation:
        try: customHeading = customHeading + '\nRotation Angle: ' + `angle` + ' Degrees'
        except: pass
    titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo[0]], lb_visualization.BoundingBoxPar, legendScale, customHeading, False, legendFont, legendFontSize, legendBold)
    
    if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
    
    if bakeIt:
        legendText.append(titleStr)
        textPt.append(titlebasePt)
        # check the study type
        newLayerIndex, l = lb_visualization.setupLayers(totalResults, 'LADYBUG', projectName_,
                                                        studyLayerName, checkTheName,
                                                        runOrientation, angle, l)
        if bakeIt == 1: lb_visualization.bakeObjects(newLayerIndex, analysisSrfs, legendSrfs, legendText, textPt, textSize, legendFont, None, decimalPlaces, True)
        else: lb_visualization.bakeObjects(newLayerIndex, analysisSrfs, legendSrfs, legendText, textPt, textSize, legendFont, None, decimalPlaces, False)
    
    return analysisSrfs, [legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)], l, legendBasePoint

def openLegend(legendRes):
    if len(legendRes)!=0:
        meshAndCrv = []
        meshAndCrv.append(legendRes[0])
        [meshAndCrv.append(c) for c in legendRes[1]]
        return meshAndCrv
    else: return

def main(north, geometry, context, gridSize, disFromBase, contextTransmit, orientationStudyP, cumSky_radiationStudy, legendPar, parallel, runIt, bakeIt, workingDir, projectName):
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
        lb_mesh = sc.sticky["ladybug_Mesh"]()
        lb_runStudy_GH = sc.sticky["ladybug_RunAnalysis"]()
        #lb_runStudy_RAD = sc.sticky["ladybug_Export2Radiance"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1
    
    # Check lengths of transmittance lists.
    if contextTransmit != []:
        if len(contextTransmit) == len(context):
            pass
        elif len(contextTransmit) == 1:
            contextTransmit = [contextTransmit[0] for x in context]
        else:
            message = "The number of values in contextTransmit_ does not match the number of contex geomtries."
            print message
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, message)
            return -1
    
    conversionFac = lb_preparation.checkUnits()
    # north direction
    northAngle, northVector = lb_preparation.angle2north(north)
    
    # read orientation study parameters
    runOrientation, rotateContext, rotationBasePt, angles = lb_preparation.readOrientationParameters(orientationStudyP)
    
    # mesh the test buildings
    if len(geometry)!=0 and disFromBase:
        ## clean the geometry and bring them to rhinoCommon separated as mesh and Brep
        analysisMesh, analysisBrep = lb_preparation.cleanAndCoerceList(geometry)
        
        if gridSize == None:
            gridSize = 4/conversionFac
            originalTestPoints = []
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
    else:
        print "Please connect the geometry and set up both the gridSize and the distance from base surface..."
        analysisSrfs = testPoints = ptsNormals = meshSrfAreas = []
        return -1, -1, -1
    ## mesh context
    if len(context)!=0 and gridSize and disFromBase:
        ## clean the geometry and bring them to rhinoCommon separated as mesh and Brep
        contextMesh, contextBrep = lb_preparation.cleanAndCoerceList(context)
        
        ## mesh Brep
        contextMeshedBrep = lb_mesh.parallel_makeContextMesh(contextBrep)
        
        ## Flatten the list of surfaces
        finalContextBrep = []
        for meshList in contextMeshedBrep:
            newMesh = rc.Geometry.Mesh()
            for mesh in meshList:
                newMesh.Append(mesh)
            finalContextBrep.append(newMesh)
        contextMeshedBrep = finalContextBrep
        
        contextSrfs = contextMesh + contextMeshedBrep
    else: contextSrfs = []
    
    ## data for visualization
    legendTitles = ['kWh/m2', 'Hours', '%']
    try: legendTitles[0] = cumSky_radiationStudy[3]
    except: pass
    
    studyLayerNames = ['RADIATION_STUDIES', 'SUNLIGHTHOURS_STUDIES', 'VIEW_STUDIES']
    CheckTheName = True
    resV = 0 # Result visualization
    ## check for orientation Study
    l = [0, 0, 0] # layer name indicator
    if runOrientation and cumSky_radiationStudy != []:
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
            viewPoints_viewStudy = []
            viewFields_Angles_D = []
            sunVectors_sunlightHour = []
            results, eachTotalResult, listInfo, intersectionMtx = runAnalyses(testPoints, ptsNormals, meshSrfAreas,
                                        analysisSrfs, mergedContextSrfs, contextTransmit, parallel, cumSky_radiationStudy,
                                        viewPoints_viewStudy, viewFields_Angles_D,
                                        sunVectors_sunlightHour, conversionFac, northVector, lb_preparation, lb_mesh, lb_runStudy_GH)
            
            #collect surfaces, results, and values
            orirntationStudyRes[angle] = {"angle" : angle,
                                          "totalResult": eachTotalResult,
                                          "results": results,
                                          "listInfo": listInfo,
                                          "contextSrf" : lb_mesh.joinMesh(mergedContextSrfs),
                                          "analysisSrf": lb_mesh.joinMesh(analysisSrfs)
                                          }
            
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
            if (bakeIt != 0 or angles[angle + 1] == angles[-1]) and results!=-1:
                
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
                        resultColored[i], legendColored[i], l[i], legendBasePoint = resultVisualization(mergedContextSrfs, analysisSrfs,
                                          results[i], eachTotalResult[i], legendPar, legendTitles[i],
                                          studyLayerNames[i], bakeIt, CheckTheName, l[i], angles[angle + 1], listInfo, lb_preparation, lb_visualization, runOrientation)
                        resV += 1
            
    else:
        # no orientation study
        angle = 0; l = [0, 0, 0]
        viewPoints_viewStudy = []; viewFields_Angles_D = []; sunVectors_sunlightHour = []
        results, totalResults, listInfo, intersectionMtx = runAnalyses(testPoints, ptsNormals, meshSrfAreas,
                                analysisSrfs, contextSrfs, contextTransmit, parallel, cumSky_radiationStudy,
                                viewPoints_viewStudy, viewFields_Angles_D,
                                sunVectors_sunlightHour, conversionFac, northVector, lb_preparation, lb_mesh, lb_runStudy_GH)
    
    if results!=-1 and len(results) == 4:
        contextSrfs, analysisSrfs, testPoints, ptsNormals = results
        return contextSrfs, analysisSrfs, testPoints, ptsNormals, originalTestPoints
    
    elif results!=-1:
        if not runOrientation:
            totalResults = [totalResults] # make a list of the list so the same process can be applied to orientation study and normal run
        else:
            bakeIt = 0
        
        resultColored = []
        legendColored = []
        [resultColored.append([]) for x in range(len(results))]
        [legendColored.append([]) for x in range(len(results))]
        for i in range(len(results)):
            if results[i]!= None:
                #angles
                # Add an option for orientation study
                resultColored[i], legendColored[i], l[i], legendBasePoint = resultVisualization(contextSrfs, analysisSrfs,
                              results[i], totalResults[0][i], legendPar, legendTitles[i],
                              studyLayerNames[i], bakeIt, CheckTheName, 0, angles[-1], listInfo, lb_preparation, lb_visualization, runOrientation)
                resV += 1
        
        
        
        # return outputs
        if runOrientation: contextSrfs = mergedContextSrfs
        if resV != 0:
            return contextSrfs, analysisSrfs, testPoints, ptsNormals, results, resultColored, legendColored, totalResults, legendBasePoint, originalTestPoints, intersectionMtx
            
        else: return -1
        return -1



if _runIt:
    
    try:
        test = contextTransmit_
    except:
        contextTransmit_ = []
    
    if (len(_geometry)!=0 and _geometry[0] != None and _disFromBase):
        
        result = main(north_, _geometry, context_, _gridSize_, _disFromBase, contextTransmit_,
                    orientationStudyP_, _selectedSkyMtx, legendPar_, parallel_,
                    _runIt, bakeIt_, workingDir_, projectName_)
        
        if result!= -1 and len(result) > 5:
            # Assign the result to GH component outputs
            contextMesh, analysisMesh, testPts_flatten, testVec_flatten = result[0], result[1], result[2], result[3]
           
            # radiation
            radiationResult_flatten = result[4][0]
            radiationMesh = result[5][0]
            radiationLegend = openLegend(result[6][0])
            
            # sunlightHours
            sunlightHoursResult = result[4][1]
            sunlightHoursMesh = result[5][1]
            sunlightHoursLegend = openLegend(result[6][1])
            
            # sunlightHours
            viewStudyResult = result[4][2]
            viewStudyMesh = result[5][2]
            viewStudyLegend = openLegend(result[6][2])
            
            # total results
            totalRadiation = []; totalSunlightHours = []; totalView = []
            for res in result[7]:
                totalRadiation.append(res[0])
                totalSunlightHours.append(res[1])
                totalView.append(res[2])
            
            legendBasePt = result[-3]
            originalTestPoints = result[-2]
            intMtx = result[-1]
            
            class conevertDictToClass(object):
                def __init__(self, valuesDict):
                    self.d = valuesDict
            
            intersectionMtx = conevertDictToClass(intMtx)
            
        elif result!= -1 and len(result) == 5:
            contextMesh, analysisMesh, testPts_flatten, testVec_flatten, originalTestPoints = result
        
        testPts = DataTree[System.Object]()
        testVec = DataTree[System.Object]() 
        
        if result!= -1:
            radiationResult = DataTree[System.Object]()
        
            # graft test points
            ptCount = 0
            for i, ptList in enumerate(originalTestPoints):
                p = GH_Path(i)
                for pt in ptList:
                    testPts.Add(pt, p)
                    testVec.Add(testVec_flatten[ptCount], p)
                    if result!= -1 and len(result) != 4:
                        try: radiationResult.Add(radiationResult_flatten[ptCount], p)
                        except: pass
                    ptCount += 1
            ghenv.Component.Params.Output[1].Hidden= True
            ghenv.Component.Params.Output[2].Hidden= True
            ghenv.Component.Params.Output[3].Hidden= True
            ghenv.Component.Params.Output[9].Hidden= True
        
    else:
        result = -1
        
    if result == -1 and not (len(_geometry)!=0 and _geometry[0] != None and _disFromBase):
        print "Please connect the geometry or the context" +\
              " and set up both the gridSize and the distance from base surface..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "Please connect the geometry or the context and set up both the gridSize and the distance from base surface...")
        
else: print 'Set runIt to True!'
