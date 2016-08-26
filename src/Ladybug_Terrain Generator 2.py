# terrain generator 2
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Djordje Spasic <djordjedspasic@gmail.com>
# with assistance of Dr. Bojan Savric <savricb@geo.oregonstate.edu>
# Component icon based on Antonello Di Nunzio's Terrain Generator icon.
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
Use this component to create a geometry of the terrain surrounding the chosen location.
Terrain will be created with SRTM 1 arc-second (20 to 30 meters depending on the latitude) grid precision.
You may notice slight terrain difference in comparison with Ladybug "Terrain Generator" component due each component using different terrain source.
-
!!! ATTENTION !!!   This component may crash Rhino 5 application if radius_ input is set to a value of tens of thousands of meters! This may happen due to Rhino's inability to create such large terrains. To prevent this, it is suggested to own a 64 bit version of Rhino 5 and have strong enough PC configuration. If you do not have either of these two, it is recommended to save your .gh definition before running this component!
-
Component requires that you are connected to the Internet, as it has to download topography data.
It also requires certain GDAL libraries to be downloaded manually. Component will provide instructions on where to download these libraries.
Additionally you can find the instructions in here:
For Rhino5 x86:  https://github.com/stgeorges/terrainShadingMask/blob/master/miscellaneous/Installation_instructions_Rhino5_x86.md
For Rhino5 x64:  https://github.com/stgeorges/terrainShadingMask/blob/master/miscellaneous/Installation_instructions_Rhino5_x64.md
-
Component mainly based on:

"Mathematical cartography", V. Jovanovic, VGI 1983.
"Vincenty solutions of geodesics on the ellipsoid" article by Chris Veness
https://books.google.rs/books/about/Matemati%C4%8Dka_kartografija.html?id=GcXEMgEACAAJ&redir_esc=y
http://www.movable-type.co.uk/scripts/latlong-vincenty.html
-
Topography data from: http://opentopography.org
GDAL Libraries from: http://gisinternals.com
-
Provided by Ladybug 0.0.63
    
    input:
        _location: The output from the "importEPW" or "constructLocation" component.  This is essentially a list of text summarizing a location on the Earth.
                   -
                   "timeZone" and "elevation" data from the location, are not important for the creation of a terrain.
        radius_: Horizontal distance to which the surrounding terrain will be taken into account.
                 -
                 It can not be shorter than 20 meters or longer than 100 000 meters.
                 -
                 The component itself might inform the user to alter the initial radius_ inputted by the user.
                 This is due to restriction of topography data, being limited to 56 latitude South to 60 latitude North range. If radius_ value for chosen location gets any closer to the mentioned range, the component will inform the user to shrink it for a certain amount, so that the radius_ stops at the range limit.
                 -
                 If not supplied, default value of 100 meters will be used.
                 -
                 In meters.
        north_: Input a vector to be used as a true North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
                -
                If not supplied, default North direction will be set to the Y-axis (0 degrees).
        type_: There are four terrain types:
               -
               0 - terrain will be created as a mesh with rectangular edges
               1 - terrain will be created as a mesh with circular edges
               2 - terrain will be created as a surface with rectangular edges
               3 - terrain will be created as a surface with circular edges
               -
               If nothing supplied, 1 will be used as a default (terrain will be created as a mesh with circular edges).
        origin_: Origin for the final "terrain" output.
                 -
                 If not supplied, default point of (0,0,0) will be used.
        workingFolder_: This component dowloads free topography data in order to create a terrain for the chosen _location.
                        The topography data will be saved as .tif files in the folder path provided by the workingFolder_ input.
                        -
                        If no folder path is supplied, the default Ladybug folder path will be used: C:\ladybug or C:\Users\%USERNAME%\AppData\Roaming\Ladybug.
        standThickness_: Thickness of the stand.
                         A stand is a basically a base constructed below the terrain mesh/surface. It can be used to create a terrain for cfd analysis or visualization purposes.
                         -
                         If not supplied, default value of 0 (no stand will be created) will be used.
                         -
                         In Rhino document units.
        numOfContours_: Number of elevation contours.
                        If you would not like the elevationContours output to be calculated, set the numOfContours_ input to 0.
                        -
                        If not supplied, default value of 10 elevation contours will be used.
        legendPar_: In case your type_ input is set to 0 or 1, you can use the legendPar_ input to control the colors with which the final "terrain" mesh will be colored with based on elevation.
                    Use Ladybug "Legend Parameters" component's "customColors_" input to control these colors.
                    Also use its font_ and legendScale_ inputs to change the font,size of the "title" output.
        bakeIt_: Set to "True" to bake the terrain geometry into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: !!! ATTENTION !!!   This component may crash Rhino 5 application if radius_ input is set to a value of tens of thousands of meters! This may happen due to Rhino's inability to create such large terrains.
                To prevent this, it is suggested to own a 64 bit version of Rhino 5 and have strong enough PC configuration. If you do not have either of these two, it is recommended to save your .gh definition before running this component!
    
    output:
        readMe!: ...
        terrain: The geometry of the terrain.
                 -
                 Depening on the type_ input it will be either a mesh (type_ = 0 and 1) or a surface (type_ = 2 and 3)
        title: Title geometry with information about location, radius, north angle.
        originPt: The origin (center) point of the "terrain" geometry.
                  -
                  Use grasshopper's "Point" parameter to visualize it.
                  -
                  Use this point to move the "terrain", geometry around in the Rhino scene with grasshopper's "Move" component.
        elevation: Elevation of the origin_ input.
                   -
                   In Rhino document units.
        elevationContours: Elevation contours.
                           Their number is defined by the numOfContours_ input. Set the numOfContours_ input to 0, if you would not like the elevationContours to be created.
        librariesFolder: Folder path where GDAL libraries should be copied.
                         -
                         It is created as:
                         Ladybug_Ladybug component's "defaultFolder_" + "terrain shading mask libraries 32-bit"  for Rhino5 x86,
                         Ladybug_Ladybug component's "defaultFolder_" + "terrain shading mask libraries 64-bit"  for Rhino5 x64.
"""

ghenv.Component.Name = "Ladybug_Terrain Generator 2"
ghenv.Component.NickName = "TerrainGenerator2"
ghenv.Component.Message = "VER 0.0.63\nAUG_26_2016"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
import rhinoscriptsyntax as rs
import scriptcontext as sc
import datetime
import System
import urllib
import Rhino
import time
import math
import clr
import os
import gc


def getLocationData(location):
    
    if location:
        try:
            # location data
            locationName, latitude, longitude, timeZone, elevation = lb_preparation.decomposeLocation(location)  # latitude positive towards north, longitude positive towards east
            latitude = float(latitude)
            longitude = float(longitude)
            locationNameCorrected = System.String.Replace(  System.String.strip(System.String.Replace(System.String.Replace(locationName,"\\","-"), "/", "-") )  ," ", "_")  # removing "/", "\", " " from locationName
            fileNameIncomplete = locationNameCorrected + "_" + str(latitude) + "_" + str(longitude) + "_TERRAIN_MASK"  # incomplete due to missing "_visibility=100KM_sph" part (for example)
            
            validLocationData = True
            printMsg = "ok"
        
        except Exception, e:
            # something is wrong with "_location" input (the input is not from Ladybug "Import epw" component "location" ouput)
            latitude = longitude = locationNameCorrected = fileNameIncomplete = None
            validLocationData = False
            printMsg = "Something is wrong with \"_location\" input."
    else:
        latitude = longitude = locationNameCorrected = fileNameIncomplete = None
        validLocationData = False
        printMsg = "Please input \"location\" ouput of Ladybug \"Import epw\" component, or make your own location data using Ladybug's \"Contruct Location\" and plug it into \"_location\" input of this component."
    
    return latitude, longitude, locationNameCorrected, fileNameIncomplete, validLocationData, printMsg


def createFolder(folderPath):
    if os.path.isdir(folderPath):
        # inputted "workingFolder_" exists
        pass
    else:
        # inputted "workingFolder_" does not exist
        try:
            # try creating the folder according to "workingFolder_"
            os.mkdir(folderPath)
        except Exception, e:
            # invalid workingFolder_ input"
            folderCreated = False
            return folderCreated
    
    folderCreated = True
    return folderCreated


def checkInputData(maxVisibilityRadiusM, north, type, origin, workingFolderPath, standThickness, numOfContours, downloadTSVLink):
    
    # trying to import gdal and osr libraries
    ladybugFolderPath = sc.sticky["Ladybug_DefaultFolder"]  # "defaultFolder_" input of Ladybug_Ladybug component
    if System.Environment.Is64BitProcess == False:
        # 32 bit GDAL,OSR,OGR libraries
        GDAL_librariesFolderPath = os.path.join(ladybugFolderPath, "terrain shading mask libraries 32-bit")
        bitVersion = "win32"
        rhino5version = "x86"
        zipFileNameWithoutExtension = "release-1800-gdal-1-11-4-mapserver-6-4-3"
        zipFileNameWithExtension = "release-1800-gdal-1-11-4-mapserver-6-4-3.zip"
        windowsXPtext = " \n" + \
                        "Note: Windows XP operating system may need a different version of GDAL libraries not available from the gisinternals.com website.\n" + \
                        "If you are using Windows XP, instead of following the step 1, download the appropriate XP GDAL libraries from: https://www.dropbox.com/s/08mt7r45l68s27v/release-1500-gdal-1-11-1-mapserver-6-4-1_windowsXP.zip?dl=0\n" + \
                        "Then follow the steps 2, 3 and 4.\n" + \
                        " "
    elif System.Environment.Is64BitProcess == True:
        # 64 bit GDAL,OSR,OGR libraries
        GDAL_librariesFolderPath = os.path.join(ladybugFolderPath, "terrain shading mask libraries 64-bit")
        bitVersion = "x64"
        rhino5version = "x64"
        zipFileNameWithoutExtension = "release-1800-x64-gdal-1-11-4-mapserver-6-4-3"
        zipFileNameWithExtension = "release-1800-x64-gdal-1-11-4-mapserver-6-4-3.zip"
        windowsXPtext = " "
    
    folderCreated = createFolder(GDAL_librariesFolderPath)
    if folderCreated == False:
        maxVisibilityRadiusM = northRad = northVec = type = typeLabel = origin = standThickness = numOfContours = workingSubFolderPath = downloadTSVLink = unitConversionFactor = unitConversionFactor2 = None
        validInputData = False
        printMsg = "\"defaultFolder_\" input you supplied to the \"Ladybug Ladybug\" component is invalid.\n" + \
                   "Input the string in the following format (example): C:\someFolder.\n" + \
                   "Or do not input anything, in which case the default Ladybug folder will be used instead."
        return maxVisibilityRadiusM, northRad, northVec, type, typeLabel, origin, standThickness, numOfContours, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, unitConversionFactor2, validInputData, printMsg
    
    
    
    try:
        clr.AddReferenceToFileAndPath(os.path.join(GDAL_librariesFolderPath, "gdal_csharp.dll"))
        clr.AddReferenceToFileAndPath(os.path.join(GDAL_librariesFolderPath, "osr_csharp.dll"))
        clr.AddReferenceToFileAndPath(os.path.join(GDAL_librariesFolderPath, "ogr_csharp.dll"))
    except:
        pass
    
    gdal_dlls_loaded_Success =  "gdal_csharp" in [assembly.GetName().Name for assembly in clr.References]
    osr_dlls_loaded_Success = "osr_csharp" in [assembly.GetName().Name for assembly in clr.References]
    ogr_dlls_loaded_Success = "ogr_csharp" in [assembly.GetName().Name for assembly in clr.References]
    
    if gdal_dlls_loaded_Success and osr_dlls_loaded_Success and ogr_dlls_loaded_Success:
        # import GDAL libraries and register GDAL drivers
        global gdalc
        global osrc
        global ogrc
        import OSGeo.GDAL as gdalc
        import OSGeo.OSR as osrc
        import OSGeo.OGR as ogrc
        
        try:
            gdalc.Gdal.AllRegister()
        except System.Exception as e:
            # gdal_csharp, osr_csharp, ogr_csharp files are located in the "terrain shading mask libraries 32(64)-bit" folder, but some of the other files are not (for example: either step 4 was completed but step 3 wasn't)
            maxVisibilityRadiusM = northRad = northVec = type = typeLabel = origin = standThickness = numOfContours = workingSubFolderPath = downloadTSVLink = unitConversionFactor = unitConversionFactor2 = None
            validInputData = False
            printMsg = "The GDAL libraries are not installed properly. Please make sure that you followed all of the previously mentioned four steps.\n" + \
                       " \n" + \
                       "Check this page for graphical preview of the steps: \n" + \
                       "https://github.com/stgeorges/terrainShadingMask/blob/master/miscellaneous/Installation_instructions_Rhino5_%s.md\n" % rhino5version + \
                       " \n" + \
                       "If after this, you still get this same message (of GDAL libraries not installed properly) please post a question about this issue at:\n" + \
                       "www.grasshopper3d.com/group/ladybug/forum/topics/terrain-shading-mask-component-released."
            return maxVisibilityRadiusM, northRad, northVec, type, typeLabel, origin, standThickness, numOfContours, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, unitConversionFactor2, validInputData, printMsg
        
        # set the folderpath for "gdal-data" folder (GDAL support files)
        gdal_data_folderPath = os.path.join(GDAL_librariesFolderPath, "gdal-data")
        gdalc.Gdal.PushFinderLocation(gdal_data_folderPath)  # necessary for 64 bit GDAL .dlls in order to identify gcs.csv file
    
    else:
        # check if the "terrain shading mask libraries 32(64)-bit" folder is not empty.
        if os.listdir(GDAL_librariesFolderPath) != []:
            # "terrain shading mask libraries 32(64)-bit" folder is not empty (for example: either step 3 was completed but step 4 wasn't or vice versa)
            maxVisibilityRadiusM = northRad = northVec = type = typeLabel = origin = standThickness = numOfContours = workingSubFolderPath = downloadTSVLink = unitConversionFactor = unitConversionFactor2 = None
            validInputData = False
            printMsg = "The GDAL libraries are not installed properly. Please make sure that you followed all of the previously mentioned four steps.\n" + \
                       " \n" + \
                       "Check this page for graphical preview of the steps: \n" + \
                       "https://github.com/stgeorges/terrainShadingMask/blob/master/miscellaneous/Installation_instructions_Rhino5_%s.md\n" % rhino5version + \
                       " \n" + \
                       "If after this, you still get this same message (of GDAL libraries not installed properly) please post a question about this issue at:\n" + \
                       "www.grasshopper3d.com/group/ladybug/forum/topics/terrain-shading-mask-component-released."
            return maxVisibilityRadiusM, northRad, northVec, type, typeLabel, origin, standThickness, numOfContours, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, unitConversionFactor2, validInputData, printMsg
        else:
            # "terrain shading mask libraries 32(64)-bit" folder is EMPTY (neither step 3 nor step 4 have been performed)
            maxVisibilityRadiusM = northRad = northVec = type = typeLabel = origin = standThickness = numOfContours = workingSubFolderPath = downloadTSVLink = unitConversionFactor = unitConversionFactor2 = None
            validInputData = False
            printMsg = "This component requires GDAL libraries in order to be able to work. To install them, follow the four simple steps below.\n" + \
                       " \n" + \
                       "Here is a page with graphical preview of the steps: \n" + \
                       "https://github.com/stgeorges/terrainShadingMask/blob/master/miscellaneous/Installation_instructions_Rhino5_%s.md\n" % rhino5version + \
                       " \n" + \
                       "And this is the shortened explanation of the steps:\n" + \
                       " \n" + \
                       "1) Go to: http://gisinternals.com/release.php\n" + \
                       "Click on the latest \"GDAL 1.x.x and MapServer 6.x.x\" \"MSVC 2013 %s\" version (at the moment that may be: %s).\n" % (bitVersion,zipFileNameWithoutExtension) + \
                       "Then click on the link at the very top (at the moment that may be: %s). This will activate the .zip file download.\n" % zipFileNameWithExtension + \
                       " \n" + \
                       "2) Check if the downloaded .zip file has been blocked: right click on it, choose \"Properties\". If there is an \"Unblock\" button, click on it, then click on \"OK\". If there is no \"Unblock\" button, just click on \"OK\".\n" + \
                       " \n" + \
                       "3) Extract the downloaded .zip file content anywhere. Then copy the content from its \"bin\" folder to the \"%s\" folder.\n" % GDAL_librariesFolderPath + \
                       "So copy the content of the \"bin\" folder, not the \"bin\" folder itself.\n" + \
                       " \n" + \
                       "4) Copy the content from the \"bin\gdal\csharp\" folder to the same \"%s\" folder.\n" % GDAL_librariesFolderPath + \
                       "So copy the content of the \"bin\gdal\csharp\" folder, not the \"bin\gdal\csharp\" folder itself.\n" + \
                       " \n" + \
                       "That's it!\n" + \
                       "Now run the component (set the \"_runIt\" to \"True\").\n" + \
                       " \n" + \
                       "%s" % windowsXPtext
            return maxVisibilityRadiusM, northRad, northVec, type, typeLabel, origin, standThickness, numOfContours, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, unitConversionFactor2, validInputData, printMsg
    
    
    
    # check inputs
    if (type == None):
        type = 1  # default
        typeLabel = "mesh-circular"  # default
    if (type == 0):
        typeLabel = "mesh-rectangular"
    elif (type == 1):
        typeLabel = "mesh-circular"
    elif (type == 2):
        typeLabel = "surface-rectangular"
    elif (type == 3):
        typeLabel = "surface-circular"
    elif (type < 0) or (type > 3):
        type = 0
        typeLabel = "mesh-rectangular"
        print "type_ input only supports values 0 to 3.\n" + \
              "type_ input set to 0 (mesh-rectangular)."
    
    
    if (origin == None):
        origin = Rhino.Geometry.Point3d(0, 0, 0)
    
    
    if (standThickness == None):
        standThickness = 0  # no stand will be created
    elif (standThickness < 0):
        standThickness = 0
        print "standThickness_ input can not be lower than 0. It can only be either 0 (no stand) or higher.\n" + \
              "standThickness_ input set to 0 (no stand)."
    
    if (numOfContours == None):
        numOfContours = 10  # default
    elif (numOfContours < 0):
        numOfContours = 0
        print "numOfContours_ input can not be lower than 0. It can only be either 0 (no elevation contours created) or higher.\n" + \
              "numOfContours_ input set to 0 (no elevation contours will be created)."
    
    
    # for locations from .epw files, the maxVisibilityRadius can be estimated from .epw file's field N24 (visibility) and its maximal annual hourly value.
    # Still this value may not be the maximal one for the chosen location.
    if (maxVisibilityRadiusM == None):
        maxVisibilityRadiusM = 200  # default in meters
    elif (maxVisibilityRadiusM >= 20) and (maxVisibilityRadiusM < 200):
        maxVisibilityRadiusM = 200  # values less than 150m can download invalid .tif file from opentopography.org. So the .tif file will always be downloaded with the minimal radius of 200 meters
    elif (maxVisibilityRadiusM < 20):
        maxVisibilityRadiusM = northRad = northVec = type = typeLabel = origin = standThickness = numOfContours = workingSubFolderPath = downloadTSVLink = unitConversionFactor = unitConversionFactor2 = None
        validInputData = False
        printMsg = "radius_ input only supports values equal or larger than 20 meters."
        
        return maxVisibilityRadiusM, northRad, northVec, type, typeLabel, origin, standThickness, numOfContours, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, unitConversionFactor2, validInputData, printMsg
    elif (maxVisibilityRadiusM > 100000):
        maxVisibilityRadiusM = northRad = northVec = type = typeLabel = origin = standThickness = numOfContours = workingSubFolderPath = downloadTSVLink = unitConversionFactor = unitConversionFactor2 = None
        validInputData = False
        printMsg = "Radii longer than 100 000 meters (100 kilometers) are not supported, due to possibility of crashing the Rhino.\n" + \
                   " \n" + \
                   "ATTENTION!!! Have in mind that even radii of a couple of thousands of meters may require stronger PC configurations and 64 bit version of Rhino 5. Otherwise Rhino 5 may crash."
        
        return maxVisibilityRadiusM, northRad, northVec, type, typeLabel, origin, standThickness, numOfContours, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, unitConversionFactor2, validInputData, printMsg
    
    #arcAngleD = math.degrees( math.atan( maxVisibilityRadiusM / (6371000+elevation) ) )  # assumption of Earth being a sphere
    #arcLength = (arcAngleD*math.pi*R)/180
    # correction of maxVisibilityRadiusM length due to light refraction can not be calculated, so it is assumed that arcLength = maxVisibilityRadiusM. maxVisibilityRadiusM variable will be used from now on instead of arcLength.
    
    
    if (north == None):
        northRad = 0  # default, in radians
        northVec = Rhino.Geometry.Vector3d(0,1,0)
    else:
        try:  # check if it's a number
            north = float(north)
            if north < 0 or north > 360:
                maxVisibilityRadiusM = northRad = northVec = type = typeLabel = origin = standThickness = numOfContours = workingSubFolderPath = downloadTSVLink = unitConversionFactor = unitConversionFactor2 = None
                validInputData = False
                printMsg = "Please input north angle value from 0 to 360."
                return maxVisibilityRadiusM, northRad, northVec, type, typeLabel, origin, standThickness, numOfContours, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, unitConversionFactor2, validInputData, printMsg
        except Exception, e:  # check if it's a vector
            north.Unitize()
        
        northRad, northVec = lb_photovoltaics.angle2northClockwise(north)
    northVec.Unitize()
    
    
    if workingFolderPath == None:
        # nothing inputted to "workingFolder_" input, use default Ladybug folder instead (C:\ladybug or C:\Users\%USERNAME%\AppData\Roaming\Ladybug.)
        workingSubFolderPath = os.path.join(ladybugFolderPath, "terrain files")
    else:
        # something inputted to "workingFolder_" input
        workingSubFolderPath = os.path.join(workingFolderPath, "terrain files")
    folderCreated = createFolder(workingSubFolderPath)
    if folderCreated == False:
        maxVisibilityRadiusM = northRad = northVec = type = typeLabel = origin = standThickness = numOfContours = workingSubFolderPath = downloadTSVLink = unitConversionFactor = unitConversionFactor2 = None
        validInputData = False
        printMsg = "workingFolder_ input is invalid.\n" + \
                   "Input the string in the following format (example): C:\someFolder.\n" + \
                   "Or do not input anything, in which case a default Ladybug folder will be used instead."
        return maxVisibilityRadiusM, northRad, northVec, type, typeLabel, origin, standThickness, numOfContours, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, unitConversionFactor2, validInputData, printMsg
    
    if downloadTSVLink == None:
        downloadTSVLink = "https://raw.githubusercontent.com/stgeorges/terrainShadingMask/master/objFiles/0_terrain_shading_masks_download_links.tsv"
    
    #unitConversionFactor = lb_preparation.checkUnits()  # factor to convert Rhino document units to meters.
    unitConversionFactor = 1  # unitConversionFactor is always fixed to "1" to avoid problems when .obj files are exported from Rhino document (session) in one Units, and then imported in some other Rhino document (session) with different Units
    
    unitConversionFactor2 = lb_preparation.checkUnits()
    # correcting Ladybug_ladybug conversion factors to higher precision
    if unitConversionFactor2 == 0.305: unitConversionFactor2 = 0.3048
    
    
    validInputData = True
    printMsg = "ok"
    
    return maxVisibilityRadiusM, northRad, northVec, type, typeLabel, origin, standThickness, numOfContours, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, unitConversionFactor2, validInputData, printMsg


def distanceBetweenTwoPoints(latitude1D, longitude1D, maxVisibilityRadiusM):
    # "Distance/bearing between two points (inverse solution)" by Vincenty solution
    # based on JavaScript code made by Chris Veness
    # http://www.movable-type.co.uk/scripts/latlong-vincenty.html
    
    # setting the latitude2D, longitude2D according to SRTM latitude range boundaries (-56 to 60)
    if latitude1D >= 0:
        # northern hemishere:
        latitude2D = 60
    elif latitude1D < 0:
        # southern hemishere:
        latitude2D = -56
    longitude2D = longitude1D
    
    # for WGS84:
    a = 6378137  # equatorial radius, meters
    b = 6356752.314245  # polar radius, meters
    f = 0.00335281066474  # flattening (ellipticity, oblateness) parameter = (a-b)/a, dimensionless
    
    latitude1R = math.radians(latitude1D)
    latitude2R = math.radians(latitude2D)
    longitude1R = math.radians(longitude1D)
    longitude2R = math.radians(longitude2D)
    
    L = longitude2R - longitude1R
    tanU1 = (1-f) * math.tan(latitude1R)
    cosU1 = 1 / math.sqrt((1 + tanU1*tanU1))
    sinU1 = tanU1 * cosU1
    tanU2 = (1-f) * math.tan(latitude2R)
    cosU2 = 1 / math.sqrt((1 + tanU2*tanU2))
    sinU2 = tanU2 * cosU2
    longitudeR = L
    longitudeR_ = 0
    
    for i in range(100):
        sinLongitudeR = math.sin(longitudeR)
        cosLongitudeR = math.cos(longitudeR)
        sinSqSigma = (cosU2*sinLongitudeR) * (cosU2*sinLongitudeR) + (cosU1*sinU2-sinU1*cosU2*cosLongitudeR) * (cosU1*sinU2-sinU1*cosU2*cosLongitudeR)
        sinSigma = math.sqrt(sinSqSigma)
        cosSigma = sinU1*sinU2 + cosU1*cosU2*cosLongitudeR
        sigma = math.atan2(sinSigma, cosSigma)
        sinBearingAngleR = cosU1 * cosU2 * sinLongitudeR / sinSigma
        cosSqBearingAngleR = 1 - sinBearingAngleR*sinBearingAngleR
        if cosSqBearingAngleR == 0:
            # if distanceM is measured along the equator line (latitude1D = latitude2D = 0, longitude1D != longitude2D != 0)
            cos2SigmaM = 0
        else:
            cos2SigmaM = cosSigma - 2*sinU1*sinU2/cosSqBearingAngleR
        C = f/16*cosSqBearingAngleR*(4+f*(4-3*cosSqBearingAngleR))
        longitudeR_ = longitudeR
        longitudeR = L + (1-C) * f * sinBearingAngleR * (sigma + C*sinSigma*(cos2SigmaM+C*cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)))
    
    uSq = cosSqBearingAngleR * (a*a - b*b) / (b*b)
    A = 1 + uSq/16384*(4096+uSq*(-768+uSq*(320-175*uSq)))
    B = uSq/1024 * (256+uSq*(-128+uSq*(74-47*uSq)))
    deltaSigma = B*sinSigma*(cos2SigmaM+B/4*(cosSigma*(-1+2*cos2SigmaM*cos2SigmaM) - B/6*cos2SigmaM*(-3+4*sinSigma*sinSigma)*(-3+4*cos2SigmaM*cos2SigmaM)))
    
    distanceM = b*A*(sigma-deltaSigma)  # in meters
    
    bearingAngleForwardR = math.atan2(cosU2*sinLongitudeR,  cosU1*sinU2-sinU1*cosU2*cosLongitudeR)
    bearingAngleReverseR = math.atan2(cosU1*sinLongitudeR, -sinU1*cosU2+cosU1*sinU2*cosLongitudeR)
    
    bearingAngleForwardD = math.degrees(bearingAngleForwardR)
    bearingAngleReverseD = math.degrees(bearingAngleReverseR)
    
    
    if latitude1D >= 0:
        SRTMlimit = "60 North"
    elif latitude1D < 0:
        SRTMlimit = "-56 South"
    
    if distanceM < 200:
        correctedMaskRadiusM = "dummy"
        validVisibilityRadiusM = False
        printMsg = "This component dowloads free topography data from opentopography.org in order to create a terrain for the chosen _location.\n" + \
                   "But mentioned free topography data has limits: from -56 South to 60 North latitude.\n" + \
                   "The closer the location is to upper mentioned boundaries, the inputted \"radius_\" value may have be shrank to make sure that the boundaries are not exceeded.\n" + \
                   "In this case the _location you chose is very close (less than 20 meters) to the %s latitude boundary.\n" % SRTMlimit + \
                   "It is not possible to create a terrain for locations less than 200 meters close to mentioned boundary, as this _location is.\n" + \
                   "Try using the Ladybug \"Terrain Generator\" component instead."
    else:
        # shortening the maxVisibilityRadiusM according to the distance remained to the SRTM latitude range boundaries (-56 to 60)
        if distanceM < maxVisibilityRadiusM:
            print "distanceM < maxVisibilityRadiusM: ", distanceM < maxVisibilityRadiusM
            print "distanceM, maxVisibilityRadiusM: ", distanceM, maxVisibilityRadiusM
            correctedMaskRadiusM = int(distanceM)  # int(distanceM) will always perform the math.floor(distanceM)
            validVisibilityRadiusM = False
            printMsg = "This component downloads free topography data from opentopography.org in order to create a terrain for the chosen _location.\n" + \
                       "But mentioned free topography data has limits: from -56 South to 60 North latitude.\n" + \
                       "The closer the location is to upper mentioned boundaries, the inputted \"radius_\" value may have to be shrank to make sure that the boundaries are not exceeded.\n" + \
                       "In this case the _location you chose is %s meters away from the %s latitude boundary.\n" % (correctedMaskRadiusM, SRTMlimit) + \
                       " \n" + \
                       "Please supply the \"radius_\" input with value: %s.\n" % correctedMaskRadiusM
        elif distanceM >= maxVisibilityRadiusM:
            correctedMaskRadiusM = maxVisibilityRadiusM
            validVisibilityRadiusM = True
            printMsg = "ok"
    
    return correctedMaskRadiusM, validVisibilityRadiusM, printMsg


def destinationLatLon(latitude1D, longitude1D, maxVisibilityRadiusM):
    # "Destination point given distance and bearing from start point" by Vincenty solution
    # based on JavaScript code made by Chris Veness
    # http://www.movable-type.co.uk/scripts/latlong-vincenty.html
    
    # for WGS84:
    a = 6378137  # equatorial radius, meters
    b = 6356752.314245  # polar radius, meters
    f = 0.00335281066474  # flattening (ellipticity, oblateness) parameter = (a-b)/a, dimensionless
    
    bearingAnglesR = [math.radians(0), math.radians(180), math.radians(270), math.radians(90)]  # top, bottom, left, right
    latitudeLongitudeRegion = []
    for bearingAngle1R in bearingAnglesR:
        latitude1R = math.radians(latitude1D)
        longitude1R = math.radians(longitude1D)
        sinbearingAngle1R = math.sin(bearingAngle1R)
        cosbearingAngle1R = math.cos(bearingAngle1R)
        tanU1 = (1 - f) * math.tan(latitude1R)
        cosU1 = 1 / math.sqrt(1 + tanU1 * tanU1)
        sinU1 = tanU1 * cosU1
        sigma1 = math.atan2(tanU1, cosbearingAngle1R)
        sinBearingAngle1R = cosU1 * sinbearingAngle1R
        cosSqBearingAngle1R = 1 - (sinBearingAngle1R * sinBearingAngle1R)
        uSq = cosSqBearingAngle1R * (a * a - (b * b)) / (b * b)
        A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - (175 * uSq))))
        B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - (47 * uSq))))
        sigma = maxVisibilityRadiusM / (b * A)  # maxVisibilityRadiusM in meters
        sigma_ = 0
        while abs(sigma - sigma_) > 1e-12:
            cos2sigmaM = math.cos(2 * sigma1 + sigma)
            sinsigma = math.sin(sigma)
            cossigma = math.cos(sigma)
            deltaSigma = B * sinsigma * (cos2sigmaM + B / 4 * (cossigma * (-1 + 2 * cos2sigmaM * cos2sigmaM) - (B / 6 * cos2sigmaM * (-3 + 4 * sinsigma * sinsigma) * (-3 + 4 * cos2sigmaM * cos2sigmaM))))
            sigma_ = sigma
            sigma = maxVisibilityRadiusM / (b * A) + deltaSigma
        
        tmp = sinU1 * sinsigma - (cosU1 * cossigma * cosbearingAngle1R)
        latitude2R = math.atan2(sinU1 * cossigma + cosU1 * sinsigma * cosbearingAngle1R, (1 - f) * math.sqrt(sinBearingAngle1R * sinBearingAngle1R + tmp * tmp))
        longitudeR = math.atan2(sinsigma * sinbearingAngle1R, cosU1 * cossigma - (sinU1 * sinsigma * cosbearingAngle1R))
        C = f / 16 * cosSqBearingAngle1R * (4 + f * (4 - (3 * cosSqBearingAngle1R)))
        L = longitudeR - ((1 - C) * f * sinBearingAngle1R * (sigma + C * sinsigma * (cos2sigmaM + C * cossigma * (-1 + 2 * cos2sigmaM * cos2sigmaM))))
        longitude2R = (longitude1R + L + 3 * math.pi) % (2 * math.pi) - math.pi  # normalise to -180...+180
        bearingAngle2R = math.atan2(sinBearingAngle1R, -tmp)
        
        latitude2D = math.degrees(latitude2R)
        longitude2D = math.degrees(longitude2R)
        bearingAngle2D = math.degrees(bearingAngle2R)
        if bearingAngle2D < 0:
            bearingAngle2D = 360-abs(bearingAngle2D)
        
        latitudeLongitudeRegion.append(latitude2D)
        latitudeLongitudeRegion.append(longitude2D)
    
    # latitude positive towards north, longitude positive towards east
    latitudeTopD, dummyLongitudeTopD, latitudeBottomD, dummyLongitudeBottomD, dummyLatitudeLeftD, longitudeLeftD, dummyLatitudeRightD, longitudeRightD = latitudeLongitudeRegion
    
    # generate download link for raster region
    # based on: http://www.opentopography.org/developers
    downloadRasterLink = "http://opentopo.sdsc.edu/otr/getdem?demtype=SRTMGL1&west=%s&south=%s&east=%s&north=%s&outputFormat=GTiff" % (longitudeLeftD,latitudeBottomD,longitudeRightD,latitudeTopD)  # 1 arc second
    
    return downloadRasterLink


def import_export_origin_0_0_0_and_terrainShadingMask_from_objFile(importExportObj, objFilePath, fileNameIncomplete, heightM, minVisibilityRadiusM, maxVisibilityRadiusM, elevationM=None, shadingMaskSrf=None, origin=None):
        
        objFilePath2 = chr(34) + objFilePath + chr(34)
        
        if importExportObj == "importObj":
            # import origin_0_0_0, terrainShadingMask from .obj file
            sc.doc = Rhino.RhinoDoc.ActiveDoc
            
            commandString = "_-Import %s _Enter" % objFilePath2; echo = False
            importObjSuccess = rs.Command(commandString, echo)
            
            terrainShadingMaskUnjoined = []
            objIds = rs.LastCreatedObjects(False)
            if objIds != None:
                for rhinoId in objIds:
                    obj = sc.doc.Objects.Find(rhinoId).Geometry
                    if isinstance(obj, Rhino.Geometry.Point):
                        origin_0_0_0 = Rhino.Geometry.Point3d(obj.Location) # convert Point to Point3d
                    elif isinstance(obj, Rhino.Geometry.Brep):
                        terrainShadingMaskUnjoined.append(obj)
                rs.DeleteObjects(objIds)
                sc.doc = ghdoc
                
                # join brep objects
                tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
                terrainShadingMask = Rhino.Geometry.Brep.MergeBreps(terrainShadingMaskUnjoined,tol)  # terrainShadingMask joined
            elif objIds == None:
                # this happens when a user opened a new Rhino file, while runIt_ input has been set to True. In this case the rs.LastCreatedObjects function returns: None
                terrainShadingMask = origin_0_0_0 = None
        
        elif importExportObj == "exportObj":
            # export the generated terrain shading mask to .obj file
            sc.doc = Rhino.RhinoDoc.ActiveDoc
            objIds = []
            objs = [shadingMaskSrf, Rhino.Geometry.Point(origin)]
            for obj in objs:
                objId = sc.doc.Objects.Add(obj)
                objIds.append(objId)
            rs.SelectObjects(objIds)  # select objects for _-Export
            commandString = "_-testMakeValidForV2 _Enter"  # convert the terrainShadingMaskUnscaledUnrotated from Surface of Revolution to NURBS Surface
            commandString2 = "_-Export %s Geometry=NURBS _Enter" % objFilePath2; echo = False
            exportObjSuccess = rs.Command(commandString, echo)
            exportObjSuccess2 = rs.Command(commandString2, echo)
            rs.DeleteObjects(objIds)  # delete the objects added to Rhino document, after the _-Export
            sc.doc = ghdoc
            
            # change exported .obj file heading
            objFileLines = []
            myFile = open(objFilePath,"r")
            for line in myFile.xreadlines():
                objFileLines.append(line)
            myFile.close()
            
            
            locationNameCorrected_latitude_longitude = (fileNameIncomplete.split("_TERRAIN_MASK")[0]).replace("_"," ")
            
            nowUTC = datetime.datetime.utcnow()  # UTC date and time
            UTCdateTimeString = str(nowUTC.year) + "-" + str(nowUTC.month) + "-" + str(nowUTC.day) + " " + str(nowUTC.hour) + ":" + str(nowUTC.minute) + ":" + str(nowUTC.second)
            
            myFile = open(objFilePath,"w")
            for line in objFileLines:
                if line == "# Rhino\n":
                    line = "# Rhino\n# Terrain shading mask generated by Grasshopper Ladybug Honeybee plugin\n# True North direction is set to the Y axis\n# Location: %s\n# Elevation: %s m\n# Visibility radius: %s-%s km\n# Mask radius: 200 document units\n# Created on (UTC): %s\n" % (locationNameCorrected_latitude_longitude, elevationM, minVisibilityRadiusM/1000, int(maxVisibilityRadiusM/1000), UTCdateTimeString)
                else:
                    pass
                myFile.write(line)
            myFile.close()
            
            
            terrainShadingMask = origin_0_0_0 = None  # not needed for "exportObj"
        
        return terrainShadingMask, origin_0_0_0


def downloadFile(downloadLink, downloadedFilePath):
    
    try:
        # try "secure http" download
        client = System.Net.WebClient()
        client.DownloadFile(downloadLink, downloadedFilePath)
    except Exception, e:
        try:
            # "secure http" failed, try "http" download:
            filePathDummy, infoHeader = urllib.urlretrieve(downloadLink, downloadedFilePath)
        except Exception, e:
            # downloading of file failed
            fileDownloaded = False
            return fileDownloaded
    
    fileDownloaded = True
    return fileDownloaded


def checkObjRasterFile(fileNameIncomplete, workingSubFolderPath, downloadTSVLink, heightM, minVisibilityRadiusM, maxVisibilityRadiusM, maskStyleLabel):
    
    # convert the float to integer if minVisibilityRadiusM == 0 (to avoid "0.0" in the .obj fileName)
    if minVisibilityRadiusM == 0:
        minVisibilityRadiusKM = 0
    else:
        minVisibilityRadiusKM = minVisibilityRadiusM/1000
    
    fileName = fileNameIncomplete + "_visibility=" + str(minVisibilityRadiusKM) + "-" + str(round(maxVisibilityRadiusM/1000, 2)) + "KM"
    fileName2 = fileNameIncomplete + "_visibility=" + str(round(maxVisibilityRadiusM/1000, 2)) + "KM"
    objFileNamePlusExtension = fileName + "_" + maskStyleLabel + ".obj"
    rasterFileNamePlusExtension = fileName2 + ".tif"
    rasterFileNamePlusExtension_aeqd = fileName2 + "_aeqd" + ".tif"
    tsvFileNamePlusExtension = "0_terrain_shading_masks_download_links" + ".tsv"
    vrtFileNamePlusExtension = fileName + "_" + maskStyleLabel + "_aeqd" + ".vrt"
    
    objFilePath = os.path.join(workingSubFolderPath, objFileNamePlusExtension)
    rasterFilePath = os.path.join(workingSubFolderPath, rasterFileNamePlusExtension)
    rasterFilePath_aeqd = os.path.join(workingSubFolderPath, rasterFileNamePlusExtension_aeqd)
    tsvFilePath = os.path.join(workingSubFolderPath, tsvFileNamePlusExtension)
    vrtFilePath = os.path.join(workingSubFolderPath, vrtFileNamePlusExtension)
    
    
    # chronology labels:  I, II, 1, 2, A, B, a, b
    
    ##### I) check if .obj file exist:
    objFileAlreadyExists = os.path.exists(objFilePath)
    if objFileAlreadyExists == True:
        # .obj file already created. Import it
        terrainShadingMask, origin_0_0_0 = import_export_origin_0_0_0_and_terrainShadingMask_from_objFile("importObj", objFilePath, fileNameIncomplete, heightM, minVisibilityRadiusM, maxVisibilityRadiusM)
        if (terrainShadingMask != None) and (origin_0_0_0 != None):
            # extract "elevationM" data from the .obj file
            myFile = open(objFilePath,"r")
            for line in myFile.xreadlines():
                if "Elevation" in line:
                    splittedLine = line.split(" ")
                    elevationM = splittedLine[2]
                    #elevationM = float(splittedLine[2])/0.305  # ovo mi ne treba. "elevation" output ce uvek da bude u meters
                    break
            else:
                elevationM = None  # is somebody opened the .obj file and deleted the heading for some reason
            myFile.close()
            
            rasterFilePath = "needless"
            valid_Obj_or_Raster_file = True
            printMsg = "ok"
        elif (terrainShadingMask == None) and (origin_0_0_0 == None):
            elevationM = None
            rasterFilePath = "needless"  # dummy
            valid_Obj_or_Raster_file = False
            printMsg = "You opened a new Rhino file while \"runIt_\" input has been set to True.\n" + \
                       "This component relies itself on Rhino document, and opening a new Rhino file results in component not working properly.\n" + \
                       "Just set the \"runIt_\" input back to False, and then again to True, to make it work again, with the newest Rhino file."
    elif objFileAlreadyExists == False:
        ##### II).obj file can not be found in "workingFolderPath" folder (example: "C:\ladybug\terrain shading masks").
        #####     check if .obj file is listed in "0_terrain_shading_masks_download_links.tsv"  file (download the "0_terrain_shading_masks_download_links.tsv" file first)
        terrainShadingMask = origin_0_0_0 = elevationM = None
        
        # connectedToInternet first check
        connectedToInternet1 = System.Net.NetworkInformation.NetworkInterface.GetIsNetworkAvailable()
        if connectedToInternet1 == False:
            # connectedToInternet second check
            try:
                client = System.Net.WebClient()
                client.OpenRead("http://www.google.com")
                connectedToInternet = True
            except:
                connectedToInternet = False
                # you are not connected to the Internet
        elif connectedToInternet1 == True:
            # no need for connectedToInternet second check
            connectedToInternet = True
        
        
        if connectedToInternet == False:
            # you are NOT connected to the Internet, exit this function
            rasterFilePath = "download failed"
            terrainShadingMask = origin_0_0_0 = None
            valid_Obj_or_Raster_file = False
            printMsg = "This component requires you to be connected to the Internet, in order to create a terrain.\n" + \
                       "Please do connect, then rerun the component (set \"_runIt\" to False, then to True)."
        elif connectedToInternet == True:
            # you ARE connected to the Internet
            
            # download "0_terrain_shading_masks_download_links.tsv" (no need to check if it is already in the "workingSubFolderPath" as a newer version of "0_terrain_shading_masks_download_links.tsv" file may exist online)
            tsvFileDownloaded = downloadFile(downloadTSVLink, tsvFilePath)
            
            if tsvFileDownloaded == False:
                #### II.2 "0_terrain_shading_masks_download_links.tsv" has NOT been downloaded
                if downloadUrl_ != None:
                    ### II.2.A inputted downloadUrl_ is either not valid, or the "0_terrain_shading_masks_download_links.tsv" file is not uploaded at that address
                    rasterFilePath = "download failed"
                    terrainShadingMask = origin_0_0_0 = None
                    valid_Obj_or_Raster_file = False
                    printMsg = "The address plugged into downloadUrl_ input is incorrect.\n" + \
                               "Try unplugging it, so that the component tries to use its default address."
                elif downloadUrl_ == None:
                    ### II.2.B default downloadUrl_ is not valid anymore, nevertheless try ignoring the "0_terrain_shading_masks_download_links.tsv" file and create the .obj file from a .tif file
                    ### it may also happen that "Error 404.htm" page will be downloaded as "0_terrain_shading_masks_download_links.tsv" file
                    ### go to switch
                    pass
            
            elif tsvFileDownloaded == True:
                #### II.1 "0_terrain_shading_masks_download_links.tsv" IS downloaded
                
                # checking if .obj file has been listed in "0_terrain_shading_masks_download_links.tsv"
                myFile = open(tsvFilePath,"r")
                downloadObjLink = None
                for line in myFile.xreadlines():
                    if fileName in line:
                        splittedLineL = line.split("\t")  # split the line with "tab"
                        for string in splittedLineL:
                            if "http" in string:
                                downloadObjLink_unstripped = string.split("\n")[0]  # split the downloadObjLink and "\n"
                                downloadObjLink = System.String.strip(downloadObjLink_unstripped)  # remove white spaces from the beginning, end of the downloadObjLink
                        break
                myFile.close()
                
                if downloadObjLink != None:
                    ### II.1.A .obj file IS listed in "0_terrain_shading_masks_download_links.tsv", so download it
                    objFileDownloadedDummy = downloadFile(downloadObjLink, objFilePath)
                    terrainShadingMask, origin_0_0_0 = import_export_origin_0_0_0_and_terrainShadingMask_from_objFile("importObj", objFilePath, fileNameIncomplete, heightM, minVisibilityRadiusM, maxVisibilityRadiusM)
                    rasterFilePath = "needless"
                    valid_Obj_or_Raster_file = True
                    printMsg = "ok"
                elif downloadObjLink == None:
                    ### II.1.B .obj file is NOT listed in "0_terrain_shading_masks_download_links.tsv", try to create it from a .tif file
                    ### go to switch
                    pass
    
    ### switch
    if ((objFileAlreadyExists == False) and (connectedToInternet == True) and (tsvFileDownloaded == False) and (downloadUrl_ == None))   or   ((objFileAlreadyExists == False) and (connectedToInternet == True) and (tsvFileDownloaded == True) and (downloadObjLink == None)):
        ### .obj file could not be found, due to one of the following two reasons:
        ### - default downloadUrl_ is not valid anymore (II.2.B); or
        ### - .obj file is NOT listed in "0_terrain_shading_masks_download_links.tsv" (II.1.B);
        ### so try to create an .obj file from a .tif file
        terrainShadingMask = origin_0_0_0 = "needs to be calculated"
        rasterFileAlreadyExists = os.path.exists(rasterFilePath)
        if rasterFileAlreadyExists == True:
            ## .tif file already downloaded previously
            valid_Obj_or_Raster_file = True
            printMsg = "ok"
        if rasterFileAlreadyExists == False:
            ## .tif file has not been downloaded up until now, download it
            
            # first check the location before download, so that it fits the opentopography.org limits (-56 to 60(59.99999 used instead of 60) latitude):
            if locationLatitudeD > 59.99999:
                # location beyond the -56 to 60 latittude limits
                # (correctedMaskRadiusM < 1) or (correctedMaskRadiusM < maxVisibilityRadiusM)
                terrainShadingMask = origin_0_0_0 = None
                valid_Obj_or_Raster_file = False
                rasterFilePath = "needless"  # dummy
                printMsg = "This component dowloads free topography data from opentopography.org in order to create a terrain for the chosen _location.\n" + \
                           "But mentioned free topography data has its limits: from -56 South to 60 North latitude.\n" + \
                           "Your _location's latitude exceeds the upper mentioned limits.\n" + \
                           " \n" + \
                           "Try using the Ladybug \"Terrain Generator\" component instead."
            else:
                # location within the -56 to 60 latittude limits
                # correct (shorten) the maxVisibilityRadiusM according to the distance remained to the SRTM latitude range boundaries (-56 to 60)
                correctedMaskRadiusM, validVisibilityRadiusM, printMsg = distanceBetweenTwoPoints(locationLatitudeD, locationLongitudeD, maxVisibilityRadiusM)
                if validVisibilityRadiusM == True:
                    # (correctedMaskRadiusM >= maxVisibilityRadiusM)
                    downloadRasterLink_withCorrectedMaskRadiusKM = destinationLatLon(locationLatitudeD, locationLongitudeD, correctedMaskRadiusM)
                    # new rasterFileNamePlusExtension and rasterFilePath corrected according to new correctedMaskRadiusM
                    rasterFileNamePlusExtension_withCorrectedMaskRadiusKM = fileNameIncomplete + "_visibility=" + str(round(maxVisibilityRadiusM/1000, 2)) + "KM" + ".tif"  # rasterFileNamePlusExtension_withCorrectedMaskRadiusKM will always be used instead of rasterFilePath from line 647 !!!
                    rasterFilePath_withCorrectedMaskRadiusKM = os.path.join(workingSubFolderPath, rasterFileNamePlusExtension_withCorrectedMaskRadiusKM)
                    tifFileDownloaded = downloadFile(downloadRasterLink_withCorrectedMaskRadiusKM, rasterFilePath_withCorrectedMaskRadiusKM)
                    if tifFileDownloaded:
                        terrainShadingMask = origin_0_0_0 = None
                        valid_Obj_or_Raster_file = True
                        printMsg = "ok"
                    else:
                        rasterFilePath = "download failed"
                        terrainShadingMask = origin_0_0_0 = elevationM = None
                        valid_Obj_or_Raster_file = False
                        printMsg = "This component requires topography data to be downloaded from opentopography.org as a prerequisite for creating a terrain. It has just failed to do that. Try the following two fixes:\n" + \
                                   " \n" + \
                                   "1) Sometimes due to large number of requests, the component fails to download the topography data even if opentopography.org website and their services are up and running.\n" + \
                                   "In this case, wait a couple of seconds and try reruning the component.\n" + \
                                   " \n" + \
                                   "2) opentopography.org website could be up and running, but their SRTM service may be down (this already happened before).\n" + \
                                   "Try again in a couple of hours.\n" + \
                                   " \n" + \
                                   "If each of two mentioned advices fails, open a new topic about this issue on: www.grasshopper3d.com/group/ladybug/forum."
                
                elif validVisibilityRadiusM == False:
                    # (correctedMaskRadiusM < 1) or (correctedMaskRadiusM < maxVisibilityRadiusM)
                    elevationM = None
                    valid_Obj_or_Raster_file = False
                    rasterFilePath = "needless"  # dummy
                    #printMsg - from distanceBetweenTwoPoints function
    
    
    return terrainShadingMask, origin_0_0_0, fileName, objFilePath, rasterFilePath, rasterFilePath_aeqd, rasterFileNamePlusExtension_aeqd, vrtFilePath, elevationM, valid_Obj_or_Raster_file, printMsg


def createTerrainMeshBrep(GDAL_librariesFolderPath, objFilePath, rasterFilePath, rasterFilePath_aeqd, rasterFileNamePlusExtension_aeqd, vrtFilePath, locationLatitudeD, locationLongitudeD, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, type, origin, legendPar, unitConversionFactor, unitConversionFactor2):
    
    # open the raster file
    accessReadOnly = gdalc.Access.GA_ReadOnly
    dataset = gdalc.Gdal.Open(rasterFilePath, accessReadOnly)
    
    # input crs
    inputCRS = osrc.SpatialReference("")
    inputCRS.ImportFromEPSG(4326)
    integer, datasetInputCRS = inputCRS.ExportToWkt()
    
    # output crs
    outputCRS = osrc.SpatialReference("")
    # by http://stackoverflow.com/a/9188972/3137724 (link given by Even Rouault even.rouault@spatialys.com)
    UTMzone = (math.floor((locationLongitudeD + 180)/6) % 60) + 1
    if locationLatitudeD >= 0:
        # for northern hemisphere
        northOrsouth = "north"
    elif locationLatitudeD < 0:
        # for southern hemisphere
        northOrsouth = "south"
    
    outputCRS_wktString = "+proj=utm +zone=%s +%s +datum=WGS84 +ellps=WGS84" % (int(UTMzone), northOrsouth)
    outputCRS.ImportFromProj4(outputCRS_wktString)
    integer2, datasetOutputCRS = outputCRS.ExportToWkt()
    
    # datasetWarped (aeqd 3 arc-second)
    resamplingMethod = gdalc.ResampleAlg.GRA_Bilinear; maximalErrorThreshold = 0.0
    datasetWarped = gdalc.Gdal.AutoCreateWarpedVRT(dataset, datasetInputCRS, datasetOutputCRS, resamplingMethod, maximalErrorThreshold)
    dataset.Dispose()
    
    # save the datasetWarped to a new aeqd.tif file
    geoTransform = System.Array[System.Double]([0.0,1.0,2.0,3.0,4.0,5.0])
    datasetWarped.GetGeoTransform(geoTransform)
    topLeftX, westEastPixelResolution, rotation1, topLeftY, rotation2, northSouthPixelResolution = geoTransform
    numOfCellsInX = datasetWarped.RasterXSize  # numOfCellsInX is actually datasetWarped.RasterXSize - 1 !!
    numOfCellsInY = datasetWarped.RasterYSize  # numOfCellsInY is actually datasetWarped.RasterYSize - 1 !!
    cellsizeX = westEastPixelResolution
    cellsizeY = northSouthPixelResolution
    
    # read the elevation values
    bandWarped = datasetWarped.GetRasterBand(datasetWarped.RasterCount)
    ptZL = System.Array.CreateInstance(System.Int32, bandWarped.XSize*bandWarped.YSize)
    bandWarped.ReadRaster(0, 0, datasetWarped.RasterXSize, datasetWarped.RasterYSize, ptZL, datasetWarped.RasterXSize, datasetWarped.RasterYSize, 0, 0)
    
    # calculate the starting point (upper left corner) of terrain mesh
    locationPt_projectedCoordinates = ogrc.Geometry(ogrc.wkbGeometryType.wkbPoint)
    locationPt_projectedCoordinates.AddPoint(locationLongitudeD, locationLatitudeD, 0)
    
    coordinateTransformation = osrc.Osr.CreateCoordinateTransformation(inputCRS, outputCRS)
    locationPt_projectedCoordinates.Transform(coordinateTransformation)  # transform the _location point from +proj=latlong(WGS84) to +proj=aeqd
    
    locationPt_projectedCoordinatesX = locationPt_projectedCoordinates.GetX(0)/unitConversionFactor2
    locationPt_projectedCoordinatesY = locationPt_projectedCoordinates.GetY(0)/unitConversionFactor2
    
    scaleFactor = 0.01  # scale terrainMesh 100 times (should never be changed), meaning 1 meter in real life is 0.01 meters in Rhino document
    origin_0_0_0 = Rhino.Geometry.Point3d(0,0,0)  # always center the terrainMesh to 0,0,0 point
    
    # positive values mean that topLeft coordinate is above the locationPt coordinate, while negative values mean it's below
    distanceFrom_topLeftX_to_locationPtX = (topLeftX/unitConversionFactor2 - locationPt_projectedCoordinatesX)*scaleFactor
    distanceFrom_topLeftX_to_locationPtY = (topLeftY/unitConversionFactor2 - locationPt_projectedCoordinatesY)*scaleFactor
    terrainMeshStartPtX = origin_0_0_0.X + distanceFrom_topLeftX_to_locationPtX
    terrainMeshStartPtY = origin_0_0_0.Y + distanceFrom_topLeftX_to_locationPtY
    
    
    xIndex = numOfCellsInX
    yIndex = numOfCellsInY
    zIndex = 0
    pts = []
    
    # create terrainMesh from 1 arc-second format
    for k in xrange(numOfCellsInY):
        for i in xrange(numOfCellsInX):
            ptZ = ptZL[zIndex]
            pt = Rhino.Geometry.Point3d(terrainMeshStartPtX+(i*abs(cellsizeX/unitConversionFactor2)*scaleFactor), terrainMeshStartPtY-(k*abs(cellsizeY/unitConversionFactor2)*scaleFactor), ptZ/unitConversionFactor2*scaleFactor)
            pts.append(pt)
            xIndex += 1
            zIndex += 1
        yIndex -= 1
        xIndex = terrainMeshStartPtX
    
    # always create a terrain mesh regardless of type_ input so that "elevationM" can be calculated on a mesh
    terrainMesh = lb_meshpreparation.meshFromPoints(datasetWarped.RasterYSize, datasetWarped.RasterXSize, pts)
    # always create a terrain brep
    uDegree = min(3, numOfCellsInY - 1)
    vDegree = min(3, numOfCellsInX - 1)
    uClosed = False; vClosed = False
    terrainBrep = Rhino.Geometry.NurbsSurface.CreateThroughPoints(pts, numOfCellsInY, numOfCellsInX, uDegree, vDegree, uClosed, vClosed).ToBrep()
    
    
    # project origin_0_0_0 (locationPt) to terrainMesh
    safeHeightDummy = 10000/unitConversionFactor2  # in meters
    elevatedOrigin = Rhino.Geometry.Point3d(origin_0_0_0.X, origin_0_0_0.Y, (origin_0_0_0.Z+safeHeightDummy)*scaleFactor)  # project origin_0_0_0 to terrainMesh
    ray = Rhino.Geometry.Ray3d(elevatedOrigin, Rhino.Geometry.Vector3d(0,0,-1))
    rayIntersectParam = Rhino.Geometry.Intersect.Intersection.MeshRay(terrainMesh, ray)
    locationPt = ray.PointAt(rayIntersectParam)
    
    elevationM = locationPt.Z/scaleFactor  # in meters
    elevationM = round(elevationM,2)
    
    
    # deleting
    datasetWarped.Dispose()
    bandWarped.Dispose()
    #os.remove(rasterFilePath)  # downloaded .tif file
    del pts
    del ptZL
    gc.collect()
    
    
    return terrainMesh, terrainBrep, locationPt, elevationM


def colorMesh(terrainMesh):
    
    if len(legendPar_) == 0: legendPar = []
    else: legendPar = legendPar_
    
    # color the "terrain" mesh
    terrainMesh_numOfVertices = list(terrainMesh.Vertices)
    terrainMesh_verticesZ = [pt.Z for pt in terrainMesh_numOfVertices]
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    colors = lb_visualization.gradientColor(terrainMesh_verticesZ, lowB, highB, customColors)
    terrainMesh.VertexColors.Clear()
    for i in range(len(terrainMesh_numOfVertices)):
        terrainMesh.VertexColors.Add(colors[i])
    
    return terrainMesh  # colored mesh


def split_createStand_colorTerrain(terrainMesh, terrainBrep, locationPt, origin, northRad, standThickness, unitConversionFactor2):
    
    scaleFactor = 0.01  # scale terrainMesh 100 times (should never be changed), meaning 1 meter in real life is 0.01 meters in Rhino document
    
    if (radius_ < (200/unitConversionFactor2)):
        # always reduce the cutting "radius_" unless radius_ is < 200
        cuttingRadiusScaled = radius_ / unitConversionFactor2 * scaleFactor
    else:
        cuttingRadiusScaled = (radius_*0.9) / unitConversionFactor2 * scaleFactor  # 0.9 to avoid the cutting sphere getting out of the terrainMesh/terrainBrep edges
    
    # always perform the cutting of either a mesh or surface regardless if type_ is 0,1,2,3
    if (type == 0) or (type == 1):
        # splitting of mesh
        if (type == 0):
           # split with a cuboid
            boxInterval = Rhino.Geometry.Interval(-cuttingRadiusScaled, cuttingRadiusScaled)
            boxIntervalZ = Rhino.Geometry.Interval(-cuttingRadiusScaled*8, cuttingRadiusScaled*8)  # always use "8"
            boxBrep = Rhino.Geometry.Box(Rhino.Geometry.Plane(locationPt, Rhino.Geometry.Vector3d(0,0,1)), boxInterval, boxInterval, boxIntervalZ).ToBrep()
            boxMeshes = Rhino.Geometry.Mesh.CreateFromBrep(boxBrep)
            boxMesh = Rhino.Geometry.Mesh();
            for mesh in boxMeshes:
                boxMesh.Append(mesh)
            terrainMeshesSplitted = terrainMesh.Split(boxMesh)
        
        elif (type == 1):
            # split with a sphere
            meshSphere = Rhino.Geometry.Mesh.CreateFromSphere(Rhino.Geometry.Sphere(locationPt, cuttingRadiusScaled), 48, 40)
            terrainMeshesSplitted = terrainMesh.Split(meshSphere)
    
    
    elif (type == 2) or (type == 3):
        # splitting of surface
        if (type == 2):
            # split with a cuboid
            boxInterval = Rhino.Geometry.Interval(-cuttingRadiusScaled, cuttingRadiusScaled)
            boxIntervalZ = Rhino.Geometry.Interval(-cuttingRadiusScaled*5, cuttingRadiusScaled*5)  # always use "5"
            boxBrep = Rhino.Geometry.Box(Rhino.Geometry.Plane(locationPt, Rhino.Geometry.Vector3d(0,0,1)), boxInterval, boxInterval, boxIntervalZ).ToBrep()
            terrainBrepsSplitted = terrainBrep.Split(boxBrep, 0.01)
        
        elif (type == 3):
            # split with a sphere
            brepSphere = Rhino.Geometry.Sphere(locationPt, cuttingRadiusScaled).ToBrep()
            terrainBrepsSplitted = terrainBrep.Split(brepSphere, 0.01)
        
        [splittedBrep.Faces.ShrinkFaces() for splittedBrep in terrainBrepsSplitted]
        terrainMeshesSplitted = [Rhino.Geometry.Mesh.CreateFromBrep(splittedBrep) for splittedBrep in terrainBrepsSplitted]  # convert terrainBrepsSplitted to meshes for quicker calculation
    
    
    tupleDistanceToLocationPt = [ (Rhino.Geometry.AreaMassProperties.Compute(splittedMesh).Centroid .DistanceTo(locationPt),  i)  for i,splittedMesh in enumerate(terrainMeshesSplitted)]  # calculate the distance from centroids of the meshes from terrainMeshesSplitted to locationPt
    tupleDistanceToLocationPt.sort()
    
    if (type == 0) or (type == 1):
        terrain_MeshOrBrep_Splitted = terrainMeshesSplitted[tupleDistanceToLocationPt[0][1]]
        terrainOutlines = [polyline.ToNurbsCurve() for polyline in terrain_MeshOrBrep_Splitted.GetNakedEdges()]
    elif (type == 2) or (type == 3):
        terrain_MeshOrBrep_Splitted = terrainBrepsSplitted[tupleDistanceToLocationPt[0][1]]
        nakedOnly = True
        terrainOutlines = terrain_MeshOrBrep_Splitted.DuplicateEdgeCurves(nakedOnly)
    
    
    
    # stand
    standThickness = standThickness/100  # due to scalling of the terrain_Mesh_colored 100 times
    if (standThickness == 0):
        # stand should not be created
        if (type == 0) or (type == 1):
            # just color the mesh
            terrain_Mesh_colored = colorMesh(terrain_MeshOrBrep_Splitted)
            del terrainBrep
            return terrain_Mesh_colored
        elif (type == 2) or (type == 3):
            del terrainMesh
            return terrain_MeshOrBrep_Splitted
    
    elif (standThickness > 0):
        # create stand
        accurate = True
        terrainBB = terrain_MeshOrBrep_Splitted.GetBoundingBox(accurate)
        lowestZcoordinatePt = terrainBB.Min  # point with the lowest Z coordinate
        terrainLowestVertexPlane = Rhino.Geometry.Plane(lowestZcoordinatePt, Rhino.Geometry.Vector3d(0,0,1))
        terrainLowestVertexPlane2 = Rhino.Geometry.Plane(terrainLowestVertexPlane.Origin, Rhino.Geometry.Vector3d(0,0,1))
        terrainLowestVertexPlane.Origin = Rhino.Geometry.Point3d(terrainLowestVertexPlane.Origin.X, terrainLowestVertexPlane.Origin.Y, terrainLowestVertexPlane.Origin.Z - standThickness)
        
        terrainOutline = Rhino.Geometry.Curve.JoinCurves(terrainOutlines)[0]
        terrainOutlineProjected = Rhino.Geometry.Curve.ProjectToPlane(terrainOutline, terrainLowestVertexPlane)  # "terrainOutline" projected to the "terrainLowestVertexPlane" plane
        
        loftType = Rhino.Geometry.LoftType.Straight; closedLoft = False
        loftedTerrain_Outline_and_OutlineProjected_Brep = Rhino.Geometry.Brep.CreateFromLoft([terrainOutline, terrainOutlineProjected], Rhino.Geometry.Point3d.Unset, Rhino.Geometry.Point3d.Unset, loftType, closedLoft)[0]
        
        terrainOutlineProjected_Brep = Rhino.Geometry.Brep.CreatePlanarBreps([terrainOutlineProjected])[0]
        loftedTerrain_Outline_and_OutlineProjected_Brep__and__terrainOutlineProjected_Brep = Rhino.Geometry.Brep.JoinBreps([loftedTerrain_Outline_and_OutlineProjected_Brep, terrainOutlineProjected_Brep],0.001)[0]
        
        
        if (type == 2) or (type == 3):
            # surface, no coloring should be performed
            loftedTerrain_Outline_and_OutlineProjected_Brep__and__terrainOutlineProjected_Brep__and__terrain = Rhino.Geometry.Brep.JoinBreps([loftedTerrain_Outline_and_OutlineProjected_Brep, terrainOutlineProjected_Brep, terrain_MeshOrBrep_Splitted],0.001)[0]
            del terrainMesh
            
            return loftedTerrain_Outline_and_OutlineProjected_Brep__and__terrainOutlineProjected_Brep__and__terrain
        elif (type == 0) or (type == 1):
            # mesh, color the meshes
            meshParam = Rhino.Geometry.MeshingParameters()
            meshParam.MinimumEdgeLength = 0.0001
            meshParam.MaximumEdgeLength = 100
            
            loftedTerrain_Outline_and_OutlineProjected_Brep__and__terrainOutlineProjected_Brep_Mesh = Rhino.Geometry.Mesh.CreateFromBrep(loftedTerrain_Outline_and_OutlineProjected_Brep__and__terrainOutlineProjected_Brep, meshParam)  # it can contain more than one mesh
            terrain_withStand = Rhino.Geometry.Mesh()  # for scaling of terrainShadingMask
            for meshMaskPart in loftedTerrain_Outline_and_OutlineProjected_Brep__and__terrainOutlineProjected_Brep_Mesh:
                terrain_withStand.Append(meshMaskPart)
            terrain_withStand.Append(terrain_MeshOrBrep_Splitted)
            
            terrain_withStand_colored = colorMesh(terrain_withStand)
            del terrainBrep
            
            return terrain_withStand_colored


def createElevationContours(terrainUnoriginUnscaledUnrotated, numOfContours, type):
    
    # create intersection planes
    accurate = True
    terrainBB_edges = terrainUnoriginUnscaledUnrotated.GetBoundingBox(accurate).GetEdges()
    terrainBB_verticalEdge = terrainBB_edges[8]  # "Rhino.Geometry.Line" type
    includeEnds = False
    terrainBB_edges_t_parameters = terrainBB_verticalEdge.ToNurbsCurve().DivideByCount(numOfContours, includeEnds)
    elevationContours_planeOrigins = [Rhino.Geometry.Line.PointAt(terrainBB_verticalEdge, t)  for t in terrainBB_edges_t_parameters]
    elevationContours_planes = [Rhino.Geometry.Plane(origin, Rhino.Geometry.Vector3d(0,0,1))  for origin in elevationContours_planeOrigins]
    
    if (type == 0) or (type == 1):
        elevationContours_Polylines = list(Rhino.Geometry.Intersect.Intersection.MeshPlane(terrainUnoriginUnscaledUnrotated, elevationContours_planes))
        elevationContours = [crv.ToNurbsCurve()  for crv in elevationContours_Polylines]  # curves
    elif (type == 2) or (type == 3):
        elevationContours = []
        for plane in elevationContours_planes:
            success, elevationContoursSubList, elevationContourPointsSubList = Rhino.Geometry.Intersect.Intersection.BrepPlane(terrainUnoriginUnscaledUnrotated, plane, 0.01)
            #elevationContoursSubList_closedCrvs = [crv  for crv in elevationContoursSubList  if crv.IsClosed] # remove elevationContours crvs which are not closed
            elevationContoursSubList_closedCrvs = [crv  for crv in elevationContoursSubList]
            if len(elevationContoursSubList_closedCrvs) > 0:  # or success == True
                elevationContours.extend(elevationContoursSubList_closedCrvs)
    
    return elevationContours


def compassCrvs_title_scalingRotating(terrainUnoriginUnscaledUnrotated, locationName, locationLatitudeD, locationLongitudeD, locationPt, maxVisibilityRadiusM, type, origin, northVec, northRad, numOfContours, unitConversionFactor):
    
    # scaling, rotating
    originTransformMatrix = Rhino.Geometry.Transform.PlaneToPlane(  Rhino.Geometry.Plane(locationPt, Rhino.Geometry.Vector3d(0,0,1)), Rhino.Geometry.Plane(origin, Rhino.Geometry.Vector3d(0,0,1)) )  # move the terrain from "locationPt" to "origin"
    scaleTransformMatrix = Rhino.Geometry.Transform.Scale( Rhino.Geometry.Plane(origin, Rhino.Geometry.Vector3d(0,0,1)), 100, 100, 100 )  # scale the whole terrain back to its real size due to previous usage of scaleFactor = 0.01
    # rotation due to north angle position
    #transformMatrixRotate = Rhino.Geometry.Transform.Rotation(-northRad, Rhino.Geometry.Vector3d(0,0,1), origin)  # counter-clockwise
    rotateTransformMatrix = Rhino.Geometry.Transform.Rotation(northRad, Rhino.Geometry.Vector3d(0,0,1), origin)  # clockwise
    
    if numOfContours_ > 0:
        # create elevationContours
        elevationContours_UnoriginUnscaledUnrotated = createElevationContours(terrainUnoriginUnscaledUnrotated, numOfContours, type)
    else:
        # no elevationContours will be created
        elevationContours_UnoriginUnscaledUnrotated = []
    geometry = [terrainUnoriginUnscaledUnrotated] + elevationContours_UnoriginUnscaledUnrotated
    for g in geometry:
        if g != None:  # exclude the elevationContours which are invalid (equal to None)
            g.Transform(originTransformMatrix)
            g.Transform(scaleTransformMatrix)
            g.Transform(rotateTransformMatrix)
    
    
    # title
    if len(legendPar_) == 0:
        legendFont = "Verdana"; legendScale = 1; legendBold = None
    else:
        lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar_, False)
    
    lb_visualization.calculateBB([terrainUnoriginUnscaledUnrotated])
    legendFontSize = ((lb_visualization.BoundingBoxPar[2]/10)/3) * legendScale
    legendFontSize = legendFontSize# * 1.2  # enlarge the title font size 1.2 times of the legend font size
    
    titleLabelOrigin = lb_visualization.BoundingBoxPar[5]
    titleLabelOrigin.Y = titleLabelOrigin.Y - lb_visualization.BoundingBoxPar[2]/15
    
    titleLabelText = "Location: %s\nLatitude: %s, Longitude: %s\nRadius: %sm, North: %s" % (locationName, locationLatitudeD, locationLongitudeD, maxVisibilityRadiusM, round(360-math.degrees(northRad),2))
    titleLabelMeshes = lb_visualization.text2srf([titleLabelText], [titleLabelOrigin], legendFont, legendFontSize*1.2, legendBold, None, 6)[0]
    titleLabelMesh = Rhino.Geometry.Mesh()
    for mesh in titleLabelMeshes:
        titleLabelMesh.Append(mesh)
    
    # hide originPt output
    ghenv.Component.Params.Output[3].Hidden = True
    
    return terrainUnoriginUnscaledUnrotated, titleLabelMesh, elevationContours_UnoriginUnscaledUnrotated


def bakingGrouping(locationName, locationLatitudeD, locationLongitudeD, maxVisibilityRadiusM, typeLabel, standThickness, terrain, title, elevationContours, origin):
    
    layerName = locationName + "_" + str(locationLatitudeD) + "_" + str(locationLongitudeD) + "_RADIUS=" + str(maxVisibilityRadiusM) + "M" + "_STAND=" + str(round(standThickness,2)) + "_"+ typeLabel
    
    layerIndex, l = lb_visualization.setupLayers(layerName, "LADYBUG", "TERRAIN_GENERATOR", "TERRAIN")
    
    attr = Rhino.DocObjects.ObjectAttributes()
    attr.LayerIndex = layerIndex
    attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
    attr.PlotColorSource = Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
    
    # bake terrain, title
    geometryIds = []
    geometry = [terrain, title, Rhino.Geometry.Point(origin)]
    for obj in geometry:
        id = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj,attr)
        geometryIds.append(id)
    
    # bake terrain, title
    elevationCrvsIds = []
    geometry2 = elevationContours
    for obj2 in geometry2:
        id2 = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj2,attr)
        elevationCrvsIds.append(id2)
    
    # grouping of elevationContours
    groupIndex = Rhino.RhinoDoc.ActiveDoc.Groups.Add(layerName + "_terrainGenerator2_elevationContours" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex, elevationCrvsIds)
    
    # grouping of terrain and title
    groupIndex2 = Rhino.RhinoDoc.ActiveDoc.Groups.Add(layerName + "_terrainGenerator2_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex2, geometryIds + elevationCrvsIds)


def printOutput(north, latitude, longitude, locationName, maxVisibilityRadiusM, type, typeLabel, origin, workingSubFolderPath, standThickness, numOfContours):
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    resultsCompletedMsg = "Terrain generator 2 component results successfully completed %s!" % bakedOrNot
    printOutputMsg = \
    """
Input data:

Location (deg.): %s
Latitude (deg.): %s
Longitude (deg.): %s
North (deg.): %s

Radius (m): %s
Type: %s (%s)
Origin: %s
Working folder: %s
Stand thickness (rhino doc. units): %s
Number of elevation contours: %s
    """ % (locationName, latitude, longitude, round(360-math.degrees(northRad),2), maxVisibilityRadiusM, type, typeLabel, origin, workingSubFolderPath, standThickness, numOfContours)
    print resultsCompletedMsg
    print printOutputMsg


level = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("ladybug_release"):
    if sc.sticky["ladybug_release"].isCompatible(ghenv.Component):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_meshpreparation = sc.sticky["ladybug_Mesh"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        lb_photovoltaics = sc.sticky["ladybug_Photovoltaics"]()
        
        if _location:
            locationLatitudeD, locationLongitudeD, locationName, fileNameIncomplete, validLocationData, printMsg = getLocationData(_location)
            if validLocationData:
                heightM = 0; minVisibilityRadiusM = 0; maskStyle = 0; maskStyleLabel = "sph"; downloadTSVLink = None  # dummy values
                maxVisibilityRadiusM, northRad, northVec, type, typeLabel, origin, standThickness, numOfContours, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, unitConversionFactor2, validInputData, printMsg = checkInputData(radius_, north_, type_, origin_, workingFolder_, standThickness_, numOfContours_, downloadTSVLink)
                librariesFolder = GDAL_librariesFolderPath
                if validInputData:
                    if _runIt:
                        if validInputData:
                            terrainShadingMaskUnscaledUnrotated, origin_0_0_0, fileName, objFilePath, rasterFilePath, rasterFilePath_aeqd, rasterFileNamePlusExtension_aeqd, vrtFilePath, elevationM, valid_Obj_or_Raster_file, printMsg = checkObjRasterFile(fileNameIncomplete, workingSubFolderPath, downloadTSVLink, heightM, minVisibilityRadiusM, maxVisibilityRadiusM, maskStyleLabel)
                            standThickness = standThickness_
                            if valid_Obj_or_Raster_file:
                                if (rasterFilePath != "needless") and (rasterFilePath != "download failed"):  # terrain shading mask NEEDS to be created
                                    terrainMesh, terrainBrep, locationPt, elevationM = createTerrainMeshBrep(GDAL_librariesFolderPath, objFilePath, rasterFilePath, rasterFilePath_aeqd, rasterFileNamePlusExtension_aeqd, vrtFilePath, locationLatitudeD, locationLongitudeD, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, type, origin, legendPar_, unitConversionFactor, unitConversionFactor2)
                                    terrainUnoriginUnscaledUnrotated = split_createStand_colorTerrain(terrainMesh, terrainBrep, locationPt, origin, northRad, standThickness, unitConversionFactor2)
                                terrain, title, elevationContours = compassCrvs_title_scalingRotating(terrainUnoriginUnscaledUnrotated, locationName, locationLatitudeD, locationLongitudeD, locationPt, maxVisibilityRadiusM, type, origin, northVec, northRad, numOfContours, unitConversionFactor)
                                if bakeIt_: bakingGrouping(locationName, locationLatitudeD, locationLongitudeD, maxVisibilityRadiusM, typeLabel, standThickness, terrain, title, elevationContours, origin)
                                printOutput(northRad, locationLatitudeD, locationLongitudeD, locationName, maxVisibilityRadiusM, type, typeLabel, origin, workingSubFolderPath, standThickness, numOfContours)
                                originPt = origin; elevation = elevationM
                            else:
                                print printMsg
                                ghenv.Component.AddRuntimeMessage(level, printMsg)
                        else:
                            print printMsg
                            ghenv.Component.AddRuntimeMessage(level, printMsg)
                    else:
                        print "All inputs are ok. Please set \"_runIt\" to True, in order to run the Terrain Generator 2 component"
                else:
                    print printMsg
                    ghenv.Component.AddRuntimeMessage(level, printMsg)
            else:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
        else:
            printMsg = "Please input location from \"importEPW\" or \"constructLocation\" components."
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        printMsg = "You need a newer version of Ladybug to use this component.\n" + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag the Ladybug_Ladybug component " + \
            "into the canvas and try again."
        print printMsg
else:
    printMsg = "First please let the Ladybug fly..."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)
