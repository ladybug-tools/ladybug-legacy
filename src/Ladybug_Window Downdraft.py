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
The model used in this component comes from physical measurements of window downdraft that were further validated using several CFD experiments.  Ther are published in these papers:
_
Heiselberg, P. (1994). Draft Risk from Cold Vertical Surfaces. Building and Environment, 29: 297-301.
Manz, H. and Frank, T. (2003). "Analysis of Thermal Comfort near Cold Vertical Surfaces by Means of Computational Fluid Dynamics." Indoor Built Environment. 13: 233-242.
-
Provided by Ladybug 0.0.63
    
    Args:
        _testPts: The test points at which downdraft conditions will be evaluated.
        _windowSrfs: Breps or Surfaces representing the window surfaces off of which downdraft flows.
        _winSrfTemp: A number representing the surface temperature of the windows in degrees Celcius.
        _airTemp: A number representing the air temperature of the room in degrees Celcius.
        defaultVeloc_: A number in m/s that represents the speed of the air that is not in the downdraft. The default is set to 0.05 m/s.
        _runIt: Set to 'True' to run the component and claculate downdraft conditions.
     Returns:
        draftAirTemp: The air temperature of the draft 10 cm off of the floor in degrees Celcius.
        draftAirVeloc: The velocity of the draft 10 cm off of the floor in m/s.
        airFlowPlanes: The planes in which the governing downdraft is flowing.
"""

ghenv.Component.Name = "Ladybug_Window Downdraft"
ghenv.Component.NickName = 'downDraft'
ghenv.Component.Message = 'VER 0.0.63\nDEC_13_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import math
import Rhino as rc
import scriptcontext as sc
import copy
import System.Threading.Tasks as tasks
import Grasshopper.Kernel as gh
import copy

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
    return 0.083*(math.sqrt(deltaT*windowHgt))

def velMaxMid(dist, deltaT, windowHgt):
    return 0.143*((math.sqrt(deltaT*windowHgt))/(dist+1.32))

def velMaxFar(deltaT, windowHgt):
    return 0.043*(math.sqrt(deltaT*windowHgt))

def main(testPts, windowSrfs, winSrfTemp, airTemp, defaultVeloc = 0.05):
    # Check Rhino model units.
    conversionFactor = lb_preparation.checkUnits()
    
    # Get the normal vectors of all the window surfaces.
    normalVecs = []
    for srf in windowSrfs:
        normVec = getSrfCenPtandNormal(srf)
        normalVecs.append(normVec)
    
    # See if any of the test points are in the wake of the downdraft.
    ptIntList = []
    for pt in testPts:
        ptIntList.append(None)
    
    def intRays(i):
        #Create the rays to be projected from each point.
        pointIntersectDict = {}
        for srfCount, srf in enumerate(windowSrfs):
            closestPt = srf.ClosestPoint(testPts[i])
            srfLine = rc.Geometry.Line(testPts[i], closestPt)
            distToSrf = srfLine.Length
            srfVec = rc.Geometry.Vector3d(closestPt.X-testPts[i].X, closestPt.Y-testPts[i].Y, closestPt.Z-testPts[i].Z)
            angle2Srf = math.degrees(rc.Geometry.Vector3d.VectorAngle(normalVecs[srfCount], srfVec))
            if abs(angle2Srf) > 90:
                angFactor = 0
            else:
                angFactor = (90-abs(angle2Srf))/90
            
            pointIntersectDict[srfCount] = [distToSrf*conversionFactor, srfVec, angle2Srf, angFactor]
        
        ptIntList[i] = pointIntersectDict
    
    for count in range(len(testPts)):
        intRays(count)
    
    # For the points that are in the wake, find the height of the glazing at the point's downdraft location.
    airFlowPlanes = []
    
    for ptCount, ptDict in enumerate(ptIntList):
        for srf in ptDict.keys():
            intSrf = windowSrfs[srf]
            directVec = ptDict[srf][1]
            directAng = ptDict[srf][2]
            if directAng < 90:
                normalPlaneVec = rc.Geometry.Vector3d(directVec.X, directVec.Y, 0)
                intPlane = rc.Geometry.Plane(testPts[ptCount], normalPlaneVec)
                intPlane.Rotate((math.pi/2)+sc.doc.ModelAngleToleranceRadians, rc.Geometry.Vector3d.ZAxis)
                airFlowPlanes.append(intPlane)
                try:
                    intCurve = rc.Geometry.Intersect.Intersection.BrepPlane(intSrf, intPlane, sc.doc.ModelAbsoluteTolerance)[1][0]
                    startPtZ = intCurve.PointAtStart.Z
                    endPtZ = intCurve.PointAtEnd.Z
                    glzHeight  = (abs(endPtZ-startPtZ))*conversionFactor
                    ptDict[srf].append(glzHeight)
                except:
                    srfBB = intSrf.GetBoundingBox(True)
                    glzHeight = (srfBB.Max.Z - srfBB.Min.Z)*conversionFactor
                    ptDict[srf].append(glzHeight)
            else:
                airFlowPlanes.append(None)
                ptDict[srf].append(1)
    
    # Set a "spread factor" to ensure conservation of mass in the flow of air to the sides
    spreadFac = .97
    
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
            angFac = ptDict[srf][3]
            windowHgt = ptDict[srf][4]
            if dist < 0.4: windSpd = velMaxClose(glassAirDelta, windowHgt)
            elif dist < 2: windSpd = velMaxMid(dist, glassAirDelta, windowHgt)
            else: windSpd = velMaxFar(glassAirDelta, windowHgt)
            floorAirTemp = calcFloorAirTemp(airTemp, dist, glassAirDelta)
            
            ptVelLists[ptCount].append((windSpd*((angFac/(1/spreadFac))+(1-spreadFac))))
            ptTemplists[ptCount].append(airTemp-((airTemp-floorAirTemp)*((angFac/(1/spreadFac))+(1-spreadFac))))
    
    # Make final lists that just have the larger of the downdraft terms.
    draftSpeeds = []
    draftAirTemps = []
    for lCount, ptList in enumerate(ptVelLists):
        if len(ptList) == 0:
            draftSpeeds.append(defaultVeloc)
            draftAirTemps.append(airTemp)
        else:
            draftSpeeds.append(max(ptList))
            draftAirTemps.append(min(ptTemplists[lCount]))
    
    
    return draftSpeeds, draftAirTemps, airFlowPlanes

#If Ladybug is not flying or is an older version, give a warning.
initCheck = True

#Ladybug check.
w = gh.GH_RuntimeMessageLevel.Warning
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
    draftAirVeloc, draftAirTemp, airFlowPlanes = main(_testPts, _windowSrfs, _winSrfTemp, _airTemp, defaultVeloc_)

ghenv.Component.Params.Output[3].Hidden= True