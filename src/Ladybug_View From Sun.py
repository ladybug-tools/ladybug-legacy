# This component opens a new viewport that shows the view from sun.
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to open a new viewport in Rhino that shows the view from the sun.  This is useful for understanding what parts of Rhino geometry are shaded at a particular hour of the day.
-
Provided by Ladybug 0.0.57
    
    Args:
        _sunVector: A sun vector from which the the Rhino view will be generated. Use the Ladybug sunPath component to generate sunVectors.
        _cenPt_: The target point of the camera for the Rhino view that will be generated.  This point should be close to Rhino geometry that you are interested in viewing from the sun. If no point is progived, the Rhino origin will be used (0,0,0).
        sunViewPt_: An optional point for the camera position (or sun position). Use this to move the camera closer to the geometry you would like to view if the initial view is too far away..
        width_: An optional interger that represents the width (in pixels) of the Rhino viewport that will be generated.
        height_: An optional interger that represents the height (in pixels) of the Rhino viewport that will be generated.
        dispMode_: An optional text input for the display mode of the Rhino viewport that will be generated. For example: Wireframe, Shaded, Rendered, etc.
    Returns:
        readMe!: ...
"""
ghenv.Component.Name = "Ladybug_View From Sun"
ghenv.Component.NickName = 'viewFromSun'
ghenv.Component.Message = 'VER 0.0.57\nFEB_26_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


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
