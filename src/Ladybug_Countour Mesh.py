# This component re-color the mesh based on new parameters
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> and Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to create contoured visualizations of any analysis mesh and corresponding numerical dataset in Ladybug + Honeybee.
Note that this component currently only works for planar meshes.
-
Provided by Ladybug 0.0.67
    
    Args:
        _analysisResult: A numerical data set whose length corresponds to the number of faces in the _inputMesh.  This data will be used to generate contours from the mesh.
        _inputMesh: An already-colored mesh from one of the Ladybug components which you would like to re-color based on data in the _analysisResult.
        _contourType_: An integer to set the type of contour visualization.  The default is set to 0 for colored regions.  Choose from the following options:
            0 - Colored Regions + Labeled Lines
            1 - Colored Regions
            2 - Labeled Lines
            3 - Colored Lines
        heightDomain_: Optional height domain to create a 3D mesh result. Use Construct Domain component to create a domain
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.  Legend Parameters can be used to change the colors, numerical range, and/or number of divisions of any Ladybug legend along with the corresponding colored mesh.
        analysisTitle_: Text representing a new title for the re-colored mesh.  If no title is input here, the default will read "unnamed."
        legendTitle_: Text representing a new legend title for re-colored mesh. Legends are usually titled with the units of the _analysisResult.  If no text is provided here, the default title will read "unkown units."
        _labelSize_: A number to set the size of the text labels for the contours when _contourType_ 0 or 2 is selected.  The default is auto-calculated based on the size of the mesh.
        bakeIt_ : An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options:
            0 (or False) - No geometry will be baked into the Rhino scene (this is the default).
            1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. 
            2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry.
        layerName_: If bakeIt_ is set to "True", input Text here corresponding to the Rhino layer onto which the resulting mesh and legend should be baked.
    Returns:
        readMe!: ...
        contourMesh: A list of colored meshes that is organized with each contour region as its own color.
        underlayMesh: A mesh that is colored face-by-face (like a typical Ladybug mesh), which is plaed under the contour mesh to make the visualization read when the Rhino intersection fails to produce a complete contourMesh.
        contourLines: Curves that show values of constant value along the results.
        contourColors: Connect these to a native Grasshopper Preview componen along with the contourLines to get a colored line visualization.
        contourLabels: A list of text meshes that show the value along each contour line.
        legend: A new legend that that corresponds to the colors of the newMesh. Connect this output to a grasshopper "Geo" component in order to preview this legend separately in the Rhino scene.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the newMesh with the grasshopper "move" component.
        legendColors: A list of colors that correspond to each step in the legend.
        intPlanes: The planes that were used to intersect the mesh to genrate the contours. Set heightDomain_ to a non-zer number to visualize.
"""

ghenv.Component.Name = "Ladybug_Countour Mesh"
ghenv.Component.NickName = 'contourMesh'
ghenv.Component.Message = 'VER 0.0.67\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass
#compatibleLBVersion = VER 0.0.59\nJAN_05_2017

import scriptcontext as sc
import Rhino as rc
import rhinoscriptsyntax as rs
import System
from math import pi as PI
import Grasshopper.Kernel as gh
from System import Object
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import copy

def checkMeshPlanarity(mesh, basePlanePt):
    #Check the planarity.
    meshIsPlanar = True
    mesh.Normals.ComputeNormals()
    mesh.FaceNormals.UnitizeFaceNormals()
    meshPlaneVec = mesh.Normals[0]
    if meshPlaneVec.Z < 0:
        meshPlaneVec.Reverse()
    meshPlaneVecReverse = copy.copy(meshPlaneVec)
    meshPlaneVecReverse.Reverse()
    meshNormals = []
    for norm in mesh.Normals:
        if not norm.Equals(meshPlaneVec):
            meshNormals.append(norm)
            if norm.Equals(meshPlaneVecReverse):
                norm.Reverse()
                meshNormals.append(norm)
            else:
                meshIsPlanar = False
    
    # Change the Mesh to be in the XYPlane.
    meshPlane = rc.Geometry.Plane(basePlanePt, meshPlaneVec)
    if meshIsPlanar:
        changeBasisTransform = rc.Geometry.Transform.ChangeBasis(rc.Geometry.Plane.WorldXY, meshPlane)
        mesh.Transform(changeBasisTransform)
    else:
        meshNormals = [meshPlaneVec for i in range(mesh.Normals.Count)]
        changeBasisTransform = rc.Geometry.Transform.ChangeBasis(rc.Geometry.Plane.WorldXY, meshPlane)
        mesh.Transform(changeBasisTransform)
    
    return meshIsPlanar, mesh, meshPlane, meshNormals


def main(analysisResult, inputMesh, contourType, heightDomain, legendPar, analysisTitle, legendTitle, bakeIt, layerName, lb_preparation, lb_visualization):
    # Get the Unit System.
    conversionFac = lb_preparation.checkUnits()
    
    # Check the mesh's structure.
    if inputMesh.Faces.Count == len(analysisResult):
        meshStruct = 0
    elif inputMesh.Vertices.Count == len(analysisResult):
        meshStruct = 1
    else:
        warning = 'length of the results [=' + str(len(analysisResult)) + '] is not equal to the number of mesh faces [=' + str(inputMesh.Faces.Count) + '] or mesh vertices[=' + str(inputMesh.Vertices.Count) + '].'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    singleValMesh = False
    
    # Read the legend and generate a list of blank colors.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    blankColors = []
    if meshStruct == 0:
        for count in inputMesh.Faces:
            blankColors.append(System.Drawing.Color.Gray)
    elif meshStruct == 1:
        for count in inputMesh.Vertices:
            blankColors.append(System.Drawing.Color.Gray)
    
    # Generate an underlay mesh to cover our ass when the intersection fails.
    underlayMesh = None
    if contourType == 0 or contourType == 1 or contourType == None:
        colors = lb_visualization.gradientColor(analysisResult, lowB, highB, customColors)
        underlayMesh = lb_visualization.colorMesh(colors, inputMesh, True, meshStruct)
        if heightDomain!=None:
            underlayMesh = lb_visualization.create3DColoredMesh(underlayMesh, analysisResult, heightDomain, colors, meshStruct)
        moveTrans = rc.Geometry.Transform.Translation(0,0,-(1/conversionFac)*.03)
        underlayMesh.Transform(moveTrans)
    
    # Check the mesh's planarity
    minPt = inputMesh.GetBoundingBox(rc.Geometry.Plane.WorldXY).Min
    meshIsPlanar, inputMesh, meshPlane, meshNormals = checkMeshPlanarity(inputMesh, minPt)
    if meshIsPlanar == False:
        warning = 'The connected inputMesh is not planar and this component only works for planar meshes.' + \
        '\n Try breaking up your mesh into planar pieces and feeding them individually into this component.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    # Find the min and max of the dataset.
    sortedData = analysisResult[:]
    sortedData.sort()
    dataMin = sortedData[0]
    dataMax = sortedData[-1]
    fullRange = dataMax - dataMin
    if lowB != 'min' and highB != 'max':
        legendRange = highB - lowB
    elif lowB != 'min':
        legendRange = dataMax - lowB
    elif highB != 'max':
        legendRange = highB - dataMin
    else:
        legendRange = fullRange
    if fullRange == 0 or fullRange < (legendRange/numSeg):
        singleValMesh = True
        fullRange = 1
        contIncr = legendRange/numSeg
    else:
        contIncr = legendRange/fullRange
    
    # Create a mesh with a height domain, which can then be contoured.
    if heightDomain!=None:
        coloredChart = lb_visualization.create3DColoredMesh(inputMesh, analysisResult, heightDomain, blankColors, meshStruct, meshNormals)
        contInterval = contIncr*(heightDomain.Max - heightDomain.Min)/(numSeg-1)
    else:
        heightD = rc.Geometry.Interval(0,(numSeg-1)*(1/conversionFac))
        contInterval = contIncr*(1/conversionFac)
        coloredChart = lb_visualization.create3DColoredMesh(inputMesh, analysisResult, heightD, blankColors, meshStruct)
    
    # Figure out some basic things about the Legend.
    lb_visualization.calculateBB([coloredChart], True)
    if not legendTitle:  legendTitle = 'unknown units  '
    if not analysisTitle: analysisTitle = '\nno title'
    if legendFont == None: legendFont = 'Verdana'
    if legendFontSize == None: legendFontSize = legendScale * (lb_visualization.BoundingBoxPar[2]/20)
    
    if contourType == 3:
        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(analysisResult
            , lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale
            , legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
    elif contourType == 2:
        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(analysisResult
            , lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale
            , legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
        legendSrfs, legendTextCrv, textPt = [], [], []
    else:
        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(analysisResult
            , lowB, highB, numSeg+1, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale
            , legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan, True)
    
    # generate legend colors.
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    
    # Generate intersection planes.
    intMeshes = []
    if contourType == 0 or contourType == 1 or contourType == None:
        BB = coloredChart.GetBoundingBox(rc.Geometry.Plane.WorldXY)
        boundBox = BB.ToBrep()
        baseSplitPlaneOrigin = boundBox.Faces[4].GetBoundingBox(rc.Geometry.Plane.WorldXY).Min
        baseSplitPlane = boundBox.Faces[4].ToBrep()
        intMeshes = [rc.Geometry.Mesh.CreateFromBrep(baseSplitPlane)[0]]
    
    lastPt = lb_visualization.BoundingBoxPar[0]
    if lowB != 'min':
        if heightDomain!=None:
            startVal = ((lowB-dataMin)/fullRange)*(heightDomain.Max - heightDomain.Min)
        else:
            startVal = ((lowB-dataMin)/fullRange)*(numSeg-1)*(1/conversionFac)
        lastPt = rc.Geometry.Point3d(lastPt.X, lastPt.Y, startVal)
        movedPlane = copy.deepcopy(baseSplitPlane)
        planeTransf = rc.Geometry.Transform.Translation(0,0,lastPt.Z-baseSplitPlaneOrigin.Z)
        movedPlane.Transform(planeTransf)
        movedPlaneMesh = rc.Geometry.Mesh.CreateFromBrep(movedPlane)[0]
        intMeshes = [movedPlaneMesh]
    intPlanes = [rc.Geometry.Plane(lastPt, rc.Geometry.Vector3d.ZAxis)]
    for count in range(int(numSeg)):
        lastPt = rc.Geometry.Point3d(lastPt.X, lastPt.Y, lastPt.Z+contInterval)
        intPlanes.append(rc.Geometry.Plane(lastPt, rc.Geometry.Vector3d.ZAxis))
        if contourType == 0 or contourType == 1 or contourType == None:
            movedPlane = copy.deepcopy(baseSplitPlane)
            planeTransf = rc.Geometry.Transform.Translation(0,0,lastPt.Z-baseSplitPlaneOrigin.Z)
            movedPlane.Transform(planeTransf)
            movedPlaneMesh = rc.Geometry.Mesh.CreateFromBrep(movedPlane)[0]
            intMeshes.append(movedPlaneMesh)
    
    # Contour the mesh.
    contourMeshArea = rc.Geometry.AreaMassProperties.Compute(inputMesh).Area
    initMeshArea = contourMeshArea
    failedIntersects = []
    contourMesh = []
    contourLines = []
    contourLabels = []
    contourColors = []
    labelText = []
    labelTextPts = []
    startTrigger = False
    failIntersecTrigger = False
    
    #Generate colored regions.
    if contourType == 0 or contourType == 1 or contourType == None:
        if singleValMesh == True:
            val = analysisResult[0]
            if lowB == 'min': lowB = val
            if legendRange == 0:
                legendRange = 1
            colorIndex = int((val-lowB)/legendRange)
            coloredChart.VertexColors.CreateMonotoneMesh(legendColors[colorIndex])
            contourMesh.append(coloredChart)
        else:
            try:
                finalSplitMesh = rc.Geometry.Mesh.Split(coloredChart, intMeshes[0])[-1]
                finalSplitMesh.VertexColors.CreateMonotoneMesh(legendColors[0])
                contourArea = rc.Geometry.AreaMassProperties.Compute(finalSplitMesh).Area
                if contourArea < contourMeshArea-sc.doc.ModelAbsoluteTolerance and finalSplitMesh.IsValid:
                    contourMesh.append(finalSplitMesh)
                startTrigger = True
            except:
                pass
            for count in range(len(intMeshes)-1):
                try:
                    if startTrigger == False:
                        finalSplitMesh = rc.Geometry.Mesh.Split(coloredChart, intMeshes[count])[-1]
                        finalSplitMesh.VertexColors.CreateMonotoneMesh(legendColors[count])
                        contourArea = rc.Geometry.AreaMassProperties.Compute(finalSplitMesh).Area
                        if contourArea < contourMeshArea-sc.doc.ModelAbsoluteTolerance and finalSplitMesh.IsValid:
                            contourMesh.append(finalSplitMesh)
                            contourColors.append([legendColors[count]])
                        startTrigger = True
                        initSplitMesh = rc.Geometry.Mesh.Split(coloredChart, intMeshes[count+1])[-1]
                        finalSplitMesh = rc.Geometry.Mesh.Split(initSplitMesh, intMeshes[count])[0]
                    elif count == len(intMeshes)-2:
                        finalSplitMesh = rc.Geometry.Mesh.Split(coloredChart, intMeshes[count])[0]
                    else:
                        initSplitMesh = rc.Geometry.Mesh.Split(coloredChart, intMeshes[count])[-1]
                        initMeshArea = rc.Geometry.AreaMassProperties.Compute(initSplitMesh).Area
                        finalSplitMesh = rc.Geometry.Mesh.Split(initSplitMesh, intMeshes[count+1])[0]
                    try:
                        lColor = legendColors[count+1]
                        finalSplitMesh.VertexColors.CreateMonotoneMesh(lColor)
                    except:
                        lColor = legendColors[count+1]
                        finalSplitMesh.VertexColors.CreateMonotoneMesh(lColor)
                    contourArea = rc.Geometry.AreaMassProperties.Compute(finalSplitMesh).Area
                    if contourArea < contourMeshArea-sc.doc.ModelAbsoluteTolerance and contourArea < initMeshArea-sc.doc.ModelAbsoluteTolerance and finalSplitMesh.IsValid:
                        contourMesh.append(finalSplitMesh)
                        contourColors.append([lColor])
                except:
                    try:
                        finalSplitMesh = rc.Geometry.Mesh.Split(coloredChart, intMeshes[count])[0]
                        finalSplitMesh.VertexColors.CreateMonotoneMesh(legendColors[count])
                        finalSplitMesh.Transform(moveTrans)
                        contourArea = rc.Geometry.AreaMassProperties.Compute(finalSplitMesh).Area
                        if contourArea < contourMeshArea-sc.doc.ModelAbsoluteTolerance:
                            failedIntersects.append(finalSplitMesh)
                    except: pass
    
    # Generate Labeled Contours
    try:
        if contourType == 0 or contourType == 2 or contourType == None:
            if lowB != 'min' and highB != 'max':
                numbers = rs.frange(lowB, highB, round((highB - lowB) / (numSeg -1), 6))
            elif lowB != 'min':
                numbers = rs.frange(lowB, dataMax, round((dataMax - lowB) / (numSeg -1), 6))
            elif highB != 'max':
                numbers = rs.frange(dataMin, highB, round((highB - dataMin) / (numSeg -1), 6))
            else:
                numbers = rs.frange(dataMin, dataMax, round((dataMax - dataMin) / (numSeg -1), 6))
            if decimalPlaces == None: decimalPlaces = 2
            formatString = "%."+str(decimalPlaces)+"f"
            numbersStr = [(formatString % x) for x in numbers]
            if _labelSize_ == None:
                labelSize = textSize/5
            else:
                labelSize = _labelSize_
            for count, plane in enumerate(intPlanes):
                contourLines.append([])
                contourLabels.append([])
                theLines = rc.Geometry.Mesh.CreateContourCurves(coloredChart, plane)
                for line in theLines:
                    contourLines[count].append(line)
                    try:
                        pts = line.DivideByLength(labelSize, True)
                        ptIndex = int(len(pts)/2)
                        ltextPt = line.PointAt(pts[ptIndex])
                        labelText.append(numbersStr[count])
                        labelTextPts.append(ltextPt)
                        labelTextMesh = lb_visualization.text2srf([numbersStr[count]], [ltextPt], legendFont, labelSize, legendBold)[0]
                        contourLabels[count].append(labelTextMesh)
                    except:
                        pass
    except:
        legendSrfs = None
    
    if contourType == 3:
        for count, plane in enumerate(intPlanes):
            try:
                contourColors.append([legendColors[count]])
            except:
                pass
            contourLines.append(rc.Geometry.Mesh.CreateContourCurves(coloredChart, plane))
    
    # Project the mesh back to the XYPlane.
    if heightDomain == None:
        planeTrans = rc.Geometry.Transform.PlanarProjection(rc.Geometry.Plane.WorldXY)
        crvMove = rc.Geometry.Transform.Translation(0,0,sc.doc.ModelAbsoluteTolerance*5)
        for geo in contourMesh: geo.Transform(planeTrans)
        for geo in failedIntersects: geo.Transform(planeTrans)
        for geo in intMeshes: geo.Transform(planeTrans)
        for crvList in contourLines:
            for geo in crvList:
                geo.Transform(planeTrans)
                geo.Transform(crvMove)
        for crvList in contourLabels:
            for geoList in crvList:
                for geo in geoList:
                    geo.Transform(planeTrans)
                    geo.Transform(crvMove)
    
    # color legend surfaces
    if contourType != 2:
        legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    else:
        legendSrfs = None
    
    titlebasePt = lb_visualization.BoundingBoxPar[-2]
    titleTextCurve = lb_visualization.text2srf(["\n\n" + analysisTitle], [titlebasePt], legendFont, legendFontSize, legendBold)
    flattenedLegend = lb_preparation.flattenList(legendTextCrv + titleTextCurve)
    if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
    
    # Change the geomtry back to its original plane.
    transfBack = rc.Geometry.Transform.ChangeBasis(meshPlane, rc.Geometry.Plane.WorldXY)
    for geo in contourMesh: geo.Transform(transfBack)
    for geo in failedIntersects: geo.Transform(transfBack)
    for geo in intMeshes: geo.Transform(transfBack)
    for crvList in contourLines:
        for geo in crvList: geo.Transform(transfBack)
    for crvList in contourLabels:
        for geoList in crvList:
            for geo in geoList: geo.Transform(transfBack)
    for geo in flattenedLegend: geo.Transform(transfBack)
    legendBasePoint.Transform(transfBack)
    if legendSrfs != None:
        try:
            legendSrfs.Transform(transfBack)
        except:
            pass
    
    # Move any failed intersections below the main surface.
    moveTrans = rc.Geometry.Transform.Translation(0,0,-(1/conversionFac)*.03)
    for geo in failedIntersects: geo.Transform(moveTrans)
    
    # If the user has requested to bake the geomtry, then bake it.
    if bakeIt > 0:
        # Greate a joined mesh.
        joinedContMesh = rc.Geometry.Mesh()
        for colMesh in contourMesh:
            joinedContMesh.Append(colMesh)
        
        # Flatten the list of contour curves.
        flatContourLines = lb_preparation.flattenList(contourLines)
        
        # Format the text to be baked as text.
        formatString = "%."+str(decimalPlaces)+"f"
        for count, item in enumerate(legendText):
            try:
                legendText[count] = formatString % item
            except:pass
        if contourType == 2:
            legendText = []
        legendText.append(analysisTitle)
        textPt.append(titlebasePt)
        legendText.extend(labelText)
        textPt.extend(labelTextPts)
        if heightDomain == None:
            for geo in textPt: geo.Transform(planeTrans)
        for geo in textPt: geo.Transform(transfBack)
        
        #Set up the study layer
        studyLayerName = 'CUSTOM_PRESENTATION'
        if layerName == None: layerName = 'Custom'
        # check the study type
        newLayerIndex, l = lb_visualization.setupLayers('Modified Version', 'LADYBUG', layerName, studyLayerName)
        if bakeIt == 1: lb_visualization.bakeObjects(newLayerIndex, joinedContMesh, legendSrfs, legendText, textPt, textSize, legendFont, flatContourLines, decimalPlaces, True)
        else: lb_visualization.bakeObjects(newLayerIndex, joinedContMesh, legendSrfs, legendText, textPt, textSize, legendFont, flatContourLines, decimalPlaces, False)
    
    return contourMesh, [underlayMesh]+failedIntersects, contourLines, contourColors, contourLabels, [legendSrfs, flattenedLegend], legendBasePoint, legendColors, intMeshes



# import the classes
initCheck = True
if sc.sticky.has_key('ladybug_release'):
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
                 "Use updateLadybug component to update userObjects.\n" + \
                 "If you have already updated userObjects drag Ladybug_Ladybug component " + \
                 "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        initCheck = False
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
else:
    print "You should let the Ladybug fly first..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should let the Ladybug fly first...")
    initCheck = False



if initCheck == True and _inputMesh and len(_analysisResult)!=0:
    result = main(_analysisResult, _inputMesh, _contourType_, heightDomain_, legendPar_, analysisTitle_, legendTitle_, bakeIt_, layerName_, lb_preparation, lb_visualization)
    if result!= -1:
        legend= []
        [legend.append(item) for item in lb_visualization.openLegend(result[5])]
        contourMesh = result[0]
        underlayMesh = result[1]
        legendBasePt = result[6]
        legendColors = result[7]
        contourLabelsInit = result[4]
        contourLinesInit = result[2]
        contourColorsInit = result[3]
        intPlanes = result[8]
        contourLines = DataTree[Object]()
        contourColors = DataTree[Object]()
        contourLabels = DataTree[Object]()
        for count, datalist in enumerate(contourLinesInit):
            for item in datalist: contourLines.Add(item, GH_Path(count))
        for count, datalist in enumerate(contourColorsInit):
            for item in datalist: contourColors.Add(item, GH_Path(count))
        for count, branchlist in enumerate(contourLabelsInit):
            for count2, datalist in enumerate(branchlist):
                for item in datalist: contourLabels.Add(item, GH_Path(count, count2))
        
        # Hide output
        ghenv.Component.Params.Output[7].Hidden = True
        ghenv.Component.Params.Output[9].Hidden = True
