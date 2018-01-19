# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to calculate discomfort from cold drafts at ankle-level.  The original tests used to create the model involved blowing cold air on subject's ankles at a height of 10 cm off of the ground.
_
The formula has been submitted to be incorporated in the ASHRAE 55 standard with a recommendation that PPD from ankle draft not exceed 20%.  The papers in which this model is published can be found here:
_
Schiavon, S., D. Rim, W. Pasut, W. Nazaroff. 2016. Sensation of draft at uncovered ankles for women exposed to displacement ventilation and underfloor air distribution systems. Building and Environment, 96, 228236.
_
Liu, S., S. Schiavon, A. Kabanshi, W. Nazaroff. 2016. Predicted percentage of dissatisfied with ankle draft. Accepted Author Manuscript. Indoor Environmental Quality. http://escholarship.org/uc/item/9076254n
-
Provided by Ladybug 0.0.66
    
    Args:
        _fullBodyPMV: The predicted mean vote (PMV) of the subject.  This can be calculated using the "Ladybug_PMV Comfort Calculator" component.  The reason for why PMV is incorporated into this draft discomfort model is that people are likely to feel more uncomfortable from downdraft when their whole body is already feeling cold.
        _draftAirVeloc: The velocity of the draft in m/s.
     Returns:
        PPD: The Percentage of People Dissatisfied from cold downdraft at ankle-level.
"""

ghenv.Component.Name = "Ladybug_Ankle Draft Discomfort"
ghenv.Component.NickName = 'ankleDraftComf'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import math

def calcPPD(airSpd, pmv):
    return 100 * ((math.exp(-2.58 + (3.05*airSpd) - (1.06*pmv)))/(1 + (math.exp(-2.58 + (3.05*airSpd) - (1.06*pmv)))))

if _fullBodyPMV and _draftAirVeloc:
    PPD = calcPPD(_draftAirVeloc, _fullBodyPMV)

