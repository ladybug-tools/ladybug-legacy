# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Draw Radiation Calla Lily
Radiation calla lily is a 3d presentation of radiation rose.
-
Provided by Ladybug 0.0.58
    
    Args:
        _selectedSkyMtx: The output from the selectSkyMtx component.
        _horAngleStep_: An angle between 0 and 360 that represents an angle step for horizontal rotation. The number should be smaller than 360 and divisible by 360.
        _verAngleStep_: Angle step between 0 and 90 that represents the vertical rotation. The number should be smaller than 90 and divisible by 90.
        _centerPoint: Input a point here to chage the center point of the Calla Lily graph and move it around the Rhino scene.  The default is set to the Rhino origin (0,0,0).
        _horScale_: Input a number here to change horizontal scale of the graph. The default value is set to 1.
        _verScale_: Input a number here to change vertical scale of the graph. The default value is set to 1.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        _runIt: Set to "True" to run the component and generate a radiation Calla Lily.
        bakeIt_: Set to "True" to bake the Calla Lily into the Rhino scene.
    Returns:
        readMe!: ...
        radiationLilyMesh: A colored mesh representing radiation of the Calla Lily.
        baseCrvs: A set of guide curves for the Calla Lily.
        legend: A legend of the Calla Lily. Connect this output to a grasshopper "Geo" component in order to preview the legend in the Rhino scene.  
        testPts: The vertices of the Calla Lily mesh.
        testPtsInfo: Information for each test point of the Calla Lily mesh.
        values: Radiation values for each test point of the Calla Lily mesh.
"""

ghenv.Component.Name = "Ladybug_Radiation Calla Lily"
ghenv.Component.NickName = 'radiationCallaLily'
ghenv.Component.Message = 'VER 0.0.58\nSEP_11_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import System
import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino as rc
import math
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

def main(genCumSkyResult, horAngleStep, verAngleStep, horScale, verScale,
                   north, centerPoint, legendPar, bakeIt):
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
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        TregenzaPatchesNormalVectors = lb_preparation.TregenzaPatchesNormalVectors
        conversionFac = lb_preparation.checkUnits()
        
        # check the input data
        warn = "Please provide a valid selctedSkyMtx!"
        try:
            if genCumSkyResult[2][:11] == 'Sky Patches':
                checkData = True
            else:
                checkData = False
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, warn)
                print warn
                return -1
        except Exception, e:
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warn)
            checkData = False
            print warn
            return -1
            
        
        if checkData:
            # separate the data
            indexList, listInfo = lb_preparation.separateList(genCumSkyResult, lb_preparation.strToBeFound)
            selList = []
            [selList.append(float(x)) for x in genCumSkyResult[indexList[0]+7:indexList[1]]]
            genCumSkyResult = selList
            
            if indexList[-1] == 456: patchesNormalVectors = lb_preparation.TregenzaPatchesNormalVectors
            elif indexList[-1] == 1752: patchesNormalVectors = lb_preparation.getReinhartPatchesNormalVectors()
            
            
            # check the scale
            try:
                if float(horScale)!=0:
                    try: horScale = float(horScale)/conversionFac
                    except: horScale = 1/conversionFac
                else:
                    horScale = 1/conversionFac
            except:
                horScale = 1/conversionFac
            
            horScale = horScale * .2
            
            try:
                if float(verScale) >= 0:
                    try: verScale = float(verScale) * 1/conversionFac
                    except: verScale = 1/conversionFac
                else:
                    verScale = 1/conversionFac
            except:
                verScale = 1/conversionFac
            
            verScale= .1*verScale

            cenPt = lb_preparation.getCenPt(centerPoint)
            
            if not horAngleStep or int(horAngleStep) < 5: horAngleStep = 10
            elif int(horAngleStep)> 90: horAngleStep = 90
            else:
                try: horAngleStep = int(horAngleStep)
                except: horAngleStep = 10
            
            if not verAngleStep or int(verAngleStep) < 5: verAngleStep = 10
            elif int(verAngleStep)> 90: verAngleStep = 90
            else:
                try: verAngleStep = int(verAngleStep)
                except: verAngleStep = 10
            
            
            # find the range of angles 
            
            roseHAngles = rs.frange(0, 360, horAngleStep)
            roseVAngles = rs.frange(0, 90, verAngleStep)
            
            if round(roseHAngles[-1]) == 360: roseHAngles.remove(roseHAngles[-1])
            if round(roseVAngles[-1]) > 90: roseVAngles.remove(roseVAngles[-1])
            elif round(roseVAngles[-1]) < 90: roseVAngles.append(90)
            
            hRotationVectors = [];
            northAngle, northVector = lb_preparation.angle2north(north)
            eastVector = rc.Geometry.Vector3d(northVector); eastVector.Rotate(math.radians(-90), rc.Geometry.Vector3d.ZAxis)
            # print eastVector
            
            def radiationForVector(vec, genCumSkyResult, TregenzaPatchesNormalVectors = lb_preparation.TregenzaPatchesNormalVectors):
                radiation = 0; patchNum = 0;
                for patchNum, patchVec in enumerate(TregenzaPatchesNormalVectors):
                    vecAngle = rs.VectorAngle(patchVec, vec)
                    if  vecAngle < 90:
                        radiation = radiation + genCumSkyResult[patchNum] * math.cos(math.radians(vecAngle))
                return radiation
            
            pts = []
            ptsClean = [] # clean points doesn't have the first point of the loop at the end
            testPtsInfos = []
            resultsFlatten = []
            radResult = []
            [pts.append([]) for a in range(len(roseVAngles))]
            [radResult.append([]) for a in range(len(roseVAngles))]
            
            for angleCount, angle in enumerate(roseVAngles):
                vectorVRotated = rc.Geometry.Vector3d(northVector)
                
                # rotate vertically
                vectorVRotated.Rotate(math.radians(angle), eastVector)
                
                for hAngle in roseHAngles:
                    hVector = rc.Geometry.Vector3d(vectorVRotated)
                    hVector.Rotate(-math.radians(hAngle), rc.Geometry.Vector3d.ZAxis)
                    
                    # calculate radiation for each vector
                    radiation = radiationForVector(hVector, genCumSkyResult, patchesNormalVectors)
                    radResult[angleCount].append(radiation)
                    resultsFlatten.append(radiation)
                    
                    # create the point
                    movingVector = rc.Geometry.Vector3d(northVector)
                    movingVector.Rotate(-math.radians(hAngle), rc.Geometry.Vector3d.ZAxis)
                    movingVector = 100 * (angleCount + 1) * horScale * movingVector
                    
                    # movingVector = radiation * horScale * movingVector
                    
                    # move in z direction
                    pt = rc.Geometry.Point3d.Add(cenPt, movingVector)
                    
                    verticalMove = radiation * verScale * rc.Geometry.Vector3d.ZAxis
                    pt = rc.Geometry.Point3d.Add(pt, verticalMove)
                    pts[angleCount].append(pt)
                    ptsClean.append(pt)
                    
                    testPtsInfo = "%.2f"%radiation + ' ' + listInfo[0][3] + '\nHRA='+ `hAngle` + '; VRA=' + `90-angle`
                    testPtsInfos.append(testPtsInfo)
                    
                radResult[angleCount].append(radResult[angleCount][0])
                # resultsFlatten.append(radResult[angleCount][0])
                pts[angleCount].append(pts[angleCount][0])
            
            
            overwriteScale = False
            if legendPar == []: overwriteScale = True
            elif legendPar[-1] == None: overwriteScale = True
            
            # generate the colors
            lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize = lb_preparation.readLegendParameters(legendPar, False)
            
            if overwriteScale: legendScale = 0.85
            
            values = []
            # generate the mesh
            vaseMesh = rc.Geometry.Mesh()
            for vStep in range(len(roseVAngles)):
                if vStep!=0:
                    for ptCount, pt in enumerate(pts[vStep]):
                        try:
                            singleMesh = rc.Geometry.Mesh()
                            pt1 = pts[vStep-1][ptCount]
                            value1 = radResult[vStep-1][ptCount]
                            pt2 = pts[vStep][ptCount]
                            value2 = radResult[vStep][ptCount]
                            pt3 = pts[vStep-1][ptCount + 1]
                            value3 = radResult[vStep-1][ptCount + 1]
                            pt4 = pts[vStep][ptCount + 1]
                            value4 = radResult[vStep][ptCount + 1]
                            singleMesh.Vertices.Add(pt1)
                            singleMesh.Vertices.Add(pt2)
                            singleMesh.Vertices.Add(pt3)
                            singleMesh.Vertices.Add(pt4)
                            singleMesh.Faces.AddFace(0, 1, 3, 2)
                            values.append([value1, value2, value4, value3])
                            vaseMesh.Append(singleMesh)
                        except:
                            pass
        
            
            values = lb_preparation.flattenList(values)
            # color the mesh
            meshColors = lb_visualization.gradientColor(values, lowB, highB, customColors)
            
            # make a monotonemesh
            vaseMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.White)
            
            #color the mesh based on the results
            for vertices in range (vaseMesh.Vertices.Count):
                vaseMesh.VertexColors[vertices] = meshColors[vertices]
                
            maxHorRadius = 100 * (angleCount + 1) * horScale
            tempCompassCrv = rc.Geometry.Circle(cenPt, 1.1*maxHorRadius).ToNurbsCurve()
            lb_visualization.calculateBB([vaseMesh, tempCompassCrv], True)
            
            # get the legend done
            legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(resultsFlatten
                    , lowB, highB, numSeg, listInfo[0][3], lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize)
            
            # generate legend colors
            legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
            
            # color legend surfaces
            legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
            
            # title
            customHeading = '\n\nRadiation Calla Lily (' + listInfo[0][3] + ')'
            titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle(listInfo, lb_visualization.BoundingBoxPar, legendScale, customHeading, False, legendFont, legendFontSize)
            
            cenPtMoved = rc.Geometry.Point3d.Add(cenPt, 0.9*lb_visualization.BoundingBoxPar[3]*rc.Geometry.Vector3d.ZAxis)
            compassCrvs, compassTextPts, compassText = lb_visualization. compassCircle(cenPtMoved, northVector, maxHorRadius, roseHAngles, 1.2*textSize)
            numberCrvs = lb_visualization.text2srf(compassText, compassTextPts, 'Times New Romans', textSize/1.2)
            compassCrvs = compassCrvs + lb_preparation.flattenList(numberCrvs)
            
            
            # bake
            if bakeIt:
                legendText.append(titleStr)
                textPt.append(titlebasePt)
                placeName = listInfo[0][1]
                studyLayerName = 'Radiation Lily'
                stMonth, stDay, stHour, endMonth, endDay, endHour = lb_visualization.readRunPeriod((listInfo[0][5], listInfo[0][6]), False)
                period = `stDay`+ ' ' + lb_visualization.monthList[stMonth-1] + ' ' + `stHour` + \
                 " - " + `endDay`+ ' ' + lb_visualization.monthList[endMonth-1] + ' ' + `endHour` 
                # check the study type
                newLayerIndex, l = lb_visualization.setupLayers(period, 'LADYBUG', placeName, studyLayerName, False, False, 0, 0)
                
                lb_visualization.bakeObjects(newLayerIndex, vaseMesh, legendSrfs, legendText, textPt, textSize, legendFont, compassCrvs)
            # done

        return ptsClean, vaseMesh, [legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)], resultsFlatten, testPtsInfos, compassCrvs
        
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1

if _runIt:
    north_ = 0
    result = main(_selectedSkyMtx, _horAngleStep_, _verAngleStep_, _horScale_, _verScale_,
                   north_, _centerPoint_, legendPar_, bakeIt_)
    maxPtAndValue = []
    if result!= -1:
       radiationLilyMesh = result[1]       
       testPts = result [0]
       legend = [result [2][0]] + result[2][1]
       values = result[3]
       testPtsInfo = result[4]
       baseCrvs = result[5]
       
       maxValue = max(values)
       i = values.IndexOf(maxValue)
       maxPtAndValue = [testPts[i], testPtsInfo[i]]
    ghenv.Component.Params.Output[4].Hidden = True
    
else:
    print "Set runIt to True!"
