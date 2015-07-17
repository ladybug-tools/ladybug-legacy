#Color Gradient Library
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2015, Chris Mackey <Chris@MackeyArchitecture.com>
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
Provided by Ladybug 0.0.60
    
    Args:
        _gradIndex: An index refering to one of the following possible gradients:
            0 - Orignal Ladybug
            1 - Nuanced Ladybug
            2 - Multi-colored Ladybug
            3 - View Analysis 1
            4 - View Analysis 2 (Red,Green,Blue)
            5 - Sunlight Hours 1
            6 - Sunlight Hours 2
            7 - Thermal Comfort Percentage
            8 - Thermal Comfort Colors 1
            9 - Thermal Comfort Colors 1 (UTCI)
            10 - Hot Hours 1
            11 - Cold Hours 1
            12 - Thermal Comfort Colors 2
            13 - Thermal Comfort Colors 2 (UTCI)
            14 - Hot Hours 2
            15 - Cold Hours 2
            16 - Black to White
            17 - CFD Colors 1
            18 - CFD Colors 2
    Returns:
        customColors: A series of colors to be plugged into the "Ladybug_Legend Parameters" component.
"""

ghenv.Component.Name = "Ladybug_Gradient Library"
ghenv.Component.NickName = 'GradientLibrary'
ghenv.Component.Message = 'VER 0.0.60\nJUL_16_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc

def main(gradIndex):
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
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

if _gradIndex >=0 and _gradIndex <=18:
    result = main(_gradIndex)
    if result != -1: customColors = result