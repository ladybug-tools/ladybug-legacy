# This script captures the views based on the view name
# Construct Time
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Capture Rhino views and save them as a .png file.
-
Provided by Ladybug 0.0.57

    Args:
        _fileName:
        folder_:
        viewNames_:
        imageWidth_:
        imageHeight_:
        displayMode_:
        keepAspectR_:
        _capture:
    Returns:
        imagePath: 

"""
ghenv.Component.Name = "Ladybug_Capture View"
ghenv.Component.NickName = 'captureView'
ghenv.Component.Message = 'VER 0.0.57\nAPR_14_2014'
ghenv.Component.Category = "Ladybug"
# ghenv.Component.SubCategory = "4 | Extra"
ghenv.Component.SubCategory = "7 | WIP"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import os
import System
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino as rc

def mdPath(workDir):
    # check user input
    if workDir is None: workDir = 'c:/Ladybug/Capturedviews/'
    
    # check working directory
    if not os.path.exists(workDir):os.makedirs(workDir)
    return workDir

def viewCapture(fileName, directory, viewNames, image_width, image_height, dispModeStr, keepAspectRatio):
    
    for viewName in viewNames:
        
        if viewName in rs.ViewNames():
            rs.CurrentView(viewName, True)
        else:
            # change to RhinoDoc to get access to NamedViews
            sc.doc = rc.RhinoDoc.ActiveDoc
            namedViews = rs.NamedViews()
            if viewName in namedViews:
                viewName = rs.RestoreNamedView(viewName)
            else:
                viewName = None
            # change back to Grasshopper
            sc.doc = ghdoc
            viewName = rs.CurrentView(viewName, True)
        
        rs.CurrentView(viewName)
        sc.doc.Views.Find(viewName, False)
        viewtoCapture = sc.doc.Views.ActiveView        
        
        try:
            dispMode = rc.Display.DisplayModeDescription.FindByName(dispModeStr)
            sc.doc.Views.ActiveView.ActiveViewport.DisplayMode = dispMode
        except:
            pass
        
        if image_height == None: image_h = viewtoCapture.ActiveViewport.Size.Height
        else: image_h = image_height 
        
        if image_width == None: image_w = viewtoCapture.ActiveViewport.Size.Width
        else: image_w = image_width
        
        # aspectRatio
        if keepAspectRatio:
            if image_height == None and image_width != None:
                image_h = image_h * (image_w/viewtoCapture.ActiveViewport.Size.Width)
            elif image_height != None and image_width == None:
                image_w = image_w * (image_h/viewtoCapture.ActiveViewport.Size.Height)
                
        
        viewSize = System.Drawing.Size(int(image_w), int(image_h))
        
        pic = rc.Display.RhinoView.CaptureToBitmap(viewtoCapture , viewSize)
        
        fullPath = os.path.join(directory, fileName +'_'+ viewName + '.png')
        
        System.Drawing.Bitmap.Save(pic , fullPath)
        
        return fullPath

if _capture and _fileName!=None:
    
    directory = mdPath(folder_)
    
    # check input
    if len(viewNames_)==0: viewNames_ = [sc.doc.Views.ActiveView.ActiveViewport.Name]
    
    fullPath = viewCapture(_fileName, directory, viewNames_, imageWidth_, imageHeight_, displayMode_, keepAspectR_)
    
    print fullPath