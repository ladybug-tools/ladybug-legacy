# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to compute the floor-level downdraft air temperature and velocity at a given set of points that are located close to a cold surface such as a window.  The draft conditions produced by this model are assumed to be 10 cm off of the floor.
_
The model used in this component comes from physical measurements of window downdraft conducted and published by Heiselberg.
-
Provided by Ladybug 0.0.63
    
    Args:
        _draftAirTemp: The air temperature of the draft in degrees Celcius.
        defaultVeloc_: A number in m/s that represents the speed of the air that is not in the downdraft. The default is set to 0.05 m/s.
     Returns:
        draftAirTemp: The air temperature of the draft 10 cm off of the floor in degrees Celcius.
        draftAirVeloc: The velocity of the draft 10 cm off of the floor in m/s.
"""

ghenv.Component.Name = "Ladybug_Window Downdraft"
ghenv.Component.NickName = 'downDraft'
ghenv.Component.Message = 'VER 0.0.63\nAUG_12_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import math
import Rhino as rc
import scriptcontext as sc
import copy
import System.Threading.Tasks as tasks

def getSrfCenPtandNormal(surface):
    brepFace = surface.Faces[0]
    if brepFace.IsPlanar and brepFace.IsSurface:
        u_domain = brepFace.Domain(0)
        v_domain = brepFace.Domain(1)
        centerU = (u_domain.Min + u_domain.Max)/2
        centerV = (v_domain.Min + v_domain.Max)/2
        
        centerPt = brepFace.PointAt(centerU, centerV)
        normalVector = brepFace.NormalAt(centerU, centerV)
    else:
        centroid = rc.Geometry.AreaMassProperties.Compute(brepFace).Centroid
        uv = brepFace.ClosestPoint(centroid)
        centerPt = brepFace.PointAt(uv[1], uv[2])
        normalVector = brepFace.NormalAt(uv[1], uv[2])
    
    return normalVector


def calcFloorAirTemp(airTemp, dist, deltaT):
    return airTemp - ((0.3-(0.034*dist))*deltaT)

def velMaxClose(deltaT, windowHgt):
    return 0.055*(math.sqrt(deltaT*windowHgt))

def velMaxMid(dist, deltaT, windowHgt):
    return 0.095*((math.sqrt(deltaT*windowHgt))/(dist+1.32))

def velMaxFar(deltaT, windowHgt):
    return 0.028*(math.sqrt(deltaT*windowHgt))

def main(testPts, windowSrfs, winSrfTemp, airTemp, defaultVeloc = 0.05, parallel = False):
    # Check Rhino model units.
    conversionFactor = lb_preparation.checkUnits()
    
    # Get the normal vectors of all the window surfaces.
    normalVecs = []
    revNormVecs = []
    winMeshes = []
    for srf in windowSrfs:
        normVec = getSrfCenPtandNormal(srf)
        normalVecs.append(normVec)
        revVec = copy.copy(normVec)
        revVec.Reverse()
        revNormVecs.append(revVec)
        winMesh = rc.Geometry.Mesh.CreateFromBrep(srf, rc.Geometry.MeshingParameters.Coarse)[0]
        winMeshes.append(winMesh)
    
    # See if any of the test points are in the wake of the downdraft.
    ptIntList = []
    for pt in testPts:
        ptIntList.append(None)
    
    def intRays(i):
        #Create the rays to be projected from each point.
        pointIntersectDict = {}
        pointRays = []
        pointRaysRev = []
        for vec in normalVecs: pointRays.append(rc.Geometry.Ray3d(testPts[i], vec))
        for vec in revNormVecs: pointRaysRev.append(rc.Geometry.Ray3d(testPts[i], vec))
        
        #Perform the intersection of the rays with the mesh.
        for rayCount, ray in enumerate(pointRays):
            intersect = rc.Geometry.Intersect.Intersection.MeshRay(winMeshes[rayCount], ray)
            if intersect != -1:
                pointIntersectDict[rayCount] = [intersect*conversionFactor, ray]
        for rayCount, ray in enumerate(pointRaysRev):
            intersect = rc.Geometry.Intersect.Intersection.MeshRay(winMeshes[rayCount], ray)
            if intersect != -1:
                pointIntersectDict[rayCount] = [intersect*conversionFactor, ray]
        
        ptIntList[i] = pointIntersectDict
    
    if parallel == True:
        tasks.Parallel.ForEach(range(len(testPts)), intRays)
    else:
        for count in range(len(testPts)):
            intRays(count)
    
    # For the points that are in the wake, find the height of the glazing at the point's downdraft location.
    for ptCount, ptDict in enumerate(ptIntList):
        for srf in ptDict.keys():
            intSrf = windowSrfs[srf]
            directVec = ptDict[srf][1].Direction
            normalPlaneVec = rc.Geometry.Vector3d(directVec.Y, directVec.X, 0)
            intPlane = rc.Geometry.Plane(testPts[ptCount], normalPlaneVec)
            intCurve = rc.Geometry.Intersect.Intersection.BrepPlane(intSrf, intPlane, sc.doc.ModelAbsoluteTolerance)[1][0]
            startPtZ = intCurve.PointAtStart.Z
            endPtZ = intCurve.PointAtEnd.Z
            glzHeight  = (abs(endPtZ-startPtZ))*conversionFactor
            ptDict[srf].append(glzHeight)
    
    # Compute the temperature difference.
    glassAirDelta = airTemp - winSrfTemp
    
    # Compute the downdraft conditions for each point.
    ptVelLists = []
    ptTemplists = []
    for ptCount, ptDict in enumerate(ptIntList):
        ptVelLists.append([])
        ptTemplists.append([])
        for srf in ptDict.keys():
            dist = ptDict[srf][0]
            windowHgt = ptDict[srf][2]
            if dist < 0.4: windSpd = velMaxClose(glassAirDelta, windowHgt)
            elif dist < 2: windSpd = velMaxMid(dist, glassAirDelta, windowHgt)
            else: windSpd = velMaxFar(glassAirDelta, windowHgt)
            floorAirTemp = calcFloorAirTemp(airTemp, dist, glassAirDelta)
            
            ptVelLists[ptCount].append(windSpd)
            ptTemplists[ptCount].append(floorAirTemp)
    
    # Make final lists that just have the larger of the downdraft terms.
    draftSpeeds = []
    draftAirTemps = []
    for lCount, ptList in enumerate(ptVelLists):
        if len(ptList) == 0:
            draftSpeeds.append(defaultVeloc)
            draftAirTemps.append(airTemp)
        elif len(ptList) == 1:
            draftSpeeds.append(ptList[0])
            draftAirTemps.append(ptTemplists[lCount][0])
        else:
            draftSpeeds.append(max(ptList))
            draftAirTemps.append(min(ptTemplists[lCount]))
    
    
    return draftSpeeds, draftAirTemps

#If Ladybug is not flying or is an older version, give a warning.
initCheck = True

#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): initCheck = False
        lb_preparation = sc.sticky["ladybug_Preparation"]()
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)




if initCheck == True and _testPts[0] != None and _windowSrfs[0] != None and _runIt == True:
    draftAirVeloc, draftAirTemp = main(_testPts, _windowSrfs, _winSrfTemp, _airTemp, defaultVeloc_, parallel_)
