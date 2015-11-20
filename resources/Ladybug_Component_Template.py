# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
#
# This file is part of Ladybug.
#
# Copyright (c) 2013-2015, ....(YOUR NAME).... <....(YOUR EMAIL)....>
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
Use this component to ....(COMPONENT DESCRIPTION)....
_
....(REFERENCES + PAPERS)....
-
Provided by Ladybug 0.0.61

    Args:
        _input1: A ....(DATE TYPE).... that represents ....(INPUT DESCRIPTION).... .
        _input2_: A ....(DATE TYPE).... that represents ....(INPUT DESCRIPTION).... .  If nothing is connected here, a default of ....(DEFAULT VALUE).... will be used.
        input3_: The output from the ....(OTHER LB COMPONENT).... component.  Use this to ....(INPUT DESCRIPTION).... .
    Returns:
        readMe!: ...
        output1: A ....(DATE TYPE).... that represents ....(OUTPUT DESCRIPTION).... .
		output2: A ....(DATE TYPE).... that represents ....(OUTPUT DESCRIPTION).... .
		output3: A ....(DATE TYPE).... that represents ....(OUTPUT DESCRIPTION).... .
"""

ghenv.Component.Name = "Ladybug_....(COMPONENT NAME)...."
ghenv.Component.NickName = '....(COMPONENT NICKNAME)....'
ghenv.Component.Message = 'VER 0.0.61\nNOV_05_2015' #Change this date to be that of your commit or pull request.
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | WIP"
#Change the following date to be that of the LB version during your commit or pull request:
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
#Change the following date to be that of the HB version of your commit or pull request (or get rid of the follwoing if your component is a part of Ladybug):
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc

w = gh.GH_RuntimeMessageLevel.Warning




def checkTheInputs():
    #....(INSERT INPUT CHECKING FUNCTIONS HERE)....

    return False


def main():
    #....(INSERT MAIN COMPONENTS FUNCTIONS HERE)....

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
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): pass
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


#Honeybee check.
if not sc.sticky.has_key('honeybee_release') == True:
    initCheck = False
    print "You should first let Honeybee fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")
else:
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): pass
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        "Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


#Check if there are missing required inputs.
missingParams = []
dataConnected = False
for param in ghenv.Component.Params.Input:
    if str(param.VolatileData) != 'empty structure': dataConnected = True
    if param.NickName.startswith("_") and not param.NickName.endswith("_"):
        if str(param.VolatileData) == 'empty structure': missingParams.append(param.NickName)


#If the intital check is good, run the component.
if initCheck and len(missingParams) == 0:
    checkData = checkTheInputs()
    if checkData:
        result = main()
        if result != -1:
            output = result
elif dataConnected == True:
    for param in missingParams:
        warning = 'Input ' + param + ' is required in order to run this component.'
        ghenv.Component.AddRuntimeMessage(w, warning)
