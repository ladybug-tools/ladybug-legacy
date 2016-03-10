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
Use this component to draw Radiation Calla Lily or Dome, which shows you how radiation would fall on an object from all directions for a given sky.
_
It is useful for finding the best direction with which to orient solar panels and gives a sense of the consequences of deviating from such an orientation.
_
The Calla Lily/Dome can be understood in three different ways:
_
1) The Calla Lily/Dome a 3D representation of all possible radiation roses for a given sky since it includes all vertical angles from 0 to 90.
2) The Calla Lily/Dome is the reciprocal of the Tergenza Sky Dome since the Cala Dome essentially shows you how the radiation from the sky will fall onto a hemispherical object.
3) The Calla Lily/Dome is a smart radiation analysis of a hemisphere.  Your results would effectively be the same if you made a hemisphere in Rhino and ran it through the "Radiation Analysis" component but, with this component, you will get a smoother color gradient and the component will automatically output the point (or vector) with the most radiation.
-
Provided by Ladybug 0.0.62
    
    Args:
        _selectedSkyMtx: The output from the selectSkyMtx component.
        _horAngleStep_: An angle in degrees between 0 and 360 that represents the step for horizontal rotation. Smaller numbers will yeild a finer and smoother mesh with smoother colors.  The number input here should be smaller than 360 and divisible by 360.  The default is set to 10 degrees.
        _verAngleStep_: Angle in degrees step between 0 and 90 that represents the step for vertical rotation. Smaller numbers will yeild a finer and smoother mesh with smoother colors.  The number input here should be smaller than 90 and divisible by 90.  The default is set to 10 degrees.
        _centerPoint: Input a point here to chage the center point of the Calla Lily and move it around the Rhino scene.  The default is set to the Rhino origin (0,0,0).
        _horScale_: Input a number here to change horizontal (XY) scale of the graph. The default value is set to 1.  Note that, for the dome representation, this input will change the scale of the entire dome (both horizontal and vertical).
        _verScale_: Input a number here to change vertical (Z) scale of the graph. The default value is set to 1. Note that, for the dome representation, this input will have no effect.
        domeOrLily_: Set to "True" to have the component create a radiation dome and set to "False" to have it generate a Lily.  The default is set to "False" for a Lily.
            _
            The difference between the Dome and the Lily is that, for the Lily, the Z scale is essentially the same as the color scale, which is redundant but also beautiful and potentially useful if you have to present data with a Black/White printer or to someone who is color blind.
            _
            For the Dome, the vertical angles of rotation serve to define the Z scale.  In this sense, the normal to the dome at any given point is the angle at which the radiation study is being run.  This gives a geometric intuitive sense of how you should orient panels to capture or avoid the most sun.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        bakeIt_ : An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options:
            0 (or False) - No geometry will be baked into the Rhino scene (this is the default).
            1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. 
            2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry.
        _runIt: Set to "True" to run the component and generate a radiation Calla Lily.
    Returns:
        readMe!: ...
        radiationLilyMesh: A colored mesh representing radiation of the Calla Lily or Dome.
        baseCrvs: A set of guide curves for the Calla Lily.
        legend: A legend of the radiation on the Calla Lily. Connect this output to a grasshopper "Geo" component in order to preview the legend in the Rhino scene.  
        testPts: The vertices of the Calla Lily mesh.  These are hidden by default.
        testPtsInfo: Information for each test point of the Calla Lily mesh.  "HRA" stands for "Horizontal Rotation Angle" while "VRA" stand for "Vertical Rotation Angle."  HRA varies from 0 to 360 while VRA varies from 0 to 90.
        values: The radiation values for each test points (or mesh faces) of the Calla Lily in kWh/m2.
        maxRadPt: The point on the Cala Lilly with the greatest amount of solar radiation.  This is useful for understanding the best direction to orient solar panels.
        maxRadVector: The vector that should be used to orient solar panels such that they recieve the greatest possible solar radiation.
        maxRadInfo: Information about the test point with the greates amount of radiation in the Calla Lily.  "HRA" stands for "Horizontal Rotation Angle" while "VRA" stand for "Vertical Rotation Angle."  HRA varies from 0 to 360 while VRA varies from 0 to 90.
"""

ghenv.Component.Name = "Ladybug_Radiation Calla Lily"
ghenv.Component.NickName = 'radiationCallaLily'
ghenv.Component.Message = 'VER 0.0.62\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.59\nJAN_24_2016
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



def createSkyDomeMesh(basePoint, resolution, scale):
    #Create a list of altitudes and azimuths based on the resolution.
    altitudes = []
    azimuths = []
    
    altitudes.append(0)
    for num in range(resolution):
        altitudes.append((90/resolution) + num*(90/resolution))
    
    azimuths.append(0)
    for num in range(4*resolution-1):
        azimuths.append((360/(4*resolution)) + num*(360/(4*resolution)))
    
    #Create the vertices of the mesh.
    meshPts = []
    startPt = rc.Geometry.Point3d(0, scale*10, 0)
    for alt in altitudes:
        for az in azimuths:
            newPt = rc.Geometry.Point3d(startPt)
            altRotate = rc.Geometry.Transform.Rotation(math.radians(alt), rc.Geometry.Vector3d.XAxis, rc.Geometry.Point3d.Origin)
            azRotate = rc.Geometry.Transform.Rotation(-math.radians(az), rc.Geometry.Vector3d.ZAxis, rc.Geometry.Point3d.Origin)
            newPt.Transform(altRotate)
            newPt.Transform(azRotate)
            meshPts.append(newPt)
    
    #Create the mesh.
    uncoloredMesh = rc.Geometry.Mesh()
    
    for point in meshPts:
        uncoloredMesh.Vertices.Add(point)
    
    numbersToWatch = range(0, len(meshPts), (resolution*4))
    for count, point in enumerate(numbersToWatch):
        numbersToWatch[count] = point -1
    
    for pointCount in range(len(meshPts) - (resolution*4)):
        if pointCount not in numbersToWatch:
            uncoloredMesh.Faces.AddFace(pointCount, pointCount+1, pointCount+(resolution*4)+1, pointCount+(resolution*4))
        else:
            uncoloredMesh.Faces.AddFace(pointCount, pointCount-(resolution*4)+1, pointCount+1, pointCount+(resolution*4))
    
    #Move the mesh from the origin to the base point location
    startPtTransform = rc.Geometry.Transform.Translation(basePoint.X, basePoint.Y, basePoint.Z)
    uncoloredMesh.Transform(startPtTransform)
    
    #Color the mesh with monotone colors.
    uncoloredMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Gray)
    
    uncoloredMesh.Flip(True, True, True)
    
    return uncoloredMesh




def main(genCumSkyResult, horAngleStep, verAngleStep, horScale, verScale, north, centerPoint, legendPar, bakeIt):
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
            testPtsVectors = []
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
                    
                    # create the horizontal moving vector
                    movingVector = rc.Geometry.Vector3d(northVector)
                    movingVector.Rotate(-math.radians(hAngle), rc.Geometry.Vector3d.ZAxis)
                    movingVector = 100 * (angleCount + 1) * horScale * movingVector
                    
                    #Check the dome or the mesh and see what should be done with the z-scale
                    if domeOrLily_:
                        #User has requested a dome.
                        vertVector = rc.Geometry.Vector3d(vectorVRotated.X, vectorVRotated.Y, vectorVRotated.Z)
                        vertVector = rc.Geometry.Vector3d.Multiply(vertVector, 1000 * horScale)
                        pt = rc.Geometry.Point3d.Add(cenPt, vertVector)
                        pointRotation = rc.Geometry.Transform.Rotation(northVector, movingVector, cenPt)
                        pt.Transform(pointRotation)
                        pts[angleCount].append(pt)
                        ptsClean.append(pt)
                    else:
                        #User has requested a lilly
                        pt = rc.Geometry.Point3d.Add(cenPt, movingVector)
                        verticalMove = radiation * verScale * rc.Geometry.Vector3d.ZAxis
                        pt = rc.Geometry.Point3d.Add(pt, verticalMove)
                        pts[angleCount].append(pt)
                        ptsClean.append(pt)
                    
                    testPtsInfo = "%.2f"%radiation + ' ' + listInfo[0][3] + '\nHRA='+ `hAngle` + '; VRA=' + `90-angle`
                    testPtsInfos.append(testPtsInfo)
                    testPtsVectors.append(hVector)
                    
                radResult[angleCount].append(radResult[angleCount][0])
                # resultsFlatten.append(radResult[angleCount][0])
                pts[angleCount].append(pts[angleCount][0])
            
            overwriteScale = False
            if legendPar == []: overwriteScale = True
            elif legendPar[-1] == None: overwriteScale = True
            
            # generate the colors
            lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
            
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
                            value1 = radResult[vStep-1][ptCount-1]
                            pt2 = pts[vStep][ptCount]
                            value2 = radResult[vStep][ptCount-1]
                            pt3 = pts[vStep-1][ptCount + 1]
                            value3 = radResult[vStep][ptCount]
                            pt4 = pts[vStep][ptCount + 1]
                            value4 = radResult[vStep-1][ptCount]
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
            
            #Flip the mesh so that it always appears correctly in Rhino Display.
            if not domeOrLily_:
                vaseMesh.Flip(True, True, True)
            
            maxHorRadius = 100 * (angleCount + 1) * horScale
            tempCompassCrv = rc.Geometry.Circle(cenPt, 1.1*maxHorRadius).ToNurbsCurve()
            lb_visualization.calculateBB([vaseMesh, tempCompassCrv], True)
            
            # get the legend done
            legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(resultsFlatten
                    , lowB, highB, numSeg, listInfo[0][3], lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
            
            # generate legend colors
            legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
            
            # color legend surfaces
            legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
            
            # title
            customHeading = '\n\nRadiation Calla Lily (' + listInfo[0][3] + ')'
            titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle(listInfo, lb_visualization.BoundingBoxPar, legendScale, customHeading, False, legendFont, legendFontSize, legendBold)
            
            if not domeOrLily_: cenPtMoved = rc.Geometry.Point3d.Add(cenPt, 0.9*lb_visualization.BoundingBoxPar[3]*rc.Geometry.Vector3d.ZAxis)
            else: cenPtMoved = cenPt
            compassCrvs, compassTextPts, compassText = lb_visualization. compassCircle(cenPtMoved, northVector, maxHorRadius, roseHAngles, 1.2*textSize)
            numberCrvs = lb_visualization.text2srf(compassText, compassTextPts, 'Times New Romans', textSize/1.2)
            compassCrvs = compassCrvs + lb_preparation.flattenList(numberCrvs)
            
            
            # bake
            if bakeIt > 0:
                #Put all of the curves together.
                finalCrvs = []
                for crv in compassCrvs:
                    try:
                        testPt = crv.PointAtEnd
                        finalCrvs.append(crv)
                    except: pass
                
                #Put all of the text together.
                legendText.append(titleStr)
                textPt.append(titlebasePt)
                legendText.extend(compassText)
                textPt.extend(compassTextPts)
                # check the study type
                placeName = listInfo[0][1]
                studyLayerName = 'RADIATION_LILLY'
                stMonth, stDay, stHour, endMonth, endDay, endHour = lb_visualization.readRunPeriod((listInfo[0][5], listInfo[0][6]), False)
                period = `stDay`+ ' ' + lb_visualization.monthList[stMonth-1] + ' ' + `stHour` + \
                 " - " + `endDay`+ ' ' + lb_visualization.monthList[endMonth-1] + ' ' + `endHour` 
                newLayerIndex, l = lb_visualization.setupLayers(period, 'LADYBUG', placeName, studyLayerName, False, False, 0, 0)
                
                if bakeIt == 1: lb_visualization.bakeObjects(newLayerIndex, vaseMesh, legendSrfs, legendText, textPt, textSize, legendFont, finalCrvs, decimalPlaces, True)
                else: lb_visualization.bakeObjects(newLayerIndex, vaseMesh, legendSrfs, legendText, textPt, textSize, legendFont, finalCrvs, decimalPlaces, False)
            
            #Find the max value and vector.
            maxValue = max(resultsFlatten)
            i = resultsFlatten.IndexOf(maxValue)
            maxRadPt = ptsClean[i]
            maxRadInfo = testPtsInfos[i]
            maxPtVec = testPtsVectors[i]
            
        return ptsClean, vaseMesh, [legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)], resultsFlatten, testPtsInfos, compassCrvs, maxRadPt, maxRadInfo, maxPtVec
        
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
       
       maxRadPt = result[6]
       maxRadInfo = result[7]
       maxRadVector = result[8]
    ghenv.Component.Params.Output[4].Hidden = True
    
else:
    print "Set runIt to True!"
