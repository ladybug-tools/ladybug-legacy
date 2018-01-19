#Color Gradient Library
#
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
Use this component to access a library of typical gradients useful throughout Ladybug.  The output from this component should be plugged into the customColors_ input of the "Ladybug_Legend Parameters" component.
_
For an image of each of the gardients in the library, check here:
https://github.com/mostaphaRoudsari/ladybug/blob/master/resources/gradients.jpg
-
Provided by Ladybug 0.0.66
    
    Args:
        _gradIndex: An index refering to one of the following possible gradients:
            0 - Orignal Ladybug
            1 - Nuanced Ladybug
            2 - Multi-colored Ladybug
            3 - View Analysis 1
            4 - View Analysis 2 (Red,Green,Blue)
            5 - Sunlight Hours
            6 - Ecotect
            7 - Thermal Comfort Percentage
            8 - Thermal Comfort Colors
            9 - Thermal Comfort Colors (UTCI)
            10 - Hot Hours
            11 - Cold Hours
            12 - Shade Benefit/Harm
            13 - Thermal Comfort Colors v2 (UTCI)
            14 - Shade Harm
            15 - Shade Benefit
            16 - Black to White
            17 - CFD Colors 1
            18 - CFD Colors 2
            19 - Energy Balance
            20 - THERM
            21 - Cloud Cover
            22 - Glare Potential
            23 - Radiation Benefit
    Returns:
        customColors: A series of colors to be plugged into the "Ladybug_Legend Parameters" component.
"""

ghenv.Component.Name = "Ladybug_Gradient Library"
ghenv.Component.NickName = 'GradientLibrary'
ghenv.Component.Message = 'VER 0.0.66\nJAN_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nSEP_21_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(gradIndex):
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        colors = lb_visualization.gradientLibrary[_gradIndex]
        return colors
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1

if _gradIndex >=0 and _gradIndex <=23:
    result = main(_gradIndex)
    if result != -1: customColors = result
elif _gradIndex != None:
    print "_gradIndex must be between 0 and 23."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "_gradIndex must be between 0 ans 22")