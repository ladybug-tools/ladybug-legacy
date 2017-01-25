# flow paths
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Djordje Spasic <djordjedspasic@gmail.com>
# Inspiration for the component came from the Sonic component: Flow, by Carson Smuts
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
Use this component to perform the analysis of gravitational water flow.
It can be a useful indicator of drainage analysis of a building, terrain, landscape or any other sort of geometry.
-
Component based on:

"Finding the downhill direction vector when given a plane defined by a normal and a point", stackoverflow.com topic by Zach Helms, 2016
http://stackoverflow.com/q/14369233/3137724
-
Provided by Ladybug 0.0.63
    
    input:
        _geometry: A surface and/or polysurface and/or mesh for which you would like to conduct the flow path analysis. That can be a building, terrain, landscape or any other sort of geometry.
        numOfInitialPts_: Number of initial points.
                          Each flowpath has a starting point - a point where a rain hit the ground. numOfInitialPts_ input represents the number of these points, therefor representing the number of flowpaths.
                          -
                          If nothing supplied, numOfInitialPts_ input will be set to 100 (initial points and flowpaths)
        initialPtsSpread_: Initial points spread type - choose one of the two types:
                           -
                           0 - Rectangular grid (flow paths will start as a regular grid of points)
                           1 - Random (flow paths will start as a random group of points)
                           -
                           If nothing supplied, initialPtsSpread_ input will be set to 1 (Random).
        stepSize_: Step size of each of the flow paths.
                   Step size can singificantly affect the final flow paths disposition. For smaller scale objects, it is advisable to use smaller step sizes (up to 1). For larger scale objects (terrains with sparse resolution), step size can be increased to more than 1.
                   -
                   If nothing supplied, stepSize_ input will be set to 1 (Rhino documents units: m, ft, in...).
                   -
                   In Rhino document units.
        flowPathsType_: Choose one of the two flow path types:
                        -
                        0 - Polyline
                        1 - Curves
                        -
                        If nothing supplied, flowPathsType_ input will be set to 0 (Polylines).
        bakeIt_: Set to "True" to bake the flowpaths geometry into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        flowPaths: A list of polylines/curves representing the flow paths and directions on the given _geometry input.
        title: Title geometry with information about the chosen inputs
        titleOrigin: Title base point, which can be used to move the "title" geometry with grasshopper's "Move" component.
                     -
                     Connect this output to a Grasshopper's "Point" parameter in order to preview the point in the Rhino scene.
"""

ghenv.Component.Name = "Ladybug_Flow Paths"
ghenv.Component.NickName = "FlowPaths"
ghenv.Component.Message = "VER 0.0.63\nSEP_30_2016"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import ghpythonlib.components as ghc
import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System
import Rhino
import time
import math
import gc


def checkInputData(geometryIds, numOfInitialPts, initialPtsSpread, stepSize, flowPathsType):
    
    # check inputs
    if len(geometryIds) == 0:
        geometryMesh = numOfInitialPts = initialPtsSpread = initialPtsSpreadLabel = stepSize = flowPathsType = flowPathsTypeLabel = None
        validInputData = False
        printMsg = "\"_geometry\" input is empty.\n" + \
                   "Please supply a surface and/or polysurface and/or mesh for which you would like to conduct the flow path analysis (that can be a building, terrain, landscape or any other sort of geometry)."
        
        return geometryMesh, numOfInitialPts, initialPtsSpread, initialPtsSpreadLabel, stepSize, flowPathsType, flowPathsTypeLabel, validInputData, printMsg
    
    
    if (numOfInitialPts == None):
        numOfInitialPts = 100  # default
    elif (numOfInitialPts < 2):
        print "\"numOfInitialPts_\" input can not be less than 2.\n" + \
              "\"numOfInitialPts_\" input set to 2."
        numOfInitialPts = 2
    
    
    if (initialPtsSpread == None):
        initialPtsSpread = 1  # default (Random)
        initialPtsSpreadLabel = "Random"
    if (initialPtsSpread == 0):
        initialPtsSpreadLabel = "Rectangular grid"
    elif (initialPtsSpread == 1):
        initialPtsSpreadLabel = "Random"
    else:
        print "\"initialPtsSpread_\" input only accepts values: 0 (Rectangular grid) and 1 (Random).\n" + \
              "\"initialPtsSpread_\" input set to 1 (Random)."
        initialPtsSpread = 1
        initialPtsSpreadLabel = "Random"
    
    
    if (stepSize == None):
        stepSize = 1  # default (in rhino document units)
    elif (stepSize < 0.01):
        print "\"stepSize_\" input only accepts values larger 0.01 rhino document units (meters, feet, inches...).\n" + \
              "\"stepSize_\" input set to 1 rhino document unit."
        stepSize = 1
    
    
    if (flowPathsType == None):
        flowPathsType = 0  # default (polylines)
        flowPathsTypeLabel = "Polylines"
    if (flowPathsType == 0):
        flowPathsTypeLabel = "Polylines"
    elif (flowPathsType == 1):
        flowPathsTypeLabel = "Curves"
    else:
        print "\"flowPathsType_\" input only accepts values: 0 (Polylines) and 1 (Curves).\n" + \
              "\"flowPathsType_\" input set to 0 (Polylines)."
        flowPathsType = 0
        flowPathsTypeLabel = "Polylines"
    
    
    
    # create a geometryMesh from _geometry inputs
    geometryMesh = Rhino.Geometry.Mesh()  # joined mesh of all geometry supplied into the "_geometry" input
    
    geometryObjs = [rs.coercegeometry(geometryId) for geometryId in geometryIds]
    for geometryObj in geometryObjs:
        if isinstance(geometryObj, Rhino.Geometry.Mesh):
            geometryMesh.Append(geometryObj)
        elif isinstance(geometryObj, Rhino.Geometry.Brep):
            meshParam = Rhino.Geometry.MeshingParameters()
            #meshParam.MaximumEdgeLength = maxEdgeLength_  # more beneficial for drainage area per flow direction
            meshParam.SimplePlanes = True
            meshesFromBrep = Rhino.Geometry.Mesh.CreateFromBrep(geometryObj, meshParam)
            for mesh in meshesFromBrep:
                geometryMesh.Append(mesh)
    
    if geometryMesh.IsValid == True:
        # a brep and/or a mesh supplied to "_geometry" input
        pass
    else:
        # neither mesh nor brep object(s) have been supplied into the "_geometry" input
        geometryMesh = numOfInitialPts = initialPtsSpread = initialPtsSpreadLabel = stepSize = flowPathsType = flowPathsTypeLabel = None
        validInputData = False
        printMsg = "The data you supplied to the \"_geometry\" input is neither a surface and/or polysurface and/or mesh.\n" + \
                   "Please input some (or all) of these types of data to the \"_geometry\" input."
        
        return geometryMesh, numOfInitialPts, initialPtsSpread, initialPtsSpreadLabel, stepSize, flowPathsType, flowPathsTypeLabel, validInputData, printMsg
    
    validInputData = True
    printMsg = "ok"
    
    return geometryMesh, numOfInitialPts, initialPtsSpread, initialPtsSpreadLabel, stepSize, flowPathsType, flowPathsTypeLabel, validInputData, printMsg


def calculateFlowPaths(geometryMesh, initialPt, flowPathsType):
    
    flowPathPts = []
    previousPt = initialPt
    for i in range(5000):
        meshPtOnMesh = geometryMesh.ClosestMeshPoint(previousPt, 0)
        if i == 0:
            previousPt = meshPtOnMesh.Point
            flowPathPts.append(previousPt)
        
        meshNormal = geometryMesh.NormalAt(meshPtOnMesh)
        rotatedMeshNormal = Rhino.Geometry.Vector3d.CrossProduct(Rhino.Geometry.Vector3d.CrossProduct(meshNormal, Rhino.Geometry.Vector3d(0,0,-1)) , meshNormal)
        rotatedMeshNormal.Unitize()
        
        pt2 = meshPtOnMesh.Point + rotatedMeshNormal*stepSize
        
        maximumDistance = 0
        meshPtOnMesh2 = geometryMesh.ClosestMeshPoint(pt2, maximumDistance)
        if previousPt.EpsilonEquals(meshPtOnMesh2.Point, 0.0001):
            # stop the creation of a list of points if the last point coincides with the point before it
            break
        
        previousPt = meshPtOnMesh2.Point
        flowPathPts.append(previousPt)
    
    
    if len(flowPathPts) > 1:  # fix for raising the "Object reference not set to an instance of an object" error for len(polylinePts) == 1
        if flowPathsType == 0:
            flowPath = Rhino.Geometry.Polyline(flowPathPts)
        elif flowPathsType == 1:
            flowPath = Rhino.Geometry.Curve.CreateInterpolatedCurve(flowPathPts, 3)
        del flowPathPts
        
        return flowPath
    
    else:
        del flowPathPts
        
        return None


def main(geometryMesh, numOfInitialPts, initialPtsSpread, flowPathsType):
    
    # create "initialPts"
    bb = geometryMesh.GetBoundingBox(False)
    upperBBsurface = bb.ToBrep().Faces[5].DuplicateSurface()
    
    initialPts = []
    bbUpperFacePts = []  # remains empty for initialPtsSpread == 0
    if initialPtsSpread == 0:
        # calculate Udivisions, Vdivisions according to approximatelly numOfInitialPts
        upperBBsurface_edge1 = bb.GetEdges()[4]
        upperBBsurface_edge2 = bb.GetEdges()[5]
        U_V_directions_ratio = upperBBsurface_edge1.Length / upperBBsurface_edge2.Length
        if U_V_directions_ratio < 1:
            # if upperBBsurface_edge1 < upperBBsurface_edge2
            U_V_directions_ratio = upperBBsurface_edge2.Length / upperBBsurface_edge1.Length
        initial_Udivisions = round(math.sqrt(U_V_directions_ratio*numOfInitialPts), 0)
        Vdivisions = round(numOfInitialPts/initial_Udivisions, 0)
        Udivisions = round(numOfInitialPts/Vdivisions, 0) # final_Udivisions
        
        # divide the upper face of the geometryMesh bounding box with points according to Udivisions, Vdivisions
        domainUV = Rhino.Geometry.Interval(0,1)
        upperBBsurface.SetDomain(0, domainUV)
        upperBBsurface.SetDomain(1, domainUV)
        uDomain = upperBBsurface.Domain(0)
        vDomain = upperBBsurface.Domain(1)
        
        uStep = uDomain.T1/(Udivisions-1)
        vStep = vDomain.T1/(Vdivisions-1)
        
        for i in xrange(Udivisions):
            u = i * uStep
            for k in xrange(Vdivisions):
                v = k * vStep
                bbUpperFacePt = upperBBsurface.PointAt(u,v)
                ray = Rhino.Geometry.Ray3d(bbUpperFacePt, Rhino.Geometry.Vector3d(0,0,-1))
                rayIntersectParam = Rhino.Geometry.Intersect.Intersection.MeshRay(geometryMesh, ray)
                if rayIntersectParam > 0:
                    initialPt = ray.PointAt(rayIntersectParam)
                    initialPts.append(initialPt)
        # end of create "initialPts"
    
    elif initialPtsSpread == 1:
        seed = 0
        bbUpperFacePts = ghc.PopulateGeometry(upperBBsurface, numOfInitialPts, seed)
        for bbUpperFacePt in bbUpperFacePts:
            ray = Rhino.Geometry.Ray3d(bbUpperFacePt, Rhino.Geometry.Vector3d(0,0,-1))
            rayIntersectParam = Rhino.Geometry.Intersect.Intersection.MeshRay(geometryMesh, ray)
            if rayIntersectParam > 0:
                initialPt = ray.PointAt(rayIntersectParam)
                initialPts.append(initialPt)
    
    
    # calculate the flow lines
    flowPaths = []
    for initialPt in initialPts:
        flowPath = calculateFlowPaths(geometryMesh, initialPt, flowPathsType)
        if flowPath != None:
            flowPaths.append(flowPath)
    
    del initialPts
    del bbUpperFacePts
    gc.collect()
    
    return flowPaths


def createTitle(geometryMesh, numOfInitialPts, initialPtsSpreadLabel, stepSize, flowPathsTypeLabel):
    
    lb_visualization.calculateBB([geometryMesh])
    
    # title
    titleFontSize = ((lb_visualization.BoundingBoxPar[2]/10)/3) * 1.2
    titleLabelOrigin = lb_visualization.BoundingBoxPar[5]
    titleLabelOrigin.Y = titleLabelOrigin.Y - lb_visualization.BoundingBoxPar[2]/15
    titleLabelText = "Flow paths analysis\n" + \
                     "numOfInitialPts: %s, initialPtsSpread: %s\nstepSize: %s, flowPathsType: %s" % (numOfInitialPts, initialPtsSpreadLabel, stepSize, flowPathsTypeLabel)
    legendFont = "Verdana"; legendBold = False
    titleLabelMeshes = lb_visualization.text2srf([titleLabelText], [titleLabelOrigin], legendFont, titleFontSize*1.2, legendBold, None, 6)[0]
    titleLabelMesh = Rhino.Geometry.Mesh()
    for mesh in titleLabelMeshes:
        titleLabelMesh.Append(mesh)
    
    # hide titleOrigin output
    ghenv.Component.Params.Output[3].Hidden = True
    
    return titleLabelMesh, titleLabelOrigin


def bakingGrouping(numOfInitialPts, initialPtsSpreadLabel, stepSize, flowPathsTypeLabel, flowPaths, titleLabelMesh):
    
    layerName = "numOfInitialPts=%s_initialPtsSpread=%s_stepSize=%s_flowPathsType=%s" % (numOfInitialPts, initialPtsSpreadLabel, stepSize, flowPathsTypeLabel)
    
    layerIndex, l = lb_visualization.setupLayers(layerName, "LADYBUG", "ANALYSIS", "FLOWPATH")
    
    attr = Rhino.DocObjects.ObjectAttributes()
    attr.LayerIndex = layerIndex
    attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
    attr.PlotColorSource = Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
    
    # bake analysedTerrain, title, originPt
    flowPathsIds = []
    geometry = [flowPath.ToNurbsCurve()  for flowPath in flowPaths]
    for obj in geometry:
        id = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj,attr)
        flowPathsIds.append(id)
    
    # bake title
    titleIds = []
    geometry2 = [titleLabelMesh]
    for obj2 in geometry2:
        id2 = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj2,attr)
        titleIds.append(id2)
    
    # grouping of flowPaths
    groupIndex = Rhino.RhinoDoc.ActiveDoc.Groups.Add("flowPaths_" + layerName + "_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex, flowPathsIds)


def printOutput(numOfInitialPts, initialPtsSpread, initialPtsSpreadLabel, stepSize, flowPathsType, flowPathsTypeLabel):
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    resultsCompletedMsg = "Flow paths component results successfully completed %s!" % bakedOrNot
    printOutputMsg = \
    """
Input data:

Number of initial points: %s
Initial points spread: %s (%s)
Step size: %s
Flow paths type: %s (%s)
    """ % (numOfInitialPts, initialPtsSpread, initialPtsSpreadLabel, stepSize, flowPathsType, flowPathsTypeLabel)
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        geometryMesh, numOfInitialPts, initialPtsSpread, initialPtsSpreadLabel, stepSize, flowPathsType, flowPathsTypeLabel, validInputData, printMsg = checkInputData(_geometry, numOfInitialPts_, initialPtsSpread_, stepSize_, flowPathsType_)
        if validInputData:
            if _runIt:
                flowPaths = main(geometryMesh, numOfInitialPts, initialPtsSpread, flowPathsType)
                titleLabelMesh, titleLabelOrigin = createTitle(geometryMesh, numOfInitialPts, initialPtsSpreadLabel, stepSize, flowPathsTypeLabel)
                if bakeIt_: bakingGrouping(numOfInitialPts, initialPtsSpreadLabel, stepSize, flowPathsTypeLabel, flowPaths, titleLabelMesh)
                printOutput(numOfInitialPts, initialPtsSpread, initialPtsSpreadLabel, stepSize, flowPathsType, flowPathsTypeLabel)
                title = titleLabelMesh; titleOrigin = titleLabelOrigin
            else:
                print "All inputs are ok. Please set \"_runIt\" to True, in order to run the Flow paths component"
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