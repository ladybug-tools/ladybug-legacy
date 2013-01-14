# This component makes a simple string for legend parameters
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component sets up the parameters to customize legends and presentation
-
Provided by Ladybug 0.0.35
    
    Args:
        lowBound: Low bound of the legend
        highBound: High bound of the legend
        numSegments: Number of segments
        customColors: A list of colors to customize the presentation color set
        legendLocation: A point to locate base point of the legend
        legendScale: A number to change the scale of the legend
    Returns:
        report: Report!!!
        legendPar: Legend parameters
"""

ghenv.Component.Name = "Ladybug_Legend Parameters"
ghenv.Component.NickName = 'legendPar'
ghenv.Component.Message = 'VER 0.0.35\nJAN_03_2013'


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

legendPar = main(lowBound, highBound, numSegments, customColors, legendLocation, legendScale)
if legendPar == -1:
    warning = "You should connect at least two colors to customColors input."
    print warning
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, warning)
    legendPar = []