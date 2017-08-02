# Open EPW and STAT weather files together
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to automatically download a .zip file from the Department of Energy's (DOE) database, unzip the file, and open both the .epw and .stat weather files into Grasshopper.
The component requires the URL of the zipped file for the specific climate that you want to import from the DOE's website.  To open the DOE's website, use the Ladybug_download EPW Weather File component.
Note that you can copy the zip file URL to your clipboard by right-clicking on the "ZIP" link for the climate that you want on the DOE's website and choosing "Copy Link Address."
-
Provided by Ladybug 0.0.65
    
    Args:
        _weatherFileURL: A text string representing the .zip file URL from the Department of Energy's (DOE's) website. To open the DOE's website, use the Ladybug_download EPW Weather File component. Note that you can copy the zip file URL to your clipboard by right-clicking on the "ZIP" link for the climate that you want on the DOE's website and choosing "Copy Link Address."
        workingDir_: An optional text string representing a file path to a working directory on your computer where you would like to download and unzip the file.  If nothing is set, the weather files will be downloaded to C:/ladybug/ and placed in a folder with the name of the weather file location.
    Returns:
        epwFile: The file path of the downloaded epw file.
        statFile: The file path of the downloaded stat file.
"""
ghenv.Component.Name = "Ladybug_Open EPW And STAT Weather Files"
ghenv.Component.NickName = 'EPW+STAT'
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import scriptcontext as sc
import urllib
import os
import zipfile,os.path
import Grasshopper.Kernel as gh
import time
import System



def checkTheInputs(_weatherFileURL):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        
        lb_defaultFolder = sc.sticky["Ladybug_DefaultFolder"]
        
        if _weatherFileURL and (_weatherFileURL.startswith('https://') or _weatherFileURL.startswith('http://')):
            folderName = _weatherFileURL.split('/')[-2]
            checkData = True
        else:
            checkData = False
            warning1 = "_weatherFileURL is not a valid URL address to an EnergyPlus weather file. \n To ensure that you have a correct weather file web address, use the links from EPWMap that you get by right-clicking on a location:"
            warning2 = "http://mostapharoudsari.github.io/epwmap/"
            print warning1
            print warning2
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning1)
            ghenv.Component.AddRuntimeMessage(w, warning2)
        
        #If no working directory is specified, default to C:\ladybug.
        if workingDir_ != None and checkData == True:
            workingDir = workingDir_
        elif workingDir_ == None and checkData == True:
            workingDir = lb_defaultFolder + folderName + '\\'
        else:
            workingDir = None
        
        return checkData, workingDir, _weatherFileURL
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return False, None, None

def download(url, workingDir):
    try:
        if not os.path.isdir(workingDir):
            os.mkdir(workingDir)
        client = System.Net.WebClient()
        webFile = os.path.join(workingDir, url.split('/')[-2] + '.zip')
        client.DownloadFile(url, webFile)
        return webFile
        
    except Exception, e:
        warning = 'You are not connected to the internet or a firewall is preventing you from downloading the EPW file.\nConnect to the internet or make an exception for Rhino in your firewall and try again.'
        warning += '\n' + `e`
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return None

def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('\\')
            path = dest_dir
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''): continue
                path = os.path.join(path, word)
            zf.extract(member, path)

def addresses(directory):
    epw, stat = None, None
    try:
        keyText = directory.split('\\')[-2].replace('.','_')
    except:
        keyText = ''
    for file in os.listdir(directory):
        if file.endswith('.epw') and keyText in file.replace('.','_'):
            epw = directory + '/' + file
        elif file.endswith('.stat')and keyText in file.replace('.','_'):
            stat = directory + '/' + file
    
    return epw, stat

def checkIfAlreadyDownloaded(workingDir, url):
    try:
        if os.path.isdir(workingDir):
            epw, stat = addresses(workingDir)
            if os.path.isfile(epw) == True and os.path.isfile(stat) == True:
                return True, epw, stat
            else:
                return False, None, None
        else:
            return False, None, None
    except:
        return False, None, None



checkData = False
#Check the inputs to make sure that they are the correct syntax.
res = checkTheInputs(_weatherFileURL)

if res!= -1:
    checkData, workingDir, _weatherFileURL = res

#Check to see if the file has already been downloaded to the C:\ladybug drive.
if checkData == True:
    checkData2, epwFile, statFile = checkIfAlreadyDownloaded(workingDir, _weatherFileURL)
else: checkData2 = True

#Download the zip file to the directory.
if checkData == True and checkData2 == False:
    zipFileAddress = download(_weatherFileURL, workingDir)
else: pass

#Unzip the file and load it into Grasshopper!!!!
if checkData == True and checkData2 == False and zipFileAddress:
    unzip(zipFileAddress, workingDir)
    epwFile, statFile = addresses(workingDir)
else: pass