# This component re-color the mesh based on new parameters
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Re-color Mesh
-
Provided by Ladybug 0.0.35
    
    Args:
        analysisResult: The result of the analysis
        inputMesh: Already colored mesh for the analysis
        legendPar: Input legend parameters from the Ladybug Legend Parameters component
        analysisTitle: Custom title for the study as a string
        legendTitle: Custom title for the legend. It is usually the unit of the analysis result.
        bakeIt: Set Boolean to True to bake the result
        layerName: Layer name
        
    Returns:
        report: Report!!!
        newMesh: A new re-colored mesh based on the new setting
        newLegend: Legend of the study. Connect to Geo for preview
        legendBasePt: Legend base point, mainly for presentation purposes
"""

ghenv.Component.Name = "Ladybug_Re-Color Mesh"
ghenv.Component.NickName = 'reColorMesh'
ghenv.Component.Message = 'VER 0.0.35\nJAN_03_2013'

import scriptcontext as sc
import Rhino as rc
import System
from math import pi as PI

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh


def main(analysisTitle, legendTitle, layerName):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        conversionFac = lb_preparation.checkUnits()
        # copy the custom code here
        # check inputs
        if inputMesh and len(analysisResult)!=0:
            if inputMesh.Faces.Count != len(analysisResult):
                warning = 'length of the results should be equal to the number of mesh faces'
                print warning
                w = gh.GH_RuntimeMessageLevel.Error
                ghenv.Component.AddRuntimeMessage(w, warning)
                return -1
            
            lowB, highB, numSeg, customColors, legendBasePoint, legendScale = lb_preparation.readLegendParameters(legendPar, False)
            
            colors = lb_visualization.gradientColor(analysisResult, lowB, highB, customColors)
            coloredChart = lb_visualization.colorMesh(colors, inputMesh)
                
            lb_visualization.calculateBB([coloredChart], True)
                
                
            if not legendTitle:  legendTitle = 'unknown units  '
            if not analysisTitle: analysisTitle = '\nno title'
            
            legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(analysisResult
                , lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale)
            
            # generate legend colors
            legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
            
            # color legend surfaces
            legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
            
            titlebasePt = lb_visualization.BoundingBoxPar[-2]
            titleTextCurve = lb_visualization.text2crv([analysisTitle], [titlebasePt], 'Veranda', legendScale * (lb_visualization.BoundingBoxPar[2]/20))
            
            if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
            
            if bakeIt:
                legendText.append(analysisTitle)
                textPt.append(titlebasePt)
                studyLayerName = 'CUSTOM_PRESENTATION'
                if layerName == None: layerName = 'Custom'
                # check the study type
                newLayerIndex, l = lb_visualization.setupLayers('Modified Version', 'LADYBUG', layerName, studyLayerName)
                lb_visualization.bakeObjects(newLayerIndex, coloredChart, legendSrfs, legendText, textPt, textSize, fontName = 'Verdana')
                
            return coloredChart, [legendSrfs, [lb_preparation.flattenList(legendTextCrv + titleTextCurve)]], legendBasePoint
        else:
            warning = 'Connect inputData!'
            print warning
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
    else:
        print "You should let the Ladybug fly first..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should let the Ladybug fly first...")
        return -1
    
    conversionFac = lb_preparation.checkUnits()


if inputMesh and len(analysisResult)!=0:
    
    def openLegend(legendRes):
        if len(legendRes)!=0:
            meshAndCrv = []
            meshAndCrv.append(legendRes[0])
            [meshAndCrv.append(curve) for curveList in legendRes[1] for curve in curveList]
            #print meshAndCrv
            return meshAndCrv
        else: return
    
    result = main(analysisTitle, legendTitle, layerName)
    if result!= -1:
        newLegend= []
        newMesh = result[0]
        [newLegend.append(item) for item in openLegend(result[1])]
        legendBasePt = result[2]