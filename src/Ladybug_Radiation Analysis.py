# This script used to be ladybug all in one
# I separated them into three parts before distribution which made it such a mess
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component uses cumulative sky result to calculate radiation on building surfaces.
No reflection is included in the studies with this component and it should be used
neither for interior studies nor for complex geometries nor geometries with surfaces with high reflectivity.
I'm testing a more sophisticated component that uses RADIANCE for calculations. Meanwhile use
one of the alternative plugins for more advanced studies. 

-
Provided by Ladybug 0.0.56
    
    Args:
        north_: Input a vector to set north
        _geometry: Input the test geometries as a Brep or Mesh
        context_: Input the context as a Brep or Mesh
        _gridSize_: Input a number to set the test points grid size
        _disFromBase: Input a number to set the distance between the test points grid and the base geometry
        orientationStudyP_: Input result from Orientation Study Parameter component
        _selectedSkyMtx: SelectSkyMtx component result
        _____________________: This is just for graphical purposes. I appreciate your curiosity though!
        legendPar_: Input legend parameters from the Ladybug Legend Parameters component
        parallel_: Set Boolean to True to use multiple CPUs
        _runIt: Set Boolean to True to run the analysis
        bakeIt_: Set Boolean to True to bake the analysis result
        workingDir_: Working directory on your system. Default is set to C:\Ladybug
        projectName_: Input the project name as a string. The result will be baked in a layer with project name.
    
    Returns:
        readMe!: ...
        contextMesh: Connect to Mesh to preview the test mesh for the context
        analysisMesh: Connect to Mesh to preview the test mesh for the test geometries
        testPts: Test points
        testVec: Test point vectors
        _____________________: This is just for graphical purposes. I appreciate your curiosity though!
        radiationResult: Result for each test point
        radiationMesh: The result of the study as a joined mesh
        radiationLegend: Legend of the study. Connect to Geo for preview
        legendBasePt: Legend base point, mainly for presentation purposes
        totalRadiation: Mass addition of result multiplied by the area of the surface for all the surfaces
"""

ghenv.Component.Name = "Ladybug_Radiation Analysis"
ghenv.Component.NickName = 'radiationAnalysis'
ghenv.Component.Message = 'VER 0.0.56\nMAR_19_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
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

if len(_selectedSkyMtx)!=0: cumSky_radiationStudy = _selectedSkyMtx
else: cumSky_radiationStudy = []

def main(north, geometry, context, gridSize, disFromBase, orientationStudyP, cumSky_radiationStudy, legendPar, parallel, runIt, bakeIt, workingDir, projectName):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
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
    northAngle, northVector = lb_preparation.angle2north(north)
        
    # read orientation study parameters
    
    runOrientation, rotateContext, rotationBasePt, angles = lb_preparation.readOrientationParameters(orientationStudyP)
    
    # mesh the test buildings
    if len(geometry)!=0 and disFromBase:
        ## clean the geometry and bring them to rhinoCommon separated as mesh and Brep
        analysisMesh, analysisBrep = lb_preparation.cleanAndCoerceList(geometry)
        
        #if len(analysisBrep)!=0 and gridSize == None: return -1
        
        if gridSize == None:
            gridSize = 4/conversionFac
            originalTestPoints = []
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
        #print len(originalTestPoints), len(testPoints)
        
        ptsNormals = lb_preparation.flattenList(ptsNormals)
        meshSrfAreas = lb_preparation.flattenList(meshSrfAreas)
        #else:
        #    testPoints = testPts
        #    if not len(testVec)==0:
        #        print 'this is a place holder...'
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
        contextMeshedBrep = lb_preparation.flattenList(contextMeshedBrep)
        contextSrfs = contextMesh + contextMeshedBrep
    else: contextSrfs = []


    def runAnalyses(testPoints, ptsNormals, meshSrfAreas, analysisSrfs, contextSrfs, parallel, cumSky_radiationStudy, viewPoints_viewStudy, viewFields_Angles_D, sunVectors_sunlightHour, conversionFac):
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
            
            # join the meshes
            joinedAnalysisMesh = lb_mesh.joinMesh(analysisSrfs)
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
        
        viewPoints_viewStudy = []
        if len(viewPoints_viewStudy)!= 0:
            viewResults, totalViewResults = lb_runStudy_GH.parallel_viewCalculator(testPoints, ptsNormals, meshSrfAreas, analysisSrfs, contextSrfs, parallel, viewPoints_viewStudy, viewFields_Angles_D, conversionFac)
        else:
            #print "No view study!"
            viewResults = totalViewResults = None
    
        if len(sunVectors_sunlightHour)!= 0:
            hoursResults, totalHoursResults = lb_runStudy_GH.parallel_sunlightHoursCalculator(testPoints, ptsNormals, meshSrfAreas, analysisSrfs, contextSrfs,
                                            parallel, sunVectors_sunlightHour, conversionFac, northVector)
        else:
            #print "No sunlight hours study!"
            hoursResults = totalHoursResults = None
            
        #results = range(len(testPoints))
        results = radResults, hoursResults, viewResults
        totalResults = totalRadResults, totalHoursResults, totalViewResults
        
        return results, totalResults, listInfo, intersectionMtx
    
    
    def resultVisualization(contextSrfs, analysisSrfs, results, totalResults, legendPar, legendTitle, studyLayerName, bakeIt, checkTheName, l, angle, listInfo):
        
        lowB, highB, numSeg, customColors, legendBasePoint, legendScale = lb_preparation.readLegendParameters(legendPar, False)
        # print legendBasePoint
        
        colors = lb_visualization.gradientColor(results, lowB, highB, customColors)

        # color mesh surfaces
        analysisSrfs = lb_visualization.colorMesh(colors, analysisSrfs)
        
        ## generate legend
        # calculate the boundingbox to find the legendPosition
        if not (runOrientation and legendBasePoint==None):
            lb_visualization.calculateBB([analysisSrfs, contextSrfs])
        
        # legend geometry
        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(results, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale)
        
        # legend colors
        legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
        # color legend surfaces
        legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)

        customHeading = '\n\nRadiation Analysis'
        if runOrientation:
            try: customHeading = customHeading + '\nRotation Angle: ' + `angle` + ' Degrees'
            except: pass
        titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo[0]], lb_visualization.BoundingBoxPar, legendScale, customHeading)
        
        if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
        
        if bakeIt:
            legendText.append(titleStr)
            textPt.append(titlebasePt)
            # check the study type
            newLayerIndex, l = lb_visualization.setupLayers(totalResults, 'LADYBUG', projectName,
                                                            studyLayerName, checkTheName,
                                                            runOrientation, angle, l)
            lb_visualization.bakeObjects(newLayerIndex, analysisSrfs, legendSrfs, legendText, textPt, textSize, fontName = 'Verdana')
        
        return analysisSrfs, [legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)], l, legendBasePoint


    ## data for visualization
    legendTitles = ['kWh/m2', 'Hours', '%']
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
                                        analysisSrfs, mergedContextSrfs, parallel, cumSky_radiationStudy,
                                        viewPoints_viewStudy, viewFields_Angles_D,
                                        sunVectors_sunlightHour, conversionFac)
            
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
                        resultColored[i], legendColored[i], l[i], legendBasePoint = resultVisualization(mergedContextSrfs, analysisSrfs,
                                          results[i], eachTotalResult[i], legendPar, legendTitles[i],
                                          studyLayerNames[i], bakeIt, CheckTheName, l[i], angles[angle + 1], listInfo)
                        resV += 1
            
    else:
        # no orientation study
        angle = 0; l = [0, 0, 0]
        viewPoints_viewStudy = []; viewFields_Angles_D = []; sunVectors_sunlightHour = []
        results, totalResults, listInfo, intersectionMtx = runAnalyses(testPoints, ptsNormals, meshSrfAreas,
                                analysisSrfs, contextSrfs, parallel, cumSky_radiationStudy,
                                viewPoints_viewStudy, viewFields_Angles_D,
                                sunVectors_sunlightHour, conversionFac)
                                
    if results!=-1 and len(results) == 4:
        contextSrfs, analysisSrfs, testPoints, ptsNormals = results
        return contextSrfs, analysisSrfs, testPoints, ptsNormals, originalTestPoints
    
    elif results!=-1:
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
                #angles
                # Add an option for orientation study
                resultColored[i], legendColored[i], l[i], legendBasePoint = resultVisualization(contextSrfs, analysisSrfs,
                              results[i], totalResults[0][i], legendPar, legendTitles[i],
                              studyLayerNames[i], bakeIt, CheckTheName, 0, angles[-1], listInfo)
                resV += 1
                
                
        # return outputs
        if runOrientation: contextSrfs = mergedContextSrfs
        if resV != 0:
            return contextSrfs, analysisSrfs, testPoints, ptsNormals, results, resultColored, legendColored, totalResults, legendBasePoint, originalTestPoints, intersectionMtx
            
        else: return -1
        return -1

if _runIt:
    
    if (len(_geometry)!=0 and _geometry[0] != None and _disFromBase):
        
        result = main(north_, _geometry, context_, _gridSize_, _disFromBase,
                    orientationStudyP_, _selectedSkyMtx, legendPar_, parallel_,
                    _runIt, bakeIt_, workingDir_, projectName_)
        
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
    elif result == -1 and sc.sticky.has_key('ladybug_release'):
        print "Canceled by user!"
        
else: print 'Set runIt to True!'

