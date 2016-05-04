#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to make daily schedules for "Honeybee_AnnualSchedule". This component changes some parameters of Galapagos Gene Pool automatically.
-
Provided by Honeybee 0.0.59
    
    Args:
        _genePool: Input Galapagos Gene Pool
        _button: Connect a button (Params/Input)
        template_: Choose one of the templates:
                   -
                   0 - minimum values from 1:00 to 6:00 and from 23:00 to 24:00
                       maximum values from 7:00 to 22:00
                   -
                   1 - minimum values from 7:00 to 22:00
                       maximum values from 1:00 to 6:00 and from 23:00 to 24:00
                   -
                   2 - minimum values from 1:00 to 24:00
                   -
                   3 - maximum values from 1:00 to 24:00
        numberOfDecimals_: Set the number of decimals. Rember that Energy Plus accept 1 decimal. The default is set to 1.
        overwriteValues_: Change the maximum and minimum values of the template without modifying the schedule range.
                          -
                          Connect a list of two numbers.
        lowBound_: A number representing the lower boundary of the schedule range.  The default is set to 0.
        highBound_: A number representing the higher boundary of the schedule range. The default is set to 1.
    Returns:
        readMe!: ...
"""

ghenv.Component.Name = "Honeybee_Daily Schedule"
ghenv.Component.NickName = 'DailySchedule'
ghenv.Component.Message = 'VER 0.0.59\nFEB_08_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "6 | WIP"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

from System import Decimal
import scriptcontext as sc
import Grasshopper.Kernel as gh

def checkTheData(genePool, button):
    if genePool == None \
    and button == None:
        checkData = False
    
    elif genePool and button !=None:
        checkData = False
    else:
        checkData = True
        print "Please provide all inputs."
    return checkData

def main():
    
    #2 values
    if overwriteValues_:
        if len(overwriteValues_) != 2:
            warning = "overwriteValues_ accepts only two numbers"
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        
    if _button:
        try:
            gp = ghenv.Component.Params.Input[0].Sources[0]
            
            #tamplates
            template0 = [gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,\
            gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,\
            gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Minimum,gp.Minimum]
            template1 = [gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,\
            gp.Maximum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum\
            ,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum]
            template2 = [gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,\
            gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,\
            gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,\
            gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum,gp.Minimum]
            template3 = [gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,\
            gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,\
            gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum\
            ,gp.Maximum,gp.Maximum,gp.Maximum,gp.Maximum]
            
            if template_ == None:
                template = template2
            if template_ == 0:
                template = template0
            elif template_ == 1:
                template = template1
            elif template_ == 2:
                template = template2
            elif template_ == 3:
                template = template3
            
            #find multiple index
            indicesMin0 = [i for i, x in enumerate(template0) if x == gp.Minimum]
            indicesMax0 = [i for i, x in enumerate(template0) if x == gp.Maximum]
            
            indicesMin1 = [i for i, x in enumerate(template1) if x == gp.Minimum]
            indicesMax1 = [i for i, x in enumerate(template1) if x == gp.Maximum]
            
            indicesMin2 = [i for i, x in enumerate(template2) if x == gp.Minimum]
            indicesMax2 = [i for i, x in enumerate(template2) if x == gp.Maximum]
            
            indicesMin3 = [i for i, x in enumerate(template3) if x == gp.Minimum]
            indicesMax3 = [i for i, x in enumerate(template3) if x == gp.Maximum]
            print indicesMax3
            
            #overwrite values
            if overwriteValues_ and template_ == 0:
                for index in sorted(indicesMin0, reverse=True):
                    template[index] = overwriteValues_[0]
                for index in sorted(indicesMax0, reverse=True):
                    template[index] = overwriteValues_[1]
            elif overwriteValues_ and template_ == 1:
                for index in sorted(indicesMin1, reverse=True):
                    template[index] = overwriteValues_[0]
                for index in sorted(indicesMax1, reverse=True):
                    template[index] = overwriteValues_[1]
            elif overwriteValues_ and template_ == 2:
                for index in sorted(indicesMin2, reverse=True):
                    template[index] = overwriteValues_[0]
                for index in sorted(indicesMax2, reverse=True):
                    template[index] = overwriteValues_[1]
            elif overwriteValues_ and template_ == 3:
                for index in sorted(indicesMin3, reverse=True):
                    template[index] = overwriteValues_[0]
                for index in sorted(indicesMax3, reverse=True):
                    template[index] = overwriteValues_[1]
            elif overwriteValues_ and template_ == None:
                for index in sorted(indicesMin2, reverse=True):
                    template[index] = overwriteValues_[0]
                for index in sorted(indicesMax2, reverse=True):
                    template[index] = overwriteValues_[1]
                    
            #mod Gene Pool
            gp.Count = 24.0
            gp.Decimals = 1
            gp.NickName = "LB_schedule"
            if highBound_ == None:
                gp.Maximum = 1.0
            else:
                gp.Maximum = highBound_
            if lowBound_ == None:
                gp.Minimum = 0.0
            else:
                gp.Minimum = lowBound_
            
            # Set gene pool count and values
            gp.Count = 24
            for i in range(gp.Count):
                gp[i] = Decimal(template[i])
        except:
            pass
    return

# import the classes
w = gh.GH_RuntimeMessageLevel.Warning
initCheck = False
if sc.sticky.has_key('honeybee_release'):
    initCheck = True
    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): initCheck = True
    except:
        initCheck = False
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)
else:
    initCheck = False
    print "You should first let Honeybee to fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee to fly...")

checkData = False
if initCheck == True:
    checkData = checkTheData(_genePool,  _button)
    
    if checkData == False :
        result = main()
        if result != -1:
            print 'Push the button to run! Push again to go back to original schedule. \nYou can also randomize lists by right-clicking on "Gene PoolLB_schedule"/ Randomize 1%...'