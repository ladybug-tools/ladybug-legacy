# This component makes a simple string for legend parameters
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component sets up the parameters to customize legends and presentation
-
Provided by Ladybug 0.0.53
    
    Args:
        lowBound_: Low bound of the legend
        highBound_: High bound of the legend
        numSegments_: Number of segments
        customColors_: A list of colors to customize the presentation color set
        legendLocation_: A point to locate base point of the legend
        legendScale_: A number to change the scale of the legend
    Returns:
        legendPar: Legend parameters
"""

ghenv.Component.Name = "Ladybug_Legend Parameters"
ghenv.Component.NickName = 'legendPar'
ghenv.Component.Message = 'VER 0.0.53\nJan_22_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "2"


from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import scriptcontext as sc


def main(lowBound, highBound, numSegments, customColors, legendLocation, legendScale):
    if len(customColors) != 1:
        if lowBound: lowBound = float(lowBound)
        if highBound: highBound = float(highBound)
        if numSegments: numSegments = int(numSegments)
        if legendScale: legendScale = float(legendScale)
        if lowBound and highBound and float(lowBound) > float(highBound):
            legendPar = [highBound, lowBound, numSegments, customColors, legendLocation, legendScale]
        else:
            
            legendPar = [lowBound, highBound, numSegments, customColors, legendLocation, legendScale]
        return legendPar
    else:
        return -1

legendPar = main(lowBound_, highBound_, numSegments_, customColors_, legendLocation_, legendScale_)
ghenv.Component.Params.Output[0].Hidden = True
if legendPar == -1:
    warning = "You should connect at least two colors to customColors input."
    print warning
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, warning)
    legendPar = []