# This component opens a new viewport that shows the view from sun.
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component opens a new viewport that shows the view from sun.
-
Provided by Ladybug 0.0.53
    
    Args:
        _sunVector: Sun vector as a vector3D
        _cenPt_: Center point for the camera target as a point3D. The origin point will be used if not provided.
        sunViewPt_: Optional input for sun position as a point3D
        width_: Optional input for width of RhinoView
        height_: Optional input for height of RhinoView 
        dispMode_: Optional input for display mode. Wireframe, Shaded, Rendered, etc.
    Returns:
        readMe!: ...
"""
ghenv.Component.Name = "Ladybug_View From Sun"
ghenv.Component.NickName = 'viewFromSun'
ghenv.Component.Message = 'VER 0.0.53\nJan_22_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import scriptcontext as sc
import Rhino as rc
import rhinoscriptsyntax as rs
import System

def main(sunVector, cenPt, sunPosition, dispModeStr, width, height, compGuid):
    
    viewName = 'viewFromSun_' + compGuid
    isView = rc.RhinoDoc.ActiveDoc.Views.Find(viewName, False)
    
    if isView and width and  width != sc.doc.Views.ActiveView.ActiveViewport.Size.Width + 16: isView = False
    elif isView and height and  height != sc.doc.Views.ActiveView.ActiveViewport.Size.Height + 34: isView = False
    
    if not isView:
        # if view is not already created creat a new floating view
        # Thanks to Florian for his help (http://www.grasshopper3d.com/forum/topics/new-floating-viewport-using-rhinocommon)
        if not width: w = sc.doc.Views.ActiveView.ActiveViewport.Size.Width
        else: w = width
        if not height: h = sc.doc.Views.ActiveView.ActiveViewport.Size.Height
        else: h = height
        # print w,h
        if rc.RhinoDoc.ActiveDoc.Views.Find(viewName, False)!= None: rc.RhinoDoc.ActiveDoc.Views.Find(viewName, False).Close()
        
        x = round((System.Windows.Forms.Screen.PrimaryScreen.Bounds.Width - w) / 2)
        y = round((System.Windows.Forms.Screen.PrimaryScreen.Bounds.Height - h) / 2)
        rectangle = System.Drawing.Rectangle(System.Drawing.Point(x, y), System.Drawing.Size(w, h))
        newRhinoView = rc.RhinoDoc.ActiveDoc.Views.Add(viewName, rc.Display.DefinedViewportProjection.Perspective, rectangle, True)
        if newRhinoView:
            newRhinoView.TitleVisible = True;
            isView = rc.RhinoDoc.ActiveDoc.Views.Find(viewName, False)
    
    rc.RhinoDoc.ActiveDoc.Views.ActiveView = isView
    
    try:
        dispMode = rc.Display.DisplayModeDescription.FindByName(dispModeStr)
        sc.doc.Views.ActiveView.ActiveViewport.DisplayMode = dispMode
    except: pass
    
    # modify the view
    sc.doc.Views.ActiveView.ActiveViewport.ChangeToParallelProjection(True)
    sc.doc.Views.ActiveView.ActiveViewport.SetCameraLocation(sunPosition, False)
    sc.doc.Views.ActiveView.ActiveViewport.SetCameraTarget(cenPt, False)
    sc.doc.Views.ActiveView.ActiveViewport.SetCameraDirection(sunVector, False)
    
    print 'view name = ' + viewName
    
if _sunVector!=None:
    if _cenPt_==None: _cenPt_ = rc.Geometry.Point3d.Origin
    if sunViewPt_!=None: sunPosition = sunViewPt_
    else: sunPosition = rc.Geometry.Point3d.Add(_cenPt_, _sunVector)
    main(_sunVector, _cenPt_, sunPosition, dispMode_, width_, height_, ghenv.Component.GetHashCode().ToString())
else:
    print "sunVector is missing."