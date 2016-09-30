# terrain analysis
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Djordje Spasic <djordjedspasic@gmail.com>
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
Use this component to perform the following terrain analysis types:
-
- Slope
- Aspect
- Elevation
- Visibility
- Hillshade
- TRI (Terrain Ruggedness Index by Riley)
- TRI categories (Terrain Ruggedness Index categories by Riley)
- Mean curvature
------
Component mainly based on:

"DEM Surface Tools for ArcGIS", Jenness Enterprises, 2013.
"How Hillshade works" article from Esri Developer Network
"A terrain ruggedness index that quantifies topographic heterogeneity", S. J. Riley, S. D. DeGloria, R. Elliot, Intermountain journal of sciences Vol 5, 1999.
"How to calculate Topographic Ruggedness Index in ArcGIS Desktop" article from gis.stackexchange.com
-
http://www.jennessent.com/downloads/DEM%20Surface%20Tools%20for%20ArcGIS_A4.pdf
http://edndoc.esri.com/arcobjects/9.2/net/shared/geoprocessing/spatial_analyst_tools/how_hillshade_works.htm
http://download.osgeo.org/qgis/doc/reference-docs/Terrain_Ruggedness_Index.pdf
http://gis.stackexchange.com/a/6059/65002
-
Provided by Ladybug 0.0.63
    
    input:
        _analysisType: Choose one of the terrain analysis types:
                       0 - Slope
                       1 - Aspect
                       2 - Elevation
                       3 - Visibility
                       4 - Hillshade
                       5 - TRI (Terrain Ruggedness Index by Riley)
                       6 - TRI categories (Terrain Ruggedness Index categories by Riley)
                       7 - Mean curvature
        _terrain: A terrain surface or polysurface.
                  Add it by supplying the "terrain" output from the Ladybug "Terrain Generator 2" component.
                  It needs to be a rectangular surface (set the "type_" input of the Ladybug "Terrain Generator 2" component to "2" !!!
        _originPt: An origin point of the upper "_terrain" input.
                   Add it by supplying the "originPt" output from the Ladybug "Terrain Generator 2" component.
        _elevation: Elevation of the upper "_originPt".
                    Add it by supplying the "elevation" output from the Ladybug "Terrain Generator 2" component.
                    -
                    In Rhino document units.
        north_: Input a vector to be used as a true North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
                -
                If not supplied, default North direction will be set to the Y-axis (0 degrees).
        sunVector_: Illuminance source direction.
                    This input is only used for _analysisType = 4 (Hillshade).
                    -
                    If not supplied, default sunVector of (0, 2.37126, -2.37126) will be used (an Y+ vector angled at 45 degrees downwards).
        hypsoStrength_: Hypsometric strength - a factor which determines shading factor's intensity due to elevation differences of terrain vertices.
                        It ranges from 0 to 100.
                        -
                        This input is only used for _analysisType = 4 (Hillshade).
                        -
                        If not supplied, default hypsoStrength of 50 will be used.
        refine_: Refines the "analysedTerrain" output's mesh to finer resolution (halves the Maximum edge length of the "analysedTerrain" mesh).
                 -
                 Final "analysedTerrain" output is created with a certain mesh resolution.
                 Depending on your terrain, sometimes a mesh resolution of higher precision is required.
                 Be cautious !!! Due to "analysedTerrain" mesh increased number of vertices-faces, setting refine_ to True, can result in much longer component runtime !!!
                 Still if your PC configuration is strong enough, you can always set this input to "True". Except for the _analysisType = 6 (TRI categories). In that case the refine_ input will not make any effect on the final "analysedTerrain" mesh.
                 -
                 If not supplied, the refine_ input will be set to False by default.
        legendPar_: Optional legend parameters from the Ladybug "Legend Parameters" component.
        bakeIt_: Set to "True" to bake the terrain analysis geometry into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        title: Title geometry with information about the chosen analysis type and other inputs
        legend: Legend geometry of the "analysedTerrain" output.
        legendBasePt: Legend base point, which can be used to move the "legend" geometry with grasshopper's "Move" component.
                      -
                      Connect this output to a Grasshopper's "Point" parameter in order to preview the "legendBasePt" point in the Rhino scene.
"""

ghenv.Component.Name = "Ladybug_Terrain Analysis"
ghenv.Component.NickName = "TerrainAnalysis"
ghenv.Component.Message = "VER 0.0.63\nSEP_30_2016"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System
import Rhino
import time
import math
import gc


def checkInputData(analysisType, terrainId, originPt, originPtElevation, north, sunVector, hypsometricStrength, refine):
    
    # check inputs
    if (analysisType == None) or ((analysisType  < 0) or (analysisType  > 7)):
        analysisType = analysisTypeLabel = originPt = originPtElevation = northRad = northD = sunVector = hypsometricStrength = refine = exportValues = unitSystem = unitConversionFactor = legendUnit = None
        validInputData = False
        printMsg = "Please supply a number from 0 to 7 to the \"_analysisGeometry\" input based on the analysis you would like to perform."
        return analysisType, analysisTypeLabel, originPt, originPtElevation, northRad, northD, sunVector, hypsometricStrength, refine, exportValues, unitSystem, unitConversionFactor, legendUnit, validInputData, printMsg
    if (analysisType == 0):
        analysisTypeLabel = "Slope"
    elif (analysisType == 1):
        analysisTypeLabel = "Aspect"
    elif (analysisType == 2):
        analysisTypeLabel = "Elevation"
    elif (analysisType == 3):
        analysisTypeLabel = "Visibility"
    elif (analysisType == 4):
        analysisTypeLabel = "Hillshade"
    elif (analysisType == 5):
        analysisTypeLabel = "Terrain Ruggedness Index"
    elif (analysisType == 6):
        analysisTypeLabel = "Terrain Ruggedness Index categories"
    elif (analysisType == 7):
        analysisTypeLabel = "Mean curvature"
    
    
    if (terrainId == None):
        analysisType = analysisTypeLabel = originPt = originPtElevation = northRad = northD = sunVector = hypsometricStrength = refine = exportValues = unitSystem = unitConversionFactor = legendUnit = None
        validInputData = False
        printMsg = "Please supply the \"terrain\" output data from the Ladybug \"Terrain Generator 2\" component, to this component's \"_terrain\" input.\n" + \
                   "It needs to be a rectangular surface/polysurface (set the \"type_\" input of the Ladybug \"Terrain Generator 2\" component to \"2\")."
        return analysisType, analysisTypeLabel, originPt, originPtElevation, northRad, northD, sunVector, hypsometricStrength, refine, exportValues, unitSystem, unitConversionFactor, legendUnit, validInputData, printMsg
    else:
        terrainObj = rs.coercegeometry(terrainId)
        if isinstance(terrainObj, Rhino.Geometry.Brep):
            # ok
            pass
        else:
            #isinstance(terrainObj, Rhino.Geometry.Mesh) or any other geometry type
            analysisType = analysisTypeLabel = originPt = originPtElevation = northRad = northD = sunVector = hypsometricStrength = refine = exportValues = unitSystem = unitConversionFactor = legendUnit = None
            validInputData = False
            printMsg = "The data you spplied to the \"_terrain\" input is not a surface nor a polysurface.\n" + \
                       "Please supply the \"terrain\" output data from the Ladybug \"Terrain Generator 2\" component, to this component's \"_terrain\" input.\n" + \
                       "It needs to be a rectangular surface (set the \"type_\" input of the Ladybug \"Terrain Generator 2\" component to \"2\")."
            return analysisType, analysisTypeLabel, originPt, originPtElevation, northRad, northD, sunVector, hypsometricStrength, refine, exportValues, unitSystem, unitConversionFactor, legendUnit, validInputData, printMsg
    
    
    if (originPt == None):
        analysisType = analysisTypeLabel = originPt = originPtElevation = northRad = northD = sunVector = hypsometricStrength = refine = exportValues = unitSystem = unitConversionFactor = legendUnit = None
        validInputData = False
        printMsg = "Please supply the \"originPt\" output data from the Ladybug \"Terrain Generator 2\" component, to this component's \"_originPt\" input.."
        return analysisType, analysisTypeLabel, originPt, originPtElevation, northRad, northD, sunVector, hypsometricStrength, refine, exportValues, unitSystem, unitConversionFactor, legendUnit, validInputData, printMsg
    
    
    if (originPtElevation == None):
        analysisType = analysisTypeLabel = originPt = originPtElevation = northRad = northD = sunVector = hypsometricStrength = refine = exportValues = unitSystem = unitConversionFactor = legendUnit = None
        validInputData = False
        printMsg = "Please supply the \"elevation\" output data from the Ladybug \"Terrain Generator 2\" component, to this component's \"_elevation\" input.."
        return analysisType, analysisTypeLabel, originPt, originPtElevation, northRad, northD, sunVector, hypsometricStrength, refine, exportValues, unitSystem, unitConversionFactor, legendUnit, validInputData, printMsg
    
    
    if (north == None):
        northRad = 0  # default, in radians
        northVec = Rhino.Geometry.Vector3d(0,1,0)
    else:
        try:  # check if it's a number
            north = float(north)
            if north < 0 or north > 360:
                analysisType = analysisTypeLabel = originPt = originPtElevation = northRad = northD = sunVector = hypsometricStrength = refine = exportValues = unitSystem = unitConversionFactor = legendUnit = None
                validInputData = False
                printMsg = "Please input north_ angle value from 0 to 360."
                return analysisType, analysisTypeLabel, originPt, originPtElevation, northRad, northD, sunVector, hypsometricStrength, refine, exportValues, unitSystem, unitConversionFactor, legendUnit, validInputData, printMsg
        except Exception, e:  # check if it's a vector
            north.Unitize()
        
        northRad, northVec = lb_photovoltaics.angle2northClockwise(north)
        northVec.Unitize()
    northD = int(360-math.degrees(northRad))
    if northD == 360: northD = 0
    
    
    if (sunVector == None):
        sunVector = Rhino.Geometry.Vector3d(0, 2.37126, -2.37126)  # default (towards +Y, angled by 45 degrees towards -Z)
    # check if sunVector is parallel to Z + or - axis (then it's invalid). If it is, angle it (set the Y coordinate to 0.01)
    Zaxis = Rhino.Geometry.Vector3d(0,0,-1)
    if sunVector.IsParallelTo(Zaxis):
        sunVector = Rhino.Geometry.Vector3d(sunVector.X, 0.01, sunVector.Z)
    
    
    if (hypsometricStrength == None):
        hypsometricStrength = 50  # default
    
    if (refine == None):
        refine = False  # default
    
    exportValues = True  # possible future input (exportValues_)
    if (exportValues == None):
        exportValues = False  # default
    
    
    
    sc.doc = Rhino.RhinoDoc.ActiveDoc
    unitSystem = "%s" % rs.UnitSystemName(False, False, False, True)
    sc.doc = ghdoc
    
    unitConversionFactor = lb_preparation.checkUnits()
    
    if (analysisType == 0) or (analysisType == 1):
        legendUnit = "degrees"
    elif (analysisType == 2) or (analysisType == 3) or (analysisType == 5):
        legendUnit = unitSystem
    elif (analysisType == 4):
        legendUnit = "HSH"
    elif (analysisType == 6):
        legendUnit = "TRI category"
    elif (analysisType == 7):
        legendUnit = "1/%s" % unitSystem
    
    validInputData = True
    printMsg = "ok"
    
    return analysisType, analysisTypeLabel, originPt, originPtElevation, northRad, northD, sunVector, hypsometricStrength, refine, exportValues, unitSystem, unitConversionFactor, legendUnit, validInputData, printMsg


def createOutputDescriptions(analysisType, unitSystem):
    
    if _runIt:
        outputDescriptions = [
        ["Terrain Slope analysis mesh.",  #analysedTerrain
        
        "Terrain Slope values.\n" + \
        "Each value represents an angle between normal and its horizontal projection, at each mesh vertex.\n" + \
        "-\n" + \
        "In degrees."]  #values
        
        ,
        
        ["Terrain Aspect (slope direction) analysis mesh.",  #analysedTerrain
        
        "Terrain Aspect (slope direction) values.\n" + \
        "Each value represents an angle between the slope direction projected normal and north vector, at each mesh vertex.\n" + \
        "-\n" + \
        "In degrees."]  #values
        
        ,
        
        ["Terrain Elevation analysis mesh.",  #analysedTerrain
        
        "Terrain Elevation values.\n" + \
        "Each value represents an elevation of each mesh vertex.\n" + \
        "-\n" + \
        "In %s." % unitSystem]  #values
        
        ,
        
        ["Terrain Visibility analysis mesh.",  #analysedTerrain
        
        "Terrain Visibility values.\n" + \
        "Each value represents the distance between the _originPt and each mesh vertex.\n" + \
        "If mesh vertex is not visible from the _originPt (these are gray colored areas), then the distance will be: 0.\n" + \
        "-\n" + \
        "In %s." % unitSystem]  #values
        
        ,
        
        ["Terrain Hillshade analysis mesh.\n" + \
        "Hillshading is a useful way to depict the topographic relief of a terrain.\n" + \
        "A somewhat better preview of the analysedTerrain mesh is given when the legendPar_ input is supplied with customColors_ consisted of two colors only (white and black for example).",  #analysedTerrain
        
        "Terrain Hillshade values.\nEach value represents a hypsometrically shaded hillshade (HSH) which is calculated as Elevation shading factor subtracted from 1 and multiplied by the actual Hillshade. Actual Hillshade being the hypothetical illumination of each mesh vertex.\n" + \
        "-\n" + \
        "In hypsometrically shaded hillshade (HSH) value."]  #values
        
        ,
        
        ["Terrain Terrain Ruggedness Index (TRI) analysis mesh.",  #analysedTerrain
        
        "Terrain Terrain Ruggedness Index (TRI) values.\n" + \
        "Each value represents difference between the elevation of the vertex and the mean of an 8-vertices neighborhood of surrounding vertices, at each mesh vertex.\n" + \
        "-\n" + \
        "In %s." % unitSystem]  #values
        
        ,
        
        ["Terrain Terrain Ruggedness Index (TRI) category analysis mesh.",  #analysedTerrain
        
        "Terrain Terrain Ruggedness Index (TRI) category values.\n" + \
        "Categories being the following:\n" + \
        "-\n" + \
        "- category 0 (<=8.94 m): Level.\n" + \
        "- category 1 (8.94-10.77 m): Nearly level.\n" + \
        "- category 2 (10.77-12.69 m): Slightly rugged.\n" + \
        "- category 3 (12.69-15.46 m): Intermediately rugged.\n" + \
        "- category 4 (15.46-22.29 m): Moderately rugged.\n" + \
        "- category 5 (22.29-30.95 m): Highly rugged.\n" + \
        "- category 6 (> 30.95 m): Extremely rugged.\n" + \
        "-\n" + \
        "Unitless."]  #values
        
        ,
        
        ["Terrain Mean curvature analysis mesh.\n" + \
        "It is useful indicator of abrupt change in the terrain curvature.",  #analysedTerrain
        
        "Terrain Mean curvature values.\n" + \
        "Each value represents mean curvature value at each mesh vertex.\n" + \
        "-\n" + \
        "In 1/%s." % unitSystem]  #values
        ]
        
        chosenOutputDescription = outputDescriptions[analysisType]
    
    else:
        chosenOutputDescription = \
        ["Analysed terrain mesh for the chosen _analysisType.",  #analysedTerrain
        
        "Values corresponding to each \"analysedTerrain\" vertex, for the chosen _analysisType."]  #values
    
    ghenv.Component.Params.Output[1].Description = chosenOutputDescription[0]  # assing description to "analysedTerrain" output
    ghenv.Component.Params.Output[2].Description = chosenOutputDescription[1]  # assign description to "values" output


# shortened version of lb_photovoltaics.correctSrfAzimuthDforNorth
def correctSrfAzimuthDforNorth(northRad, srfAzimuthD):
    northDeg = 360-math.degrees(northRad)
    correctedSrfAzimuthD = northDeg + srfAzimuthD
    if correctedSrfAzimuthD > 360:
        correctedSrfAzimuthD = correctedSrfAzimuthD-360
    return correctedSrfAzimuthD


def createAnalysedTerrainMesh(analysisType, terrainId, originPt, originPtElevation, northRad, sunVector, hypsometricStrength, refine, exportValues, unitConversionFactor):
    
    terrainBrep = rs.coercegeometry(terrainId)
    # shrink the upper terrain brepface in case it is not shrinked (for example: the terrain surface inputted to _terrain input is not created by "Terrain Generator 2" component)
    terrainBrepFaces = terrainBrep.Faces
    terrainBrepFaces.ShrinkFaces()
    
    terrainSrf = terrainBrepFaces[0].DuplicateSurface()
    
    # convert _terrain input to a mesh
    meshParam = Rhino.Geometry.MeshingParameters()
    #preparing for "refine_" input
    terrainSrfControlPts = terrainSrf.Points
    terrainSrfControlPtsCoordinates = [pt.Location for pt in terrainSrfControlPts]
    distanceBetweenFirstSecondControlPt = terrainSrfControlPtsCoordinates[int((len(terrainSrfControlPtsCoordinates)/2)-4)].DistanceTo(terrainSrfControlPtsCoordinates[int(len(terrainSrfControlPtsCoordinates)/2-5)])
    # for analysisType 5, 6 only:
    bb = terrainBrep.GetBoundingBox(False)
    bb_bottom_Xdirection_edge = bb.GetEdges()[0]
    bb_bottom_Ydirection_edge = bb.GetEdges()[1]
    numberOfRows = int( (bb_bottom_Ydirection_edge.Length/distanceBetweenFirstSecondControlPt) )  # if "refine_" input set to False
    numberOfColumns = int( (bb_bottom_Xdirection_edge.Length/distanceBetweenFirstSecondControlPt) )  # if "refine_" input set to False
    
    if refine and (analysisType != 6):  # "refine_ == True" will not affect the TRI categories (analysisType = 6)
        # if refine_ input set to True, limit the meshParam.MaximumEdgeLength (this is for analysisType 0 to 4 and 7)
        meshParam.MaximumEdgeLength = int(distanceBetweenFirstSecondControlPt) / 2
        # for analysisType 5 and 6
        numberOfRows = 2 * numberOfRows  # for "refine_" input set to True, double the numberOfRows
        numberOfColumns = 2 * numberOfColumns  # for "refine_" input set to True, double the numberOfColumns
    
    terrainMesh = Rhino.Geometry.Mesh.CreateFromBrep(terrainBrep, meshParam)[0]
    terrainMesh_vertices = list(terrainMesh.Vertices)
    
    lowB, highB, numSeg, customColors, legendBasePt, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar_, False)
    
    
    originPtZ = originPt.Z
    # for _analysisStyle == 2,5,6
    def calculateVertexElevation(vertexZ):
        vertexElevation = (vertexZ-originPtZ)+originPtElevation
        return vertexElevation
    
    if (analysisType == 0):
        # slope
        slopeAngles = []
        for vertex in terrainMesh_vertices:
            success, u, v = terrainSrf.ClosestPoint(vertex)
            surfaceNormal = terrainSrf.NormalAt(u,v)
            projectedSurfaceNormal = Rhino.Geometry.Vector3d(surfaceNormal.X, surfaceNormal.Y, 0)
            slopeAngleR = Rhino.Geometry.Vector3d.VectorAngle(surfaceNormal, projectedSurfaceNormal)
            slopeAngleD = math.degrees(slopeAngleR)
            slopeAngles.append(slopeAngleD)
        customColors2 = customColors[:]
        customColors2.reverse()
        colors = lb_visualization.gradientColor(slopeAngles, lowB, highB, customColors2)
    
    
    elif (analysisType == 1):
        # aspect (slope direction)
        Yaxis = Rhino.Geometry.Vector3d(0,1,0)
        slopeDirections = []
        for vertex in terrainMesh_vertices:
            success, u, v = terrainSrf.ClosestPoint(vertex)
            surfaceNormal = terrainSrf.NormalAt(u,v)
            projectedSurfaceNormal = Rhino.Geometry.Vector3d(surfaceNormal.X, surfaceNormal.Y, 0)
            # clockwise
            slopeDirectionR = Rhino.Geometry.Vector3d.VectorAngle(projectedSurfaceNormal, Yaxis, Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0,0,0), Rhino.Geometry.Vector3d(0,0,1)))
            # counter clockwise
            #slopeDirectionR = Rhino.Geometry.Vector3d.VectorAngle(projectedSurfaceNormal, Yaxis, Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0,0,0), Rhino.Geometry.Vector3d(0,0,-1)))
            slopeDirectionD = math.degrees(slopeDirectionR)
            correctedSlopeDirectionD_forNorth = correctSrfAzimuthDforNorth(northRad, slopeDirectionD)
            slopeDirections.append(correctedSlopeDirectionD_forNorth)
        colors = lb_visualization.gradientColor(slopeDirections, lowB, highB, customColors)
    
    
    elif (analysisType == 2):
        # elevation
        elevations = []
        for vertex in terrainMesh_vertices:
            vertexElevation = calculateVertexElevation(vertex.Z)
            elevations.append(vertexElevation)
        colors = lb_visualization.gradientColor(elevations, lowB, highB, customColors)
    
    
    elif (analysisType == 3):
        # visibility
        hittedPts = []
        hittedLines = []
        
        distanceToEachMeshVertex_notHitted = []
        distanceToEachMeshVertex_all = []
        eachMeshVertexIndex_notHitted = []
        colors = [None]*len(terrainMesh_vertices)
        
        liftedOriginPt = Rhino.Geometry.Point3d(originPt.X, originPt.Y, originPt.Z + 0.4)  # radi sa + 0.05, ali refine = True
        for index,vertex in enumerate(terrainMesh_vertices):
            liftedVertex = Rhino.Geometry.Point3d(vertex.X, vertex.Y, vertex.Z + 0.4)  # radi sa + 0.05, ali refine = True
            line = Rhino.Geometry.Line(liftedOriginPt, liftedVertex)
            intersectionPts, intersectionFaceIndex = Rhino.Geometry.Intersect.Intersection.MeshLine(terrainMesh,line)
            if len(intersectionPts) != 0:
                # terrainMesh hitted
                hittedPts.append(liftedVertex)
                hittedLines.append(line)
                colors[index] = System.Drawing.Color.FromArgb(70,70,70)  # set it to gray color
                distanceToEachMeshVertex_all.append(0)  # if vertex can not be seen from liftedOriginPt, then set the distance between a vertex and liftedOriginPt to 0
            else:
                # nothing hitted
                eachMeshVertexIndex_notHitted.append(index)
                distance = liftedOriginPt.DistanceTo(vertex)
                distanceToEachMeshVertex_notHitted.append(distance)  # will be used to create a legend
                distanceToEachMeshVertex_all.append(distance)  # will be used for "values" output
        if len(distanceToEachMeshVertex_notHitted) == 0:  # fix when all vertices can not be seen
            distanceToEachMeshVertex_notHitted = [System.Drawing.Color.FromArgb(70,70,70)]*len(terrainMesh_vertices)
        
        customColors2 = customColors[:]
        customColors2.reverse()
        colors_notHitted = lb_visualization.gradientColor(distanceToEachMeshVertex_notHitted, lowB, highB, customColors2)
        
        for dummyIndex, notHittedVertexIndex in enumerate(eachMeshVertexIndex_notHitted):
            colors[notHittedVertexIndex] = colors_notHitted[dummyIndex]
    
    
    elif (analysisType == 4):
        # hillshade
        # based on: http://edndoc.esri.com/arcobjects/9.2/net/shared/geoprocessing/spatial_analyst_tools/how_hillshade_works.htm
        # http://www.jennessent.com/downloads/DEM%20Surface%20Tools%20for%20ArcGIS_A4.pdf
        
        # deconstruct sunVector to sunAltitudeR, sunZenithR, sunAzimuthR
        projectedSunvector = Rhino.Geometry.Vector3d(sunVector.X, sunVector.Y, 0)
        sunAltitudeR = Rhino.Geometry.Vector3d.VectorAngle(sunVector, projectedSunvector)
        sunZenithR = (math.pi/2) - sunAltitudeR
        
        Yaxis = Rhino.Geometry.Vector3d(0,1,0)
        # clockwise
        sunAzimuthR = Rhino.Geometry.Vector3d.VectorAngle(projectedSunvector, Yaxis, Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0,0,0), Rhino.Geometry.Vector3d(0,0,1)))
        # counter clockwise
        #sunAzimuthR = Rhino.Geometry.Vector3d.VectorAngle(projectedSunvector, Yaxis, Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0,0,0), Rhino.Geometry.Vector3d(0,0,-1)))
        
        # for shadingFactor
        # (there is no need to use "calculateVertexElevation" function because the ratio between vertices actual elevations and their Rhino Z coordinates is the same)
        vertexZ = [vertex.Z  for vertex in terrainMesh_vertices]
        vertexZmin = min(vertexZ)
        vertexZmax = max(vertexZ)
        
        hypsometricallyShadedHillshadeL = []
        for vertex in terrainMesh_vertices:
            success, u, v = terrainSrf.ClosestPoint(vertex)
            surfaceNormal = terrainSrf.NormalAt(u,v)
            projectedSurfaceNormal = Rhino.Geometry.Vector3d(surfaceNormal.X, surfaceNormal.Y, 0)
            slopeAngleR = Rhino.Geometry.Vector3d.VectorAngle(surfaceNormal, projectedSurfaceNormal)
            slopeAngleD = math.degrees(slopeAngleR)
            # clockwise
            slopeDirectionR = Rhino.Geometry.Vector3d.VectorAngle(projectedSurfaceNormal, Yaxis, Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0,0,0), Rhino.Geometry.Vector3d(0,0,1)))
            # counter clockwise
            #slopeDirectionR = Rhino.Geometry.Vector3d.VectorAngle(projectedSurfaceNormal, Yaxis, Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0,0,0), Rhino.Geometry.Vector3d(0,0,-1)))
            slopeDirectionD = math.degrees(slopeDirectionR)
            correctedSlopeDirectionD_forNorth = correctSrfAzimuthDforNorth(northRad, slopeDirectionD)
            correctedSlopeDirectionR_forNorth = math.radians(correctedSlopeDirectionD_forNorth)
            
            hillshade = 255 * ( ( math.cos(sunZenithR) * math.cos(slopeAngleR) ) + ( math.sin(sunZenithR) * math.sin(slopeAngleR) * math.cos(sunAzimuthR - correctedSlopeDirectionR_forNorth) ) )
            if hillshade < 0: hillshade = 0
            
            hypsometricStrength2 = -hypsometricStrength
            shadingFactor = 1 - ((vertex.Z - vertexZmin)/(vertexZmax-vertexZmin))*(hypsometricStrength2/100)-((100-hypsometricStrength2)/100)
            hypsometricallyShadedHillshade = (1-shadingFactor) * hillshade   # also called HSH
            hypsometricallyShadedHillshadeL.append(hypsometricallyShadedHillshade)
        colors = lb_visualization.gradientColor(hypsometricallyShadedHillshadeL, lowB, highB, customColors)
    
    
    elif (analysisType == 5) or (analysisType == 6) or (analysisType == 8):
        # TRI (Terrain Ruggedness Index by Riley)  and  TRI categories (Terrain Ruggedness Index categories by Riley)
        # based on: http://download.osgeo.org/qgis/doc/reference-docs/Terrain_Ruggedness_Index.pdf
        # http://gis.stackexchange.com/a/6059/65002
        def calculate_TRI_category(TRI_rhinoUnits):
            TRI_meters = TRI_rhinoUnits/unitConversionFactor
            
            if TRI_meters <=math.sqrt(80):
                TRI_category = 0
            elif math.sqrt(80)<TRI_meters<=math.sqrt(116):
                TRI_category = 1
            elif math.sqrt(116)<TRI_meters<=math.sqrt(161):
                TRI_category = 2
            elif math.sqrt(161)<TRI_meters<=math.sqrt(239):
                TRI_category = 3
            elif math.sqrt(239)<TRI_meters<=math.sqrt(497):
                TRI_category = 4
            elif math.sqrt(497)<TRI_meters<=math.sqrt(958):
                TRI_category = 5
            elif TRI_meters>math.sqrt(958):
                TRI_category = 6
            return TRI_category
        
        # TPI categories based on: "GIS-Based Automated Landform Classification and Topographic, Landcover and Geologic Attributes of Landforms Around the Yazoren Polje", S. Tagil, J. Jenness, Journal of applied sciences 8, 2008
        # http://scialert.net/qredirect.php?doi=jas.2008.910.921&linkid=pdf
        def calculate_TPI_category(TPI_rhinoUnits, SD, slopeD):
            
            if TPI_rhinoUnits <=-1:
                TPI_category = 0  # valley bottom
            elif (-1<TPI_rhinoUnits<1) and (slopeD <= 6):
                TPI_category = 1  # flat
            elif (-1<TPI_rhinoUnits<1) and (slopeD > 6):
                TPI_category = 2  # flat
            elif TPI_rhinoUnits >= 1:
                TPI_category = 3  # hilltop
            return TPI_category
        
        
        # generates points on terrainSrf (ptsOnTerrainSrf) and its elevation values (vertexElevations). They are used to calculate TRI and TRI categories after that
        domainUV = Rhino.Geometry.Interval(0,1)
        terrainSrf.SetDomain(0, domainUV)
        terrainSrf.SetDomain(1, domainUV)
        uDomain = terrainSrf.Domain(0)
        vDomain = terrainSrf.Domain(1)
        
        uStep = uDomain.T1/(numberOfRows-1)
        vStep = vDomain.T1/(numberOfColumns-1)
        
        
        ptsOnTerrainSrf = []  # to create the mesh by lb_meshpreparation.meshFromPoints
        vertexElevations = []
        vertexNormals = []
        for i in xrange(numberOfRows):
            u = i * uStep
            for k in xrange(numberOfColumns):
                v = k * vStep
                pt = terrainSrf.PointAt(u,v)
                ptsOnTerrainSrf.append(pt)
                ptZ = pt.Z
                vertexElevation = calculateVertexElevation(ptZ)
                vertexElevations.append(vertexElevation)
                surfaceNormal = terrainSrf.NormalAt(u,v)
                surfaceNormal.Unitize()
                vertexNormals.append(surfaceNormal)
        # end of generation of points on terrainSrf (ptsOnTerrainSrf) and its elevation values (vertexElevations)
        
        
        # calculation of surrounding set of neighboring indices in a matrix. equations by: http://math.stackexchange.com/users/71915/dolma
        def rowOfIndexFunc(index):
            rowOfIndex = int(math.floor(index/numberOfColumns)+1)
            return rowOfIndex
        
        TRI_List = []
        TPI_List = []
        TRI_category_List = []
        TPI_category_List = []
        for wantedIndex in xrange(len(vertexElevations)):
            rowOfWantedIndex = rowOfIndexFunc(wantedIndex)
            
            indicesInRowBeforeWantedIndex = [wantedIndex-numberOfColumns-1, wantedIndex-numberOfColumns, wantedIndex-numberOfColumns+1]
            indicesInRowOfWantedIndex = [wantedIndex-1, wantedIndex+1]
            indicesInRowAfterWantedIndex = [wantedIndex+numberOfColumns-1, wantedIndex+numberOfColumns, wantedIndex+numberOfColumns+1]
            
            kept_indicesInRowBeforeWantedIndex = [index  for index in indicesInRowBeforeWantedIndex  if rowOfIndexFunc(index) ==  rowOfWantedIndex-1]
            kept_indicesInRowOfWantedIndex = [index2  for index2 in indicesInRowOfWantedIndex  if rowOfIndexFunc(index2) ==  rowOfWantedIndex]
            kept_indicesInRowAfterWantedIndex = [index3  for index3 in indicesInRowAfterWantedIndex  if rowOfIndexFunc(index3) ==  rowOfWantedIndex+1]
            mergedThreeLists_kept_indices = kept_indicesInRowBeforeWantedIndex + kept_indicesInRowOfWantedIndex + kept_indicesInRowAfterWantedIndex
            
            indicesRange = range(0, numberOfRows*numberOfColumns)
            neighborIndices = [index4  for index4 in mergedThreeLists_kept_indices  if index4 in indicesRange]
            neighboringVertexElevations = [vertexElevations[index] for index in neighborIndices]
            neighboringVertexNormals = [vertexNormals[index] for index in neighborIndices]
            centralVertexElevation = vertexElevations[wantedIndex]
            centralVertexNormal = vertexNormals[wantedIndex]
            neighboringVertexElevations_plus_centralVertexElevation = neighboringVertexElevations + [centralVertexElevation]
            neighboringVertexNormals_plus_centralVertexNormal = neighboringVertexNormals + [centralVertexNormal]
            
            #SRF_rhinoUnits = math.sqrt( (sum([normal.X  for normal in neighboringVertexNormals_plus_centralVertexNormal]))**2 + (sum([normal.Y  for normal in neighboringVertexNormals_plus_centralVertexNormal]))**2 + (sum([normal.Z  for normal in neighboringVertexNormals_plus_centralVertexNormal]))**2 ) / len(neighboringVertexElevations_plus_centralVertexElevation)  # Hobson’s Surface Roughness Factor
            TRI_rhinoUnits = math.sqrt( sum([(centralVertexElevation-ptsZ)**2  for ptsZ in neighboringVertexElevations]) )  # in rhino document units
            TRI_List.append(TRI_rhinoUnits)
            
            TRI_category = calculate_TRI_category(TRI_rhinoUnits)  # unitless
            TRI_category_List.append(TRI_category)
            """
            TPI_rhinoUnits = centralVertexElevation - sum(neighboringVertexElevations)/len(neighboringVertexElevations)  # unitless
            TPI_List.append(TPI_rhinoUnits)
            
            averageElevationOfCellsWindow = sum(neighboringVertexElevations_plus_centralVertexElevation) / len(neighboringVertexElevations_plus_centralVertexElevation)
            SD = math.sqrt(  sum( [(elevation - averageElevationOfCellsWindow)**2  for elevation in neighboringVertexElevations_plus_centralVertexElevation] ) / (len(neighboringVertexElevations_plus_centralVertexElevation) - 1)  )  # standard deviation of the elevation, in rhino document units
            projectedCentralVertexNormal = Rhino.Geometry.Vector3d(centralVertexNormal.X, centralVertexNormal.Y, 0)
            slopeAngleR = Rhino.Geometry.Vector3d.VectorAngle(centralVertexNormal, projectedCentralVertexNormal)
            slopeAngleD = math.degrees(slopeAngleR)
            TPI_category = calculate_TPI_category(TPI_rhinoUnits, SD, slopeAngleD)  # unitless
            TPI_category_List.append(TPI_category)
            """
        
        if (analysisType == 5):
            colors = lb_visualization.gradientColor(TRI_List, lowB, highB, customColors)
            terrainMesh_colored = lb_meshpreparation.meshFromPoints(numberOfRows, numberOfColumns, ptsOnTerrainSrf, colors)
            del terrainMesh_vertices; del ptsOnTerrainSrf; del colors; del TRI_category_List; del TPI_List
            
            return terrainMesh_colored, TRI_List, TRI_List
        elif (analysisType == 6):
            colors = lb_visualization.gradientColor(TRI_category_List, lowB, highB, customColors)
            terrainMesh_colored = lb_meshpreparation.meshFromPoints(numberOfRows, numberOfColumns, ptsOnTerrainSrf, colors)
            del terrainMesh_vertices; del ptsOnTerrainSrf; del colors; del TRI_List; del TPI_List
            
            return terrainMesh_colored, TRI_category_List, TRI_category_List
        elif (analysisType == 8):
            # for TPI values
            colors = lb_visualization.gradientColor(TPI_List, lowB, highB, customColors)
            terrainMesh_colored = lb_meshpreparation.meshFromPoints(numberOfRows, numberOfColumns, ptsOnTerrainSrf, colors)
            del terrainMesh_vertices; del ptsOnTerrainSrf; del colors; del TRI_List; del TRI_category_List
            
            return terrainMesh_colored, TPI_List, TPI_List
    
    
    elif (analysisType == 7):
        # mean curvature
        MeanCurvatures = []
        for vertex in terrainMesh_vertices:
            success, u, v = terrainSrf.ClosestPoint(vertex)
            surfaceCurvatureParameters = terrainSrf.CurvatureAt(u,v)
            meanCurvature = surfaceCurvatureParameters.Mean
            MeanCurvatures.append(meanCurvature)
        colors = lb_visualization.gradientColor(MeanCurvatures, lowB, highB, customColors)
    
    
    
    # color the terrainMesh with generated colors for every analysisType except 5 and 6 types
    terrainMesh.VertexColors.Clear()
    for i in xrange(len(terrainMesh_vertices)):
        terrainMesh.VertexColors.Add(colors[i])
    
    
    #terrainMesh, values, legend values
    if (analysisType == 0):
        del terrainMesh_vertices; del colors
        return terrainMesh, slopeAngles, slopeAngles
    elif (analysisType == 1):
        del terrainMesh_vertices; del colors
        return terrainMesh, slopeDirections, slopeDirections
    elif (analysisType == 2):
        del terrainMesh_vertices; del colors
        return terrainMesh, elevations, elevations
    elif (analysisType == 3):
        del terrainMesh_vertices; del colors
        return terrainMesh, distanceToEachMeshVertex_all, distanceToEachMeshVertex_notHitted
    elif (analysisType == 4):
        del terrainMesh_vertices; del colors
        return terrainMesh, hypsometricallyShadedHillshadeL, hypsometricallyShadedHillshadeL
    elif (analysisType == 7):
        del terrainMesh_vertices; del colors
        return terrainMesh, MeanCurvatures, MeanCurvatures


def joinTerrainStand_withTerrainMesh(terrainId, terrainMesh):
    
    terrainBrep = rs.coercegeometry(terrainId)
    terrainBrepFaces = list(terrainBrep.Faces)
    if len(terrainBrepFaces) > 1:
        # inputted _terrain has a stand
        terrainMesh_withStand = Rhino.Geometry.Mesh()
        terrainMesh_withStand.Append(terrainMesh)
        
        terrainNotJoinedBreps_withoutTerrainSrf = []
        for brepFaceIndex, brepFace in enumerate(terrainBrepFaces):
            if brepFaceIndex != 0:
                # filter the terrainSrf
                terrainNotJoinedBreps_withoutTerrainSrf.append(brepFace.DuplicateFace(False))
        terrainJoinedBrep_withoutTerrainSrf = Rhino.Geometry.Brep.JoinBreps(terrainNotJoinedBreps_withoutTerrainSrf,0.001)[0]
        standMeshesWithout_terrainMesh = Rhino.Geometry.Mesh.CreateFromBrep(terrainJoinedBrep_withoutTerrainSrf)
        
        for mesh in standMeshesWithout_terrainMesh:
            terrainMesh_withStand.Append(mesh)  # terrainMesh will loose its colors
        
        
        # color the terrainMesh_withStand with terrainMesh colors
        terrainMesh_Colors = list(terrainMesh.VertexColors)
        
        # fix for error on line 637 (success = terrainMesh_withStand.VertexColors.SetColor(vertexIndex2,color))
        terrainMesh_withStand.VertexColors.Clear()
        for i in xrange(len(list(terrainMesh_withStand.Vertices))):
            terrainMesh_withStand.VertexColors.Add(System.Drawing.Color.FromArgb(255,255,255))  # dummy color due to error on line 637
        # end of fix for erro on line 637
        
        terrainMesh_Vertices_Point3f = list(terrainMesh.Vertices)
        terrainMesh_Vertices_Point3d = [Rhino.Geometry.Point3d(point3f)  for point3f in terrainMesh_Vertices_Point3f]
        
        terrainMesh_withStand_Vertices = list(terrainMesh_withStand.Vertices)
        terrainMesh_Point3dlist = Rhino.Collections.Point3dList(terrainMesh_Vertices_Point3d)
        
        for vertexIndex2,vertex2 in enumerate(terrainMesh_withStand_Vertices):
            vertexIndex1 = Rhino.Collections.Point3dList.ClosestIndexInList(terrainMesh_Point3dlist, vertex2)
            vertex1 = terrainMesh_Vertices_Point3d[vertexIndex1]
            distanceFrom_vertex1_to_vertex2 = vertex1.DistanceTo(vertex2)
            if distanceFrom_vertex1_to_vertex2 == 0:
                color = terrainMesh_Colors[vertexIndex1]
                success = terrainMesh_withStand.VertexColors.SetColor(vertexIndex2,color)
        
        del terrainMesh  # deletes instance of terrainMesh in this function. Instance of terrainMesh out of it, will not be deleted
        
        return terrainMesh_withStand
    else:
        # inputted _terrain has no stand
        return terrainMesh


def createTitleLegend(analysisType, terrainMesh_withWithoutStand, legendValues, analysisTypeLabel, northD, sunVector, hypsometricStrength, refine, unitSystem, legendUnit, legendPar):
    
    lb_visualization.calculateBB([terrainMesh_withWithoutStand])
    
    # extract data from "legendPar_" input
    if len(legendPar) == 0:
        lowB = "min"; highB = "max"; numSeg = None; customColors = []; legendBasePt = None; legendScale = 1; legendFont = "Verdana"; legendFontSize = None; legendBold = None; decimalPlaces = 2; removeLessThan = False
        legendPar = [lowB, highB, numSeg, customColors, legendBasePt, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan]
        if legendBasePt == None:
            legendBasePt = lb_visualization.BoundingBoxPar[0]
    lowB, highB, numSeg, customColors, legendBasePt, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    
    
    # title
    titleFontSize = ((lb_visualization.BoundingBoxPar[2]/10)/3) * legendScale * 1.2
    titleLabelOrigin = lb_visualization.BoundingBoxPar[5]
    titleLabelOrigin.Y = titleLabelOrigin.Y - lb_visualization.BoundingBoxPar[2]/15
    
    if (analysisType == 4):
        titleLabelText = "Terrain %s analysis\nsunVector: (%0.2f,%0.2f,%0.2f), hypsoStrength: %s\nnorth: %s, refine: %s" % (analysisTypeLabel, sunVector.X, sunVector.Y, sunVector.Z, str(hypsometricStrength), str(northD), refine)
    elif (analysisType == 5) or (analysisType == 6):
        titleLabelText = "Terrain %s analysis\nnorth: %s, refine: %s, for fixed cells window: 3x3" % (analysisTypeLabel, northD, refine)
    else:
        titleLabelText = "Terrain %s analysis\nnorth: %s, refine: %s" % (analysisTypeLabel, northD, refine)
    titleLabelMeshes = lb_visualization.text2srf([titleLabelText], [titleLabelOrigin], legendFont, titleFontSize*1.2, legendBold, None, 6)[0]
    titleLabelMesh = Rhino.Geometry.Mesh()
    for mesh in titleLabelMeshes:
        titleLabelMesh.Append(mesh)
    
    
    # legend
    if legendBasePt == None:
        legendBasePt = lb_visualization.BoundingBoxPar[0]
    legendSrfs, legendText, legendTextSrfs, textPt, textSize = lb_visualization.createLegend(legendValues, lowB, highB, numSeg, legendUnit, lb_visualization.BoundingBoxPar, legendBasePt, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
    # generate legend colors
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    # color legend surfaces
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    legendMeshes = [legendSrfs] + lb_preparation.flattenList(legendTextSrfs)
    legendMesh = Rhino.Geometry.Mesh()
    for mesh in legendMeshes:
        legendMesh.Append(mesh)
    
    # hide legendBasePt output
    ghenv.Component.Params.Output[5].Hidden = True
    
    gc.collect()
    
    return titleLabelMesh, legendMesh, legendBasePt


def bakingGrouping(analysisType, analysisTypeLabel, terrainMesh_withWithoutStand, titleLabelMesh, legendMesh, legendBasePt, originPt):
    
    if (analysisType == 4):
        # for Hillshade
        layerName = "%s_north=%s_refine=%s_sunVector=%0.2f,%0.2f,%0.2f_hypsoStrength=%s" % (analysisTypeLabel, northD, refine, sunVector.X, sunVector.Y, sunVector.Z, hypsometricStrength)
    else:
        layerName = "%s_north=%s_refine=%s" % (analysisTypeLabel, northD, refine)
    
    layerIndex, l = lb_visualization.setupLayers(layerName, "LADYBUG", "TERRAIN_ANALYSIS", "TERRAIN")
    
    attr = Rhino.DocObjects.ObjectAttributes()
    attr.LayerIndex = layerIndex
    attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
    attr.PlotColorSource = Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
    
    # bake analysedTerrain, title, originPt
    geometryIds = []
    geometry = [terrainMesh_withWithoutStand, titleLabelMesh, Rhino.Geometry.Point(originPt)]
    for obj in geometry:
        id = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj,attr)
        geometryIds.append(id)
    
    # bake legend
    legendIds = []
    geometry2 = [legendMesh] + [Rhino.Geometry.Point(legendBasePt)]
    for obj2 in geometry2:
        id2 = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj2,attr)
        legendIds.append(id2)
    
    # grouping of legend
    groupIndex = Rhino.RhinoDoc.ActiveDoc.Groups.Add(layerName + "_terrainAnalysis_" + analysisTypeLabel + "_legend_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex, legendIds)
    
    # grouping of analysedTerrain, title, originPt with legend
    groupIndex2 = Rhino.RhinoDoc.ActiveDoc.Groups.Add(layerName + "_terrainAnalysis_" + analysisTypeLabel + "_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex2, geometryIds + legendIds)


def printOutput(analysisType, analysisTypeLabel, originPt, originPtElevation, northD, sunVector, hypsometricStrength, refine, unitSystem):
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    resultsCompletedMsg = "Terrain analysis component results successfully completed %s!" % bakedOrNot
    printOutputMsg = \
    """
Input data:

Analysis type: %s (%s)
Origin: %s
Elevation (%s): %s
North (deg.): %s

SunVector: %s
Hypsometric strength: %s
Refine: %s
    """ % (analysisType, analysisTypeLabel, originPt, unitSystem, originPtElevation, northD, sunVector, hypsometricStrength, refine)
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_meshpreparation = sc.sticky["ladybug_Mesh"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        analysisType, analysisTypeLabel, originPt, originPtElevation, northRad, northD, sunVector, hypsometricStrength, refine, exportValues, unitSystem, unitConversionFactor, legendUnit, validInputData, printMsg = checkInputData(_analysisType, _terrain, _originPt, _elevation, north_, sunVector_, hypsoStrength_, refine_)
        if validInputData:
            createOutputDescriptions(analysisType, unitSystem)
            if _runIt:
                terrainMesh, values, legendValues = createAnalysedTerrainMesh(analysisType, _terrain, originPt, originPtElevation, northRad, sunVector, hypsometricStrength, refine, exportValues, unitConversionFactor)
                terrainMesh_withWithoutStand = joinTerrainStand_withTerrainMesh(_terrain, terrainMesh)
                titleLabelMesh, legendMesh, legendBasePt = createTitleLegend(analysisType, terrainMesh_withWithoutStand, legendValues, analysisTypeLabel, northD, sunVector, hypsometricStrength, refine, unitSystem, legendUnit, legendPar_)
                if bakeIt_: bakingGrouping(analysisType, analysisTypeLabel, terrainMesh_withWithoutStand, titleLabelMesh, legendMesh, legendBasePt, originPt)
                printOutput(analysisType, analysisTypeLabel, originPt, originPtElevation, northD, sunVector, hypsometricStrength, refine, unitSystem)
                analysedTerrain = terrainMesh_withWithoutStand; title = titleLabelMesh; legend = legendMesh; del legendValues;
            else:
                print "All inputs are ok. Please set \"_runIt\" to True, in order to run the Terrain analysis component"
        else:
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        printMsg = "You need a newer version of Ladybug to use this component.\n" + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag the Ladybug_Ladybug component " + \
            "into the canvas and try again."
        print printMsg
else:
    printMsg = "First please let the Ladybug fly..."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)