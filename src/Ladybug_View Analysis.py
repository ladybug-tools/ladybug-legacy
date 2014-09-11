# This script used to be ladybug all in one
# I separated them into three parts before distribution which made it such a mess
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to evaluate the visibility of input _geometry from a set of key viewing points.
For example, this component can be used to evaluate the visibility of an 3D architectural feature from a set of key viewing points along a nearby street or park where people congregate.
Another example would be evaluating the visibility of park vegetation geometry from a set of key sun position points from the sunPath component.
Yet another example would be evaluating the "visibility" of an outdoor overhead radiative heater from a set of key "viewing" points located over a human body standing beneath it.
This component outputs a percentage of viewpoints seen by the input _geometry.  In the three examples here, this would be the percentage of the 3D architectural feature seen from the street, the percentage of sunlit hours received by the vegetation, or the percentage of the human body warmed by the heater.
This component will evaluate view from the test points objectively in all directions. 

-
Provided by Ladybug 0.0.58
    
    Args:
        _geometry: Geometry for which visibility analysis will be conducted.  Geometry must be either a Brep, a Mesh, or a list of Breps or Meshes.
        context_: Context geometry that could block the view from the _viewPoints to the test _geometry.  Conext geometry must be either a Brep, a Mesh, or a list of Breps or Meshes.
        _gridSize_: A number in Rhino model units that represents the average size of a grid cell for visibility analysis on the test _geometry.  This value should be smaller than the smallest dimension of the test _geometry for meaningful results.  Note that, the smaller the grid size, the higher the resolution of the analysis and the longer the calculation will take.
        _disFromBase: A number in Rhino model units that represents the offset distance of the test point grid from the input test _geometry.  Usually, the test point grid is offset by a small amount from the test _geometry in order to ensure that visibility analysis is done for the correct side of the test _geometry.  If the resulting mesh of this component is offset to the wrong side of test _geometry, you should use the "Flip" Rhino command on the test _geometry before inputting it to this component.
        orientationStudyP_: Optional output from the "Orientation Study Parameter" component.  You can use an Orientation Study input here to answer questions like "What orientation of my building will give me the highest or lowest visibility from the street?"  An Orientation Study will automatically rotate your input _geometry around several times and record the visibility results each time in order to output a list of values for averageView and a grafted data stream for viewStudyResult.
        _viewPoints: Key viewing points from which the visibility of the test _geometry is important.
        viewPtsWeights_: Use this input to assign weights of importance to the several _viewPoints that have been connected.  Weighted values should be between 0 and 1 and should be closer to 1 if a certain point is more important. The default value for all points is 0, which means they all have an equal importance. This input could be useful in cases such as the radiative heater example where points on the human body with exposed skin could be weighted at a higher value.
        _____________________: ...
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        parallel_: Set to "True" to run the visibility analysis using multiple CPUs.  This can dramatically decrease calculation time but can interfere with other intense computational processes that might be running on your machine.
        _runIt: Set to "True" to run the component and perform visibility analysis of the input _geometry.
        bakeIt_: Set to "True" to bake the analysis results into the Rhino scene.
        workingDir_: Use this input to change the working directory of the visibility analysis on your system. Input here must be a valid file path location on your computer.  The default is set to "C:\Ladybug" and it is from this file location that visibility results are loaded into grasshopper after the analysis is done.
        projectName_: Use this input to change the project name of the files generated in the working directory.  Input here must be a string without special characters.  If "bakeIt_" is set to "True", the result will be baked into a layer with this project name.
    
    Returns:
        readMe!: ...
        contextMesh: An uncolored mesh representing the context_ geometry that was input to this component. Connect this output to a "Mesh" grasshopper component to preview this output seperately from the others of this component. Note that this mesh is generated before the analysis is run, allowing you to be sure that the right geometry will be run through the analysis before running this component.
        analysisMesh: An uncolored mesh representing the test _geometry that will be analyzed.  Connect this output to a "Mesh" grasshopper component to preview this output seperately from the others of this component. Note that this mesh is generated before the analysis is run, allowing you to be sure that the right geometry will be run through the analysis before running this component.
        testPts: The grid of test points on the test _geometry that will be used to perform the visibility analysis.  Note that these points are generated before the analysis is run, allowing you to preview the resolution of the result before you run the component.
        testVec: Vectors for each of the test points on the test _geometry, which indicate the direction for which visibility analysis is performed.  Hook this and the test points up to a Grasshopper "Vector Display" component to see how analysis is performed on the test _geometry.
        _____________________: ...
        viewStudyResult: The percentage of _viewPoints visible from each of the test points of the input test _geometry.
        viewStudyMesh: A colored mesh of the test _geometry representing the percentage of _viewPoints visible by each part of the input _geometry.
        viewStudyLegend: A legend for the visibility analysis showing the percentage of visible points that correspond to the colors of the viewStudyMesh. Connect this output to a grasshopper "Geo" component in order to preview the legend separately in the Rhino scene.  
        legendBasePt: The legend base point, which can be used to move the legend in relation to the view study mesh with the grasshopper "move" component.
        averageView: The average percentage of the _viewPoints seen by all of the test _geometry.
        ptIsVisible: A grafted data stream for each _geometry test point with a "1" for each _viewPoint that is visible by the test point and a "0" for each _viewPoint that is blocked.
"""

ghenv.Component.Name = "Ladybug_View Analysis"
ghenv.Component.NickName = 'viewAnalysis'
ghenv.Component.Message = 'VER 0.0.58\nSEP_11_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
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

northVector = []
if len(_viewPoints)!=0: viewPoints_viewStudy = _viewPoints
else: viewPoints_viewStudy = []


def main(geometry, context, gridSize, disFromBase, orientationStudyP,
            viewPoints_viewStudy, viewPtsWeights, legendPar, parallel,
            bakeIt, workingDir, projectName):
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
        lb_mesh = sc.sticky["ladybug_Mesh"]()
        lb_runStudy_GH = sc.sticky["ladybug_RunAnalysis"]()
        #lb_runStudy_RAD = sc.sticky["ladybug_Export2Radiance"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1
    
    conversionFac = lb_preparation.checkUnits()
    
    # north direction
    # northAngle, northVector = lb_preparation.angle2north(north)
    
    # read orientation study parameters
    runOrientation, rotateContext, rotationBasePt, angles = lb_preparation.readOrientationParameters(orientationStudyP)
    
    # mesh the test buildings
    if (len(geometry)!=0 and disFromBase):
        ## clean the geometry and bring them to rhinoCommon separated as mesh and Brep
        analysisMesh, analysisBrep = lb_preparation.cleanAndCoerceList(geometry)
        
        # if len(analysisBrep)!=0 and gridSize == None: return -1
        originalTestPoints = []
        
        if gridSize == None:
            gridSize = 4/conversionFac
            
        
        ## mesh Brep
        analysisMeshedBrep = lb_mesh.parallel_makeSurfaceMesh(analysisBrep, float(gridSize))
        
        ## Flatten the list of surfaces
        analysisMeshedBrep = lb_preparation.flattenList(analysisMeshedBrep)
        analysisSrfs = analysisMesh + analysisMeshedBrep
        
        ## extract test points
        #if not testPts or testPts[0] == None:
        testPoints, ptsNormals, meshSrfAreas = lb_mesh.parallel_testPointCalculator(analysisSrfs, float(disFromBase), parallel)
        originalTestPoints = testPoints
        testPoints = lb_preparation.flattenList(testPoints)
        ptsNormals = lb_preparation.flattenList(ptsNormals)
        meshSrfAreas = lb_preparation.flattenList(meshSrfAreas)
        #else:
        #    testPoints = testPts
        #    if not len(testVec)==0:
        #        print 'this is a place holder...'
    else:
        print "Please connect the geometry and set up both the gridSize and the distance from base surface..."
        analysisSrfs = testPoints = ptsNormals = meshSrfAreas = []
        return -1
        
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


    def runAnalyses(testPoints, ptsNormals, meshSrfAreas, analysisSrfs, contextSrfs, parallel, cumSky_radiationStudy, viewPoints_viewStudy, viewPtsWeights, sunVectors_sunlightHour, conversionFac):
        RADIANCE_radiationStudy =[]
        if len(RADIANCE_radiationStudy)!=0:
            pass
        elif cumSky_radiationStudy != None and len(cumSky_radiationStudy) == 146:
            radResults, totalRadResults = lb_runStudy_GH.parallel_radCalculator(testPoints, ptsNormals, meshSrfAreas, joinedAnalysisMesh, joinedContext,
                                        parallel, cumSky_radiationStudy, lb_preparation.TregenzaPatchesNormalVectors, conversionFac, 2200000000000000, northVector)
        else:
            #print "No radiation study!"
            radResults = totalRadResults = None
        
        if len(viewPoints_viewStudy)!= 0 and viewPoints_viewStudy!=[]:
            listInfo = ['key:location/dataType/units/frequency/startsAt/endsAt', 'City/Latitude', 'View Analysis', '%', 'NA', (1, 1, 1), (12, 31, 24)]
            if parallel:
                try:
                    for geo in analysisSrfs + contextSrfs: geo.EnsurePrivateCopy()
                except:
                    pass
            
            # join the meshes
            joinedAnalysisMesh = lb_mesh.joinMesh(analysisSrfs)
            if contextSrfs: joinedContext = lb_mesh.joinMesh(contextSrfs)
            else: joinedContext = None
            
            viewResults, averageViewResults, ptVisibility = lb_runStudy_GH.parallel_viewCalculator(testPoints, ptsNormals, meshSrfAreas, joinedAnalysisMesh, joinedContext, parallel, viewPoints_viewStudy, viewPtsWeights, conversionFac)
        else:
            print "View points should be provided... No view study!"
            viewResults = totalViewResults = None
            return [contextSrfs, analysisSrfs, testPoints, ptsNormals], -1, -1, -1
        
        if len(sunVectors_sunlightHour)!= 0:
            hoursResults, totalHoursResults = lb_runStudy_GH.parallel_sunlightHoursCalculator(testPoints, ptsNormals, meshSrfAreas, analysisSrfs, contextSrfs,
                                            parallel, sunVectors_sunlightHour, conversionFac, northVector)
        else:
            #print "No sunlight hours study!"
            hoursResults = totalHoursResults = None
            
        #results = range(len(testPoints))
        results = radResults, hoursResults, viewResults
        totalResults = totalRadResults, totalHoursResults, averageViewResults
        
        return results, totalResults, listInfo, ptVisibility
    
    def resultVisualization(contextSrfs, analysisSrfs, results, totalResults, legendPar, legendTitle, studyLayerName, bakeIt, checkTheName, l, angle, listInfo):
        
        lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize = lb_preparation.readLegendParameters(legendPar, False)
        
        colors = lb_visualization.gradientColor(results, lowB, highB, customColors)

        # color mesh surfaces
        analysisSrfs = lb_visualization.colorMesh(colors, analysisSrfs)
        
        ## generate legend
        # calculate the boundingbox to find the legendPosition
        if not (runOrientation and legendBasePoint==None):
            lb_visualization.calculateBB([analysisSrfs, contextSrfs])
        # legend geometry
        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(results, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize)
        
        # legend colors
        legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
        # color legend surfaces
        legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
        
        customHeading = '\n\nView Analysis' + '\n#View Points = ' + `len(_viewPoints)`
        if runOrientation:
            try: customHeading = customHeading + '\nRotation Angle: ' + `angle` + ' Degrees'
            except: pass
        titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo], lb_visualization.BoundingBoxPar, legendScale, customHeading, True, legendFont, legendFontSize)
        
        if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
        
        if bakeIt:
            legendText.append(titleStr)
            textPt.append(titlebasePt)
            # check the study type
            newLayerIndex, l = lb_visualization.setupLayers(totalResults, 'LADYBUG', projectName,
                                                            studyLayerName, checkTheName,
                                                            runOrientation, angle, l)
            lb_visualization.bakeObjects(newLayerIndex, analysisSrfs, legendSrfs, legendText, textPt, textSize, legendFont)
        
        return analysisSrfs, [legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)], l, legendBasePoint


    ## data for visualization
    legendTitles = ['kWh/m2', 'Hours', '%']
    studyLayerNames = ['RADIATION_STUDIES', 'SUNLIGHTHOURS_STUDIES', 'VIEW_STUDIES']
    CheckTheName = True
    resV = 0 # Result visualization
    ## check for orientation Study
    l = [0, 0, 0] # layer name indicator
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
                                        analysisSrfs, mergedContextSrfs, parallel, cumSky_radiationStudy,
                                        viewPoints_viewStudy, viewPtsWeights,
                                        sunVectors_sunlightHour, conversionFac)
            
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
                listMin = min(orirntationStudyRes[key]["results"][2])
                listMax = max(orirntationStudyRes[key]["results"][2])
                if  listMin < minValue: minValue = listMin
                if  listMax > maxValue: maxValue = listMax
                
                if legendPar== [] or legendPar[4] == None:
                    allBuildingsAndContext.extend([orirntationStudyRes[key]["analysisSrf"], orirntationStudyRes[key]["contextSrf"]])
            
            # find the collective bounding box
            if legendPar== [] or legendPar[4] == None:
                lb_visualization.calculateBB(allBuildingsAndContext)
            
            # preset the legen parameters if it is not set by the user
            if legendPar== []:
                legendPar = [minValue, maxValue, None, [], lb_visualization.BoundingBoxPar, None]
            else:
                if legendPar[0] == None: legendPar[0] = [minValue]
                if legendPar[1] == None: legenPar[1] = maxValue
                if legendPar[4] == None: legendPar[4] = lb_visualization.BoundingBoxPar
                
        
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
                        eachTotalResult = [[],[],[]]
                        resultColored[i], legendColored[i], l[i], legendBasePoint = resultVisualization(mergedContextSrfs, analysisSrfs,
                                          results[i], eachTotalResult[i], legendPar, legendTitles[i],
                                          studyLayerNames[i], bakeIt, CheckTheName, l[i], angles[angle + 1], listInfo)
                        resV += 1
    
    else:
        # no orientation study
        angle = 0; l = [0, 0, 0]
        cumSky_radiationStudy = []
        sunVectors_sunlightHour = []
        results, totalResults, listInfo, pointVisiblity = runAnalyses(testPoints, ptsNormals, meshSrfAreas,
                                analysisSrfs, contextSrfs, parallel, cumSky_radiationStudy,
                                viewPoints_viewStudy, viewPtsWeights,
                                sunVectors_sunlightHour, conversionFac)
                                
    if results!=-1 and len(results) == 4:
        contextSrfs, analysisSrfs, testPoints, ptsNormals = results
        return contextSrfs, analysisSrfs, testPoints, ptsNormals, originalTestPoints
    elif results != -1:
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
                                  results[i], totalResults[0][i], legendPar, legendTitles[i],
                                  studyLayerNames[i], bakeIt, CheckTheName, 0, angles[-1], listInfo)
                resV += 1
    
        # return outputs
        if runOrientation: contextSrfs = mergedContextSrfs
        if resV != 0: return contextSrfs, analysisSrfs, testPoints, ptsNormals, results, resultColored, legendColored, totalResults, legendBasePoint, originalTestPoints, pointVisiblity
        else: return -1
    else:
        return -1


if _runIt:
    if (len(_geometry)!=0 and _geometry[0] != None and _disFromBase):
        result = main(_geometry, context_, _gridSize_, _disFromBase, orientationStudyP_,
                        viewPoints_viewStudy, viewPtsWeights_, legendPar_, parallel_,
                        bakeIt_, workingDir_, projectName_)
        
        if result!= -1 and len(result) > 5:
            def openLegend(legendRes):
                if len(legendRes)!=0:
                    meshAndCrv = []
                    meshAndCrv.append(legendRes[0])
                    [meshAndCrv.append(c) for c in legendRes[1]]
                    return meshAndCrv
                else: return
            
            # Assign the result to GH component outputs
            contextMesh, analysisMesh, testPts_flatten, testVec_flatten = result[0], result[1], result[2], result[3]
            
            # radiation
            radiationResult = result[4][0]
            radiationMesh = result[5][0]
            radiationLegend = openLegend(result[6][0])
            
            # sunlightHours
            sunlightHoursResult = result[4][1]
            sunlightHoursMesh = result[5][1]
            sunlightHoursLegend = openLegend(result[6][1])
            
            # sunlightHours
            viewStudyResult_flatten = result[4][2]
            viewStudyMesh = result[5][2]
            viewStudyLegend = openLegend(result[6][2])
            
            # total results
            totalRadiation = []; totalSunlightHours = []; averageView = []
            for res in result[7]:
                totalRadiation.append(res[0])
                totalSunlightHours.append(res[1])
                averageView.append(res[2])
            
            legendBasePt = result[-3]
            originalTestPoints = result[-2]
            pointsVisibility = result[-1]
            
        elif result!= -1 and len(result) == 5:
            contextMesh, analysisMesh, testPts_flatten, testVec_flatten, originalTestPoints = result
        
        testPts = DataTree[System.Object]()
        testVec = DataTree[System.Object]() 
        ptIsVisible = DataTree[System.Object]()
        
        if result!= -1:
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
                
        ghenv.Component.Params.Output[1].Hidden = True
        ghenv.Component.Params.Output[2].Hidden = True
        ghenv.Component.Params.Output[3].Hidden = True
        ghenv.Component.Params.Output[9].Hidden = True
        
        
    else:
        result = -1
        
    if result == -1 and not (len(_geometry)!=0 and _geometry[0] != None and _disFromBase):
        warnM = "Please connect the geometry or the context and set up both the gridSize and the distance from base surface..."
        print warnM
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warnM)
    elif result == -1 and sc.sticky.has_key('ladybug_release'):
        print "Canceled by user!"
    
else: print 'Set runIt to True!'
