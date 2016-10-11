# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
#
# This file is part of Ladybug.
#
# Copyright (c) 2013-2015, Byron Mardas <byronmardas@gmail.com>
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
Use this component to link Rhino solar system to grasshopper and create sun positions according to the weatherfile. Furthermore, this component can be used to render the active viewport (with the selected renderer), and/or save the image of the viewport or render.
-
Provided by Ladybug 0.0.63
    Args:
        _location: get location from Ladybug_Import epw component. This will update rhino solar system to the correct coordinates and timezone
        North_: North direction of the model. This can be either an number representing angle, or a vector. (by default North is set on the y axis)
        _Month_: A number that represents the month you want to visualize
        _Day_: A number that represents the Day you want to visualize
        _Hour_: A number that represents the Hour you want to visualize
        analysisPeriod_: An optional analysis period from the Analysis Period component.  Inputs here will override the hour, day, and month inputs above. (this is to visualize up to a full)
        timeStep: if analysisPeriod is used, this will divide the hour into steps (2 = 30 minutes, 4 = 15 minutes..)
        Ground_: enable if you want to create a generic floor at 0.0 in order to visualize shadows in case there is no floor in the model.
        --------------- : ....
        _workingDir_: A folder path where your images or renders will be saved. Each image will be named according to the time of day that it represents
        _render_: Enable to render the active viewport. (current rendered will be used, set up the render setting according to your need)
        _save_: Enable to save a print of the active viewport. If _render_ is also active, this will save a copy of the rendered image in your folder
        viewWidth_: A number that represents the image width in pixels
        viewHeight_: A number that represents the image height in pixels
    Returns:
        readMe!: ...
        imagePath: A path that represents the last saved image
"""

ghenv.Component.Name = "Ladybug_Visualize_Shadows"
ghenv.Component.NickName = 'Visualize_Shadows'
ghenv.Component.Message = 'VER 0.0.63\nAUG_10_2016'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#Change the following date to be that of the LB version during your commit or pull request:
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
#Change the following date to be that of the HB version of your commit or pull request (or get rid of the follwoing if your component is a part of Ladybug):
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc
import Rhino
import rhinoscriptsyntax as rs
import Rhino.Render.Sun as sun
import ghpythonlib.components as ghp
import scriptcontext as sc
import math
import os

w = gh.GH_RuntimeMessageLevel.Warning


#If Honeybee or Ladybug is not flying or is an older version, give a warning.
initCheck = True

#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


#Honeybee check.
if not sc.sticky.has_key('honeybee_release') == True:
    initCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): initCheck = False
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)




def checkTheInputs():
    if _Month_ > 12 or _Month_ <1:
        ghenv.Component.AddRuntimeMessage(w, "_Month_ has to be a number between 1 and 12")
    else:
        if _Day_ >31 or _Day_ <1:
            ghenv.Component.AddRuntimeMessage(w, "_Day_ has to be a number between 1 and 31")
        else:
            if _Hour_ >24 or _Hour_ <1:
                ghenv.Component.AddRuntimeMessage(w, "_Hour_ has to be a number between 1 and 24")
            else:
                return True
    return False




#Set display mode to "Rendered" in Rhino
rendered = Rhino.Display.DisplayModeDescription.FindByName("Rendered")
Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport.DisplayMode = rendered


#from _location split and referense Latitude, Longitude and Timezone
change = str(_location)
Lat = (change.split("\n"))[2]
Latitude = Lat.split(",")[0]
Long = (change.split("\n"))[3]
Longitude = Long.split(",")[0]
Off = (change.split("\n"))[4]
Offset = Off.split(",")[0]
offset = int(math.ceil(float(Offset)))

#Enable Ground if needed to show shadows
ground = Rhino.RhinoDoc.ActiveDoc.GroundPlane #Link to Rhino GrounPlance system 
Rhino.Render.GroundPlane.Enabled.SetValue(ground,Ground_) #Enable ground

#Change the int(_Month_) into a 3 letter string to save the month name for the image file
StrMonth = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")

if analysisPeriod_ == []: 
    analysisPeriod_ = None

if _timeStep_ == None: #If there is no timeStep input, the default will be 1
    _timeStep_ = 1

if _workingDir_ == None:
    dir = sc.sticky["Ladybug_DefaultFolder"] #If no path is defined, the default Ladybug folder will be used. 
else:
    dir = str(_workingDir_)#Define the path, if path does not exist, create, otherwise use existing one
if os.path.exists(dir) == False:
    os.mkdir(dir)

if viewWidth_ == None:#Change view width and heights by pixel
    viewWidth_ = 800
if viewHeight_ == None:
    viewHeight_ = 800

def main():
    if _runIt == True:
        #Give priority to analysisPeriod over Month/Day/Hour.
        if analysisPeriod_ != None:
            Months = int((analysisPeriod_)[0][0])
            Days = int((analysisPeriod_)[0][1])
            for hourRange in range((int((analysisPeriod_)[0][2])*100),(int((analysisPeriod_)[1][2])*100),int((1/_timeStep_)*100)):
                H = int(math.modf(hourRange/100)[1])
                M = int(60*(math.modf(hourRange/100)[0]))
                Date = ghp.ConstructDate(2015,Months,Days,H,M,0) #Date = ghp.ConstructDate(2015,Months,Days,H,M,0)
                Sunposition = Rhino.RhinoDoc.ActiveDoc.Lights.Sun #Link grasshopper definition to Rhino Sun system
                sun.Enabled.SetValue(Sunposition,True)
                sun.TimeZone.SetValue(Sunposition,offset)
                sun.SetPosition(Sunposition, Date, float(Latitude), float(Longitude)) #Adjust _location and Date of Rhino Sun
                if sun.Altitude.Info.GetValue(Sunposition) > 10:
                    #set Orientation
                    if North_ == None:
                        sun.North.SetValue(Sunposition, 90)
                    else:
                        if type(North_) is float:
                            sun.North.SetValue(Sunposition, (90-North_))
                        else:
                            #Set North
                            zero = Rhino.Geometry.Vector3d(1.0,0.0,0.0)
                            Xaxis = Rhino.Geometry.Vector3d(0.0,0.0,1.0)
                            Origin = Rhino.Geometry.Point3d(0.0,0.0,0.0)
                            Plane = Rhino.Geometry.Plane(Origin,Xaxis)
                            angle = Rhino.Geometry.Vector3d.VectorAngle(zero,North_,Plane)
                            sun.North.SetValue(Sunposition, math.degrees(angle))
                    if _render_ == True:
                        rs.Command("!_render") #send the command to render on your active renderer
                        if _save_ == True: #Enable to save the view as a .png
                            dir = str(_workingDir_) #Define the path, if path does not exist, create, otherwise use existing one
                            rs.Command("_-SaveRenderWindowAs \"" + (dir) + "\\" + str(StrMonth[int(Months)-1])+"_"+str(H)+"_"+str(M) + ".png\"")
                            rs.Command ("_-CloseRenderWindow") #close the rendered window when in saving mode to avoid stacking a series of renderWindows when running on Rhino renderer.
                    else:
                        if _save_ == True:
                            dir = str(_workingDir_) #Define the path, if path does not exist, create, otherwise use existing one
                            rs.Command("_-ViewCaptureToFile \""+dir+"\\" +str(StrMonth[int(Months)-1])+"_"+str(H)+"_"+str(M) + ".png\"" + " w " +str(viewWidth_)+" "+"h "+str(viewHeight_)+" "+ " enter")
                else:
                    DarkHours = (str(StrMonth[int(Months)-1])+"_"+str(H)+"_"+str(M)+" is Nighttime")
        else:
            Hours = _Hour_
            Months = _Month_
            Days = _Day_
            H = int(math.modf(Hours)[1])
            M = int(60*(math.modf(Hours)[0]))
            Date = ghp.ConstructDate(2015,Months,Days,H,M,0) #Date = ghp.ConstructDate(2015,Months,Days,H,M,0)
            Sunposition = Rhino.RhinoDoc.ActiveDoc.Lights.Sun #Link grasshopper definition to Rhino Sun system
            sun.Enabled.SetValue(Sunposition,True)
            sun.TimeZone.SetValue(Sunposition,offset)
            sun.SetPosition(Sunposition, Date, float(Latitude), float(Longitude)) #Adjust _location and Date of Rhino Sun
            if sun.Altitude.Info.GetValue(Sunposition) > 10:
                #set Orientation
                if North_ == None:
                    sun.North.SetValue(Sunposition, 90)
                else:
                    if type(North_) is float:
                        sun.North.SetValue(Sunposition, (90-North_))
                    else:
                        #Set North
                        zero = Rhino.Geometry.Vector3d(1.0,0.0,0.0)
                        Xaxis = Rhino.Geometry.Vector3d(0.0,0.0,1.0)
                        Origin = Rhino.Geometry.Point3d(0.0,0.0,0.0)
                        Plane = Rhino.Geometry.Plane(Origin,Xaxis)
                        angle = Rhino.Geometry.Vector3d.VectorAngle(zero,North_,Plane)
                        sun.North.SetValue(Sunposition, math.degrees(angle))
                if _render_ == True:
                    rs.Command("!_render") #send the command to render on your active renderer
                    if _save_ == True: #Enable to save the view as a .png
                        dir = str(_workingDir_) #Define the path, if path does not exist, create, otherwise use existing one
                        if os.path.exists(dir) == False:
                            os.mkdir(dir)
                        rs.Command("_-SaveRenderWindowAs \"" + (dir) + "\\" + str(StrMonth[int(Months)-1])+"_"+str(H)+"_"+str(M) + ".png\"")
                        rs.Command ("_-CloseRenderWindow") #close the rendered window when in saving mode to avoid stacking a series of renderWindows when running on Rhino renderer.
                        imagePath = (dir+"\\" +str(StrMonth[int(Months)-1])+"_"+str(H)+"_"+str(M) + ".png")
                        return imagePath
                else:
                    if _save_ == True:
                        dir = str(_workingDir_) #Define the path, if path does not exist, create, otherwise use existing one
                        rs.Command("_-ViewCaptureToFile \""+ (dir) +"\\" +str(StrMonth[int(Months)-1])+"_"+str(H)+"_"+str(M) + ".png\"" + " w " +str(viewWidth_)+" "+"h "+str(viewHeight_)+" "+ " enter")
                        imagePath = (dir+"\\" +str(StrMonth[int(Months)-1])+"_"+str(H)+"_"+str(M) + ".png")
                        return imagePath
            else:
                pass
    else:
        return -1

#If the intital check is good, run the component.
if initCheck:
    checkData = checkTheInputs()
    if checkData:
        imagePath = main()
        if imagePath != -1:
            pass

