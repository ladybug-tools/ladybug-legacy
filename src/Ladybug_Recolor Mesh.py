# This component re-color the mesh based on new parameters
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
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
Use this component to re-color a mesh with new a numerical data set whose length corresponds to the number of faces in the _inputMesh.
This component is useful if you have post-processed any of the numerical data out of the Ladybug components using Grasshopper math components.
It is also necessary to view results from the Ladybug Real Time Radiation Analysis.
-
Provided by Ladybug 0.0.63
    
    Args:
        _analysisResult: A numerical data set whose length corresponds to the number of faces in the _inputMesh.  This data will be used to re-color the _inputMesh.
        _inputMesh: An already-colored mesh from one of the Ladybug components which you would like to re-color based on data in the _analysisResult.
        heightDomain_: Optional height domain to create a 3D mesh result. Use Construct Domain component to create a domain
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.  Legend Parameters can be used to change the colors, numerical range, and/or number of divisions of any Ladybug legend along with the corresponding colored mesh.
        analysisTitle_: Text representing a new title for the re-colored mesh.  If no title is input here, the default will read "unnamed."
        legendTitle_: Text representing a new legend title for re-colored mesh. Legends are usually titled with the units of the _analysisResult.  If no text is provided here, the default title will read "unkown units."
        bakeIt_ : An integer that tells the component if/how to bake the bojects in the Rhino scene.  The default is set to 0.  Choose from the following options:
            0 (or False) - No geometry will be baked into the Rhino scene (this is the default).
            1 (or True) - The geometry will be baked into the Rhino scene as a colored hatch and Rhino text objects, which facilitates easy export to PDF or vector-editing programs. 
            2 - The geometry will be baked into the Rhino scene as colored meshes, which is useful for recording the results of paramteric runs as light Rhino geometry.
        layerName_: If bakeIt_ is set to "True", input Text here corresponding to the Rhino layer onto which the resulting mesh and legend should be baked.
        lowBoundColor_: A color representing the higher boundary of the legend's numerical range, use the Swatch component to specify a color.
        highBoundColor_: A color representing the lowest boundary of the legend's numerical range, use the Swatch component to specify a color.
    Returns:
        readMe!: ...
        newMesh: A new mesh that has been re-colored based on the _analysisResult data.
        newLegend: A new legend that that corresponds to the colors of the newMesh. Connect this output to a grasshopper "Geo" component in order to preview this legend separately in the Rhino scene.  
        legendBasePt: The legend base point, which can be used to move the legend in relation to the newMesh with the grasshopper "move" component.
        meshColors: The colors associated with each face of the newMesh.
        legendColors: The colors associated with each segment of the newLegend.
"""

ghenv.Component.Name = "Ladybug_Recolor Mesh"
ghenv.Component.NickName = 'reColorMesh'
ghenv.Component.Message = 'VER 0.0.63\nJAN_02_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass
#compatibleLBVersion = VER 0.0.59\nJAN_02_2017

import scriptcontext as sc
import Rhino as rc
import System
from math import pi as PI

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh


def main(analysisResult, inputMesh, heightDomain, legendPar, analysisTitle, legendTitle, bakeIt, layerName, lowBoundColor, highBoundColor, lb_preparation, lb_visualization):
    conversionFac = lb_preparation.checkUnits()
    
    if inputMesh.Faces.Count == len(analysisResult):
        meshStruct = 0
    elif inputMesh.Vertices.Count == len(analysisResult):
        meshStruct = 1
    else:
        warning = 'length of the results [=' + str(len(analysisResult)) + '] is not equal to the number of mesh faces [=' + str(inputMesh.Faces.Count) + '] or mesh vertices[=' + str(inputMesh.Vertices.Count) + '].'
        print warning
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    colors = lb_visualization.gradientColor(analysisResult, lowB, highB, customColors,lowBoundColor,highBoundColor)
    coloredChart = lb_visualization.colorMesh(colors, inputMesh, True, meshStruct)
    
    if heightDomain!=None:
        coloredChart = lb_visualization.create3DColoredMesh(coloredChart, analysisResult, heightDomain, colors, meshStruct)
    
    lb_visualization.calculateBB([coloredChart], True)
    
    if not legendTitle:  legendTitle = 'unknown units  '
    if not analysisTitle: analysisTitle = '\nno title'
    
    legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(analysisResult
        , lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale
        , legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
    
    # generate legend colors
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors,lowBoundColor,highBoundColor)
    
    # color legend surfaces
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    
    titlebasePt = lb_visualization.BoundingBoxPar[-2]
    if legendFont == None: legendFont = 'Veranda'
    if legendFontSize == None: legendFontSize = legendScale * (lb_visualization.BoundingBoxPar[2]/20)
    titleTextCurve = lb_visualization.text2srf(["\n\n" + analysisTitle], [titlebasePt], legendFont, legendFontSize, legendBold)
    
    if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
    
    if bakeIt > 0:
        formatString = "%."+str(decimalPlaces)+"f"
        for count, item in enumerate(legendText):
            try:
                legendText[count] = formatString % item
            except:pass
        legendText.append(analysisTitle)
        textPt.append(titlebasePt)
        studyLayerName = 'CUSTOM_PRESENTATION'
        if layerName == None: layerName = 'Custom'
        # check the study type
        newLayerIndex, l = lb_visualization.setupLayers('Modified Version', 'LADYBUG', layerName, studyLayerName)
        if bakeIt == 1: lb_visualization.bakeObjects(newLayerIndex, coloredChart, legendSrfs, legendText, textPt, textSize, legendFont, None, decimalPlaces, True)
        else: lb_visualization.bakeObjects(newLayerIndex, coloredChart, legendSrfs, legendText, textPt, textSize, legendFont, None, decimalPlaces, False)
    return coloredChart, [legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)], legendBasePoint, colors, legendColors



# import the classes
initCheck = True
if sc.sticky.has_key('ladybug_release'):
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
                 "Use updateLadybug component to update userObjects.\n" + \
                 "If you have already updated userObjects drag Ladybug_Ladybug component " + \
                 "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        initCheck = False
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
else:
    print "You should let the Ladybug fly first..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should let the Ladybug fly first...")
    initCheck = False



if initCheck == True and _inputMesh and len(_analysisResult)!=0:
    result = main(_analysisResult, _inputMesh, heightDomain_, legendPar_, analysisTitle_, legendTitle_, bakeIt_, layerName_, lowBoundColor_, highBoundColor_, lb_preparation, lb_visualization)
    if result!= -1:
        newLegend= []
        newMesh = result[0]
        [newLegend.append(item) for item in lb_visualization.openLegend(result[1])]
        legendBasePt = result[2]
        meshColors = result[3]
        legendColors = result[4]
        
        # Hide output
        ghenv.Component.Params.Output[3].Hidden = True
