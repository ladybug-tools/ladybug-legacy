# Tregenza Sky Dome
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component uses GenCumulativeSky result to visualize the Tregenza sky patches for total, diffuse and direct radiation.

For more information about sky subdivisions, reference: "http://naturalfrequency.com/wiki/sky-subdivision"
-
Provided by Ladybug 0.0.35
    
    Args:
        genCumSkyResult: GenCumulativeSky component result
        centerPoint: Input a point to locate the center point of the Tregenza sky patches
        scale: Input a number to set the scale of the Tregenza sky patches
        legendPar: Input legend parameters from the Ladybug Legend Parameters component
        showTotalOnly: Set Boolean to True to show the total radiation only
        runIt: Set Boolean to True to run
        bakeIt: Set Boolean to True to bake the sky patches
    Returns:
        report: Report!!!
        skyPatchesMesh: Sky Patches as a joined mesh
        baseCrvs: Base curves of the graph
        legend: Legend of the study. Connect to Geo for preview
        legendBasePts: Legend base points, mainly for presentation purposes 
        skyPatchesCenPts: Center points of sky patches; mainly for presentation purposes
        legendBasePts: Legend base point mainly for presentation purposes
        values: Radiation values for sky patches
"""

ghenv.Component.Name = "Ladybug_Tregenza Sky Dome"
ghenv.Component.NickName = 'TregenzaSkyDome'
ghenv.Component.Message = 'VER 0.0.35\nJAN_03_2013'

import scriptcontext as sc
import Rhino as rc
from System import Object
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

def main(legendPar, scale):
    
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        conversionFac = lb_preparation.checkUnits()
        
        # check the input data
        try:
            if genCumSkyResult[2][:11] == 'Sky Patches': checkData = True
            else:
                checkData = False
                print "Please provide valid genCumSkyResult!"
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "Please provide valid genCumSkyResult!")
                return -1
        except:
            checkData = False
            print "Please provide valid genCumSkyResult!"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Please provide valid genCumSkyResult!")
            return -1
        
        if checkData:
            # separate the data
            indexList, listInfo = lb_preparation.separateList(genCumSkyResult, lb_preparation.strToBeFound)
            
            # check the scale
            try:
                if float(scale)!=0:
                    try:scale = float(scale)/conversionFac
                    except: scale = 1/conversionFac
                else:
                    scale = 1/conversionFac
            except:
                scale = 1/conversionFac
            
            cenPt = lb_preparation.getCenPt(centerPoint)
            
            # generate the Tregenza sky dome
            skyDomeSrfs = lb_preparation.generateTregenzaSkyGeo(cenPt,float(scale))
            
            # calculate the bounding box for the skyDome
            tmpCrv = rc.Geometry.Circle( cenPt, 1.05 * 100 * scale).ToNurbsCurve()
            lb_visualization.calculateBB([skyDomeSrfs, tmpCrv])
            movingDist = 1.75 * lb_visualization.BoundingBoxPar[1] # moving distance for sky domes
            
            #separate total, diffuse and direct radiations
            separatedLists = []
            for i in range(len(indexList)-1):
                selList = []
                [selList.append(float(x)) for x in genCumSkyResult[indexList[i] + 7:indexList[i+1]]]
                separatedLists.append(selList)
            
            ######################
            # start visualization#
            ######################
            
            # generate the legend
            legendTitles = [listInfo[0][3], listInfo[1][3], listInfo[2][3]]
            customHeading = ['\n\nTotal Radiation (kWh/m2)', '\n\nDiffuse Radiation (kWh/m2)', '\n\nDirect Radiation (kWh/m2)']
            
            legendMax = [max(separatedLists[0]), max(separatedLists[1] + separatedLists[2]), max(separatedLists[1] + separatedLists[2])]
            legendMin = [0,0,0]
            
            def visualizeData(i, results, skyDomeSrfs, legendTitle, legendPar, bakeIt):
                movingVector = rc.Geometry.Vector3d(i * movingDist,0,0)
                overwriteScale = False
                if legendPar == []: overwriteScale = True
                elif legendPar[-1] == None: overwriteScale = True
                
                lowB, highB, numSeg, customColors, legendBasePoint, legendScale = lb_preparation.readLegendParameters(legendPar, False)
                
                if overwriteScale: legendScale = 0.9
                
                legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(results
                , lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale)
                
                
                titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo[i]], lb_visualization.BoundingBoxPar, legendScale, customHeading[i])
                
                northVector = rc.Geometry.Vector3d.YAxis
                compassCrvs, compassTextPts, compassText = lb_visualization. compassCircle(cenPt, northVector, 100 * scale, range(0, 360, 10), 1.2*textSize)
                numberCrvs = lb_visualization.text2crv(compassText, compassTextPts, 'Times New Romans', textSize/1.2)
                compassCrvs = compassCrvs + lb_preparation.flattenList(numberCrvs)
                
                for crv in legendTextCrv + [compassCrvs]:
                    for c in crv: c.Translate(movingVector) # move it to the right place
                
                for crv in titleTextCurve:
                    for c in crv: c.Translate(movingVector) # move it to the right place
                
                textPt.append(titlebasePt)
                
                ptCount  = 0
                for pt in textPt:
                    ptLocation = rc.Geometry.Point(pt)
                    ptLocation.Translate(movingVector) # move it to the right place
                    textPt[ptCount] = rc.Geometry.Point3d(ptLocation.Location)
                    ptCount += 1
                    
                # generate legend colors
                legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
                
                # color legend surfaces
                legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
                legendSrfs.Translate(movingVector) # move it to the right place
                
                # generate dome patches colors
                totalRadiationColors = lb_visualization.gradientColor(results, lowB, highB, customColors)
                domeMeshed = rc.Geometry.Mesh();
                
                # mesh the patches
                meshParam = rc.Geometry.MeshingParameters.Smooth
                colForMesh = []; patchCount = 0;
                
                skyPatchCenPts = []
                
                for patch in skyDomeSrfs:
                    newPatch = patch.DuplicateFace(False) # make a copy
                    newPatch.Translate(movingVector) # move it to the right place
                    MP = rc.Geometry.AreaMassProperties.Compute(newPatch)
                    patchCenPt = MP.Centroid
                    skyPatchCenPts.append(patchCenPt)
                    MP.Dispose()
                    patchMeshed = rc.Geometry.Mesh.CreateFromBrep(newPatch, meshParam) # create mesh
                    domeMeshed.Append(patchMeshed[0]) # append to the main mesh
                    for face in range(patchMeshed[0].Faces.Count): colForMesh.append(totalRadiationColors[patchCount]) #generate color list
                    newPatch.Dispose() # delete the polysurface
                    patchCount += 1
                    
                placeName = listInfo[i][1]
                skyTypes = ['Total Radiation' + placeName[:3], 'Diffuse Radiation' + placeName[:3], 'Direct Radiation' + placeName[:3]]
                
                # color the meshed patches
                domeMeshed = lb_visualization.colorMesh(colForMesh, domeMeshed)
                
                if legendBasePoint == None:
                    nlegendBasePoint = lb_visualization.BoundingBoxPar[0]
                    movedLegendBasePoint = rc.Geometry.Point3d.Add(nlegendBasePoint, movingVector);
                else:
                    movedLegendBasePoint = rc.Geometry.Point3d.Add(legendBasePoint, movingVector);
                
                strResults = []
                [strResults.append('%.2f'%num) for num in results]
                
                
                if bakeIt:
                    # projectName = listInfo[0][1] + '_Total'
                    legendText.append(titleStr)
                    studyLayerName = 'SkyDome'
                    
                    # check the study type
                    newLayerIndex, l = lb_visualization.setupLayers(skyTypes[i], 'LADYBUG', placeName, studyLayerName, False, False, 0, 0)
                    
                    lb_visualization.bakeObjects(newLayerIndex, domeMeshed, legendSrfs, legendText, textPt, textSize, 'Verdana', compassCrvs)
                    
                return domeMeshed, [legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)], compassCrvs, movedLegendBasePoint, skyPatchCenPts, strResults
            
            if not showTotalOnly: skyTypes = 3
            else: skyTypes = 1
            
            normLegend = False; res = [[], [], [], [], [], []];
            for i in range(skyTypes):
                # fix the bake
                try:
                    if legendPar[1] is None or normLegend:
                        legendPar[0] = legendMin[i]
                        legendPar[1] = legendMax[i]
                        normLegend = True
                except:
                    # make an initial legend parameter to replace the max
                    legendPar = [None,None,None,[],None, None]
                    legendPar[0] = legendMin[i]
                    legendPar[1] = legendMax[i]
                    normLegend = True
                
                skyMesh, leg, compassCrvs, movedBasePt, skyPatchCenPts,radValues = visualizeData(i, separatedLists[i], skyDomeSrfs, legendTitles[i], legendPar, bakeIt)
                
                res[0].append(skyMesh)
                res[1].append(leg)
                res[2].append(compassCrvs)
                res[3].append(movedBasePt)
                res[4].append(skyPatchCenPts)
                res[5].append(radValues)
            # remove the sky polysurfaces
            for patch in skyDomeSrfs: patch.Dispose()
            
            return res
            
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1


if runIt:
    result = main(legendPar, scale)
    if result!= -1:
        legend = DataTree[Object]()
        skyPatchesMesh = DataTree[Object]()
        baseCrvs = DataTree[Object]()
        legendBasePts = DataTree[Object]()
        skyPatchesCenPts = DataTree[Object]()
        values = DataTree[Object]()
        
        for i, leg in enumerate(result[1]):
            p = GH_Path(i)
            skyPatchesMesh.Add(result[0][i], p)
            baseCrvs.AddRange(result[2][i], p)
            legend.Add(leg[0], p)
            legend.AddRange(leg[1], p)
            legendBasePts.Add(result[3][i], p)
            skyPatchesCenPts.AddRange(result[4][i], p)
            values.AddRange(result[5][i], p)