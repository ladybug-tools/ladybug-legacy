# This script captures a png image file of a Rhino viewport.
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to capture Rhino views and save them to your hard drive as as a .png files.
This is particularly useful if you are trying to create animations of Grasshopper geometry and want to automate the capturing of views.
Note that your images will have a Rhino world axes icon in the lower left of the image unless you go to Options > Grid > and uncheck "Show world axes icon" in Rhino.

-
Provided by Ladybug 0.0.58

    Args:
        _fileName: The file name that you would like the image to be saved as.  Note that, for animations, you want to make sure that each saved images has a different filename otherwise the previous image will be overwritten by each successive image.
        folder_: The folder into which you would like to write the image file.  This should be a complete file path to the folder.  If no folder is provided, the images will be written to C:/Ladybug/Capturedviews/.
        viewNames_: The Rhino viewport name which you would like to take a snapshot of.  Acceptable inputs include "Perspective", "Top", "Bottom", "Left", "Right", "Front", "Back" or any view name that you have already saved within the Rhino file (note that you do not need to input quotations).  If no text is input here, the default will be an image of the active viewport (or the last viewport in which you navigated).
        imageWidth_: The width of the image that you would like to take in pixels.  If no value is provided here, the component will set the width to that of the active Rhino viewport on your screen.
        imageHeight_: The height of the image that you would like to take in pixels.  If no value is provided here, the component will set the height to that of the active Rhino viewport on your screen.
        displayMode_: The display mode of the viewport that you would like to take an image of. Acceptable inputs include "Wireframe", "Shaded", "Rendered", "Ghosted", "X-Ray", "Technical", "Atristic", and "Pen".  If no text is input here, the default will be the displaymode of the active viewport (or the last viewport in which you navigated).
        keepAspectR_: Set to "True" to keep the aspect ratio of the viewport in the images that you save.  By default, this is set to "False" if you have connected an imageHeight_ but will override this input to ensure correct aspect ratio if set to "True".
        _capture: Set to "True" to capture the image of the Rhino viewport and save it to your hard drive.
    Returns:
        imagePath: The filepath of the image taken with this component.

"""
ghenv.Component.Name = "Ladybug_Capture View"
ghenv.Component.NickName = 'captureView'
ghenv.Component.Message = 'VER 0.0.58\nSEP_11_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
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
        
        try:
            System.Drawing.Bitmap.Save(pic , fullPath)
        except:
            try:
                fullPath = os.path.join(directory, fileName +'_'+ viewName + '_1.png')
                System.Drawing.Bitmap.Save(pic , fullPath)
            except:
                print "Failed!"
                return
                pass
        
        return fullPath

if _capture and _fileName!=None:
    
    directory = mdPath(folder_)
    
    # check input
    if len(viewNames_)==0: viewNames_ = [sc.doc.Views.ActiveView.ActiveViewport.Name]
    
    fullPath = viewCapture(_fileName, directory, viewNames_, imageWidth_, imageHeight_, displayMode_, keepAspectR_)
    if fullPath:
        print fullPath