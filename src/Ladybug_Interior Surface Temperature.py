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
Use this component to calculate a steady state interior surface temperature from given conditions and surface U-Values.
-
Provided by Ladybug 0.0.63
    
    Args:
        _outTemp: The outdoor air temperature in degrees Celcius.
        _inTemp: The indoor air temperature in degrees Celcius.
        _uValue: The U-Value of the surface dividing the interior and exterior in SI (W/Km2).
        intEmiss_: A number between 0 and 1 that represents the interior emissivity of the surface dividing the interior and exterior.  The default is set to 0.9 for a non-metallic surface.
        srfOrient_: A number between 180 (downwards) and -180 (upwards) that represents the angle in degrees of the direction of heat flow.  This is related to the orientation of the surface dividing the interior and exterior. This input can also be the normal vector of a surface that is facing the correct direction of heat flow.  The default is set to 0 degrees for a verically-oriented surface (horizontal heat flow).
    Returns:
        filmCoeff: The interior film coefficient as calculated by the interior emissivity, surface orientation and Chapter 26, Table 10 of AHSHRAE Fundemantals.
        inSrfTemp: The steady state interior surface temperature in degrees Celcius.
"""

ghenv.Component.Name = "Ladybug_Interior Surface Temperature"
ghenv.Component.NickName = 'intSrfTemp'
ghenv.Component.Message = 'VER 0.0.63\nAUG_12_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Rhino as rc
import math

def main(outTemp, inTemp, uValue, srfOrient = None, emissivity = 0.9):
    if emissivity == None:
        emissivity = 0.9
    
    if srfOrient == None:
        dimHeatFlow = 0.5
    else:
        try:
            heatFlowDirect = rc.Geometry.Vector3d(srfOrient)
            #Turn the heat flow direction into a dimensionless value for a linear interoplation.
            dimHeatFlow = 1 - (math.degrees(rc.Geometry.Vector3d.VectorAngle(heatFlowDirect, rc.Geometry.Vector3d.ZAxis))/180)
        except:
            dimHeatFlow = 1 - (srfOrient/180)
    
    #Compute a film coefficient from the emissivity, heat flow direction, and a paramterization of AHSHRAE fundemantals.
    heatFlowFactor = (-12.443 * (math.pow(dimHeatFlow,3))) + (24.28 * (math.pow(dimHeatFlow,2))) - (16.898 * dimHeatFlow) + 8.1275
    filmCoeff = (heatFlowFactor * dimHeatFlow) + (5.81176 * emissivity) + 0.9629
    
    intTemp = (uValue * abs(inTemp - outTemp))/filmCoeff
    
    return intTemp, filmCoeff



if _outTemp and _inTemp and _uValue:
    inSrfTemp, filmCoeff = main(_outTemp, _inTemp, _uValue, srfOrient_, intEmiss_)