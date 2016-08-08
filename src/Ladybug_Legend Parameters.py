# This component makes a simple string for legend parameters
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Use this component to change the colors, numerical range, and/or number of divisions of any Ladybug legend along with the corresponding colored mesh that the legend refers to.
This component can also move a legend and change its scale.
Any Ladybug component that outputs a colored mesh and a legend will have an input that can accept Legend Parameters from this component.
This component particularly helpful in making the colors of Ladybug graphics consistent for a presentation or for synchonizing the numerical range and colors between Ladybug graphics.
-
Provided by Ladybug 0.0.62
    
    Args:
        lowBound_: A number representing the lower boundary of the legend's numerical range.  The default is set to the lowest value of the data stream that the legend refers to.
        highBound_: A number representing the higher boundary of the legend's numerical range. The default is set to the highest value of the data stream that the legend refers to.
        numSegments_: An interger representing the number of steps between the high and low boundary of the legend.  The default is set to 11 and any custom values put in here should always be greater than or equal to 2.
        customColors_: A list of colors that will be used to re-color the legend and the corresponding colored mesh(es).  The number of colors input here should match the numSegments_ value input above.  An easy way to generate a list of colors to input here is with the Grasshopper "Gradient" component and a Grasshopper "Series" component connected to the Gradient component's "t" input.  A bunch of Grasshopper "Swatch" components is another way to generate a list of custom colors.  The default colors are a gradient spectrum from blue to yellow to red.
        legendLocation_: Input a point here to change the location of the legend in the Rhino scene.  The default is usually set to the right of the legend's corresponding Ladybug graphic.
        legendScale_: Input a number here to change the scale of the legend in relation to its corresponding Ladybug graphic.  The default is set to 1.
        font_: An optional text string that sets the font of the text. Examples include "Arial", "Times New Roman" or "Courier" (all without quotations).  The text input here can be any font that is on your computer but the font must be of an Editable file type (as seen in the font folder off of your control panel).  Font files that are Print and Preview will not work.  If you wish to use a Bolded version of the font, include a ", Bold" at the end of the font name (example: "Arial, Bold").
        fontSize_: An optional number to set the size of the text in Rhino model units.
        decimalPlaces_: An interger representing the number of decimal places to make the legend values.  The default is set to 2 decimal places.
        removeLessThan_: Set to 'True' to have the "<=" and ">=" symbols removed from the legend.  The default is set to 'False' to have these symbols included.
    Returns:
        legendPar: A list of legend parameters to be plugged into any of the Ladybug components with a legend.
"""

ghenv.Component.Name = "Ladybug_Legend Parameters"
ghenv.Component.NickName = 'legendPar'
ghenv.Component.Message = 'VER 0.0.62\nAUG_08_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nNOV_20_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass



from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import scriptcontext as sc
import Rhino as rc
import System.Drawing.Text as textCollection


def getFontsList():
    fonts = []
    fontColletion = textCollection.InstalledFontCollection().Families
    
    for fontObj in fontColletion:
        fontName = fontObj.Name
        if fontName not in fonts: fonts.append(fontName.lower())
    fonts.sort()
    return fonts

def main(lowBound, highBound, numSegments, customColors, legendLocation, legendScale, font, fontSize, decimalPlaces, removeLessThan):
    if len(customColors) != 1:
        if lowBound: lowBound = float(lowBound)
        if highBound: highBound = float(highBound)
        if numSegments: numSegments = int(numSegments)
        if legendScale: legendScale = float(legendScale)
        bold = False
        if font!= None:
            if font.upper().endswith(', BOLD') or font.upper().endswith(',BOLD'):
                bold = True
                font = font.split(',')[0]
            fonts = getFontsList()
            if font.lower() not in fonts:
                msg = "Cannot find input font " + font + "."
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, msg)
                font = None 
        if lowBound and highBound and float(lowBound) > float(highBound):
            legendPar = [highBound, lowBound, numSegments, customColors, legendLocation, legendScale]
        else:
            legendPar = [lowBound, highBound, numSegments, customColors, legendLocation, legendScale]
        
        legendPar.extend([font, fontSize, bold, decimalPlaces, removeLessThan])
        return legendPar
    else:
        return -1

legendPar = main(lowBound_, highBound_, numSegments_, customColors_, legendLocation_, legendScale_, font_, fontSize_, decimalPlaces_, removeLessThan_)
ghenv.Component.Params.Output[0].Hidden = True
if legendPar == -1:
    warning = "You should connect at least two colors to customColors input."
    print warning
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, warning)
    legendPar = []