# schedule Day
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
Use this component to make daily schedules for "Ladybug_AnnualSchedule". This component changes some parameters of Galapagos Gene Pool automatically.
-
Provided by Ladybug 0.0.62
    
    Args:
        _genePool: Input Galapagos Gene Pool
        _template: Connect a number slider (from 0 to 3)
        _button: Connect a button (Params/Input)
    Returns:
        readMe!: ...
"""

ghenv.Component.Name = "Ladybug_Daily Schedule"
ghenv.Component.NickName = 'DailySchedule'
ghenv.Component.Message = 'VER 0.0.62\nFEB_08_2016'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | WIP"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

from System import Decimal
import scriptcontext as sc
import Grasshopper.Kernel as gh

def checkTheData(genePool, template, button):
    if genePool == None \
    and template == None and button == None:
        checkData = False
    
    elif genePool and template != None and button !=None:
        checkData = False
    else:
        checkData = True
        print "Please provide all inputs."
    return checkData

def main():
    if _button:
        try:
            gp = ghenv.Component.Params.Input[0].Sources[0]
            
            
            #choose the template
            template0 = [0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0]
            template1 = [1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1]
            template2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            template3 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
            
            if _template == 0:
                template = template0
            elif _template == 1:
                template = template1
            elif _template == 2:
                template = template2
            elif _template == 3:
                template = template3
                
            #mod Gene Pool
            gp.Count = 24
            gp.NickName = "LB_schedule"
            gp.Maximum = 1.0
            gp.Decimals = 1
            for i in range(gp.Count):
                gp[i] = template[i]
            gp.ExpireSolution(True)
        except:
            pass
    return

# import the classes
initCheck = False
if sc.sticky.has_key('ladybug_release'):
    initCheck = True
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = True
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    lb_preparation = sc.sticky["ladybug_Preparation"]()
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")

checkData = False
if initCheck == True:
    checkData = checkTheData(_genePool, _template, _button)
    
    if checkData == False :
        result = main()
        if result != -1:
            print 'Push the button to run! Push again to go back to original schedule. \nYou can also randomize lists by right-clicking on "Gene PoolLB_schedule"/ Randomize 1%...'