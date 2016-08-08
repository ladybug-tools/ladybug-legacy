# terrain shading mask
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Djordje Spasic <djordjedspasic@gmail.com>
# with assistance of Dr. Bojan Savric <savricb@geo.oregonstate.edu>
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
Use this component to create a 3D Terrain shading mask for a particular location.
It's a diagram which maps the silhouette of the surrounding terrain (hills, valleys, mountains, tree tops...) in 360 degrees directions seen from above the astronomical horizon.
It can be used as a "context_" input in mountainous or higher latitude regions for any kind of sun related analysis: sunlight hours analysis, solar radiation analysis, view analysis, photovoltaics/solar water heating sunpath shading ...
-
!!! ATTENTION !!!   This component may crash Rhino 5 application due to requirement to generate large topography data! To prevent this, it is suggested to own a 64 bit version of Rhino 5 and have strong enough PC configuration. If you do not have either of these two, it is recommended to keep the maxVisibilityRadius_ value to default value of 100 to prevent the crash of Rhino.
Also try saving your .gh definition before running this component!
-
Component requires that you are connected to the Internet, as it has to download topography data for each terrain shading mask.
It also requires certain GDAL libraries to be downloaded manually. Component will provide instructions on where to download these libraries.
Additionally you can find the instructions in here:
For Rhino5 x86:  https://github.com/stgeorges/terrainShadingMask/blob/master/miscellaneous/Installation_instructions_Rhino5_x86.md
For Rhino5 x64:  https://github.com/stgeorges/terrainShadingMask/blob/master/miscellaneous/Installation_instructions_Rhino5_x64.md
-
Component mainly based on:

"Mathematical cartography", V. Jovanovic, VGI 1983.
"Surveying and Levelling Second Edition", Tata McGraw-Hill Education Pvt. Ltd., 5.7 Corrections to be applied, N.N. Basak, 2004
"Vincenty solutions of geodesics on the ellipsoid" article by Chris Veness
https://books.google.rs/books/about/Matemati%C4%8Dka_kartografija.html?id=GcXEMgEACAAJ&redir_esc=y
https://books.google.rs/books?id=fIvvAwAAQBAJ&printsec=frontcover#v=onepage&q&f=false
http://www.movable-type.co.uk/scripts/latlong-vincenty.html
-
Topography data from: http://opentopography.org
GDAL Libraries from: http://gisinternals.com
-
Provided by Ladybug 0.0.63
    
    input:
        _location: The output from the "importEPW" or "constructLocation" component.  This is essentially a list of text summarizing a location on the Earth.
                   -
                   "timeZone" and "elevation" data from the location, are not important for the creation of a Terrain shading mask.
        context_: Input every kind of context to this input: buildings, houses, trees; and all the other objects: PV/SWHsurfaces or planar "_geometry" (surface) on which the future analysis (view, sunlight hours, radiation...) will be conducted.
                  -
                  This input is important for calculation of the final radius of the Terrain shading mask (that's "maskRadius" output). The larger the context_ input, the Terrain shading mask radius might be longer.
                  For sunpath visualization purposes, you can make this input empty (not supply anything to it). In this way the "maskRadius" output will always be equal to 200 meters (655 feets) which corresponds to the _sunPathScale_ = 1 input of the Ladybug_Sunpath component.
                  -
                  If nothing supplied to the context_ input, the default Terrain shading mask radius of 200 meters (655 feets) will be used.
        minVisibilityRadius_: Horizontal distance FROM which the surrounding terrain will be taken into account. Anything closer than that will not be considered for creation of a Terrain shading mask.
                              Unless you are doing an analysis of large areas, for example longer than 200 meters in radius (e.g. city's blocks) do not change this input's default value (0)!
                              -
                              If it is not equal to 0, it can not be shorter than 0.1 km nor longer than 10 km.
                              Also it must not be longer than one third of maxVisibilityRadius_. For example, if maxVisibilityRadius_ is 27, the maximal minVisibilityRadius_ can not be longer than 9.
                              It should be mentioned that every number supplied to the minVisibilityRadius_ input will by rounded at 1 decimal. For example, if you supply: 0.2345, it will be rounded to 0.2 kilometers.
                              -
                              This input depends on the radius of your context geometry (that's "contextRadius" output). If the radius of your context geometry ranges up to 200 meters (which will likely happen in most cases), just keep the minVisibilityRadius_ equal to 0.
                              However, if you intend to use Terrain shading mask for a context whose radius is a couple of hundreds of meters (e.g. solar radiation analysis of a city block), you need to remove the terrain very near to your _location.
                              This is what the minVisibilityRadius_ input is used for. For example you can use the value 3 times the radius of your contextRadius: let's say the radius of your context is 600 meters, then you can use the minVisibilityRadius_ of 1.8 km.
                              -
                              If not supplied, default value of 0 km will be used (all the terrain from the _location point will be taken into account up to maxVisibilityRadius_).
                              -
                              In kilometers.
        maxVisibilityRadius_: Horizontal distance TO which the surrounding terrain will be taken into account. Anything beyond that will not be considered for creation of a Terrain shading mask.
                              -
                              It can not be shorter than 1km or longer than 400 km.
                              -
                              The component itself might inform the user to alter the initial maxVisibilityRadius_ inputted by the user.
                              This is due to restriction of topography data, being limited to 56 latitude South to 60 latitude North range. If maxVisibilityRadius_ value for chosen location gets any closer to the mentioned range, the component will inform the user to shrink it for a certain amount, so that the maxVisibilityRadius_ stops at the range limit.
                              -
                              If not supplied, default value of 100 km will be used.
                              -
                              In kilometers.
        north_: Input a vector to be used as a true North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
                -
                If not supplied, default North direction will be set to the Y-axis (0 degrees).
        maskStyle_: The style of the mask
                    -
                    0 - spherical terrain shading mask - the terrain shading mask "is cut" from a half sphere.
                    1 - extruded (vertical) terrain shading mask - the terrain shading mask "is cut" from a cylinder.
                    -
                    !!! NOTICE !!!   Changing maskStyle_ input will result in reruning the component from the very start, and creating a new Terrain shading mask. This can be time consuming.
                    It could be better, in order to see how extruded(1) maskStyle_ looks like, to lower the value of the maxVisibilityRadius_ input to 10, for example.
                    In this way, the time needed for reruning the component and creating a new Terrain shading mask will vastly be reduced.
                    Once you see the effect of extruded maskStyle_, in case you prefer it over the spherical(0) maskStyle_, simply edit the maxVisibilityRadius_ input to the value it had before you lowered it to 10.
                    -
                    If not supplied, 0 will be used as a default (spherical terrain shading mask).
        workingFolder_: Folder path where downloaded and created terrain shading mask files will be located.
                        -
                        This component may download topography files up to 600 MB in size from the Internet, and then create the Terrain shading masks from them.
                        Make sure that the "workingFolder_" you choose is a hard disk partition with enough space on it.
                        -
                        If not supplied, the default Ladybug folder path will be used: C:\ladybug or C:\Users\%USERNAME%\AppData\Roaming\Ladybug.
        downloadUrl_: Address of a web page which contains download links of already created Terrain shading masks.
                      -
                      This component downloads a topography data first, then creates a terrain model from it, and in the end creates a Terrain shading mask.
                      Mentioned process can be both time consuming (component may ran for 10 minutes) or even crash your Rhino 5, in case you have 32 bit Rhino 5 with lower performance PC.
                      In order to avoid this, a number of premade Terrain shading masks will be uploaded to the Internet. Another reason for uploading premade masks is that some of them might not be able to be created with this component. But they could be directly downloaded through downloadUrl_ input.
                      Downloading a premade Terrain shading mask can last only a couple of seconds.
                      -
                      !!! NOTICE !!!  Only premade Terrain shading masks with minVisibilityRadius_ = 0, maxVisibilityRadius_ = 100 and maskStyle_ = 0 (spherical) will be uploaded!
                      So if you would like to download a premade Terrain shading mask, make sure that you set your inputs to the same upper mentioned values (minVisibilityRadius_ = 0, maxVisibilityRadius_ = 100, maskStyle_ = 0).
                      -
                      If not supplied, the following default downloadUrl_ input will be used
                      raw.githubusercontent.com/stgeorges/terrainShadingMask/master/objFiles/0_terrain_shading_masks_download_links.tsv
        bakeIt_: Set to "True" to bake the Terrain shading mask results into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: !!! ATTENTION !!!   This component may crash Rhino 5 application due to requirement to generate large topography data! To prevent this, it is suggested to own a 64 bit version of Rhino 5 and have strong enough PC configuration.
                If you do not have either of these two, try keeping the maxVisibilityRadius_ value to its default value: 100.
                Also try saving your .gh definition before running this component.
    
    output:
        readMe!: ...
        terrainShadingMask: The geometry of the terrain shading mask.
                            -
                            It is scaled according to "context_" input (that is its "contextRadius"), and centered to "context_" centroid (this is "originPt" output).
        compassCrvs: Compass azimuth labels and curves.
                     -
                     Connect this output to a Grasshopper's "Geo" parameter in order to preview the compassCrvs geometry in the Rhino scene.
        title: Title geometry with information about location, maxVisibilityRadius, elevation.
               -
               Connect this output to a Grasshopper's "Geo" parameter in order to preview the title geometry in the Rhino scene.
        originPt: The origin (center) point of the "terrainShadingMask" and "compassCrvs" geometry.
                  - 
                  The originPt represent the center point of the inputted "context_" geometry. It's Z coordinate will always correspond to the Z coordinate of the lowest part of the "context_" geometry.
                  -
                  Use this point to move the "terrainShadingMask", "compassCrvs" and "title" geometry around in the Rhino scene with grasshopper's "Move" component.
        librariesFolder: Folder path where GDAL libraries should be copied.
                         -
                         It is created as:
                         Ladybug_Ladybug component's "defaultFolder_" + "terrain shading mask libraries 32-bit"  for Rhino5 x86,
                         Ladybug_Ladybug component's "defaultFolder_" + "terrain shading mask libraries 64-bit"  for Rhino5 x64.
        contextRadius: The radius of the "context_" input
                       -
                       If nothing supplied to the "context_" input, the contextRadius will be equal to 0.
                       -
                       In Rhino document units.
        maskRadius: The radius of the "terrainShadingMask" output.
                    -
                    If nothing supplied to the "context_" input, the maskRadius is set to 200 meters (655 feets).
                    If something supplied to the "context_" input, the minimal maskRadius is set to 10000 meters (32786 feets).
                    -
                    In Rhino document units.
        elevation: Elevation of the viewpoint.
                   The default and fixed height of the viewpoint from the ground is set to 2 meters.
                   The summation of the height of the viewpoint and location's elevation represents this "elevation" output.
                   -
                   In meters.
"""

ghenv.Component.Name = "Ladybug_Terrain Shading Mask"
ghenv.Component.NickName = "TerrainShadingMask"
ghenv.Component.Message = "VER 0.0.63\nAUG_08_2016"
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


def checkInputData(minVisibilityRadiusKM, maxVisibilityRadiusKM, north, maskStyle, workingFolderPath, downloadTSVLink):
    
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
        heightM = minVisibilityRadiusM = maxVisibilityRadiusM = northRad = northVec = maskStyle = maskStyleLabel = workingSubFolderPath = downloadTSVLink = unitConversionFactor = None
        validInputData = False
        printMsg = "\"defaultFolder_\" input you supplied to the \"Ladybug Ladybug\" component is invalid.\n" + \
                   "Input the string in the following format (example): C:\someFolder.\n" + \
                   "Or do not input anything, in which case the default Ladybug folder will be used instead."
        return heightM, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, northVec, maskStyle, maskStyleLabel, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, validInputData, printMsg
    
    
    unitSystem = Rhino.RhinoDoc.ActiveDoc.ModelUnitSystem
    if (unitSystem != Rhino.UnitSystem.Meters) and (unitSystem != Rhino.UnitSystem.Feet):
        # only Meters and Feets Rhino Document units are allowed
        heightM = minVisibilityRadiusM = maxVisibilityRadiusM = northRad = northVec = maskStyle = maskStyleLabel = workingSubFolderPath = downloadTSVLink = unitConversionFactor = None
        validInputData = False
        printMsg = "The component allows the usage of either Meter or Feet Rhino Document units.\n" + \
                   " \n" + \
                   "A radius of the Terrain shading mask will be determined according to the context_ input. This radius may range to a couple of thousands of meters.\n" + \
                   "Using such mask with %s unit can result in very high radius number when converted from meters to %s. Which means that the mask can be very distant from the 0,0,0 origin. Due to floating-point precision, such distant geometry can often experience inaccuracy problems.\n" % (unitSystem, unitSystem) + \
                   "This is why Terrain shading mask component can only be used with either Meters and Feets Rhino document units. Choose one of these two, and then rerun the component."
        return heightM, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, northVec, maskStyle, maskStyleLabel, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, validInputData, printMsg
    
    
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
            heightM = minVisibilityRadiusM = maxVisibilityRadiusM = northRad = northVec = maskStyle = maskStyleLabel = workingSubFolderPath = downloadTSVLink = unitConversionFactor = None
            validInputData = False
            printMsg = "The GDAL libraries are not installed properly. Please make sure that you followed all of the previously mentioned four steps.\n" + \
                       " \n" + \
                       "Check this page for graphical preview of the steps: \n" + \
                       "https://github.com/stgeorges/terrainShadingMask/blob/master/miscellaneous/Installation_instructions_Rhino5_%s.md\n" % rhino5version + \
                       " \n" + \
                       "If after this, you still get this same message (of GDAL libraries not installed properly) please post a question about this issue at:\n" + \
                       "www.grasshopper3d.com/group/ladybug/forum/topics/terrain-shading-mask-component-released."
            return heightM, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, northVec, maskStyle, maskStyleLabel, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, validInputData, printMsg
        
        # set the folderpath for "gdal-data" folder (GDAL support files)
        gdal_data_folderPath = os.path.join(GDAL_librariesFolderPath, "gdal-data")
        gdalc.Gdal.PushFinderLocation(gdal_data_folderPath)  # necessary for 64 bit GDAL .dlls in order to identify gcs.csv file
    
    else:
        # check if the "terrain shading mask libraries 32(64)-bit" folder is not empty.
        if os.listdir(GDAL_librariesFolderPath) != []:
            # "terrain shading mask libraries 32(64)-bit" folder is not empty (for example: either step 3 was completed but step 4 wasn't or vice versa)
            heightM = minVisibilityRadiusM = maxVisibilityRadiusM = northRad = northVec = maskStyle = maskStyleLabel = workingSubFolderPath = downloadTSVLink = unitConversionFactor = None
            validInputData = False
            printMsg = "The GDAL libraries are not installed properly. Please make sure that you followed all of the previously mentioned four steps.\n" + \
                       " \n" + \
                       "Check this page for graphical preview of the steps: \n" + \
                       "https://github.com/stgeorges/terrainShadingMask/blob/master/miscellaneous/Installation_instructions_Rhino5_%s.md\n" % rhino5version + \
                       " \n" + \
                       "If after this, you still get this same message (of GDAL libraries not installed properly) please post a question about this issue at:\n" + \
                       "www.grasshopper3d.com/group/ladybug/forum/topics/terrain-shading-mask-component-released."
            return heightM, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, northVec, maskStyle, maskStyleLabel, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, validInputData, printMsg
        else:
            # "terrain shading mask libraries 32(64)-bit" folder is EMPTY (neither step 3 nor step 4 have been performed)
            heightM = minVisibilityRadiusM = maxVisibilityRadiusM = northRad = northVec = maskStyle = maskStyleLabel = workingSubFolderPath = downloadTSVLink = unitConversionFactor = None
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
            return heightM, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, northVec, maskStyle, maskStyleLabel, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, validInputData, printMsg
    
    
    
    # check inputs
    heightM = 2
    if (heightM == None):
        heightM = 2  # default 2 meters
    elif (heightM < 2):
        heightM = 2
        print "heightM_ input only supports values equal or larger than 2 meters.\n" + \
              "heightM_ input set to 2 meters."
    
    
    if (minVisibilityRadiusKM == None):
        minVisibilityRadiusKM = 0  # default in kilometers
    elif (minVisibilityRadiusKM < 0):
        minVisibilityRadiusKM = 0
        print "minVisibilityRadius_ input only supports values equal or larger than 0 kilometer.\n" + \
              "minVisibilityRadius_ input set to 0 kilometer."
    elif (minVisibilityRadiusKM > 10):
        heightM = minVisibilityRadiusM = maxVisibilityRadiusM = northRad = northVec = maskStyle = maskStyleLabel = workingSubFolderPath = downloadTSVLink = unitConversionFactor = None
        validInputData = False
        printMsg = "minVisibilityRadius_ values longer than 10 are not supported.\n" + \
                   "Please set the minVisibilityRadius_ to some value from 0 to 10 (0 being recommended unless you are doing an analysis of big parts of a city)."
        return heightM, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, northVec, maskStyle, maskStyleLabel, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, validInputData, printMsg
    if (3 * minVisibilityRadiusKM > maxVisibilityRadiusKM):
        heightM = minVisibilityRadiusM = maxVisibilityRadiusM = northRad = northVec = maskStyle = maskStyleLabel = workingSubFolderPath = downloadTSVLink = unitConversionFactor = None
        validInputData = False
        printMsg = "minVisibilityRadius_ value can not be longer than one third of maxVisibilityRadius_.\n" + \
                   "Please set the minVisibilityRadius_ to some value from 0 to 10 so that the minVisibilityRadius_ is equal or less than 0.3*maxVisibilityRadius_."
        return heightM, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, northVec, maskStyle, maskStyleLabel, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, validInputData, printMsg
    minVisibilityRadiusKM_rounded = round(minVisibilityRadiusKM,1)  # round the "minVisibilityRadius_" input to 0.1 value
    minVisibilityRadiusM = minVisibilityRadiusKM_rounded * 1000  # convert to meters
    
    
    # for locations from .epw files, the maxVisibilityRadius can be estimated from .epw file's field N24 (visibility) and its maximal annual hourly value.
    # Still this value may not be the maximal one for the chosen location.
    if (maxVisibilityRadiusKM == None):
        maxVisibilityRadiusKM = 100  # default in kilometers
    elif (maxVisibilityRadiusKM < 1):
        maxVisibilityRadiusKM = 1
        print "maxVisibilityRadius_ input only supports values equal or larger than 1 kilometer.\n" + \
              "maxVisibilityRadius_ input set to 1 kilometer."
    elif (maxVisibilityRadiusKM > 400):
        heightM = minVisibilityRadiusM = maxVisibilityRadiusM = northRad = northVec = maskStyle = maskStyleLabel = workingSubFolderPath = downloadTSVLink = unitConversionFactor = None
        validInputData = False
        printMsg = "Radii longer than 400 are not supported, due to the following reason:\n" + \
                   "The longest recorded horizontal visibility distance (which is the maxVisibilityRadius_ in our case) during daylight is 388 km.\n" + \
                   " \n" + \
                   "In general visibility distances over 100 km can be rare, and may happen in specific cases once or twice a year.\n" + \
                   " \n" + \
                   "It is advicable to take 100 as the default maxVisibilityRadius_ value for all locations. Then you can try to increase it to 200, or 300 and see if affects the Terrain mask in a significant way. Sometimes the higher \"maxVisibilityRadius_\" values (200,300) are not even required.\n" + \
                   " \n" + \
                   "ATTENTION!!! Have in mind that even radii above 100 km may require stronger PC configurations and 64 bit version of Rhino 5. Otherwise Rhino 5 may crash.\n" + \
                   "If this happens (Rhino 5 crashes) get back to the \"maxVisibilityRadius_\" input of 100."
        
        return heightM, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, northVec, maskStyle, maskStyleLabel, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, validInputData, printMsg
    maxVisibilityRadiusM = maxVisibilityRadiusKM * 1000  # convert to meters
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
                heightM = minVisibilityRadiusM = maxVisibilityRadiusM = northRad = northVec = maskStyle = maskStyleLabel = workingSubFolderPath = downloadTSVLink = unitConversionFactor = None
                validInputData = False
                printMsg = "Please input north angle value from 0 to 360."
                return heightM, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, northVec, maskStyle, maskStyleLabel, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, validInputData, printMsg
        except Exception, e:  # check if it's a vector
            north.Unitize()
        
        northRad, northVec = lb_photovoltaics.angle2northClockwise(north)
    northVec.Unitize()
    
    
    if (maskStyle == None) or (maskStyle == 0):  # shperical terrain shading mask style
        maskStyle = 0
        maskStyleLabel = "sph"
    elif (maskStyle == 1):  # extruded, vertical terrain shading mask style
        maskStyle = 1
        maskStyleLabel = "ext"
    elif (maskStyle < 0) or (maskStyle > 1):
        maskStyle = 0
        maskStyleLabel = "sph"
        print "maskStyle_ input only supports values 0 (spherical) or 1 (extruded,vertical).\n" + \
              "maskStyle_ input set to 0 (spherical)."
    
    if workingFolderPath == None:
        # nothing inputted to "workingFolder_" input, use default Ladybug folder instead (C:\ladybug or C:\Users\%USERNAME%\AppData\Roaming\Ladybug.)
        workingSubFolderPath = os.path.join(ladybugFolderPath, "terrain shading masks")
    else:
        # something inputted to "workingFolder_" input
        workingSubFolderPath = os.path.join(workingFolderPath, "terrain shading masks")
    folderCreated = createFolder(workingSubFolderPath)
    if folderCreated == False:
        heightM = minVisibilityRadiusM = maxVisibilityRadiusM = northRad = northVec = maskStyle = maskStyleLabel = workingSubFolderPath = downloadTSVLink = unitConversionFactor = None
        validInputData = False
        printMsg = "workingFolder_ input is invalid.\n" + \
                   "Input the string in the following format (example): C:\someFolder.\n" + \
                   "Or do not input anything, in which case a default Ladybug folder will be used instead."
        return heightM, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, northVec, maskStyle, maskStyleLabel, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, validInputData, printMsg
    
    if downloadTSVLink == None:
        downloadTSVLink = "https://raw.githubusercontent.com/stgeorges/terrainShadingMask/master/objFiles/0_terrain_shading_masks_download_links.tsv"
    
    #unitConversionFactor = lb_preparation.checkUnits()  # factor to convert Rhino document units to meters.
    unitConversionFactor = 1  # unitConversionFactor is always fixed to "1" to avoid problems when .obj files are exported from Rhino document (session) in one Units, and then imported in some other Rhino document (session) with different Units
    
    
    validInputData = True
    printMsg = "ok"
    
    return heightM, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, northVec, maskStyle, maskStyleLabel, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, validInputData, printMsg


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
    
    if distanceM < 1000:  # (the shortest allowed "maxVisibilityRadius_" is 1)
        correctedMaskRadiusM = "dummy"
        validVisibilityRadiusM = False
        printMsg = "This component dowloads free topography data from opentopography.org in order to create a Terrain shading mask for the chosen _location.\n" + \
                   "But mentioned free topography data has limits: from -56 South to 60 North latitude.\n" + \
                   "The closer the location is to upper mentioned boundaries, the inputted \"maxVisibilityRadius_\" value may have be shrank to make sure that the boundaries are not exceeded.\n" + \
                   "In this case the _location you chose is very close (less than 1 km) to the %s latitude boundary.\n" % SRTMlimit + \
                   "It is not possible to create a Terrain shading mask for locations less than 1 km close to mentioned boundary, as this _location is.\n" + \
                   " \n" + \
                   "There might be a way to create a Terrain shading mask for your _location not based on upper mentioned opentopography.org data, but rather from different topography sources.\n" + \
                   "To get help, open a new topic about this issue at:\n" + \
                   "http://www.grasshopper3d.com/group/ladybug/forum/topics/terrain-shading-mask-component-released or\n" + \
                   "https://github.com/stgeorges/terrainShadingMask/issues"
    else:
        # shortening the maxVisibilityRadiusM according to the distance remained to the SRTM latitude range boundaries (-56 to 60)
        if distanceM < maxVisibilityRadiusM:
            correctedMaskRadiusM = int(distanceM)
            validVisibilityRadiusM = False
            printMsg = "This component downloads free topography data from opentopography.org in order to create a Terrain shading mask for the chosen _location.\n" + \
                       "But mentioned free topography data has limits: from -56 South to 60 North latitude.\n" + \
                       "The closer the location is to upper mentioned boundaries, the inputted \"maxVisibilityRadius_\" value may have be shrank to make sure that the boundaries are not exceeded.\n" + \
                       "In this case the _location you chose is %s km away from the %s latitude boundary.\n" % (int(correctedMaskRadiusM/1000), SRTMlimit) + \
                       " \n" + \
                       "Please supply the \"maxVisibilityRadius_\" input with value: %s.\n" % int(correctedMaskRadiusM/1000) + \
                       " \n" + \
                       "Also if upper mentioned value is less than 50 (km), it means that opentopography.org topography data may not be good enough to generate this Terrain shading mask.\n" + \
                       "There might be a way to create a Terrain shading mask for your _location not based on upper mentioned opentopography.org data, but rather from different topography sources.\n" + \
                       "To get help, open a new topic about this issue at:\n" + \
                       "http://www.grasshopper3d.com/group/ladybug/forum/topics/terrain-shading-mask-component-released or\n" + \
                       "https://github.com/stgeorges/terrainShadingMask/issues"
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
    downloadRasterLink = "http://opentopo.sdsc.edu/otr/getdem?demtype=SRTMGL3&west=%s&south=%s&east=%s&north=%s&outputFormat=GTiff" % (longitudeLeftD,latitudeBottomD,longitudeRightD,latitudeTopD)
    
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
    
    fileName = fileNameIncomplete + "_visibility=" + str(minVisibilityRadiusKM) + "-" + str(int(maxVisibilityRadiusM/1000)) + "KM"
    fileName2 = fileNameIncomplete + "_visibility=" + str(int(maxVisibilityRadiusM/1000)) + "KM"
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
            printMsg = "This component requires you to be connected to the Internet, in order to create a Terrain shading mask.\n" + \
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
                printMsg = "This component dowloads free topography data from opentopography.org in order to create a Terrain shading mask for the chosen _location.\n" + \
                           "But mentioned free topography data has its limits: from -56 South to 60 North latitude.\n" + \
                           "Your _location's latitude exceeds the upper mentioned limits.\n" + \
                           " \n" + \
                           "There might be a way to create a Terrain shading mask for your _location not based on upper mentioned opentopography.org data, but rather from different topography sources.\n" + \
                           "To get help, open a new topic about this issue at:\n" + \
                           "http://www.grasshopper3d.com/group/ladybug/forum/topics/terrain-shading-mask-component-released or\n" + \
                           "https://github.com/stgeorges/terrainShadingMask/issues"
            else:
                # location within the -56 to 60 latittude limits
                # correct (shorten) the maxVisibilityRadiusM according to the distance remained to the SRTM latitude range boundaries (-56 to 60)
                correctedMaskRadiusM, validVisibilityRadiusM, printMsg = distanceBetweenTwoPoints(locationLatitudeD, locationLongitudeD, maxVisibilityRadiusM)
                if validVisibilityRadiusM == True:
                    # (correctedMaskRadiusM >= maxVisibilityRadiusM)
                    downloadRasterLink_withCorrectedMaskRadiusKM = destinationLatLon(locationLatitudeD, locationLongitudeD, correctedMaskRadiusM)
                    # new rasterFileNamePlusExtension and rasterFilePath corrected according to new correctedMaskRadiusM
                    rasterFileNamePlusExtension_withCorrectedMaskRadiusKM = fileNameIncomplete + "_visibility=" + str(int(maxVisibilityRadiusM/1000)) + "KM" + ".tif"  # rasterFileNamePlusExtension_withCorrectedMaskRadiusKM will always be used instead of rasterFilePath from line 647 !!!
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
                        printMsg = "This component requires topography data to be downloaded from opentopography.org as a prerequisite for creating a Terrain shading mask. It has just failed to do that. Try the following two fixes:\n" + \
                                   " \n" + \
                                   "1) Sometimes due to large number of requests, the component fails to download the topography data even if opentopography.org website and their services are up and running.\n" + \
                                   "In this case, wait a couple of seconds and try reruning the component.\n" + \
                                   " \n" + \
                                   "2) opentopography.org website could be up and running, but their SRTM service may be down (this already happened before).\n" + \
                                   "Try again in a couple of hours or tomorrow.\n" + \
                                   " \n" + \
                                   "If each of two mentioned advices fails, open a new topic about this issue on: www.grasshopper3d.com/group/ladybug/forum."
                
                elif validVisibilityRadiusM == False:
                    # (correctedMaskRadiusM < 1) or (correctedMaskRadiusM < maxVisibilityRadiusM)
                    elevationM = None
                    valid_Obj_or_Raster_file = False
                    rasterFilePath = "needless"  # dummy
                    #printMsg - from distanceBetweenTwoPoints function
    
    
    return terrainShadingMask, origin_0_0_0, fileName, objFilePath, rasterFilePath, rasterFilePath_aeqd, rasterFileNamePlusExtension_aeqd, vrtFilePath, elevationM, valid_Obj_or_Raster_file, printMsg


def resampleRasterFile(rasterFileNamePlusExtension_aeqd, vrtFilePath, numOfCellsInX, numOfCellsInY, topLeftX, westEastPixelResolution, rotation1, topLeftY, rotation2, northSouthPixelResolution):
    
    rasterCellsReductionFactor = 2  # resample from 3 arc-second to 6 arc-second format
    
    reducedNumOfCellsInX = int(numOfCellsInX/rasterCellsReductionFactor)
    reducedNumOfCellsInY = int(numOfCellsInY/rasterCellsReductionFactor)
    
    if reducedNumOfCellsInX % 2 == 0:
        # reducedNumOfCellsInX is even number, convert it to odd
        reducedNumOfCellsInX = reducedNumOfCellsInX + 1
    
    if reducedNumOfCellsInY % 2 == 0:
        # reducedNumOfCellsInY is even number, convert it to odd
        reducedNumOfCellsInY = reducedNumOfCellsInY + 1
    
    
    reducedWestEastPixelResolution = (abs(westEastPixelResolution)*numOfCellsInX)/reducedNumOfCellsInX
    if westEastPixelResolution >= 0:
        reducedWestEastPixelResolution = reducedWestEastPixelResolution
    elif westEastPixelResolution < 0:
        reducedWestEastPixelResolution = -reducedWestEastPixelResolution
    
    reducedNorthSouthPixelResolution = (abs(northSouthPixelResolution)*numOfCellsInY)/reducedNumOfCellsInY
    if northSouthPixelResolution >= 0:
        reducedNorthSouthPixelResolution = reducedNorthSouthPixelResolution
    elif northSouthPixelResolution < 0:
        reducedNorthSouthPixelResolution = -reducedNorthSouthPixelResolution
    
    # based on: http://www.gdal.org/gdal_vrttut.html
    vrtFileList = [
    '    <VRTDataset rasterXSize="%s" rasterYSize="%s">\n' % (reducedNumOfCellsInX, reducedNumOfCellsInY),
    '      <GeoTransform>%s, %s, %s, %s, %s, %s</GeoTransform>\n' % (topLeftX, reducedWestEastPixelResolution, rotation1, topLeftY, rotation2, reducedNorthSouthPixelResolution),
    '      <VRTRasterBand dataType="Byte" band="1">\n',
    '        <ColorInterp>Gray</ColorInterp>\n',
    '        <SimpleSource>\n',
    '          <SourceFilename relativeToVRT="1">%s</SourceFilename>\n' % rasterFileNamePlusExtension_aeqd,
    '          <SourceBand>1</SourceBand>\n',
    '          <SrcRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>\n' % (numOfCellsInX, numOfCellsInY),
    '          <DstRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>\n' % (reducedNumOfCellsInX, reducedNumOfCellsInY),
    '        </SimpleSource>\n',
    '      </VRTRasterBand>\n',
    '    </VRTDataset>'
    ] 
    
    # create a .vrt file
    objFileLines = []
    myFile = open(vrtFilePath,"w")
    for line in vrtFileList:
        myFile.write(line)
    myFile.close()
    
    # returning reducedNumOfCellsInX, reducedNumOfCellsInY, reducedCellsizeX, reducedCellsizeY
    return reducedNumOfCellsInX, reducedNumOfCellsInY, reducedWestEastPixelResolution, reducedNorthSouthPixelResolution


def ptZcorrectedHeight(locationPt, meshPt, scaleFactor):
    # Correcting mesh vertices for Earth's curvature and refraction  
    # source: "Surveying And Levelling" second edition, N.N. Basak, McGraw Hill Education (India) Private Limited, p161
    
    meshPtDistanceFromOriginMeters = locationPt.DistanceTo(meshPt)  # in Rhino units (meters if Rhino document is set to meters)
    meshPtDistanceFromOriginMeters = meshPtDistanceFromOriginMeters/scaleFactor
    meshPtDistanceFromOriginKM = meshPtDistanceFromOriginMeters/1000  # in km
    ptZCorrection = (0.0675 * (meshPtDistanceFromOriginKM**2))  # refraction and curvature correction (in meters)
    
    return ptZCorrection


def createTerrainShadingMask(GDAL_librariesFolderPath, objFilePath, rasterFilePath, rasterFilePath_aeqd, rasterFileNamePlusExtension_aeqd, vrtFilePath, locationLatitudeD, locationLongitudeD, heightM, minVisibilityRadiusM, maxVisibilityRadiusM, maskStyle, context, unitConversionFactor):
    
    # open the raster file
    accessReadOnly = gdalc.Access.GA_ReadOnly
    dataset = gdalc.Gdal.Open(rasterFilePath, accessReadOnly)
    
    # input crs
    inputCRS = osrc.SpatialReference("")
    inputCRS.ImportFromEPSG(4326)
    integer, datasetInputCRS = inputCRS.ExportToWkt()
    
    # output crs
    outputCRS = osrc.SpatialReference("")
    outputCRS_wktString = "+proj=aeqd +datum=WGS84 +ellps=WGS84 +lat_0=%s +lon_0=%s" % (locationLatitudeD, locationLongitudeD)
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
    numOfCellsInX = datasetWarped.RasterXSize
    numOfCellsInY = datasetWarped.RasterYSize
    
    reducedNumOfCellsInX, reducedNumOfCellsInY, reducedCellsizeX, reducedCellsizeY = resampleRasterFile(rasterFileNamePlusExtension_aeqd, vrtFilePath, numOfCellsInX, numOfCellsInY, topLeftX, westEastPixelResolution, rotation1, topLeftY, rotation2, northSouthPixelResolution)
    
    driver = gdalc.Gdal.GetDriverByName("GTiff")  
    datasetWarpedDummy = driver.CreateCopy(rasterFilePath_aeqd, datasetWarped, False, None, None, None)  # datasetWarpedDummy equals to datasetWarped
    datasetWarpedDummy.Dispose()
    
    # resample the saved aeqd.tif file from 3 arc-second to 6 arc-second format
    datasetWarped = gdalc.Gdal.Open(rasterFilePath_aeqd, accessReadOnly)
    datasetWarped.Dispose()
    datasetWarped = gdalc.Gdal.Open(vrtFilePath, gdalc.Access.GA_ReadOnly)  # datasetWarped6arcsec
    
    # read the elevation values
    bandWarped = datasetWarped.GetRasterBand(datasetWarped.RasterCount)
    ptZL = System.Array.CreateInstance(System.Int32, bandWarped.XSize*bandWarped.YSize)
    bandWarped.ReadRaster(0, 0, datasetWarped.RasterXSize, datasetWarped.RasterYSize, ptZL, datasetWarped.RasterXSize, datasetWarped.RasterYSize, 0, 0)
    
    # check if reprojection of initial WGS84 raster file ended up with correct center point
    locationPt_projectedCoordinates = ogrc.Geometry(ogrc.wkbGeometryType.wkbPoint)
    locationPt_projectedCoordinates.AddPoint(locationLongitudeD, locationLatitudeD, 0)
    
    #coordinateTransformation = osrc.Osr.CreateCoordinateTransformation(inputCRS, outputCRS)
    #locationPt_projectedCoordinates.Transform(coordinateTransformation)  # transform the _location point from +proj=latlong(WGS84) to +proj=aeqd
    #print "locationPt_projectedCoordinates (X,Y): ", locationPt_projectedCoordinates.GetX(0), locationPt_projectedCoordinates.GetY(0)  # always use "0" as an argument
    
    # calculate the starting point (upper left corner) of terrain mesh
    scaleFactor = 0.01  # scale terrainMesh 100 times (should never be changed), meaning 1 meter in real life is 0.01 meters in Rhino document
    origin_0_0_0 = Rhino.Geometry.Point3d(0,0,0)  # always center the terrainMesh to 0,0,0 point
    terrainMeshStartPtX = origin_0_0_0.X - ((reducedNumOfCellsInX-1)* (abs(reducedCellsizeX)*scaleFactor)/2)
    terrainMeshStartPtY = origin_0_0_0.Y + ((reducedNumOfCellsInY-1)* (abs(reducedCellsizeY)*scaleFactor)/2)
    terrainMeshStartPtXCorrection = ( topLeftX + (reducedCellsizeX * (reducedNumOfCellsInX/2)) )*scaleFactor
    terrainMeshStartPtYCorrection = ( topLeftY + (reducedCellsizeY * (reducedNumOfCellsInY/2)) )*scaleFactor
    
    terrainMeshStartPtX = terrainMeshStartPtX + terrainMeshStartPtXCorrection
    terrainMeshStartPtY = terrainMeshStartPtY + terrainMeshStartPtYCorrection
    
    xIndex = reducedNumOfCellsInX
    yIndex = reducedNumOfCellsInY
    zIndex = 0
    pts = []
    
    # create terrainMesh from 6 arc-second format
    for k in xrange(reducedNumOfCellsInY):
        for i in xrange(reducedNumOfCellsInX):
            ptZ = ptZL[zIndex]
            pt_ZcoordZero = Rhino.Geometry.Point3d(terrainMeshStartPtX+(i*abs(reducedCellsizeX)*scaleFactor), terrainMeshStartPtY-(k*abs(reducedCellsizeY)*scaleFactor), 0)
            ptZCorrection = ptZcorrectedHeight(origin_0_0_0, pt_ZcoordZero, scaleFactor)  # in meters, unscaled
            ptCorrected = Rhino.Geometry.Point3d(pt_ZcoordZero.X, pt_ZcoordZero.Y, (ptZ-ptZCorrection)*scaleFactor)
            pts.append(ptCorrected)
            xIndex += 1
            zIndex += 1
        yIndex -= 1
        xIndex = terrainMeshStartPtX
    
    terrainMesh = lb_meshpreparation.meshFromPoints(datasetWarped.RasterYSize, datasetWarped.RasterXSize, pts)
    
    # deleting
    datasetWarped.Dispose()
    bandWarped.Dispose()
    #os.remove(rasterFilePath)  # downloaded .tif file
    os.remove(rasterFilePath_aeqd)
    os.remove(vrtFilePath)
    del ptZL
    del pts
    
    
    # project origin_0_0_0 (locationPt) to terrainMesh
    safeHeightDummy = 10000  # in meters
    elevatedOrigin = Rhino.Geometry.Point3d(origin_0_0_0.X, origin_0_0_0.Y, (origin_0_0_0.Z+safeHeightDummy)*scaleFactor)  # project origin_0_0_0 to terrainMesh
    ray = Rhino.Geometry.Ray3d(elevatedOrigin, Rhino.Geometry.Vector3d(0,0,-1))
    rayIntersectParam = Rhino.Geometry.Intersect.Intersection.MeshRay(terrainMesh, ray)
    locationPt = ray.PointAt(rayIntersectParam)
    
    heightScaled = heightM * scaleFactor
    locationPt.Z = locationPt.Z + heightScaled  # lifting up the locationPt for "height_" input (minimum 2 meters)
    elevationM = locationPt.Z/scaleFactor  # in meters
    elevationM = round(elevationM,2)
    
    
    minVisibilityRadiusScaled = minVisibilityRadiusM * scaleFactor
    if minVisibilityRadiusM > 0:
        # split the terrainMesh with a sphere to exclude the terrainMesh area minVisibilityRadiusKM around the locationPt
        meshSphere = Rhino.Geometry.Mesh.CreateFromSphere(Rhino.Geometry.Sphere(locationPt, minVisibilityRadiusScaled), 12, 10)
        terrainMeshSplitted = terrainMesh.Split(meshSphere)[0]
    else:
        # minVisibilityRadius_ input == 0. No splitting of the terrainMesh
        terrainMeshSplitted = terrainMesh
    
    
    # create skyDome
    skyDomeRadius = 200 / unitConversionFactor  # in meters
    skyDomeSphere = Rhino.Geometry.Sphere(locationPt, skyDomeRadius)
    skyDomeSrf = skyDomeSphere.ToBrep().Faces[0]
    
    # small number of rays (for example: precisionU = 30, precisionV = 10) can result in rays missing the terrainMesh, thererfor the shadingMaskSrf will not be created
    precisionU = 3600  # rays shot per 0.1 degrees (10th of a degree)
    precisionV = 1200  # rays shot per 0.075 degrees - more denser than precisionU
    
    halvedSkyDomeSrf = skyDomeSrf.Trim(Rhino.Geometry.Interval(skyDomeSrf.Domain(0)[0], skyDomeSrf.Domain(0)[1]), Rhino.Geometry.Interval(0, skyDomeSrf.Domain(1)[1])) # split the skyDome sphere in half
    halvedSkyDomeSrf.SetDomain(1, Rhino.Geometry.Interval(0, halvedSkyDomeSrf.Domain(1)[1]))  # shrink the halvedSkyDomeSrf V start domain
    skyDomeDomainUmin, skyDomeDomainUmax = halvedSkyDomeSrf.Domain(0)
    skyDomeDomainVmin, skyDomeDomainVmax = halvedSkyDomeSrf.Domain(1)
    stepU = (skyDomeDomainUmax - skyDomeDomainUmin)/precisionU
    stepV = (skyDomeDomainVmax - skyDomeDomainVmin)/precisionV
    
    # check for intersection between the terrainMesh and rays
    lines = []
    lastRowPoints = []
    
    hitted = False  # initial switch
    for i in xrange(0,precisionU):
        for k in xrange(0,precisionV):
            u = skyDomeDomainUmin + stepU*i
            v = skyDomeDomainVmin + stepV*k
            skyDomePt = halvedSkyDomeSrf.PointAt(u,v)
            rayVector = skyDomePt-locationPt
            ray = Rhino.Geometry.Ray3d(locationPt, rayVector)
            rayIntersectParam = Rhino.Geometry.Intersect.Intersection.MeshRay(terrainMeshSplitted,ray)
            if rayIntersectParam >= 0:
                # ray hitted something in that column
                hitted = True
                lastRowPt = skyDomePt
                continue
            else:
                # ray did not hit anything in that column
                pass
        if hitted == False:
            lastRowPt = halvedSkyDomeSrf.PointAt(u,0)
        line = Rhino.Geometry.Line(locationPt, lastRowPt)
        lines.append(line.ToNurbsCurve())
        lastRowPoints.append(lastRowPt)
        hitted = False  # reset the hitted switch
    
    del terrainMesh
    del terrainMeshSplitted
    
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    if maskStyle == 0:  # spherical terrain shading mask
        loftType = Rhino.Geometry.LoftType.Loose
        loftedLinesBrep = Rhino.Geometry.Brep.CreateFromLoft(lines, Rhino.Geometry.Point3d.Unset, Rhino.Geometry.Point3d.Unset, loftType, True)[0]
        loftedLinesSrf = loftedLinesBrep.Faces[0]
        extendedLoftedLinesSrf = loftedLinesSrf.Extend(Rhino.Geometry.IsoStatus.North, skyDomeRadius, False)
        splittedHalvedSkyDomeSrfs = halvedSkyDomeSrf.ToBrep().Split(extendedLoftedLinesSrf.ToBrep(), tol)[:-1]
        shadingMaskBreps = splittedHalvedSkyDomeSrfs
    elif maskStyle == 1:  # extruded (vertical) terrain shading mask
        curveLastRowPoints = Rhino.Geometry.Curve.CreateControlPointCurve(lastRowPoints+[lastRowPoints[0]], 3)
        extrudedShadingMaskSrf = Rhino.Geometry.Surface.CreateExtrusion(curveLastRowPoints, Rhino.Geometry.Vector3d(0,0,-skyDomeRadius)).ToBrep()
        shadingMaskBreps = extrudedShadingMaskSrf.Trim(Rhino.Geometry.Plane(locationPt, Rhino.Geometry.Vector3d(0,0,-1)), tol)
    [brep.Faces.ShrinkFaces() for brep in shadingMaskBreps]  # shrinking the breps in-place, so that they can be exported to an .obj file
    
    
    if len(shadingMaskBreps) == 0:
        # no intersection between rays and mesh (low precisionU and precisionV values may result in this too)
        terrainShadingMaskUnscaledUnrotated = None
        level = gh.GH_RuntimeMessageLevel.Warning
        printMsg = "There is no shading from terrain. This could be due to two reasons:\n" + \
                   " \n" + \
                   "1) There really is no shading from the surrounding terrain: For example, you chose your _location to be on a peak point of an island, without any terrain or islands around it.\n" + \
                   "2) There might be shading from a terrain, but the \"maxVisibilityRadius_\" you inputted is too short to show this. Try increasing the size of the \"maxVisibilityRadius_\"."
        ghenv.Component.AddRuntimeMessage(level, printMsg)
        print printMsg
    else:
        # there is an intersection between rays and mesh
        terrainShadingMaskUnscaledUnrotated = Rhino.Geometry.Brep.MergeBreps(shadingMaskBreps, tol)  # merge the shadingMaskBreps into a single brep
        # allign the terrainShadingMaskUnscaledUnrotated to "origin_0_0_0" point, instead of locationPt
        translationVec = origin_0_0_0 - locationPt
        transformMatrix = Rhino.Geometry.Transform.Translation(translationVec)
        transformSuccess = terrainShadingMaskUnscaledUnrotated.Transform(transformMatrix)
        
        # export the created Terrain shading mask to .obj
        terrainShadingMaskDummy, origin_0_0_0Dummy = import_export_origin_0_0_0_and_terrainShadingMask_from_objFile("exportObj", objFilePath, fileNameIncomplete, heightM, minVisibilityRadiusM, maxVisibilityRadiusM, elevationM, terrainShadingMaskUnscaledUnrotated, origin_0_0_0)
    
    
    # final deleting
    del lines
    del lastRowPoints
    gc.collect()
    
    return terrainShadingMaskUnscaledUnrotated, origin_0_0_0, elevationM


def scaleTerrainShadingMask(context, terrainShadingMaskUnscaledUnrotated, origin_0_0_0, latitude):
    
    # remove "None" from context_
    contextMeshesFiltered = []
    for mesh in context:
        if mesh != None:
            contextMeshesFiltered.append(mesh)
    
    contextMeshOnly = Rhino.Geometry.Mesh()  # for finding the contextBBoxBottom4points
    for filteredContextMesh in contextMeshesFiltered:
        contextMeshOnly.Append(filteredContextMesh)
    
    unitConversionFactor2 = lb_preparation.checkUnits()
    if len(contextMeshesFiltered) == 0:
        # "context_" input is empty, or it contains the data but with "None" values
        scale = 1 / unitConversionFactor2
        terrainShadingMaskScaled_radius = int(200 / unitConversionFactor2)
        contextRadius = 0
        contextCentroid = Rhino.Geometry.Point3d(0,0,0)
    
    else:
        # valid geometry (other than "None") inputted to "context_"
        # get the bounding box of the "context_"
        accurate = False
        bboxAroundContextMeshesOnly = contextMeshOnly.GetBoundingBox(accurate)
        contextBBoxBottom4points = bboxAroundContextMeshesOnly.GetCorners()[:4]  # pick four bottom points of the bounding box surrounding all of the "context_" input
        contextRadius = int(contextBBoxBottom4points[0].DistanceTo(contextBBoxBottom4points[2])/2)  # in Rhino document units
        # calculate contextCentroid
        startingSumPts = Rhino.Geometry.Point3d(0,0,0)
        for pt in contextBBoxBottom4points:
            startingSumPts += pt
        contextCentroid = startingSumPts/len(contextBBoxBottom4points)  # average point
        
        # check the distance between the 0,0,0 origin and the contextCentroid
        if origin_0_0_0.DistanceTo(contextCentroid) > 500:  # the distance between the 0,0,0 point and originPt should not be larger than 500 Rhino document Units (not meters!)
            scale = terrainShadingMaskScaled_radius = contextRadius = None
            validContextCentroid = False
            printMsg = "Radius of the terrain shading mask may range to a couple of kilometers. If not centered to the 0,0,0 point, such distant geometry can experience inaccuracy problems due to floating-point precision.\n" + \
                       "To prevent this the center of the terrain shading mask (that's the \"originPt\" output) should not be more than 500 Rhino document units distant from the Rhino document's 0,0,0 origin.\n" + \
                       "The \"originPt\" output is calculated as the centroid of the bottom face of the context_ bounding box. So to make the component work, just try to approximately center the \"originPt\" to the 0,0,0 point.\n" + \
                       "Then rerun the component."
            return scale, terrainShadingMaskScaled_radius, contextRadius, contextCentroid, validContextCentroid, printMsg
        
        diagonalDistance = contextBBoxBottom4points[0].DistanceTo(contextBBoxBottom4points[2])   # in Rhino document units
        terrainShadingMaskScaled_startingRadius = int(math.ceil((diagonalDistance/2)/100)*100)  # round the radius to 100 (in Rhino document units)
        if terrainShadingMaskScaled_startingRadius < (300/unitConversionFactor2): terrainShadingMaskScaled_startingRadius = int(300/unitConversionFactor2)  # minimal terrainShadingMaskScaled_startingRadius set to 300 meters
        
        # move the terrainShadingMaskUnscaledUnrotated from origin_0_0_0 to contextCentroid, and rotate it for the north_ input. This "terrainShadingMaskScaledRotated_forMesh" variable is only used for scaling not as the final "terrainShadingMask"
        terrainShadingMaskScaledRotated_forMesh = terrainShadingMaskUnscaledUnrotated.DuplicateBrep()
        originTransformMatrix = Rhino.Geometry.Transform.PlaneToPlane(  Rhino.Geometry.Plane(origin_0_0_0, Rhino.Geometry.Vector3d(0,0,1)), Rhino.Geometry.Plane(contextCentroid, Rhino.Geometry.Vector3d(0,0,1)) )
        # rotation due to north angle position
        #transformMatrixRotate = Rhino.Geometry.Transform.Rotation(-northRad, Rhino.Geometry.Vector3d(0,0,1), contextCentroid)  # counter-clockwise
        rotateTransformMatrix = Rhino.Geometry.Transform.Rotation(northRad, Rhino.Geometry.Vector3d(0,0,1), contextCentroid)  # clockwise
        terrainShadingMaskScaledRotated_forMesh.Transform(originTransformMatrix)
        terrainShadingMaskScaledRotated_forMesh.Transform(rotateTransformMatrix)
        
        meshParam = Rhino.Geometry.MeshingParameters()
        meshParam.MinimumEdgeLength = 0.0001
        meshParam.SimplePlanes = True
        shadingTerrainMaskMeshes = Rhino.Geometry.Mesh.CreateFromBrep(terrainShadingMaskScaledRotated_forMesh, meshParam)  # it can contain more than one mesh
        terrainShadingMaskMesh = Rhino.Geometry.Mesh()  # for scaling of terrainShadingMask
        for meshMaskPart in shadingTerrainMaskMeshes:
            terrainShadingMaskMesh.Append(meshMaskPart)
        
        skyDomeRadius = 200/unitConversionFactor2  # fixed to 200 meters always
        objFileRadius = 200  # in Rhino units
        precision = 100  # low "precision" values can result in low "terrainShadingMaskScaled_radius" values
        skyDomeMeshes = []
        scaledTerrainShadingMaskMeshL = []
        for terrainShadingMaskScaled_radius in rs.frange(terrainShadingMaskScaled_startingRadius, int(10100/unitConversionFactor2), int(300/unitConversionFactor2)):  # iterrate terrainShadingMaskScaled_radius from 300 to 10000
            scale = terrainShadingMaskScaled_radius/objFileRadius
            
            transformMatrix = Rhino.Geometry.Transform.Scale(Rhino.Geometry.Plane(contextCentroid,Rhino.Geometry.Vector3d(0,0,1)), scale, scale, scale)
            scaledTerrainShadingMaskMesh = Rhino.Geometry.Mesh()  # always initialize new mesh
            scaledTerrainShadingMaskMesh.Append(terrainShadingMaskMesh)
            scaledTerrainShadingMaskMesh.Transform(transformMatrix)
            scaledTerrainShadingMaskMeshL.append(scaledTerrainShadingMaskMesh)
            
            conditionSum = 0
            for i,cornerPt in enumerate(contextBBoxBottom4points):
                skyExposureFactor = lb_photovoltaics.calculateSkyExposureFactor(cornerPt, [scaledTerrainShadingMaskMesh], latitude, skyDomeRadius, precision)
                
                if i == 0:
                    skyExposureFactor0 = skyExposureFactor  # for the first step, both skyExposureFactor0 and skyExposureFactor1 equal to skyExposureFactor
                skyExposureFactor1 = skyExposureFactor
                skyExposureFactorDifference = abs(skyExposureFactor0 - skyExposureFactor1)
                
                if skyExposureFactorDifference < 0.01:
                    condition = True
                else:
                    condition = False
                conditionSum += condition
            
            if (conditionSum == len(contextBBoxBottom4points)):
                break
            else:
                conditionSum = 0
        
        # the 1% skyExposureFactorDifference may be fulfilled, but annualShading might not. Increase the "terrainShadingMaskScaled_radius" 3 times
        terrainShadingMaskScaled_radius = 3 * terrainShadingMaskScaled_radius
        scale = 3 * scale
        
        # check if terrainShadingMaskScaled_radius is smaller than 10000 meters (32786 feets)
        if (terrainShadingMaskScaled_radius < 10000/unitConversionFactor2):
            terrainShadingMaskScaled_radius = int(10000/unitConversionFactor2)  # minimal terrainShadingMaskScaled_radius set to 10000 meters (32786 feets)
            scale = terrainShadingMaskScaled_radius/objFileRadius
    
    validContextCentroid = True
    printMsg = "ok"
    
    return scale, terrainShadingMaskScaled_radius, contextRadius, contextCentroid, validContextCentroid, printMsg


def compassCrvs_title_scalingRotating(origin_0_0_0, contextCentroid, scale, northVec, terrainShadingMaskUnscaledUnrotated, locationName, locationLatitudeD, locationLongitudeD, heightM, elevationM, minVisibilityRadiusM, maxVisibilityRadiusM, unitConversionFactor):
    
    skyDomeRadius = 200 / unitConversionFactor  # in meters
    outerBaseCrv = Rhino.Geometry.Circle(origin_0_0_0, 1.08*skyDomeRadius).ToNurbsCurve()  # compassCrv outerBaseCrv
    
    
    # title
    legendFont = "Verdana"; legendScale = 1; legendBold = None
    lb_visualization.calculateBB([outerBaseCrv])
    legendFontSize = ((lb_visualization.BoundingBoxPar[2]/10)/3) * legendScale
    legendFontSize = legendFontSize * 1.2  # enlarge the title font size 1.2 times of the legend font size
    
    titleLabelOrigin = lb_visualization.BoundingBoxPar[5]
    titleLabelOrigin.Y = titleLabelOrigin.Y - skyDomeRadius/3
    
    descriptionLabelOrigin = Rhino.Geometry.Point3d(titleLabelOrigin.X, titleLabelOrigin.Y-skyDomeRadius/5, titleLabelOrigin.Z)
    
    titleLabelText = "Terrain shading mask"
    titleLabelMeshes = lb_visualization.text2srf([titleLabelText], [titleLabelOrigin], legendFont, legendFontSize*1.2, legendBold, None, 6)[0]
    
    descriptionLabelText = "Location: %s\nLatitude: %s, Longitude: %s\nElevation: %sm, Visibility radius: %s-%skm" % (locationName, locationLatitudeD, locationLongitudeD, elevationM, int(minVisibilityRadiusM/1000), int(maxVisibilityRadiusM/1000))
    descriptionLabelMeshes = lb_visualization.text2srf([descriptionLabelText], [descriptionLabelOrigin], legendFont, legendFontSize, legendBold, None, 6)[0]
    
    titleDescriptionLabelMeshes = titleLabelMeshes + descriptionLabelMeshes
    
    
    # compass curves
    textSize3 = skyDomeRadius/25; legendBold3 = True; 
    compassCrvs, compassTextPts, compassText = lb_visualization.compassCircle(origin_0_0_0, northVec, skyDomeRadius, range(0, 360, 30), textSize3)
    numberCrvs = lb_visualization.text2srf(compassText, compassTextPts, legendFont, textSize3, legendBold3)
    compassCrvs = compassCrvs + lb_preparation.flattenList(numberCrvs)
    compassCrvs = compassCrvs + [outerBaseCrv]
    
    
    
    ## scaling
    # move to a new contextCentroid
    origin_0_0_0_point3d = Rhino.Geometry.Point3d(origin_0_0_0)  # convert Point to Point3d
    transformMatrixOrigin = Rhino.Geometry.Transform.PlaneToPlane( Rhino.Geometry.Plane(origin_0_0_0_point3d, Rhino.Geometry.Vector3d(0,0,1)), Rhino.Geometry.Plane(contextCentroid, Rhino.Geometry.Vector3d(0,0,1)) )
    
    # rotation due to north angle position
    #transformMatrixRotate = Rhino.Geometry.Transform.Rotation(-northRad, Rhino.Geometry.Vector3d(0,0,1), contextCentroid)  # counter-clockwise
    transformMatrixRotate = Rhino.Geometry.Transform.Rotation(northRad, Rhino.Geometry.Vector3d(0,0,1), contextCentroid)  # clockwise
    # scaling
    transformMatrixScale = Rhino.Geometry.Transform.Scale(Rhino.Geometry.Plane(contextCentroid, Rhino.Geometry.Vector3d(0,0,1)), scale, scale, scale)
    
    terrainShadingMaskScaledRotated = terrainShadingMaskUnscaledUnrotated.DuplicateBrep()
    geometryList = [terrainShadingMaskScaledRotated]
    for geometry in geometryList:
        if geometry != None:  # if "terrainShadingMaskUnscaledUnrotated" is not created (equals None) due to no intersection between rays and mesh, exclude it
            transformBoolSuccess = geometry.Transform(transformMatrixOrigin)
            transformBoolSuccess = geometry.Transform(transformMatrixRotate)
            transformBoolSuccess = geometry.Transform(transformMatrixScale)
    
    geometryList2 = compassCrvs + titleDescriptionLabelMeshes
    for geometry2 in geometryList2:
        # never rotate the compassCrvs!!
        transformBoolSuccess = geometry2.Transform(transformMatrixOrigin)
        transformBoolSuccess = geometry2.Transform(transformMatrixScale)
    
    
    # hide compassCrvs, title outputs, because they are not hidden in "Horizon angles" component
    ghenv.Component.Params.Output[3].Hidden = True
    ghenv.Component.Params.Output[4].Hidden = True
    
    return terrainShadingMaskScaledRotated, compassCrvs, titleDescriptionLabelMeshes


def bakingGrouping(locationName, locationLatitudeD, locationLongitudeD, heightM, minVisibilityRadiusM, maxVisibilityRadiusM, maskStyleLabel, origin, terrainShadingMask, compassCrvs, titleDescriptionLabelMeshes):
    
    layerName = locationName + "_" + str(locationLatitudeD) + "_" + str(locationLongitudeD) + "_VISIB=" + str(int(minVisibilityRadiusM/1000)) + "-" + str(int(maxVisibilityRadiusM/1000)) + "KM"
    
    layerIndex, l = lb_visualization.setupLayers(layerName, "LADYBUG", "TERRAIN_SHADING_MASK", "PHOTOVOLTAICS")
    
    attr = Rhino.DocObjects.ObjectAttributes()
    attr.LayerIndex = layerIndex
    attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
    attr.PlotColorSource = Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
    
    # bake terrainShadingMask, origin
    geometryIds = []
    geometry = [terrainShadingMask, Rhino.Geometry.Point(origin)]
    for obj in geometry:
        id = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj,attr)
        geometryIds.append(id)
    
    # bake compassCrvs
    geometryIds2 = []
    geometry2 = compassCrvs
    for obj2 in geometry2:
        id2 = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj2,attr)
        geometryIds2.append(id2)
    
    # bake title
    geometryIds3 = []
    geometry3 = titleDescriptionLabelMeshes
    for obj3 in geometry3:
        id3 = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj3,attr)
        geometryIds3.append(id3)
    
    # grouping of terrainShadingMask, origin
    groupIndex = Rhino.RhinoDoc.ActiveDoc.Groups.Add(layerName + "_terrainShadingMask_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex, geometryIds)
    
    # grouping of compassCrvs
    groupIndex2 = Rhino.RhinoDoc.ActiveDoc.Groups.Add(layerName + "_terrainShadingMask_compassCrvs_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex2, geometryIds2)
    
    # grouping of title
    groupIndex3 = Rhino.RhinoDoc.ActiveDoc.Groups.Add(layerName + "_terrainShadingMask_title_" + str(time.time()))
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex3, geometryIds3)


def printOutput(north, latitude, longitude, locationName, heightM, minVisibilityRadiusM, maxVisibilityRadiusM, maskStyle, workingSubFolderPath, downloadTSVLink):
    if maskStyle == 0:
        maskStyleLabel2 = "spherical"
    elif maskStyle == 1:
        maskStyleLabel2 = "extruded"
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    resultsCompletedMsg = "Terrain shading mask component results successfully completed %s!" % bakedOrNot
    printOutputMsg = \
    """
Input data:

Location (deg.): %s
Latitude (deg.): %s
Longitude (deg.): %s
North (deg.): %s

Minimal visibility radius (km): %s
Maximal visibility radius (km): %s
Mask style: %s (%s)
Working folder: %s
Download Url: %s
    """ % (locationName, latitude, longitude, 360-math.degrees(northRad), int(minVisibilityRadiusM/1000), int(maxVisibilityRadiusM/1000), maskStyle, maskStyleLabel2, workingSubFolderPath, downloadTSVLink)
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
                heightM, minVisibilityRadiusM, maxVisibilityRadiusM, northRad, northVec, maskStyle, maskStyleLabel, GDAL_librariesFolderPath, workingSubFolderPath, downloadTSVLink, unitConversionFactor, validInputData, printMsg = checkInputData(minVisibilityRadius_, maxVisibilityRadius_, north_, maskStyle_, workingFolder_, downloadUrl_)
                librariesFolder = GDAL_librariesFolderPath
                if validInputData:
                    if _runIt:
                        if validInputData:
                            terrainShadingMaskUnscaledUnrotated, origin_0_0_0, fileName, objFilePath, rasterFilePath, rasterFilePath_aeqd, rasterFileNamePlusExtension_aeqd, vrtFilePath, elevationM, valid_Obj_or_Raster_file, printMsg = checkObjRasterFile(fileNameIncomplete, workingSubFolderPath, downloadTSVLink, heightM, minVisibilityRadiusM, maxVisibilityRadiusM, maskStyleLabel)
                            if valid_Obj_or_Raster_file:
                                if (rasterFilePath != "needless") and (rasterFilePath != "download failed"):  # terrain shading mask NEEDS to be created
                                    terrainShadingMaskUnscaledUnrotated, origin_0_0_0, elevationM = createTerrainShadingMask(GDAL_librariesFolderPath, objFilePath, rasterFilePath, rasterFilePath_aeqd, rasterFileNamePlusExtension_aeqd, vrtFilePath, locationLatitudeD, locationLongitudeD, heightM, minVisibilityRadiusM, maxVisibilityRadiusM, maskStyle, context_, unitConversionFactor)
                                scale, terrainShadingMaskScaled_radius, contextRadius, contextCentroid, validContextCentroid, printMsg = scaleTerrainShadingMask(context_, terrainShadingMaskUnscaledUnrotated, origin_0_0_0, locationLatitudeD)
                                originPt = contextCentroid
                                if validContextCentroid:
                                    terrainShadingMaskScaledRotated, compassCrvs, titleDescriptionLabelMeshes = compassCrvs_title_scalingRotating(origin_0_0_0, contextCentroid, scale, northVec, terrainShadingMaskUnscaledUnrotated, locationName, locationLatitudeD, locationLongitudeD, heightM, elevationM, minVisibilityRadiusM, maxVisibilityRadiusM, unitConversionFactor)
                                    if bakeIt_: bakingGrouping(locationName, locationLatitudeD, locationLongitudeD, heightM, minVisibilityRadiusM, maxVisibilityRadiusM, maskStyleLabel, contextCentroid, terrainShadingMaskScaledRotated, compassCrvs, titleDescriptionLabelMeshes)
                                    printOutput(northRad, locationLatitudeD, locationLongitudeD, locationName, heightM, minVisibilityRadiusM, maxVisibilityRadiusM, maskStyle, workingSubFolderPath, downloadTSVLink)
                                    terrainShadingMask = terrainShadingMaskScaledRotated; title = titleDescriptionLabelMeshes; maskRadius = terrainShadingMaskScaled_radius; elevation = elevationM
                                else:
                                    print printMsg
                                    ghenv.Component.AddRuntimeMessage(level, printMsg)
                            else:
                                print printMsg
                                ghenv.Component.AddRuntimeMessage(level, printMsg)
                        else:
                            print printMsg
                            ghenv.Component.AddRuntimeMessage(level, printMsg)
                    else:
                        print "All inputs are ok. Please set \"_runIt\" to True, in order to run the Terrain shading mask component"
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
