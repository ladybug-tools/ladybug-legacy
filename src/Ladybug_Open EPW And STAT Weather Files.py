# Open EPW and STAT weather files together
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2015, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Provided by Ladybug 0.0.62
    
    Args:
        _weatherFileURL: A text string representing the .zip file URL from the Department of Energy's (DOE's) website. To open the DOE's website, use the Ladybug_download EPW Weather File component. Note that you can copy the zip file URL to your clipboard by right-clicking on the "ZIP" link for the climate that you want on the DOE's website and choosing "Copy Link Address."
        workingDir_: An optional text string representing a file path to a working directory on your computer where you would like to download and unzip the file.  If nothing is set, the weather files will be downloaded to C:/ladybug/ and placed in a folder with the name of the weather file location.
    Returns:
        epwFile: The file path of the downloaded epw file.
        statFile: The file path of the downloaded stat file.
"""
ghenv.Component.Name = "Ladybug_Open EPW And STAT Weather Files"
ghenv.Component.NickName = 'Open EPW + STAT'
ghenv.Component.Message = 'VER 0.0.62\nJAN_23_2016'
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


def updateUrl(oldurl):
    """Update old url to new url"""
    # old: http://apps1.eere.energy.gov/buildings/energyplus/weatherdata/4_north_and_central_america_wmo_region_4/1_usa/USA_PA_Philadelphia.Intl.AP.724080_TMY3.zip
    # new: https://www.energyplus.net/weather-download/north_and_central_america_wmo_region_4/USA/PA/USA_PA_Philadelphia.Intl.AP.724080_TMY3/all
    
    if not oldurl: return
    
    oldurl = oldurl.replace("https://energyplus.net", "https://www.energyplus.net")
    if not _weatherFileURL.endswith('.zip'): return oldurl
    
    oldurl = oldurl \
        .replace("http://apps1.eere.energy.gov/buildings/energyplus/weatherdata", \
        "https://www.energyplus.net/weather-download")
    linkdata = oldurl.split("/")
    # update region name
    linkdata[4] = ("_").join(linkdata[4].split("_")[1:])
    city, state = linkdata[-1].split("_")[:2]
    if oldurl.find("CAN_")==-1 and oldurl.find("USA_")==-1:
        state = ''
        linkdata.insert(5, "")
        
    linkdata[5] = city + "/" + state
    linkdata[-1] = linkdata[-1].replace(".zip","/all")
    
    updatedLink = "/".join(linkdata)
    return updatedLink
    
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



        #Check the inputs to make sure that a valid DOE URL has been connected.
        _weatherFileURL = updateUrl(_weatherFileURL)
            
        if _weatherFileURL and \
            _weatherFileURL.startswith('https://www.energyplus.net/weather-download/') and _weatherFileURL.endswith('all'):
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
        warning = 'You are not connected to the internet and you do not have the weather files already on your computer. You must be connected to the internet to download the files with this component.'
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

def addresses(filename, directory):
    filenamewords = filename.replace(".zip", "")
    epw = filenamewords + '.epw'
    stat = filenamewords + '.stat'
    return epw, stat

def checkIfAlreadyDownloaded(workingDir, url):
    zipFileAddress = workingDir + url.split('/')[-2] + '.zip'
    epw, stat = addresses(zipFileAddress, workingDir)
    if os.path.isfile(epw) == True and os.path.isfile(stat) == True:
        return True, epw, stat
    else:
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
    epwFile, statFile = addresses(zipFileAddress, workingDir)
else: pass