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
Use this component to calculate a steady state interior/exterior surface temperature from given given indoor/outdoor air temperatures and surface U-Values.  Note that this component does not currently account for solar radiation, which can greatly alter surface temperatures in the real world.
_
The formulas used to account for air film resistance in this component come from ASHRAE Fundementals 2013, Chapter 26, Table 10 (26.20).
-
Provided by Ladybug 0.0.64
    
    Args:
        _outTemp: A number (or list of numbers) that represent the outdoor air temperature in degrees Celcius.
        _inTemp: A number (or list of numbers) that represent the indoor air temperature in degrees Celcius.
        _uValue: A number that represents the U-Value of the surface dividing the interior and exterior in SI (W/Km2).
        intEmiss_: A number between 0 and 1 that represents the interior emissivity of the surface dividing the interior and exterior.  The default is set to 0.9 for a non-metallic surface.
        srfOrient_: A number between 180 (downwards) and -180 (upwards) that represents the angle in degrees of the direction of heat flow.  This is related to the orientation of the surface dividing the interior and exterior. This input can also be the normal vector of a surface that is facing the correct direction of heat flow.  The default is set to 0 degrees for a verically-oriented surface (horizontal heat flow).
        outWindSpd_: A number (or list of numbers) that represents the outdoor wind speed in m/s.  This is used to calculate the outdoor film coefficient.  If no value is input here, a default of 6.7 m/s will be assumed (indicating a winter design day).
    Returns:
        inFilmCoeff: The interior film coefficient as calculated by the interior emissivity, surface orientation and Chapter 26, Table 10 of AHSHRAE Fundemantals.
        inSrfTemp: The steady state interior surface temperature in degrees Celcius.
        extSrfTemp: The steady state exterior surface temperature in degrees Celcius.
"""

ghenv.Component.Name = "Ladybug_Steady State Surface Temperature"
ghenv.Component.NickName = 'ssSrfTemp'
ghenv.Component.Message = 'VER 0.0.64\nFEB_05_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Rhino as rc
import math

def dupdata(data, calcLen):
    return [data for i in range(calcLen)]

def checkData(outTemp, inTemp, outWindSpd):
    listLengs = [len(outTemp), len(inTemp), len(outWindSpd)]
    listLengs.sort()
    calcLength = listLengs[-1]
    
    if len(outTemp) != calcLength:
        outTemp = dupdata(outTemp[0], calcLength)
    if len(inTemp) != calcLength:
        inTemp = dupdata(inTemp[0], calcLength)
    if len(outWindSpd) == 0:
        outWindSpd = dupdata(6.7, calcLength)
    elif len(outWindSpd) != calcLength:
        outWindSpd = dupdata(outWindSpd[0], calcLength)
    
    return inTemp, outTemp, outWindSpd

def main(outTemp, inTemp, uValue, windSpd, srfOrient = None, emissivity = 0.9):
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
    
    extFilmCoeff = []
    intTemp = []
    extTemp = []
    for count in range(len(inTemp)):
        intTemp.append(inTemp[count] - (uValue * (inTemp[count] - outTemp[count]))/filmCoeff)
        
        extFilmCo = (-0.1215*windSpd[count]*windSpd[count]) + (4.6513*windSpd[count]) + 8.29
        extTemp.append(outTemp[count] + (uValue * (inTemp[count] - outTemp[count]))/extFilmCo)
        extFilmCoeff.append(extFilmCo)
    
    return intTemp, filmCoeff, extTemp, extFilmCoeff



if _outTemp != [] and _inTemp != [] and _uValue:
    inTemp, outTemp, windSpd = checkData(_outTemp, _inTemp, outWindSpd_)
    inSrfTemp, inFilmCoeff, extSrfTemp, extFilmCoeff = main(outTemp, inTemp, _uValue, windSpd, srfOrient_, intEmiss_)