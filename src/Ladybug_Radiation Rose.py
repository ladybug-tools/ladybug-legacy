# Radiation Rose
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to make a radiation rose in the Rhino scene.  Radiation roses give a sense of how much radiation comes from the different cardinal directions, which will give an initial idea of where glazing should be minimized, shading applied, or solar collectors placed.

-
Provided by Ladybug 0.0.58
    
    Args:
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _selectedSkyMtx: The output from the selectSkyMtx component.
        context_: Optional breps or meshes representing context surrounding the point at the center of the radiation rose.  This context geometry will block the radiation that shows up in the rose.
        _numOfArrows_: An interger that sets the number of arrows (or cardingal directions) in the radiation rose. The default is set to 36.
        _surfaceTiltAngle_: A number between 0 and 90 that sets the tilt angle in degrees of the analysis plane (0 = roof, 90 = vertical wall). The defult is set to 90 for a radiation study of a wall (ie. radiation on a curtain wall).
        _centerPoint_: A point that sets the location of the radiation rose.  The default is set to the Rhino origin (0,0,0).
        _scale_: Use this input to change the scale of the radiation rose.  The default is set to 1.
        _arrowHeadScale_: Use this input to change the scale of the arrow heads of the radiation rose.  The default is set to 1.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        showTotalOnly_: Set to "True" to only show a radiation rose with the total radiation.  The default is "False", which will produce 3 radiation roses: one of diffuse radiation, one of direct radiation, and one of the total radiation.
        _runIt: Set to "True" to run the component and generate a radiation rose.
        bakeIt_: Set to "True" to bake the radiation rose into the Rhino scene.
    Returns:
        readMe!: ...
        radiationArrowsMesh: A colored mesh representing the intensity of radiation from different cardinal directions.
        radRoseBaseCrvs: A set of guide curves that mark the directions of radiation analysis.
        legend:  A legend of the radiation rose. Connect this output to a grasshopper "Geo" component in order to preview the legend separately in the Rhino scene.  
        legendBasePts: The legend base point(s), which can be used to move the legend(s) in relation to the rose with the grasshopper "move" component.
        radRoseEndPts: The end points of the rose arrows.
        radRoseValues: The radiation values in Wh/m2 for each rose arrow.
"""

ghenv.Component.Name = "Ladybug_Radiation Rose"
ghenv.Component.NickName = 'radiationRose'
ghenv.Component.Message = 'VER 0.0.58\nDEC_05_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.58\nDEC_02_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino as rc
from System import Object
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

def main(north, genCumSkyResult, context, numOfArrows, surfaceTiltAngle, centerPoint, scale, arrowHeadScale, legendPar, showTotalOnly, bakeIt):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_mesh = sc.sticky["ladybug_Mesh"]()
        lb_runStudy_GH = sc.sticky["ladybug_RunAnalysis"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        
        conversionFac = lb_preparation.checkUnits()
        
        
        # north direction
        northAngle, northVector = lb_preparation.angle2north(north)
        
        # copy the custom code here
        # check the input data
        try:
            if genCumSkyResult[2][:11] == 'Sky Patches': checkData = True
            else: checkData = False
        except: checkData = False
        
        if checkData:
            # separate the data
            indexList, listInfo = lb_preparation.separateList(genCumSkyResult, lb_preparation.strToBeFound)
            
            if indexList[-1] == 456: patchesNormalVectors = list(lb_preparation.TregenzaPatchesNormalVectors)
            elif indexList[-1] == 1752: patchesNormalVectors = list(lb_preparation.getReinhartPatchesNormalVectors())
            
            # check num of arrows
            if not numOfArrows or int(numOfArrows) < 4: numOfArrows = 36
            else:
                try: numOfArrows = int(numOfArrows)
                except: numOfArrows = 36
            
            # define angles
            roseAngles = rs.frange(0,360,(360/numOfArrows));
            if round(roseAngles[-1]) == 360: roseAngles.remove(roseAngles[-1])
    
            # check the scale
            try:
                if float(scale)!=0:
                    try:scale = 0.5 * float(scale)/conversionFac
                    except: scale = 0.5/conversionFac
                else: scale = 0.5/conversionFac
            except: scale = 0.5/conversionFac
            
            # check vertical surface angle
            if surfaceTiltAngle == None: surfaceTiltAngle = 90
            else:
                try: surfaceTiltAngle = float(surfaceTiltAngle)
                except: surfaceTiltAngle = 90 
            
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
            customHeading = ['Total Radiation('+ listInfo[0][3]+')', 'Diffuse Radiation(' + listInfo[1][3] + ')', 'Direct Radiation(' + listInfo[2][3] + ')']
            
            def visualizeData(i, northAngle, northVector, results, arrows, legendTitle, legendPar, bakeIt, cenPt):
                
                movingVector = rc.Geometry.Vector3d(i * movingDist, 0, 0)
                
                overwriteScale = False
                if legendPar == []: overwriteScale = True
                elif legendPar[5] == None: overwriteScale = True
                
                lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar, False)
                if overwriteScale: legendScale = 0.9
                
                legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(results
                , lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold)
                
                titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo[i]], lb_visualization.BoundingBoxPar, legendScale, customHeading[i], False, legendFont, legendFontSize, legendBold)
                
                # print legendMax[i]
                compassCrvs, compassTextPts, compassText = lb_visualization. compassCircle(cenPt, northVector, 0.3 * scale * legendMax[i], roseAngles, 1.2*textSize, True)
                numberCrvs = lb_visualization.text2srf(compassText, compassTextPts, 'Times New Romans', textSize/1.7)
                compassCrvs = compassCrvs + lb_preparation.flattenList(numberCrvs)
                
                for crv in legendTextCrv + [compassCrvs]:
                    for c in crv:
                        c.Translate(movingVector) # move it to the right place
                
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
                arrowsJoined = rc.Geometry.Mesh();
                # mesh the patches
                meshParam = rc.Geometry.MeshingParameters.Smooth
                
                cenPtMoved = rc.Geometry.Point3d.Add(cenPt, movingVector)
                
                colForMesh = []; arrowsEndPts = []
                
                for arrow in arrows:
                    newMesh = arrow.DuplicateMesh()
                    if newMesh:
                        newMesh.Translate(movingVector) # move it to the right place
                        arrowsJoined.Append(newMesh) # append to the main mesh
                        endPt = newMesh.Vertices[2]
                        # if endPt.X < cenPtMoved.X:
                        endPt = rc.Geometry.Point3d.Add(endPt, -1.1*textSize* rc.Geometry.Vector3d.XAxis)
                        arrowsEndPts.append(endPt)
                        newMesh.Dispose() # delete the polysurface
                
                # color the meshed patches
                domeMeshed = lb_visualization.colorMesh(totalRadiationColors, arrowsJoined, False)
                
                placeName = listInfo[i][1]
                skyTypes = ['Total_Radiation' + placeName[:3], 'Diffuse_Radiation' + placeName[:3], 'Direct_Radiation' + placeName[:3]]
                
                if legendBasePoint == None:
                    nlegendBasePoint = lb_visualization.BoundingBoxPar[0]
                    movedLegendBasePoint = rc.Geometry.Point3d.Add(nlegendBasePoint, movingVector);
                else:
                    movedLegendBasePoint = rc.Geometry.Point3d.Add(legendBasePoint, movingVector);
                
                
                if bakeIt:
                    legendText.append(titleStr)
                    studyLayerName = 'RadiationRose'
                    
                    # check the study type
                    newLayerIndex, l = lb_visualization.setupLayers(skyTypes[i], 'LADYBUG', placeName, studyLayerName, False, False, 0, 0)
                    
                    lb_visualization.bakeObjects(newLayerIndex, domeMeshed, legendSrfs, legendText, textPt, textSize, legendFont, compassCrvs)
                
                return domeMeshed, [legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)], compassCrvs, arrowsEndPts, movedLegendBasePoint
            
            if not showTotalOnly: skyTypes = 3
            else: skyTypes = 1
            
            zVector = (0,0,1)
            # calculate the vectors
            # this is a copy-paste from the old version
            NVecTilted = rs.VectorRotate(zVector, -float(surfaceTiltAngle), (1,0,0))
            movingVectors = []; tiltedRoseVectors = []
            for angle in roseAngles:
                movingVectors.append(rs.VectorRotate(northVector, float(angle), (0,0,1)))
                tiltedRoseVectors.append(rs.VectorRotate(NVecTilted, float(angle), (0,0,1)))
            
            
            ## mesh the context geometires
            if len(context)!=0:
                ## clean the geometry and bring them to rhinoCommon separated as mesh and Brep
                contextMesh, contextBrep = lb_preparation.cleanAndCoerceList(context)
                
                ## mesh Brep
                contextMeshedBrep = lb_mesh.parallel_makeContextMesh(contextBrep)
                
                ## Flatten the list of surfaces
                contextMeshedBrep = lb_preparation.flattenList(contextMeshedBrep)
                contextSrfs = contextMesh + contextMeshedBrep
                
                # join the mesh
                if contextSrfs: contextSrfs = lb_mesh.joinMesh(contextSrfs)
                
            else: contextSrfs = []
            

            radResult = []
            for i in range(skyTypes):
                if centerPoint == None: cenPt = rc.Geometry.Point3d.Origin
                else: cenPt = centerPoint
                
                # rotating the vectors
                if northVector != rc.Geometry.Vector3d.YAxis:
                    rotatoionAngle= rc.Geometry.Vector3d.VectorAngle(northVector, rc.Geometry.Vector3d.YAxis, rc.Geometry.Plane.WorldXY)
                    for vectorCount, vec in enumerate(tiltedRoseVectors):
                        rcVector = rc.Geometry.Vector3d(vec)
                        rcVector.Rotate(rotatoionAngle, rc.Geometry.Vector3d.ZAxis)
                        patchesNormalVectors[vectorCount] = (rcVector.X, rcVector.Y, rcVector.Z)
                        
                    if contextSrfs!=[]: contextSrfs.Rotate(rotatoionAngle, rc.Geometry.Vector3d.ZAxis, cenPt)
                    
                radResult.append(lb_runStudy_GH.calRadRoseRes(tiltedRoseVectors, patchesNormalVectors, separatedLists[i], cenPt, contextSrfs))
            
            normLegend = False; res = [[], [], [], [], [], []];
            if not showTotalOnly:
                legendMax = [max(radResult[0]), max(radResult[1] + radResult[2]), max(radResult[1] + radResult[2])]
                legendMin = [0,0,0]
            else:
                legendMax = [max(radResult[0])]
                legendMin = [0]
            
            for i in range(skyTypes):
                # fix the bake
                try:
                    if legendPar[1] is None or normLegend:
                        legendPar[1] = legendMax[i]
                        legendPar[0] = legendMin[i]
                        normLegend = True
                except:
                    # make an initial legend parameter to replace the max
                    legendPar = [None,None,None,[],None, None, None, None]
                    legendPar[1] = legendMax[i]
                    legendPar[0] = legendMin[i]
                    normLegend = True
                
                internalScale = 0.3
                # generate arrows
                cenPt = lb_preparation.getCenPt(centerPoint)
                arrows = lb_preparation.genRadRoseArrows(movingVectors, radResult[i], cenPt, float(scale), internalScale, arrowHeadScale)
                
                tempCircle = rc.Geometry.Circle(cenPt, 1.2 * internalScale * float(scale)*max(radResult[i])).ToNurbsCurve()
                # calculate the bounding box for the skyDome
                if i == 0:
                    try:
                        lb_visualization.calculateBB([tempCircle]) #arrows)
                        movingDist = 1.5 * lb_visualization.BoundingBoxPar[1] # moving distance for radiation rose
                    except:
                        print "Input Radiation values are all 0"
                        w = gh.GH_RuntimeMessageLevel.Warning
                        ghenv.Component.AddRuntimeMessage(w, "Input Radiation values are all 0")
                        return -1
                
                arrowsColored, leg, compassCrvs, arrowsEndPts, legendBsePt= visualizeData(i, northAngle, northVector, radResult[i], arrows, legendTitles[i], legendPar, bakeIt, cenPt)
                
                res[0].append(arrowsColored)
                res[1].append(leg)
                res[2].append(compassCrvs)
                res[3].append(legendBsePt)
                res[4].append(arrowsEndPts)
                strResult = []
                [strResult.append("%.2f"%num) for num in radResult[i]]
                res[5].append(strResult)
            # remove the sky polysurfaces
            for arrow in arrows: arrow.Dispose()
            
            return res
        else:
            print "Please provide valid selctedSkyMtx!"
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Please provide valid selctedSkyMtx!")
            return -1
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return -1


if _runIt:
    result = main(north_, _selectedSkyMtx, context_, _numOfArrows_, _surfaceTiltAngle_, _centerPoint_,
                   _scale_, _arrowHeadScale_, legendPar_, showTotalOnly_, bakeIt_)
    
    if result!= -1:
        legend = DataTree[Object]()
        radiationArrowsMesh = DataTree[Object]()
        radRoseBaseCrvs = DataTree[Object]()
        legendBasePts = DataTree[Object]()
        radRoseEndPts = DataTree[Object]()
        radRoseValues = DataTree[Object]()
        for i, leg in enumerate(result[1]):
            p = GH_Path(i)
            radiationArrowsMesh.Add(result[0][i], p)
            radRoseBaseCrvs.AddRange(result[2][i], p)
            legend.Add(leg[0], p)
            legend.AddRange(leg[1], p)
            legendBasePts.Add(result[3][i], p)
            radRoseEndPts.AddRange(result[4][i], p)
            radRoseValues.AddRange(result[5][i], p)
        ghenv.Component.Params.Output[4].Hidden = True       
        ghenv.Component.Params.Output[5].Hidden = True
else: print "Set _runIt to True!"

