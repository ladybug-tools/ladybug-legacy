# Sky Domes
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component allows you to visualize a selected sky matrix from the selectSkyMxt component in order to see the patches of the sky dome where radiation is coming from.
The component will produce 3 sky domes by default: a dome showing just the diffuse radiation, a dome showing just the direct radiation, and a dome showing the total radiation.
-
Provided by Ladybug 0.0.57
    
    Args:
        _selectedSkyMtx: The output from the selectSkyMtx component.
        _centerPoint_: A point that sets the location of the sky domes.  The default is set to the Rhino origin (0,0,0).
        _scale_: Use this input to change the scale of the sky dome.  The default is set to 1.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        showTotalOnly_: Set to "True" to only show a sky dome with the total radiation.  The default is "False", which will produce 3 sky domes: one of diffuse radiation, one of direct radiation, and one of the total radiation.
        _runIt: Set to "True" to run the component and generate a sky dome.
        bakeIt_: Set to "True" to bake the sky dome into the Rhino scene.
    Returns:
        readMe!: ...
        skyPatchesMesh:  A colored mesh representing the intensity of radiation for each of the sky patches of the sky dome.
        baseCrvs:  A set of guide curves that mark information on the sky dome.
        legend: A legend for the sky dome. Connect this output to a grasshopper "Geo" component in order to preview the legend separately in the Rhino scene.  
        legendBasePts: The legend base point(s), which can be used to move the legend(s) in relation to the sky domes with the grasshopper "move" component.
        skyPatchesCenPts: The center points of sky patches, which can be used to shape Rhino geometry in relation to radiation from different sky patches.
        skyPatchesAreas: The area of sky patches in Rhino model units.
        skyPatchesAsBrep: The geometry of sky patches as breps.
        values: Radiation values for the sky patches in Wh/m2.
"""

ghenv.Component.Name = "Ladybug_Sky Dome"
ghenv.Component.NickName = 'SkyDome'
ghenv.Component.Message = 'VER 0.0.57\nAPR_20_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import scriptcontext as sc
import Rhino as rc
from System import Object
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import time
import math
import System.Threading.Tasks as tasks
startTime = time.time()

def skyPreparation(skyType):
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
        class LBSKY(object):
            def __init__(self, geometries):
                self.geo = []
                [self.geo.append(g) for g in geometries]
                
        if not sc.sticky.has_key("LB_Skies"): sc.sticky["LB_Skies"] = {}
        
        if not sc.sticky["LB_Skies"].has_key(skyType):
            skyGeo = lb_preparation.generateSkyGeo(rc.Geometry.Point3d.Origin, skyType, 100)
            thisSky = LBSKY(skyGeo)
            sc.sticky["LB_Skies"][skyType] = thisSky
        
        sky = sc.sticky["LB_Skies"][skyType]
        
        return sky.geo
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1
        


def main(north, genCumSkyResult, originalSkyDomeSrfs, centerPoint, scale, legendPar, showTotalOnly, bakeIt, skyType):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    
    if genCumSkyResult[2][:11] != 'Sky Patches':
        print "selectedSkyMtx is not a valid Ladybug sky information!"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "selectedSkyMtx is not a valid Ladybug sky information!")
        return -1
    
    def visualizeData(i, northAngle, results, originalSkyDomeSrfs, legendTitle, legendPar, bakeIt):
        # creat moving vector for each sky
        movingVector = rc.Geometry.Vector3d(i * movingDist,0,0)
        
        # check if the user has an input for legend parameters
        overwriteScale = False
        if legendPar == []: overwriteScale = True
        elif legendPar[5] == None: overwriteScale = True
        
        # read the legend parameters legend
        lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize = lb_preparation.readLegendParameters(legendPar, False)
        
        # this is not a good idea to set the default to 0.9!
        # should be fixed later
        if overwriteScale: legendScale = 0.9
        
        # generate the legend
        legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(results
        , lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize)
        
        #print listInfo[i], customHeading[i]
        # generate the title
        titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo[i]], lb_visualization.BoundingBoxPar, legendScale, customHeading[i], False,  legendFont, legendFontSize)
        
        # generate compass curve
        northVector = rc.Geometry.Vector3d.YAxis
        compassCrvs, compassTextPts, compassText = lb_visualization. compassCircle(cenPt, northVector, 100 * scale, range(0, 360, 10), 1.2*textSize)
        numberCrvs = lb_visualization.text2srf(compassText, compassTextPts, 'Times New Romans', textSize/1.2)
        compassCrvs = compassCrvs + lb_preparation.flattenList(numberCrvs)
        
        # move all the geometries to the right place
        [c.Translate(movingVector) for crv in legendTextCrv + [compassCrvs] for c in crv]
        # move it to the right place
        [c.Translate(movingVector) for crv in titleTextCurve for c in crv]
        
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
        
        # mesh the patches and join them together
        domeMeshed = rc.Geometry.Mesh();
        
        # mesh the patches
        meshParam = rc.Geometry.MeshingParameters.Smooth
        colForMesh = []; patchCount = 0;
        
        skyPatchCenPts = []
        skyPatchAreas = []
        movedSkyPatches = []
        for patchCount, patch in enumerate(skyDomeSrfs):
            newPatch = patch.DuplicateShallow() # make a copy so I can
            if northAngle!=0: newPatch.Rotate(northAngle, rc.Geometry.Vector3d.ZAxis, rc.Geometry.Point3d.Origin)
            newPatch.Translate(movingVector) # move it to the right place
            movedSkyPatches.append(newPatch)
            MP = rc.Geometry.AreaMassProperties.Compute(newPatch)
            patchCenPt = MP.Centroid
            area = MP.Area
            skyPatchCenPts.append(patchCenPt)
            # thanks to rob guglielmetti for suggesting this
            skyPatchAreas.append(area)
            MP.Dispose()
            patchMeshed = rc.Geometry.Mesh.CreateFromBrep(newPatch, meshParam) # create mesh
            domeMeshed.Append(patchMeshed[0]) # append to the main mesh
            for face in range(patchMeshed[0].Faces.Count):
                colForMesh.append(totalRadiationColors[patchCount]) #generate color list
            
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
            
            lb_visualization.bakeObjects(newLayerIndex, domeMeshed, legendSrfs, legendText, textPt, textSize,  legendFont, compassCrvs)
            
        return domeMeshed, [legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)], compassCrvs, movedLegendBasePoint, skyPatchCenPts, skyPatchAreas, strResults, movedSkyPatches
    
    
    
    # north direction
    northAngle, northVector = lb_preparation.angle2north(north)
    
    # separate ladybug input data into lists
    indexList, listInfo = lb_preparation.separateList(genCumSkyResult, lb_preparation.strToBeFound)
    
    #separate total, diffuse and direct radiations
    separatedLists = []
    for i in range(len(indexList)-1):
        selList = []
        [selList.append(float(x)) for x in genCumSkyResult[indexList[i] + 7:indexList[i+1]]]
        separatedLists.append(selList)
    
    # set the scale number
    conversionFac = lb_preparation.checkUnits()
    try: scale = float(scale)/conversionFac
    except: scale = 1/conversionFac
    if scale==0: scale = 1/conversionFac #catch case of 0 for scale
    
    #set the center point
    cenPt = lb_preparation.getCenPt(centerPoint)
    
    skyDomeSrfs = range(len(originalSkyDomeSrfs))
    # move the skies to the right position
    if cenPt != rc.Geometry.Point3d.Origin:
        movingVector = rc.Geometry.Vector3d(cenPt - rc.Geometry.Point3d.Origin)
        for i, srf in enumerate(originalSkyDomeSrfs):
            newSrf = srf.DuplicateShallow()
            newSrf.Translate(movingVector)
            skyDomeSrfs[i] = newSrf
    
    if scale!= 1 and isinstance(skyDomeSrfs[i], int):
        # center point hasn't moved so original list should be used
        scaleT = rc.Geometry.Transform.Scale(cenPt, scale)
        for i, srf in enumerate(originalSkyDomeSrfs):
            newSrf = srf.DuplicateShallow()
            newSrf.Transform(scaleT)
            skyDomeSrfs[i] = newSrf
    elif scale!= 1:
        # scale the surfaces already moved in the first place
        scaleT = rc.Geometry.Transform.Scale(cenPt, scale)
        for srf in skyDomeSrfs: srf.Transform(scaleT)
    
    if cenPt == rc.Geometry.Point3d.Origin and scale== 1:
        for i, srf in enumerate(originalSkyDomeSrfs): skyDomeSrfs[i] = srf.DuplicateShallow()
    
    #calculate the bounding box for moving distance
    tmpCrv = rc.Geometry.Circle( cenPt, 1.05 * 100 * scale).ToNurbsCurve()
     
    lb_visualization.calculateBB([skyDomeSrfs, tmpCrv], True)
    
    # set the moving distance between sky domes
    movingDist = 1.75 * lb_visualization.BoundingBoxPar[1]
    
    # prepare legend information
    legendTitles = [listInfo[0][3], listInfo[1][3], listInfo[2][3]]
    customHeading = ['\n\nTotal Radiation('+ listInfo[0][3]+')', '\n\nDiffuse Radiation(' + listInfo[1][3] + ')', '\n\nDirect Radiation(' + listInfo[2][3] + ')']
    
    legendMax = [max(separatedLists[0]), max(separatedLists[1] + separatedLists[2]), max(separatedLists[1] + separatedLists[2])]
    legendMin = [0,0,0]
    
    # number of skies to be generated
    if showTotalOnly: skyTypes = 1
    else: skyTypes = 3
    
    normLegend = False
    # palce holder for results
    # I'l replace all this lists of lists with dictionaries later
    result = [[], [], [], [], [], [], [], []]
    
    # generate the skies
    for i in range(skyTypes):
        # no idea why I wrote it in the first place but for now I just keep it as it is
        try:
            if legendPar[1] is None or normLegend:
                legendPar[0] = legendMin[i]
                legendPar[1] = legendMax[i]
                normLegend = True
        except:
            # make an initial legend parameter to replace the max
            legendPar = [None,None,None,[],None, None, None, None]
            legendPar[0] = legendMin[i]
            legendPar[1] = legendMax[i]
            normLegend = True
        
        # this was a stupid idea to separate this function
        coloredSkyMesh, legend, compassCrvs, movedBasePt, skyPatchCenPts, skyPatchAreas, radValues, movedSkySrfs = visualizeData(i, northAngle, separatedLists[i], skyDomeSrfs, legendTitles[i], legendPar, bakeIt)
        
        result[0].append(coloredSkyMesh)
        result[1].append(legend)
        result[2].append(compassCrvs)
        result[3].append(movedBasePt)
        result[4].append(skyPatchCenPts)
        result[5].append(skyPatchAreas)
        result[6].append(radValues)
        result[7].append(movedSkySrfs)
    
    return result

if _runIt and _selectedSkyMtx:
    if len(_selectedSkyMtx) == 456: skyType = 0
    elif len(_selectedSkyMtx) == 1752: skyType = 1
    # generate sky domes and put them in the shared library
    skyGeometries = skyPreparation(skyType)
    
    north_ = 0 # I will apply rotation for north later! It is partially applied
    if skyGeometries != -1:
        result = main(north_, _selectedSkyMtx, skyGeometries, _centerPoint_, _scale_, legendPar_, showTotalOnly_, bakeIt_, skyType)
        
        if result!=-1:
            legend = DataTree[Object]()
            skyPatchesMesh = DataTree[Object]()
            baseCrvs = DataTree[Object]()
            legendBasePts = DataTree[Object]()
            skyPatchesCenPts = DataTree[Object]()
            skyPatchesAreas = DataTree[Object]()
            values = DataTree[Object]()
            skyPatchesAsBrep = DataTree[Object]()
            
            for i, leg in enumerate(result[1]):
                p = GH_Path(i)
                skyPatchesMesh.Add(result[0][i], p)
                baseCrvs.AddRange(result[2][i], p)
                legend.Add(leg[0], p)
                legend.AddRange(leg[1], p)
                legendBasePts.Add(result[3][i], p)
                skyPatchesCenPts.AddRange(result[4][i], p)
                skyPatchesAreas.AddRange(result[5][i], p)
                values.AddRange(result[6][i], p)
                skyPatchesAsBrep.AddRange(result[7][i], p)
            ghenv.Component.Params.Output[4].Hidden = True
            ghenv.Component.Params.Output[6].Hidden = True
            ghenv.Component.Params.Output[7].Hidden = True
else:
    print "Set runIt to True!"
