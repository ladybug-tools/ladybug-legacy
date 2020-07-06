# FacadeSelector
# Copyright (c) 2017, Abraham Yezioro <ayez@technion.ac.il>
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
# See <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Select surfaces based on orientation.
-
Provided by Ladybug 0.0.69
    
    Args:
        _geometry: Geometry for which facades will be selected.  Geometry must be either a Brep, a Mesh or a list of Breps or Meshes.
        _maxUpDecAngle_: Maximum normal declination angle from ZAxis that should be still considerd up
        _maxDownDecAngle_: Maximum normal declination angle from ZAxis that should be still considerd down
        _orientation_: A number between 0 and 8 for desired orientation. 0 = North, 1 = NE, 2 = East, ... 7 = NW, 8 = Roof. Default is South.
        _plusDeg_: Angle in degrees for deviation from _orientation. Default = 23. For selecting all vertical orientations give 359 for this input and 0 for the _minusDeg_ (or viceversa)
        _minusDeg_: Angle in degrees for deviation from _orientation. Default = 23. For selecting all vertical orientations give 359 for this input and 0 for the _plusDeg_ (or viceversa)
    Returns:
        readMe!: ...
        selFaces: Selected faces/surfaces
"""

ghenv.Component.Name = "Ladybug_Separate By Normal"
ghenv.Component.NickName = 'separate By Normal'
ghenv.Component.Message = 'VER 0.0.69\nJUL_07_2020'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "LB-Legacy"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import rhinoscriptsyntax as rs
import math
import Rhino as rc
import scriptcontext as sc

import Grasshopper.Kernel as gh
w = gh.GH_RuntimeMessageLevel.Warning

def checkInputs():
    checkData = False
    roofOrient  = False
    floorOrient = False
    
    if _geometry != None:
        if _maxUpDecAngle_ == None: 
            maxUpDecAngle   = 30
        else: 
            maxUpDecAngle   = _maxUpDecAngle_
        if _maxDownDecAngle_ == None:
            maxDownDecAngle = 30
        else: 
            maxDownDecAngle = _maxDownDecAngle_
    
        geometry = _geometry
        checkData = True
        
        if _orientation_ != None:
            ori = int(_orientation_)
            sin45 = math.sin(math.radians(45))
            cos45 = math.cos(math.radians(45))
            if ori >= 0 and ori <= 9:
                if   ori == 0: orient = rc.Geometry.Vector3d( 0,          1, 0)    # N 
                elif ori == 1: orient = rc.Geometry.Vector3d( sin45,  cos45, 0)    # NE
                elif ori == 2: orient = rc.Geometry.Vector3d( 1,          0, 0)    # E
                elif ori == 3: orient = rc.Geometry.Vector3d( sin45, -cos45, 0)    # SE
                elif ori == 4: orient = rc.Geometry.Vector3d( 0,         -1, 0)    # S
                elif ori == 5: orient = rc.Geometry.Vector3d(-sin45, -cos45, 0)    # SW
                elif ori == 6: orient = rc.Geometry.Vector3d(-1,          0, 0)    # W
                elif ori == 7: orient = rc.Geometry.Vector3d( -sin45, cos45, 0)    # NW
                elif ori == 8: 
                    orient =            rc.Geometry.Vector3d( 0,          0, 1)    # ROOF    #**
                    roofOrient = True
                elif ori == 9: 
                    orient =            rc.Geometry.Vector3d( 0,          0, -1)   # FLOOR    #**
                    floorOrient = True
                #print 'orient ', orient
            else:
                #orient = None
                warning = "_orientation_ must be between 0 and 9."
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                #print 'Orient ', orient
                return -1
                #return None, None, None, None, None, None, None, None, None
        else:
            orient = rc.Geometry.Vector3d(0, -1, 0)
    
        if _plusDeg_ != None:
            plusDeg = _plusDeg_
        else:
            plusDeg = 23.
            
        if _minusDeg_ != None:
            minusDeg = _minusDeg_
        else:
            minusDeg = 23.
    else:
        warning = "No geometry supplied"
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
        #return None, None, None, None, None, None, None, None, None
    #print 'Orient ', orient
    return checkData, geometry, roofOrient, floorOrient, orient, plusDeg, minusDeg, maxUpDecAngle, maxDownDecAngle


def getSrfCenPtandNormal(surface):
    surface  = surface.Faces[0]
    u_domain = surface.Domain(0)
    v_domain = surface.Domain(1)
    centerU  = (u_domain.Min + u_domain.Max)/2
    centerV  = (v_domain.Min + v_domain.Max)/2
    
    centerPt = surface.PointAt(centerU, centerV)
    normalVector = surface.NormalAt(centerU, centerV)
    
    normalVector.Unitize()
    return centerPt, normalVector

###########################################################################################
#Check the inputs.
##selFaces = []
#checkData, geometry, roofOrient, floorOrient, orient, plusDeg, minusDeg, maximumRoofAngle, maximumFloorAngle = checkInputs()
results = checkInputs()
if results != -1:
    checkData         = results[0]
    geometry          = results[1]
    roofOrient        = results[2]
    floorOrient       = results[3]
    orient            = results[4]
    plusDeg           = results[5]
    minusDeg          = results[6]
    maximumRoofAngle  = results[7]
    maximumFloorAngle = results[8] 
    
    #If the inputs are good, GO and do your think
    if checkData == True:
        pass
        
        selFaces = []
        if roofOrient == False and floorOrient == False:
            vNorth   = rc.Geometry.Vector3d(0, 1, 0)
            v2       = rc.Geometry.Vector3d(orient[0],  orient[1], 0)
            DB       = rc.Geometry.Vector3d.Multiply(vNorth, v2)
        
            CP = math.degrees(math.acos(DB))
            aDB = math.degrees(math.acos(DB))
            
            aTanOrient = round( math.degrees( math.atan2(1, 0) - math.atan2(orient[1], orient[0]) ) )
            if aTanOrient < 0: aTanOrient +=360
            aTanOrientPlus  = aTanOrient + plusDeg
            aTanOrientMinus = aTanOrient - minusDeg
            if aTanOrientPlus  <    0.: aTanOrientPlus  +=360.
            if aTanOrientPlus  >= 360.: aTanOrientPlus  -=360.
            if aTanOrientMinus <    0.: aTanOrientMinus +=360.
            if aTanOrientMinus >  360.: aTanOrientMinus +=360.
            
            for i, geog in enumerate (geometry):
                for cnt in range(geog.Faces.Count):
                    face = geog.Faces[cnt].DuplicateFace(False)
                    #print i, geog, cnt, face

                    centerPt, normalVector = getSrfCenPtandNormal(face)
                    dblDotProductNorthrient = rc.Geometry.Vector3d.Multiply(vNorth, orient)
                    dblDotProduct           = rc.Geometry.Vector3d.Multiply(orient, normalVector)
                    angArcCos               = math.degrees(math.acos(dblDotProduct))
                    
                    vX = 0
                    vY = 1
                    uXF = normalVector[0]
                    uYF = normalVector[1]
                    uZF = round(normalVector[2])
                    aTanFace = round( math.degrees( math.atan2(vY, vX) - math.atan2(uYF, uXF) ) )
                    if aTanFace < 0: aTanFace += 360
                    aTanFaceInv = aTanFace
                    if aTanOrientMinus > aTanOrientPlus:
                        aTanFaceInv = aTanFace + (360 - aTanFace)
                        if (aTanFace <= aTanOrientPlus  and aTanFaceInv >= aTanOrientMinus and (uZF == 0.0)) or \
                           (aTanFace >= aTanOrientMinus and aTanFaceInv >= aTanOrientPlus  and (uZF == 0.0)): 
                            selFaces.append(face)
                    else:
                        FaceRad     = math.radians(aTanFace)
                        if (aTanFace    <= aTanOrientPlus  and aTanFace    >= aTanOrientMinus and (uZF == 0.0)):
                            selFaces.append(face)
                #print 'Facade surfaces picked'
        elif roofOrient == True or floorOrient == True:
            if orient[0] == 0 and  orient[1] == 0 and  (orient[02] == 1 or orient[02] == -1):
                pass
            for i, geog in enumerate (geometry):
                for cnt in range(geog.Faces.Count):
                    face = geog.Faces[cnt].DuplicateFace(False)

                    centerPt, normalVector = getSrfCenPtandNormal(face)
                    if normalVector:
                        angle2Z = math.degrees(rc.Geometry.Vector3d.VectorAngle(normalVector, rc.Geometry.Vector3d.ZAxis))
                    else:
                        angle2Z = 0
                    
                    if roofOrient == True:
                        if  angle2Z < maximumRoofAngle or angle2Z > 360- maximumRoofAngle:
                            selFaces.append(face)
                            #up.append(surface)
                        #if normalVector[0] == 0 and  normalVector[1] == 0 and  normalVector[02] == 1:
                        #    selFaces.append(face)
                    else:
                        if  180 - maximumFloorAngle < angle2Z < 180 + maximumFloorAngle:
                            #down.append(surface)
                            selFaces.append(face)
                        #if normalVector[0] == 0 and  normalVector[1] == 0 and  normalVector[02] == -1:
                        #    selFaces.append(face)
            print 'For now only horizontal surfaces picked'
    else:
        print 'Don''t know what do you want from me'
        warning = "Don''t know what do you want from me"
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
