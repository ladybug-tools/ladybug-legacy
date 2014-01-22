# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component [removes | updates] Ladybug components from [grasshopper | a source folder]
-
Provided by Ladybug 0.0.53
    
    Args:
        _sourceDirectory: A local folder that you have the newer version of Ladybug
        _update: Set update to True to update the Ladybug from the source folder
        removeOldVer_: Set removeOldVer to true to remover the currently installed Ladybug
    Returns:
        readMe!: ...
"""

ghenv.Component.Name = "Ladybug_Update Ladybug"
ghenv.Component.NickName = 'updateLadybug'
ghenv.Component.Message = 'VER 0.0.53\nJan_22_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | Developers"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

from clr import AddReference
AddReference ('Grasshopper')
import Grasshopper.Kernel as gh
import os
import shutil

def main(sourceDirectory, update, removeOldVer):
    
    destinationDirectory = 'c:/Users/' + os.getenv("USERNAME") + '/AppData/Roaming/Grasshopper/UserObjects'
    
    if removeOldVer:
        print 'Removing the old version...'
        dstFiles = os.listdir(destinationDirectory)
        for dstFileName in dstFiles:
            # check for ladybug userObjects and delete the files
            if dstFileName.StartsWith('Ladybug') or dstFileName.StartsWith('Honeybee'):
                dstFullPath = os.path.join(destinationDirectory, dstFileName)
                os.remove(dstFullPath)
                
    # copy files from source to destination
    if update:
        if not sourceDirectory or not os.path.exists(sourceDirectory):
            warning = 'source directory address is not a valid address!'
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        print 'Updating...'
        srcFiles = os.listdir(sourceDirectory)
        for srcFileName in srcFiles:
            # check for ladybug userObjects
            if srcFileName.StartsWith('Ladybug') or srcFileName.StartsWith('Honeybee'):
                srcFullPath = os.path.join(sourceDirectory, srcFileName)
                dstFullPath = os.path.join(destinationDirectory, srcFileName) 
                
                # check if a newer version is not aleady exist
                if not os.path.isfile(dstFullPath): shutil.copy2(srcFullPath, dstFullPath)
                # or is older than the new file
                elif os.stat(srcFullPath).st_mtime - os.stat(dstFullPath).st_mtime > 1: shutil.copy2(srcFullPath, dstFullPath)
        return 1
if _update or removeOldVer_:
    up = main(_sourceDirectory, _update, removeOldVer_)
    if up == 1: print 'Done!'
else:
    print "At the minimum one of the components are missing!"