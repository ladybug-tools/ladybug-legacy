# ENVI-Met Find Output Folder
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
This component let you select output folders from Workspace folder.
-
Provided by Ladybug 0.0.65
    
    Args:
        _folder: Workspace folder where there are output folders.
        _runIt: Set to "True" to run the component.
    Returns:
        outputFolder: ENVI-Met output folder path.
"""

ghenv.Component.Name = "Ladybug_ENVI-Met Find Output Folder"
ghenv.Component.NickName = 'ENVI-MetFindOutputFolder'
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import os


def findOutputFolder():
    # only output folders
    subFolderList = [subFolder[0] for subFolder in os.walk(_folder)]
    outputFolderList = [folder for folder in subFolderList if folder[-7:] == '_output']
    
    return outputFolderList

if _runIt:
    if _folder:
        outputFolder = findOutputFolder()