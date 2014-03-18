# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component [removes | updates] Ladybug components from [grasshopper | a source folder]
-
Provided by Ladybug 0.0.56
    
    Args:
        sourceDirectory_: Optional address to a folder that contains Ladybug updated userObjects. If None the component will download the latest version from GitHUB.
        _updateThisFile: Set to True if you want the Ladybug components in this file be updated from the source directory
        _updateAllUObjects: Set to True to sync all the Ladybug and Honeybee userObjects
    Returns:
        readMe!: ...
"""

ghenv.Component.Name = "Ladybug_Update Ladybug"
ghenv.Component.NickName = 'updateLadybug'
ghenv.Component.Message = 'VER 0.0.56\nMAR_17_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | Developers"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Grasshopper.Kernel as gh
import os
import shutil
import zipfile
import time
import urllib


def downloadSourceAndUnzip(lb_preparation):
    """
    Download the source code from github and unzip it in temp folder
    """
    url = "https://github.com/mostaphaRoudsari/ladybug/archive/master.zip"
    targetDirectory = os.path.join(sc.sticky["Ladybug_DefaultFolder"], "ladybugSrc")
    

    
    # download the zip file
    print "Downloading the source code..."
    zipFile = os.path.join(targetDirectory, os.path.basename(url))
    
    # if the source file is just downloded then just use the available file
    if os.path.isfile(zipFile) and time.time() - os.stat(zipFile).st_mtime < 1000: download = False
    else:
        download = True
        try:
            lb_preparation.nukedir(targetDirectory, True)
        except:
            pass
    
    # create the target directory
    if not os.path.isdir(targetDirectory): os.mkdir(targetDirectory)

    if download:
        webFile = urllib.urlopen(url)
        localFile = open(zipFile, 'wb')
        localFile.write(webFile.read())
        webFile.close()
        localFile.close()
        if not os.path.isfile(zipFile):
            print "Download failed! Try to download and unzip the file manually form:\n" + url
            return
    
    #unzip the file
    with zipfile.ZipFile(zipFile) as zf:
        for f in zf.namelist():
            if f.endswith('/'):
                try: os.makedirs(f)
                except: pass
            else:
                zf.extract(f, targetDirectory)
    
    userObjectsFolder = os.path.join(targetDirectory, r"ladybug-master\userObjects")
    
    return userObjectsFolder

def getAllTheComponents(onlyGHPython = True):
    components = []
    
    document = ghenv.Component.OnPingDocument()
    
    for component in document.Objects:
        if onlyGHPython and type(component)!= type(ghenv.Component):
            pass
        else:
            components.append(component)
    
    return components

def updateTheComponent(component, newUOFolder, lb_preparation):
    
    def isNewerVersion(currentUO, component):
        """
        check if the component has a newer version than the current userObjects
        """
        # get the code insider the userObject
        ghComponent = currentUO.InstantiateObject()
        
        # version of the connected component
        if component.Message == None:
            return True, ghComponent.Code
        if len(component.Message.split("\n"))<2:
            return True, ghComponent.Code
        
        ghVersion, ghDate = component.Message.split("\n")
        ghCompVersion = map(int, ghVersion.split("VER ")[1].split("."))
        month, day, ghYear  = ghDate.split("_")
        # print version, date
        month = lb_preparation.monthList.index(month.upper()) + 1
        ghCompDate = int(lb_preparation.getJD(month, day))
        
        # this is not the best way but works for now!
        # should be a better way to compute the component and get the message
        componentCode = ghComponent.Code.split("\n")
        UODate = ghCompDate - 1
        # version of the file
        for lineCount, line in enumerate(componentCode):
            if lineCount > 200: break
            if line.strip().startswith("ghenv.Component.Message"):
                #print line
                # print line.split("=")[1].strip().split("\n")
                version, date = line.split("=")[1].strip().split("\\n")
                
                # in case the file doesn't have an standard Ladybug message let it be updated
                try:
                    UOVersion = map(int, version.split("VER ")[1].split("."))
                except Exception, e:
                    return True, ghComponent.Code
                month, day, UOYear  = date.split("_")
                month = lb_preparation.monthList.index(month.upper()) + 1
                UODate = int(lb_preparation.getJD(month, day))
                break
        
        # check if the version of the code is newer
        if int(ghYear.strip()) < int(UOYear[:-1].strip()):
                return True, ghComponent.Code
        elif ghCompDate < UODate:
            return True, ghComponent.Code
        elif ghCompDate == UODate:
            for ghVer, UOVer in zip(UOVersion, UOVersion):
                if ghVer > UOVer: return False, " "
            return True, ghComponent.Code
        else:
            return False, " "
    
    # check if the userObject is already existed in the folder
    try:
        filePath = os.path.join(newUOFolder, component.Name + ".ghuser")
        newUO = gh.GH_UserObject(filePath)
    except:
        # there is no newer userobject with the same name so just return
        return
    
    # if is newer remove
    isNewer, newCode = isNewerVersion(newUO, component)
    # replace the code inside the component with userObject code
    if isNewer:
        component.Code = newCode
        component.ExpireSolution(True)
    

def main(sourceDirectory, updateThisFile, updateAllUObjects):
    if not sc.sticky.has_key('ladybug_release'): return "you need to let Ladybug fly first!", False
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    if sourceDirectory == None:
        userObjectsFolder = downloadSourceAndUnzip(lb_preparation)
        if userObjectsFolder==None: return "Download failed! Read component output for more information!", False
    else:
        userObjectsFolder = sourceDirectory
    
    destinationDirectory = 'c:/Users/' + os.getenv("USERNAME") + '/AppData/Roaming/Grasshopper/UserObjects'
    
    if updateThisFile:
        # find all the userObjects
        ghComps = getAllTheComponents()
        
        # for each of them check and see if there is a userObject with the same name is available
        for ghComp in ghComps:
            if ghComp.Name != "Ladybug_Update Ladybug":
                updateTheComponent(ghComp, userObjectsFolder, lb_preparation)
        
        return "Done!", True
        
    # copy files from source to destination
    if updateAllUObjects:
        if not userObjectsFolder  or not os.path.exists(userObjectsFolder ):
            warning = 'source directory address is not a valid address!'
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        print 'Updating...'
        srcFiles = os.listdir(userObjectsFolder )
        for srcFileName in srcFiles:
            # check for ladybug userObjects
            if srcFileName.StartsWith('Ladybug') or srcFileName.StartsWith('Honeybee'):
                srcFullPath = os.path.join(userObjectsFolder, srcFileName)
                dstFullPath = os.path.join(destinationDirectory, srcFileName) 
                
                # check if a newer version is not aleady exist
                if not os.path.isfile(dstFullPath): shutil.copy2(srcFullPath, dstFullPath)
                # or is older than the new file
                elif os.stat(srcFullPath).st_mtime - os.stat(dstFullPath).st_mtime > 1: shutil.copy2(srcFullPath, dstFullPath)
        return "Done!" , True

if _updateThisFile or _updateAllUObjects:
    msg, success = main(sourceDirectory_, _updateThisFile, _updateAllUObjects)
    if not success:
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    else:
        print msg
else:
    print " "
