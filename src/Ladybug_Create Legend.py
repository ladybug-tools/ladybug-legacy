# Create legend
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Use this component to create a custom legend for any set of data or to create a more flexible legend for any ladybug component with a legend.  Specifically, this component outputs data that can be plugged into the grasshopper "Text Tag 3D" component so that the legend text can be baked into the Rhino scene as actual text instead of surfaces representing text.
-
Provided by Ladybug 0.0.65

    Args:
        _valuesOrRange: The list of numerical data that the legend refers to (or just the minimum and maximum numerical values of this data).  If the original numerical data is hooked up, the legend's maximum and minimum values will be set by the max and min of the data set.
        legendBasePt_: An optional point to set the location of the legend.  This can be the output legendBasePt of any of the Ladybug components that have a legend.  If a point is hooked up here and another point is hooked up at a legendPar component that is connected to this one, the point on the legendPar component will override the input point here.
        legendTitle_: A text string representing a legend title. Legends are usually titled with the units of the data.  If no text is provided here, the default title will read "unkown units."
        legendSize_: The initial size of a single colored cell of the legend mesh, which determines the size of the whole legend.  This should be a numerical value corresponding to the length of a legend cell in Rhino model units.  The default is set to 10 Rhino units.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
    Returns:
        legendMesh: A colored mesh that corresponds to the input _valuesOrRange. Connect this output to a grasshopper "Mesh" component in order to preview this separately in the Rhino scene.  
        legendTextSrf: A list of surfaces representing the text labels of the legend.  These surfaces will reflect the font and size input to the legendPar.
        legendBasePt: The legend base point, which can be used to move the legend with the grasshopper "move" component.
        -------------------------: ...
        textValuesBasePts: The base points that correspond to the title text and numerical value text of the legend.  Plug this into the "Location" input of the grasshopper "Text Tag 3D" component in order to display as text in Rhino.
        legendTextValues: The text strings that correspond to the title and numerical values of the legend.  Plug this into the "Text" input of the grasshopper "Text Tag 3D" component in order to display as text in Rhino.
        recommendedTextSize: Values representing recommended text sizes that correspond to the title and numerical values of the legend.  These values are generated based on the legend size and scale. Plug this into the "Size" input of the grasshopper "Text Tag 3D" component in order to display as text in Rhino.

"""

ghenv.Component.Name = "Ladybug_Create Legend"
ghenv.Component.NickName = 'createLegend'
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nNOV_20_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Grasshopper.Kernel as gh
import scriptcontext as sc
import Rhino as rc

def main(results, legendPar, legendTitle, legendWidth):
    if not sc.sticky.has_key('ladybug_release'):
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1
        
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    
    if not legendTitle:  legendTitle = 'unknown units  '
    
    # read the legend parameters legend
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    
    if legendBasePoint == None and legendBasePt_ != None: legendBasePoint = legendBasePt_
    else: legendBasePoint = rc.Geometry.Point3d(0,0,0)
    if legendWidth == None: legendWidth = 10
    boundingBoxPar = [legendBasePoint, None, 10 * legendWidth] 
    
    # generate the legend
    legendSrfs, legendText, legendTextSrfs, textPt, textSize = lb_visualization.createLegend(results
    , lowB, highB, numSeg, legendTitle, boundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
    
    #
    legendTextSrfsFlattened = []
    [legendTextSrfsFlattened.extend(srf) for srf in legendTextSrfs]
    
    # generate legend colors
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    
    # color legend surfaces
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    
    #Define a function to duplicate data
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data)
        return dupData
    
    # calculate a recommended text size.
    rTextSize = 3.5*(legendWidth/10)*legendScale
    titleTextSize = rTextSize*1.35
    recommendedTextSize = duplicateData(rTextSize, len(textPt)-1)
    recommendedTextSize.append(titleTextSize)
    
    # move the text legend points over just a little bit so that they are not right up against the legend.
    transforMatrix = rc.Geometry.Transform.Translation((3.5*(legendWidth/10)*legendScale), 0, 0)
    for point in textPt:
        point.Transform(transforMatrix)
    
    return legendBasePoint, legendSrfs, legendText, legendTextSrfsFlattened, textPt, recommendedTextSize

if _valuesOrRange:
    results = main(_valuesOrRange, legendPar_, legendTitle_, legendSize_)
    
    if results!=-1:
        legendBasePt, legendMesh, legendTextValues, legendTextSrf, textValuesBasePts, recommendedTextSize = results
        
        # hide points preview
        
        ghenv.Component.Params.Output[2].Hidden = True
        ghenv.Component.Params.Output[4].Hidden = True
