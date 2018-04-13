# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
#
# This file is part of Ladybug.
#
# Copyright (c) 2013-2018, Devang Chauhan <devang@outlook.in>
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
Use this to look for the components in the Ladybug suite of tools that are most relevant to your query.
-
Provided by Ladybug 0.0.66

    Args:
        _keyword: A word. This only accepts text inputs. Example is ("drybulb Temperature" or "tunnel") without quotation marks.
        _occurrences_: An integer. This number determines the search resolution. The default value is set to 3. 
            Meaning, all the components in which the keyword appears at least 3 times, will be served as results.
            You may raise or reduce this number as per your convenience. This number can not be less than 1.
        open_: A boolean. If boolean of True value is provided, primer pages for the components that appear in the result
            will be opened in your browser. PLEASE BE MINDFUL of the number of components in the result. If the list of components
            in the result is long, opening up the primer pages for all of them at once may free your browser. If the number of
            components in result is large, you are advised to raise the number to _occurrences_ input before connecting 
            a boolean value of True to this input.
    Returns:
        out: Run time messages
        result: The list of components across all Lasybug Tools plugins in which the keyword appears at least the number of times set in
            _occurrences_ input.
"""

ghenv.Component.Name = "Ladybug_Search"
ghenv.Component.NickName = 'Search'
ghenv.Component.Message = 'VER 0.0.66\nAPR_13_2018'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#Change the following date to be that of the LB version during your commit or pull request:
#compatibleLBVersion = VER 0.0.66\nMAR_04_2018
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc
import os
import scriptcontext as sc
import System
import zipfile
import time
import webbrowser as wb
from itertools import izip
System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12
w = gh.GH_RuntimeMessageLevel.Warning


def downloadSourceAndUnzip(directory, url, markdown):
    """
    Download the source code from github and unzip it in the markdown folder
    Args:
        directory: A string. This will be used to give the name of the directory
            where the markdown files from the particular primer will be hosted.
        url: A string. Web address of the primer page.
        markdown: A folder path as a string. The path for markdown folder inside which
            other subfolder will be created to host the markdown files.
    Returns:
        userObjectsFolder: A folder inside the markdown folder where markdown files
            from a particular primer are either successfully downloaded or are already there.
    Crdits: This is a slightly modified version of the original function of the same name 
        written by Mostapha Sadeghipour Roudsari.
    """
    targetDirectory = os.path.join(markdown, directory)
    
    # download the zip file
    zipFile = os.path.join(targetDirectory, os.path.basename(url))
    
    # if the source file is just downloded then just use the available file
    if os.path.isfile(zipFile) and time.time() - os.stat(zipFile).st_mtime < 1000:
        print "Primer for {} is already found. Hence, not downloaded.".format(directory)
        download = False
    else:
        download = True
        print "Downloading primer for {}".format(directory)
        try:
            lb_preparation.nukedir(targetDirectory, True)
        except:
            pass
    
    # create the target directory
    if not os.path.isdir(targetDirectory):
        os.mkdir(targetDirectory)

    if download:
        try:
            client = System.Net.WebClient()
            client.DownloadFile(url, zipFile)
            if not os.path.isfile(zipFile):
                print "Download failed! Try to download and unzip the file manually form:\n" + url
                return
        except Exception, e:
            print `e` + "\nDownload failed! Try to download and unzip the file manually form:\n" + url
            return
    
    #unzip the file
    with zipfile.ZipFile(zipFile) as zf:
        for f in zf.namelist():
            if f.endswith('/'):
                try: os.makedirs(f)
                except: pass
            else:
                zf.extract(f, targetDirectory)
    
    userObjectsFolder = os.path.join(targetDirectory)
    return userObjectsFolder
    
    
def getFolderSize(path):
    """This function calculates the size of a folder.
    Args:
        path: A valid path of the folder for which size is to be calculated
    Returns:
        totalSize: The size of the folder in mb.
    """
    totalSize = 0
    for item in os.walk(path):
        for file in item[2]:
            try:
                totalSize = totalSize + os.path.getsize(os.path.join(item[0], file))
            except Exception:
                print("error with file:  " + os.path.join(item[0], file))
    return totalSize
    
    
def countOccurrences(filePath, keyword):
    """This function returns the number of times the keyWord
    appears in the file."""
    count = 0
    with open(filePath) as f:
        lines = f.readlines()
        for line in lines:
            if keyword.lower() in line.lower():
                count += 1
            else:
                pass
    return count


def main():
    
    keyword = _keyword
    level = _occurrences_
    if _occurrences_ == None:
        level = 3
        print "The value of occurrences cannot be None. Default value 3 is applied."
        print "-"*50
    elif _occurrences_ < 1:
        level = 3
        print "The value of occurrences cannot be less than 1. Default value 3 is applied."
        print "-"*50
    else:
        level = _occurrences_
        print "The value of occurrences is set to {}.".format(level)
        print "-"*50 
    
    open = open_
    
    # Links to primers
    urls = {
    "Ladybug": "https://github.com/mostaphaRoudsari/ladybug-primer/archive/master.zip",
    "Honeybee": "https://github.com/mostaphaRoudsari/honeybee-primer/archive/master.zip", 
    "Butterfly" :"https://github.com/ladybug-tools/butterfly-primer/archive/master.zip",
    "LadybugPlus": "https://github.com/ladybug-tools/ladybug-primer/archive/master.zip",
    "HoneybeePlus": "https://github.com/ladybug-tools/honeybee-primer/archive/master.zip"
    }
    
    # Default ladybug folder path
    lb_preparation = sc.sticky["ladybug_Preparation"]()

    # Create a folder in ladybug folder to catch all the markdown files that will be downloaded
    primers = os.path.join(sc.sticky["Ladybug_DefaultFolder"], "Primers")
    try:
        if not os.path.isdir(primers):
            os.mkdir(primers)
            print "Primers folder created inside the default ladybug folder on your system."
            print "-"*50
        else:
            print "Primers folder already exists inside the default ladybug folder on your system. Hence, not created."
            print "-"*50
    except Exception as e:
        print e
    
    # Try to download markdown files for all the primers, if they're not already downloaded.
    for key, value  in urls.iteritems():
        downloadSourceAndUnzip(key, value, primers)
    
    # Checking if markdowns from all the primers are found
    if len(urls.keys()) == len(os.listdir(primers)):
        print "-"*50
        print "Primers for all five plugins are found on your system."
        # Absolute paths to all the primer folders
        primerFolders = [os.path.join(primers, key) for key in urls.keys()]
        
        # All the absolute paths to the folders to look into
        foldersToSearchIn = []
        for path in primerFolders:
            subFolders = os.listdir(path)
            for folderName in subFolders:
                tempPath = os.path.join(path, folderName)
                if folderName == "master.zip" or getFolderSize(tempPath) == 0:
                    pass
                else:
                    foldersToSearchIn.append(tempPath)
        
        # List of paths to all the markdown files in which the keyword is found more than once
        mdPath = []
        # The number of times the keyword appears
        hitCount = []
        
        # Getting the last folders in which markdown files live
        for searchPath in foldersToSearchIn:
            extension = "text\components"
            searchFolderPath = os.path.join(searchPath, extension)
            markDownList = os.listdir(searchFolderPath)
            for item in markDownList:
                filePath = os.path.join(searchFolderPath, item)
                if countOccurrences(filePath, keyword) >= level:
                    mdPath.append(filePath)
                    hitCount.append(countOccurrences(filePath, keyword))
                else:
                    pass
                    
        # This dictionary has all absolute paths to all the files in which
        # the keyword appears at least once
        # the structure of the dictoonary is path : count
        matchDict = dict(izip(mdPath, hitCount))
        
        # Sorting the results for plugins
        Ladybug, Honeybee, Butterfly, LadybugPlus, HoneybeePlus = ({}, {}, {}, {}, {})
        for key in matchDict.keys():
            check = key.split("\\")[-5]
            if check == "Ladybug":
                Ladybug[os.path.splitext(os.path.basename(key))[0]] = matchDict[key]
            elif check == "Honeybee":
                Honeybee[os.path.splitext(os.path.basename(key))[0]] = matchDict[key]
            elif check == "Butterfly":
                Butterfly[os.path.splitext(os.path.basename(key))[0]] = matchDict[key]
            elif check == "LadybugPlus":
                LadybugPlus[os.path.splitext(os.path.basename(key))[0]] = matchDict[key]
            elif check == "HoneybeePlus":
                HoneybeePlus[os.path.splitext(os.path.basename(key))[0]] = matchDict[key]
        
        # Dictionary structure: component name : count of keyword occurence
        listOfDicts = [Ladybug, Honeybee, Butterfly, LadybugPlus, HoneybeePlus]
        listOfSortedDicts = []
        for item in listOfDicts:
            if len(item.keys()) > 0:
                item = sorted(item.items(), key=lambda x: x[1], reverse = True)
                listOfSortedDicts.append(item)
            else:
                listOfSortedDicts.append([])
        
        nameOfPlugins = {0:"Ladybug", 1:"Honeybee", 2:"Butterfly", 3:"LadybugPlus", 4:"HoneybeePlus"}
        
        # Creating URLs to open webpages. These are not complete
        urlsToBeExtended = {
        "Ladybug": "https://mostapharoudsari.gitbooks.io/ladybug-primer/content/text/components/",
        "Honeybee": "https://mostapharoudsari.gitbooks.io/honeybee-primer/content/text/components/", 
        "Butterfly" :"https://ladybug-tools.gitbooks.io/butterfly-primer/content/text/components/",
        "LadybugPlus": "https://ladybug-tools.gitbooks.io/ladybug-primer/content/text/components/",
        "HoneybeePlus": "https://ladybug-tools.gitbooks.io/honeybee-primer/content/text/components/"
        }
        
        # Catching complete URLs for opening in browser
        urlsToOpen = []
        for i in range(len(listOfSortedDicts)):
            if len(listOfSortedDicts[i]) == 0:
                pass
            else:
                for item in listOfSortedDicts[i]:
                    fileExtension = item[0] + ".html"
                    push = os.path.join(urlsToBeExtended[nameOfPlugins[i]], fileExtension)
                    urlsToOpen.append(push)
  
        # Open primer pages
        if open == True:
            print "-"*50
            print "Primer pages are requested"
            chrome_path="C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            if os.path.isfile(chrome_path) == True:
                wb.register('chrome', None,wb.BackgroundBrowser(chrome_path),1)
                for url in urlsToOpen:
                    wb.get('chrome').open(url,2,True)
            else:
                print "Chrome browser not found on your machine. Therefore, the default browser is used."
                wb.open(url,2,True)
        else:
            pass
                
        result = []
        
        # Producing result output
        for i in range(len(listOfSortedDicts)):
            if len(listOfSortedDicts[i]) == 0:
                pass
            else:
                for item in listOfSortedDicts[i]:
                    delimiter = "_"
                    temp = [nameOfPlugins[i], item[0]]
                    push = delimiter.join(temp)
                    result.append(push)
                separator =  "-"*50   
                result.append(separator)
        
        if result == []:
            print "-"*50
            print "This keyword did not produce result. Please try some other alternative keyword. You can join words or add spaces. Examples are, 'DryBulb', 'DryBulb Temperature', 'DrybulbTemperature'."
        if result != []:
            print "-"*50
            print "Please check the result"
            return result[:-1]
        
    else:
        print "-"*50
        print "Primers for all five plugins are not found on your system. Something went wrong!"
        return -1
    
    return -1


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


#If the intital check is good, run the component.
if initCheck:
    result = main()
    if result != -1:
        output = result
