# North Arrow
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
North Arrow

-
Provided by Ladybug 0.0.53
    
    Args:
        _north_: Input a number or a vector to set north; default is set to the Y-axis
        _centerPt_: Input a point to locate the center point of the sun-path
        _scale_: Input a number to set the scale of the sun-path
    Returns:
        readMe!: ...
        northSign: northSign geometry
"""

ghenv.Component.Name = "Ladybug_North"
ghenv.Component.NickName = 'northArrow'
ghenv.Component.Message = 'VER 0.0.53\nJan_22_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import scriptcontext as sc
import Rhino as rc


def main(north, centerPt, scale):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1
    
    conversionFac = lb_preparation.checkUnits()
    
    # north direction
    northAngle, northVector = lb_preparation.angle2north(north)
    cenPt = lb_preparation.getCenPt(centerPt)
    scale = lb_preparation.setScale(scale, conversionFac)
    
    # main Circle
    radius = 10*scale
    mainCircle = rc.Geometry.Circle(cenPt, radius).ToNurbsCurve()
    offsetCircle =  rc.Geometry.Circle(cenPt, .85*radius).ToNurbsCurve()
    
    # main North line
    arrow = rc.Geometry.Line(cenPt, rc.Geometry.Point3d.Add(cenPt, 1.5*radius*northVector)).ToNurbsCurve()
    
    # offset to both sides
    rOffset = arrow.Offset(rc.Geometry.Plane.WorldXY, .15*radius, sc.doc.ModelAbsoluteTolerance, rc.Geometry.CurveOffsetCornerStyle.None)[0]
    lOffset = arrow.Offset(rc.Geometry.Plane.WorldXY, -.15*radius, sc.doc.ModelAbsoluteTolerance, rc.Geometry.CurveOffsetCornerStyle.None)[0]
    
    # creat the rectangle
    pts = [rOffset.PointAtStart, rOffset.PointAtEnd, lOffset.PointAtEnd, lOffset.PointAtStart, rOffset.PointAtStart]
    rect = rc.Geometry.Polyline(pts).ToNurbsCurve()
    
    # boolean union the curves
    outlineCrv = rc.Geometry.Curve.CreateBooleanUnion([rect, mainCircle])[0].ToNurbsCurve()
    inlineCrv = rc.Geometry.Curve.CreateBooleanDifference(offsetCircle, rect)[0].ToNurbsCurve()
    
    # create the planar surface
    northSign = rc.Geometry.Brep.CreatePlanarBreps([outlineCrv, inlineCrv])[0]
    
    # additional lines
    eastVector = rc.Geometry.Vector3d.CrossProduct(northVector, rc.Geometry.Vector3d.ZAxis)
    southPt = rc.Geometry.Point3d.Add(cenPt, -1.2*radius*northVector)
    eastPt = rc.Geometry.Point3d.Add(cenPt, 1.2*radius*eastVector)
    westPt = rc.Geometry.Point3d.Add(cenPt, -1.2*radius*eastVector)
    
    eastWestLine = rc.Geometry.Line(eastPt, westPt).ToNurbsCurve()
    southNorthLine = rc.Geometry.Line(southPt, cenPt).ToNurbsCurve()
    
    return northSign, southNorthLine, eastWestLine
    

if not _north_: _north_ == 0
northSign = main(_north_, _centerPt_, _scale_)