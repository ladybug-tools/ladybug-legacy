# Comfort Parameters
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to set Adaptive comfort parameters for the Adaptive Comfort Calculator or the Adaptive Comfort Chart.  
_
Parameters include the ability to use either US (ASHRAE) or European (EN) standards as well as set the acceptability threshold for the percent of the occupants that are comfortable (which varies for different building types between the two standards).
_
This component also includes the ability to set a custom correlation between outdoor temperature and indoor desired temperature using a 'levelOfConditioning' variable and research that is not an official part of the ASHRAE or EN standards but is endorsed by many of the scientists who helped create these standards.
_
Detailed information on all of these parameters is described in this book:
Fergus Nicol, Michael Humphreys, Susan Roaf. Adaptive Thermal Comfort: Principles and Practice. Routledge, 2012. (https://books.google.com/books?id=vE7FBQAAQBAJ&dq=adaptive+thermal+comfort)
_
Users are also encouraged to use the 'Ladybug_Adaptive Comfort Chart' component or the Center for the Built Environment's (CBE) comfort tool to help visualize the differences between these parameters:
Special thanks goes to the authors of the online CBE Thermal Comfort Tool who first coded the javascript: Hoyt Tyler, Schiavon Stefano, Piccioli Alberto, Moon Dustin, and Steinfeld Kyle. http://cbe.berkeley.edu/comforttool/
-
Provided by Ladybug 0.0.62
    
    Args:
        ASHRAEorEN_: Set to 'True' to have the Adpative components use the US (ASHRAE 55 2013) adaptive standard and set to 'False' to have the Adaptive components use the European (EN-15251) standard.  The default is set to use the US (ASHRAE 55 2013) standard.  Note that changing the standard will also change some of the inputs below.  The ASHRAE standard will use the average monthly temperature by default and the European standard will use a running mean temperature by default.  Also, the European standard uses building classes instead of 80 / 90 percent acceptability.
        eightyOrNinetyComf_: Set to "True" to have the comfort standard be 80 percent of occupants comfortable and set to "False" to have the comfort standard be 90 percent of all occupants comfortable.  The default is set to "False" for 90 percent, which is what most members of the building industry seem to aim for in today's world.  However some projects will occasionally use 80% as this was originally the benchmark that engineers set around the dawn of air conditioning.
        avgMonthOrRunMean_: Set to 'True' to have the Adpative components compute the prevailing outdoor temperature from the average monthly temperature (the official method used by the US's ASHRAE 55 2013) and set to 'False' compute the prevailing outdoor temperature from a weighted running mean of the last week (the official method used by Europe's EN-15251).  The default is set to align with the chosen comfort standard above (either ASHRAE 55 2013 or EN-15251) but this option is included to allow users to explore differences and variations between the two standards.
        levelOfConditioning_: An optional number between 0 and 1 that represents how 'air conditioned' a space is. By default, this value is always set to 0 because both the ASHRAE 55 2013 and EN-15251 standards are strictly meant to be used for buildings without any installed air conditioning whatsoever.
            _
            However, the researchers who developed the original Adaptive models also surveyed many people in conditioned buildings to show that the adaptive model did not contradict the PMV model when it was applied to buildings that resembled the conditioned climate chamber used to validate the PMV model.  From these surveys of fully-conditioned buildings, researchers produced a correlation between prevailing outdoor temperature and desired indoor temperature that had a much shallower slope than that for fully naturally-ventilated buildings.  This input allows you to use this fully conditioned correlation (by setting this input to 1) or create any custom correlation in between these two (arguably representative of mixed-mode or hybrid AC/naturally ventilated buildings).
            _
            The conditioned building correlation used in the Ladybug Adaptive model can be found in the book refenced in the component description and specifically comes from this study:
            CIBSE (2006) Environmental Criteria for Design, Chapter 1: Environmental Design: CIBSE Guide A. London: Chartered Institution of Building Services Engineers.
    Returns:
        comfortPar: Comfort parameters that you can plug into either the "Ladybug_Adaptive Comfort Calculator" or the "Ladybug_Adaptive Comfort Chart."
"""
ghenv.Component.Name = "Ladybug_Adaptive Comfort Parameters"
ghenv.Component.NickName = 'AdaptComfortPar'
ghenv.Component.Message = 'VER 0.0.62\nJAN_23_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.60\nJUL_06_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import Grasshopper.Kernel as gh

inputsDict = {
    
0: ["ASHRAEorEN_", "Set to 'True' to have the Adpative components use the US (ASHRAE 55 2013) adaptive standard and set to 'False' to have the Adaptive components use the European (EN-15251) standard.  The default is set to use the US (ASHRAE 55 2013) standard.  Note that changing the standard will also change some of the inputs below.  The ASHRAE standard will use the average monthly temperature by default and the European standard will use a running mean temperature by default.  Also, the European standard uses building classes instead of 80 / 90 percent acceptability."],
1: ["eightyOrNinetyComf_", "Set to 'True' to have the comfort standard be 80 percent of occupants comfortable and set to 'False' to have the comfort standard be 90 percent of all occupants comfortable.  The default is set to 'False' for 90 percent, which is what most members of the building industry seem to aim for in today's world.  However some projects will occasionally use 80% as this was originally the benchmark that engineers set around the dawn of air conditioning."]
}

comfortPar = []

if ASHRAEorEN_ == False:
    comfortPar.append(False)
    for input in range(2):
        if input == 1:
            ghenv.Component.Params.Input[input].NickName = "comfortClass_"
            ghenv.Component.Params.Input[input].Name = "comfortClass_"
            ghenv.Component.Params.Input[input].Description = "A number between 1 and 3 that represents the comfort class of the building as defined by EN-15251.  A comfort class of 1 denotes the strictest control of indoor temperatures (offsets of +/- 2C from the comfort temperature are accepted) while a class of 3 denotes the loosest control of inddor temperature (offsets of +/- 4C from the comfort temperature are accepted).  The default is set to 2, which roughly corresponds to 90% of occupants comfortable and offsets of +/- 3C from the comfort temperature are accepted."
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
else:
    comfortPar.append(True)
    for input in range(2):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]

try: comfortClass_
except: comfortClass_ = None
try: eightyOrNinetyComf_
except: eightyOrNinetyComf_ = None

officalStandard = True
allOk = True

if ASHRAEorEN_ == False:
    if comfortClass_ != None:
        if comfortClass_ <= 3 and comfortClass_ >= 1:
            comfortPar.append(comfortClass_)
        else:
            allOk = False
            comfortPar.append(2)
            warning = 'The comfortClass_ must be a number between 1 and 3.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        comfortPar.append(2)
else:
    if eightyOrNinetyComf_ != None:
        if eightyOrNinetyComf_ <= 1 and eightyOrNinetyComf_ >= 0:
            comfortPar.append(bool(eightyOrNinetyComf_))
        else:
            allOk = False
            comfortPar.append(False)
            warning = 'The eightyOrNinetyComf_ must be a True / False value.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        comfortPar.append(False)

if avgMonthOrRunMean_ != None:
    comfortPar.append(avgMonthOrRunMean_)
    if ASHRAEorEN_ == False and avgMonthOrRunMean_ == True: officalStandard = False
    elif ASHRAEorEN_ != False and avgMonthOrRunMean_ == False: officalStandard = False
else:
    if ASHRAEorEN_ == False: comfortPar.append(False)
    else: comfortPar.append(True)

if levelOfConditioning_ != None:
    if levelOfConditioning_ <= 1 and levelOfConditioning_ >= 0:
        comfortPar.append(levelOfConditioning_)
        if levelOfConditioning_ != 0: officalStandard = False
    else:
        allOk = False
        comfortPar.append(0)
        warning = 'The levelOfConditioning_ must be a number between 0 and 1.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
else:
    comfortPar.append(0)


if officalStandard == False and allOk == True:
    remark = 'The input parameters are not officially endorsed by either the ASHRAE 55 or EN-15251 standards. \n However, there is precedent in adaptive comfort research for using these criteria.'
    print remark
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Remark, remark)