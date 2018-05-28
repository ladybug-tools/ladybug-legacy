# ENVI-Met Manage Workspace
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
Use this component to create a Workspace folder.
-
Connect "folder" output to ENVI-Met Spaces.
-
Provided by Ladybug 0.0.66
    
    Args:
        _workspaceFolder: Main folder where you have to save an Envimet project.
        _projectName: Name of Envimet project folder where you have to save:
        1) EnviMet geometry file (*.INX)
        2) Configuration file (*.SIM)
        ENVImetInstallFolder_: Optional folder path for ENVImet4 installation folder.
    Returns:
        readMe!: ...
        folder: Envimet project folder. Connect it to "_folder" input of ENVI-Met Spaces
"""

ghenv.Component.Name = "Ladybug_ENVI-Met Manage Workspace"
ghenv.Component.NickName = 'ENVI-MetManageWorkspace'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import Grasshopper.Kernel as gh
import datetime
import socket
import os


def checkInputs(workspaceFolder):
    if workspaceFolder == None:
        return False
    elif workspaceFolder:
        return True


def findENVI_MET():
    appdata = os.getenv("APPDATA")
    directory = os.path.join(appdata[:3], "ENVImet4\sys.basedata\\")
    
    if ENVImetInstallFolder_:
        directory = os.path.join(ENVImetInstallFolder_, 'sys.basedata\\')
    
    try:
        if os.listdir(directory):
            print("Good to go!")
            return directory
    except:
        w = gh.GH_RuntimeMessageLevel.Warning
        message = "Envimet Main Folder not found!"
        ghenv.Component.AddRuntimeMessage(w, message)
        return -1


def main():
    
    # default value
    if _projectName_ == None: projectFolderName = 'LBDATA'
    else: projectFolderName = _projectName_
    
    
    # date
    timeTxt = datetime.datetime.now()
    timeTxt = str(timeTxt)[:-7]
    
    
    # file folder
    fullFolder = _workspaceFolder + '\\'+ projectFolderName
    
    if not os.path.exists(fullFolder):
        os.makedirs(fullFolder)
    
    
    # PROJECTS and INI name
    fileNamePrj = socket.gethostname().upper() + '.projects'
    iniFileName = 'envimet.ini'
    worspaceName = 'workspace.infoX'
    projectName = 'project.infoX'
    edbFileName = 'projectdatabase.edb'
    
    
    mainDirectory = findENVI_MET()
    if mainDirectory != -1:
        # PROJECTS
        prjFile = os.path.join(mainDirectory, fileNamePrj)
        
        with open(prjFile, 'w') as f:
            f.write(fullFolder)
        
        
        # INI and workspace file
        iniFile = os.path.join(mainDirectory, iniFileName)
        workspaceXml = os.path.join(mainDirectory, worspaceName)
        projectFileInFolder = os.path.join(fullFolder, projectName)
        edbFileInFolder = os.path.join(fullFolder, edbFileName)
        
        
        with open(iniFile, 'w') as f:
            f.writelines('[projectdir]' + '\n')
            f.writelines('dir' + '=' + _workspaceFolder)
        
        
        with open(workspaceXml, 'w') as f:
            text = ['<ENVI-MET_Datafile>', '<Header>', '<filetype>workspacepointer</filetype>',
                    '<version>6811715</version>', '<revisiondate>{}</revisiondate>'.format(timeTxt),
                    '<remark></remark>', '<encryptionlevel>5150044</encryptionlevel>', '</Header>',
                    '<current_workspace>', r'<absolute_path> {} </absolute_path>'.format(_workspaceFolder),
                    '<last_active> {} </last_active>'.format(projectFolderName), '</current_workspace>', '</ENVI-MET_Datafile>']
            
            f.write('\n'.join(text))
        
        
        with open(projectFileInFolder, 'w') as f:
            text = ['<ENVI-MET_Datafile>', '<Header>', '<filetype>infoX ENVI-met Project Description File</filetype>',
                    '<version>4240697</version>', '<revisiondate>{}</revisiondate>'.format(timeTxt),
                    '<remark></remark>', '<encryptionlevel>5220697</encryptionlevel>', '</Header>',
                    '<project_description>', '<name> {} </name>'.format(projectFolderName),
                    '<description>  </description>', '<useProjectDB> 1 </useProjectDB>', '</project_description>', '</ENVI-MET_Datafile>']
            
            f.write('\n'.join(text))
        
        
        with open(edbFileInFolder, 'w') as f:
            text = ['<ENVI-MET_Datafile>', '<Header>', '<filetype>DATA</filetype>',
                    '<version>1</version>', '<revisiondate>{}</revisiondate>'.format(timeTxt),
                    '<remark>Envi-Data</remark>', '<encryptionlevel>1701377</encryptionlevel>', 
                    '</Header>', '</ENVI-MET_Datafile>']
            
            f.write('\n'.join(text))
        
        
        return fullFolder

# check and run component
if checkInputs(_workspaceFolder):
    result = main()
    if result != -1:
        folder = result
else:
    w = gh.GH_RuntimeMessageLevel.Warning
    message = "Please provide _workspaceFolder input."
    ghenv.Component.AddRuntimeMessage(w, message)