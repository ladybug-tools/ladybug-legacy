# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component copies Ladybug components to a new folder
-
Provided by Ladybug 0.0.52
    
    Args:
        _destinationDirectory: A local folder that you want to export Ladybug to.
        _export: Set Boolean to True to export Ladybug to destination folder
    Returns:
        readMe!: ...
"""

ghenv.Component.Name = "Ladybug_Export Ladybug"
ghenv.Component.NickName = 'exportLadybug'
ghenv.Component.Message = 'VER 0.0.52\nNOV_01_2013'

from clr import AddReference
AddReference ('Grasshopper')
import Grasshopper.Kernel as gh
import os
import shutil

def makeDir(path):
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
            return True
        except:
            return False
    else:
        return True

def main(destinationDirectory):
    
    if not destinationDirectory or not makeDir(destinationDirectory):
        warning = 'Destination directory address is not a valid address!'
        print warning
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    sourceDirectory = 'c:/Users/' + os.getenv("USERNAME") + '/AppData/Roaming/Grasshopper/UserObjects'
    srcFiles = os.listdir(sourceDirectory)
    count = 0
    for srcFileName in srcFiles:
        # check for ladybug userObjects
        if srcFileName.StartsWith('Ladybug') or srcFileName.StartsWith('Honeybee'):
            srcFullPath = os.path.join(sourceDirectory, srcFileName)
            dstFullPath = os.path.join(destinationDirectory, srcFileName) 
            shutil.copy2(srcFullPath, dstFullPath)
        count += 1
    print `count+ 1` + ' files are copied to destination folder...'
    

if _export:
    main(_destinationDirectory)