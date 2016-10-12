# Cone Of Vision
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
Use this component to generate and visualize cones of vision.
-
This component can help you to customize view analysis. Plug its outputs into Ladybug_View Analysis.
-
Car at 25 mph, Car at 45 mph, Car at 65 mph (horizontal angle, distance limits)
Source: U. S. Bureau of Land Management. Visual Resource Management Program (Course 8400-05) 2008.
-
Human, Color Recognition, Sign Recognition, Word Recognition (horizontal angle)
Human, Color Recognition, Optimal Video Display Area (vertical angle)
Source: INO - CNR Istituto Nazionale di Ottica www.ino.it Titolo: Il processo della Visione e Stereoscopia Relatore: Luca Mercatelli 16 aprile 2010 Polo viale.
-
Provided by Ladybug 0.0.63
    
    Args:
        type_ : This input sets the cone of vision, the cone is defined by four values that are vertical angle+, vertical angle-, horizontal angle+, horizontal angle-, distance limits.
        -
        Connect a number from 0 to 9.
        -
        0 =     Human (50, 70, 62, 62, 10 meters)
        1 =     Peripheral vision (60, 70, 60, 60, 10 meters)
        2 =     Outdoor (90, 15, 180, 180, 100 meters)
        3 =     Car at 25 mph (50, 15, 50, 50, 182.88 meters)
        4 =     Car at 45 mph (50, 15, 33, 32.5, 365.76 meters)
        5 =     Car at 65 mph (50, 15, 22, 20, 609.60 meters)
        6 =     Color Recognition (30, 40, 30, 30, 10 meters)    
        7 =     Sign Recognition (30, 40, 15, 15, 10 meters)   
        8 =     Word Recognition (30, 40, 5, 5, 10 meters) 
        9 =     Optimal Video Display Area (0, 30, 30, 30, 10 meters)
        -
        If no value is provided, it will be 2 ("Outdoor").
        _viewPoint_ : The point of vision in which to generate the cone of vision.
        If not supplied, default value will be the Rhino origin.
        _viewDirection_ : A vector that represents the view direction.
        If not supplied, default value will be the vector of Y-Axis.
        --------------: --------------
        distanceLimit_ : Set the limit of the view.
        -
        This input let you customize the cone of vision.
        vAngleUp_ : The vertical angle of the upper visual field. A number from 0.0 to 90.0.
        -
        This input let you customize the cone of vision.
        vAngleDown_ : The vertical angle of the lower visual field. A number from 0.0 to 90.0.
        -
        This input let you customize the cone of vision.
        hAngle_ : The horizontal angle from the standard line of sight. A number from 0.0 to 180.0.
        -
        This input let you customize the cone of vision.
    Returns:
        readMe!: ...
        coneOfVision : Brep that represent the cone of vision.
        parameters : Connect this list to Ladybug_View Analysis for customizing the view analysis.
        -
        the parameters are vertical angle+ (), vertical angle- (), horizontal angle (), distance limit (meters), view direction in the horizontal plane ().
        NB. 0 is the direction of green axis of Rhino.
"""

ghenv.Component.Name = "Ladybug_Cone Of Vision"
ghenv.Component.NickName = 'ConeOfVision'
ghenv.Component.Message = "VER 0.0.63\nOCT_07_2016"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import Rhino as rc
from math import *
import scriptcontext as sc
import clr
import System

clr.AddReference("Grasshopper")
import Grasshopper.Kernel as gh
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree


class ConeOfVision:
    
    def __init__(self, Vdown, Vup, H, distanceLimit, unitConversionFactor):
        self.Vdown = Vdown
        self.Vup = Vup
        self.H = H
        self.distanceLimit = distanceLimit / unitConversionFactor
    
    
    def curvedSurface(self, viewPoint, viewDirection):
        """This method to generate a curved surface which represent the field of view."""
        if viewDirection == rc.Geometry.Vector3d.ZAxis:
            viewDirection.Y = -0.001 # avoid bug if you connect z vector
        
        line1 = rc.Geometry.Line(viewPoint, viewDirection, self.distanceLimit).ToNurbsCurve()
        yV = rc.Geometry.Vector3d.CrossProduct(rc.Geometry.Vector3d.ZAxis, viewDirection)
        zV = rc.Geometry.Vector3d.CrossProduct(yV, viewDirection)
        
        rotate2 = rc.Geometry.Transform.Rotation(radians(-self.Vup), yV, viewPoint)
        rotate3 = rc.Geometry.Transform.Rotation(radians(self.Vdown),yV, viewPoint)
        line2 = line1.Duplicate()
        line3 = line1.Duplicate()
        line2.Transform(rotate2)
        line3.Transform(rotate3)
        
        viewArc = rc.Geometry.Arc(line2.PointAtEnd, line1.PointAtEnd, line3.PointAtEnd).ToNurbsCurve()
        
        conePart1 = rc.Geometry.RevSurface.Create(viewArc, rc.Geometry.Line(viewPoint, zV), -radians(self.H), radians(self.H)).ToBrep()
        
        return conePart1
    
    
    def coneOfView(self, viewPoint, viewDirection):
        """This method generate solid cone of vision."""
        
        conePart1 = self.curvedSurface(viewPoint, viewDirection)
        
        conePart2 = []
        for crv in conePart1.DuplicateEdgeCurves():
            conePart2.append(rc.Geometry.Extrusion.CreateExtrusionToPoint(crv, viewPoint).ToBrep())
        conePart2.append(conePart1)
        
        viewCone = rc.Geometry.Brep.JoinBreps(conePart2, sc.doc.ModelAbsoluteTolerance)
        
        for srf in viewCone:
            if not srf.IsSurface or srf.IsSolid:
                viewCone = srf
        
        return viewCone


def checkLenghtOfDirection(pt, dir, dirInput):
    if pt != [] and dirInput == []:
        dir = dir * len(pt)
    else: dir = dir
    
    return dir


def checkPointOfView(pt, dir):
    if len(pt) == len(dir):
        print("number of cones of vision: {}".format(len(pt)))
        return True
    else:
        warning = "the number of points of view should be equals to the number of directions."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)            
        return False


def main():
    # type:
    # type structure (vAngleUp, vAngleDown, hAngle, distanceLimit)
    # I suggest to resize the last parameter (distanceLimit) apart from the car25mph, car45mph, car65mph because they have a source.
    human = dict(vAngleUp = 50, vAngleDown = 70, hAngle = 62, distanceLimit = 10)
    peripheralVision = dict(vAngleUp = 60, vAngleDown = 70, hAngle = 60, distanceLimit = 10)
    outdoor = dict(vAngleUp = 90, vAngleDown = 70, hAngle = 180, distanceLimit = 10)
    carAt25mph = dict(vAngleUp = 50, vAngleDown = 15, hAngle = 50, distanceLimit = 182.88)
    carAt45mph = dict(vAngleUp = 50, vAngleDown = 15, hAngle = 32.5, distanceLimit = 365.76)
    carAt65mph = dict(vAngleUp = 50, vAngleDown = 15, hAngle = 20, distanceLimit = 609.60)
    colorRecognition = dict(vAngleUp = 30, vAngleDown = 40, hAngle = 30, distanceLimit = 10)
    signRecognition = dict(vAngleUp = 30, vAngleDown = 40, hAngle = 15, distanceLimit = 10)
    wordRecognition = dict(vAngleUp = 30, vAngleDown = 40, hAngle = 5, distanceLimit = 10)
    optimalVideoDisplayArea = dict(vAngleUp = 0.001, vAngleDown = 30, hAngle = 30, distanceLimit = 10)
    
    type = (human, peripheralVision, outdoor, carAt25mph, carAt45mph, carAt65mph, colorRecognition, signRecognition, wordRecognition, optimalVideoDisplayArea)
    
    if type_ != None:
        vAngleUp, vAngleDown, hAngle, distanceLimit = type[type_]['vAngleUp'], type[type_]['vAngleDown'], type[type_]['hAngle'], type[type_]['distanceLimit']
    else: vAngleUp, vAngleDown, hAngle, distanceLimit = (90, 70, 180, 10)
    
    if _viewPoint_ == []:
        viewPoint = [rc.Geometry.Point3d.Origin]
    else: viewPoint = _viewPoint_
    if _viewDirection_ == []:
        viewDirection = [rc.Geometry.Vector3d.YAxis]
    else: viewDirection = _viewDirection_
    
    # if user want to study outdoor spaces with many view  without using directions
    viewDirection = checkLenghtOfDirection(viewPoint, viewDirection, _viewDirection_)
    check = checkPointOfView(viewPoint, viewDirection)  
    
    
    if check:
        # remark for users
        if type_ != 3 and type_ != 4 and type_ != 5 and distanceLimit_ == None:
            remark = "Note that the distance limit you are using is not the real limit of normal human vision. It is only used for visualizing."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, remark)
        
        if (type_ == 3 or type_ == 4 or type_ == 5) and distanceLimit_ != None:
            remark = "Please keep in mind that the default distanceLimit of 3, 4, 5 comes from \n U. S. Bureau of Land Management. Visual Resource Management Program (Course 8400-05) 2008."
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, remark)
        
        if vAngleUp_ != None:
            if vAngleUp_ == 0.0:
                vAngleUp = 0.0001
            else: vAngleUp = vAngleUp_
        if vAngleDown_ != None:
            if vAngleDown_ == 0.0:
                vAngleDown = 0.0001
            else: vAngleDown = vAngleDown_
        if hAngle_ != None:
            if hAngle_ == 0.0:
                hAngle = 0.0001
            else: hAngle = hAngle_
        if distanceLimit_ != None:
            if distanceLimit_ == 0.0:
                distanceLimit = 0.0001
            else: distanceLimit = distanceLimit_
        
        # set cone of vision
        view = ConeOfVision(vAngleDown, vAngleUp, hAngle, distanceLimit, unitConversionFactor)
        
        coneOfVision = DataTree[System.Object]()
        parameters = DataTree[System.Object]()
        
        for i, point in enumerate(viewPoint):
            cone = view.coneOfView(point, viewDirection[i])
            try:
                directionAngle = degrees(rc.Geometry.Vector3d.VectorAngle(viewDirection[i], rc.Geometry.Vector3d.YAxis, rc.Geometry.Plane.WorldXY))
            except OverflowError: directionAngle = 0.0 # if the direction is ZAxis
            # move a bit
            xmove = rc.Geometry.Transform.Translation(-viewDirection[i]*0.01)
            cone.Transform(xmove)
            path = GH_Path(i)
            parameters.AddRange((vAngleUp, vAngleDown, hAngle, distanceLimit, directionAngle), path) # (vertical angle+, vertical angle-, horizontal angle, distance limits, vector, direction as angle on world XY plane)
            coneOfVision.Add(cone, path)
        
        return coneOfVision, parameters
    
    else: return -1


initCheck = False
if sc.sticky.has_key('ladybug_release'):
    initCheck = True
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = True
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    unitConversionFactor = lb_preparation.checkUnits()
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")

if initCheck:
    result = main()
    if result != -1:
        coneOfVision, parameters = result
        print('Well Done!')