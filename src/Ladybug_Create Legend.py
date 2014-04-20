# Create legend
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Create legend
-
Provided by Ladybug 0.0.57

    Args:
        values_: Input values
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        legendTitle_: Text representing a new legend title for re-colored mesh. Legends are usually titled with the units of the _analysisResult.  If no title is provided, no text will appear above the legend.
        legendWidth_: Width of the legend in units of Rhino model
    Returns:
        legendMesh: A new legend that that corresponds to the colors of the newMesh. Connect this output to a grasshopper "Geo" component in order to preview this legend separately in the Rhino scene.  
        legendTextSrf: ...
        legendBasePt: The legend base point, which can be used to move the legend in relation to the newMesh with the grasshopper "move" component.
        legendValues: ...
        valuesBasePt: ...
"""

ghenv.Component.Name = "Ladybug_Create Legend"
ghenv.Component.NickName = 'createLegend'
ghenv.Component.Message = 'VER 0.0.57\nAPR_20_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
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
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize = lb_preparation.readLegendParameters(legendPar, False)
    
    if legendBasePoint == None: legendBasePoint = rc.Geometry.Point3d(0,0,0)
    if legendWidth == None: legendWidth = 10
    boundingBoxPar = [legendBasePoint, None, 10 * legendWidth] 
    
    # generate the legend
    legendSrfs, legendText, legendTextSrfs, textPt, textSize = lb_visualization.createLegend(results
    , lowB, highB, numSeg, legendTitle, boundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize)
    
    #
    legendTextSrfsFlattened = []
    [legendTextSrfsFlattened.extend(srf) for srf in legendTextSrfs]
    
    # generate legend colors
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    
    # color legend surfaces
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    
    
    return legendBasePoint, legendSrfs, legendText, legendTextSrfsFlattened, textPt

if _values:
    results = main(_values, legendPar_, legendTitle_, legendWidth_)
    
    if results!=-1:
        legendBasePt, legendMesh, legendValues, legendTextSrf, valuesBasePt = results
        
        # hide points preview
        
        ghenv.Component.Params.Output[2].Hidden = True
        ghenv.Component.Params.Output[4].Hidden = True
