# This script captures a png image file of a Rhino viewport.
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Use this component to render Rhino views and save them to your hard drive.  This component is fully-functional with both Rhino Render and V-Ray for Rhino.  Other rendering plugins may still work but are not fully supported yet.
_
This component is particularly useful if you are trying to create animations of Grasshopper geometry and want to automate the capturing of views.

-
Provided by Ladybug 0.0.66

    Args:
        _fileName: The file name that you would like the image to be saved as.  Note that, for animations, you want to make sure that each saved images has a different filename otherwise the previous image will be overwritten by each successive image.
        folder_: The folder into which you would like to write the image file.  This should be a complete file path to the folder.  If no folder is provided, the images will be written to C:/Ladybug/Capturedviews/.
        renderTime_: An optional number in seconds that represents the time you anticipate the render taking.  This can be used to create rendered animations for V-Ray 3, which currently does not have a dot net interface.
        viewNames_: The Rhino viewport name which you would like to render.  Acceptable inputs include "Perspective", "Top", "Bottom", "Left", "Right", "Front", "Back" or any view name that you have already saved within the Rhino file (note that you do not need to input quotations).  If no text is input here, the default will be an image of the active viewport (or the last viewport in which you navigated).
        imageWidth_: The width of the image that you would like to render in pixels.  If no value is provided here, the component will set the width to that of the active Rhino viewport on your screen.
        imageHeight_: The height of the image that you would like to render in pixels.  If no value is provided here, the component will set the height to that of the active Rhino viewport on your screen.
        keepAspectR_: Set to "True" to keep the aspect ratio of the viewport in the images that you save.  By default, this is set to "False" if you have connected an imageHeight_ but will override this input to ensure correct aspect ratio if set to "True".
        saveAlpha_: Set to "True" to have an alpah image saved next to the RGB rendering and set to "False" to have only have the RGB image saved.  The default is set to "False" to only save the RGB.
        _capture: Set to "True" to render the image and save it to your hard drive.
    Returns:
        imagePath: The filepath of the image taken with this component.

"""
ghenv.Component.Name = "Ladybug_Render View"
ghenv.Component.NickName = 'renderView'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import os
import System
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino as rc
import time
import clr
try:
    clr.AddReferenceToFileAndPath("C:\ProgramData\ASGVIS\VfR564\VRayForRhinoNETInterface.dll")
    import VRayForRhinoNETInterface
    vRayPresent = True
except:
    vRayPresent = False



def mdPath(workDir):
    # check user input
    if workDir is None: workDir = 'c:/Ladybug/Capturedviews/'
    
    # check working directory
    if not os.path.exists(workDir):os.makedirs(workDir)
    return workDir

def viewCapture(fileName, directory, viewNames, image_width, image_height, keepAspectRatio, saveAlpha):
    fullPathList = []
    if saveAlpha == None:
        saveAlpha = False
    
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
        
        fullPath = os.path.join(directory, fileName +'_'+ viewName + '.png')
        fullPathList.append(fullPath)
        
        # Set the image size
        rc.RhinoDoc.ActiveDoc.RenderSettings.UseViewportSize = False
        viewSize = System.Drawing.Size(int(image_w), int(image_h))
        rc.RhinoDoc.ActiveDoc.RenderSettings.ImageSize = viewSize
        
        try:
            VRayForRhinoNETInterface.VRayInterface.SetRenderOutputSize(int(image_w), int(image_h))
        except:
            pass
        
        print "Image dimensions set to (" + str(int(image_w)) + "x" + str(int(image_h)) + ")"
        
        # Render the image and save it.
        try:
            # V-Ray is the renderer.
            VRayForRhinoNETInterface.VRayInterface.HasRenderFinished()
            
            rs.Command("!_Render", echo=False)
            print "Rendering " + viewName + "..."
            
            while not VRayForRhinoNETInterface.VRayInterface.HasRenderFinished():
                if sc.escape_test(False):
                    print ("Rendering cancelled")
                    rs.Command("_CloseRenderWindow", echo=False)
                    rs.GetPlugInObject("V-Ray for Rhino").SetBatchRenderOn(True)
                    vray.CancelRender()
                    rs.GetPlugInObject("V-Ray for Rhino").SetBatchRenderOn(False)
                    esc = True
                    break
                rs.Sleep(10)
            rs.Command("_-SaveRenderWindowAs \"" + directory + "\\" + fileName +'_'+ viewName + ".png\"")
            rs.Command ("_-CloseRenderWindow") #close the rendered window when in saving mode to avoid stacking a series of renderWindows when running on Rhino renderer.
            if saveAlpha == False:
                try:
                    alphaPath = os.path.join(directory, fileName +'_'+ viewName + '.Alpha.png')
                    os.remove(alphaPath)
                except: pass
        except:
            if renderTime_ != None:
                # V-Ray is probably the renderer.
                start = time.clock()
                
                rs.Command("!_Render", echo=False)
                print "Rendering " + viewName + "..."
                
                while float(time.clock() - start) < renderTime_:
                    rs.Sleep(10)
                
                rs.Command("_-SaveRenderWindowAs \"" + directory + "\\" + fileName +'_'+ viewName + ".jpeg\"")
                rs.Command ("_-CloseRenderWindow") #close the rendered window when in saving mode to avoid stacking a series of renderWindows when running on Rhino renderer.
                if saveAlpha == False:
                    try:
                        alphaPath = os.path.join(directory, fileName +'_'+ viewName + '.Alpha.jpeg')
                        os.remove(alphaPath)
                    except: pass
            else:
                # Hopefully Rhino is the renderer.
                print "Rendering " + viewName + "..."
                rs.Command("!_render")
                rs.Command("_-SaveRenderWindowAs \"" + directory + "\\" + fileName +'_'+ viewName + ".png\"")
                rs.Command ("_-CloseRenderWindow") #close the rendered window when in saving mode to avoid stacking a series of renderWindows when running on Rhino renderer.
    
    
    return fullPathList

if _capture and _fileName!=None:
    directory = mdPath(folder_)
    # check input
    if len(viewNames_)==0: viewNames_ = [sc.doc.Views.ActiveView.ActiveViewport.Name]
    
    imagePath = viewCapture(_fileName, directory, viewNames_, imageWidth_, imageHeight_, keepAspectR_, saveAlpha_)