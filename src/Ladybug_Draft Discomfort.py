# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to calculate discomfort from cold drafts on the back of the neck (arguably the most sensitive part of the human body to cold drafts).  This model was derived from empircal tests that involved blowing cold air on the back of subjects's necks who were otherwise at thermally neutral conditions by the pmv standard.  
_
This model used to be the standard endorsed by ASHRAE 55 and EN-12521 for all draft cases but has since been replaced with a model that more accurately targets draft discomfort at foot level. The paper in which this model was published can be found here:
_
Fanger, P.O., Melikov, A.K., Hanzawa, H., Ring, J. Air Turbulence and Sensation of Draught. Energy and Buildings 12, no. 1 (1988): 2139.
-
Provided by Ladybug 0.0.64
    
    Args:
        _draftAirTemp: The air temperature of the draft in degrees Celcius.
        _draftAirVeloc: The velocity of the draft in m/s.
     Returns:
        PPD: The Percentage of People Dissatisfied from cold downdraft.
"""

ghenv.Component.Name = "Ladybug_Draft Discomfort"
ghenv.Component.NickName = 'draftComf'
ghenv.Component.Message = 'VER 0.0.64\nFEB_05_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import math

def calcPPD(windSpd, airTemp):
    return 13800*(math.pow((((windSpd*0.8)-0.04)/(airTemp-13.7))+0.0293, 2) - 0.000857)

if _draftAirTemp and _draftAirVeloc:
    PPD = calcPPD(_draftAirVeloc, _draftAirTemp)

