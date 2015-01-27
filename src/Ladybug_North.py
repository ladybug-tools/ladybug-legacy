# North Arrow
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to create a compass sign that indicates the direction of North in the Rhino scene.

-
Provided by Ladybug 0.0.58
    
    Args:
        _north_: Input a vector to be used as a North direction or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _centerPt_: Input a point here to change the location of the North sign in the Rhino scene.  The default is set to the Rhino model origin (0,0,0).
        _scale_: Input a number here to change the scale of the sun path.  The default is set to 1.
    Returns:
        readMe!: ...
        northSign: A set of surfaces and curves that indicate the direction of North in Rhino.
"""

ghenv.Component.Name = "Ladybug_North"
ghenv.Component.NickName = 'northArrow'
ghenv.Component.Message = 'VER 0.0.58\nSEP_11_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Rhino as rc
import Grasshopper.Kernel as gh

def main(north, centerPt, scale):
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
