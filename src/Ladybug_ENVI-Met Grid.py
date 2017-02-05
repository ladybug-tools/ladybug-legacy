# ENVI-Met Grid
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
Use this component to visualize ENVI-Met v4.0 data. Connect "resultFileAddress" which comes from ENVI-Met reader.
-
Component mainly based on:
https://www.researchgate.net/publication/281031049_Outdoor_Comfort_the_ENVI-BUG_tool_to_evaluate_PMV_values_point_by_point
-
Provided by Ladybug 0.0.63
    
    Args:
        _resultFileAddress: Output comes from "ENVI-Met Reader".
        _selXY_: Connect an integer to generate a XY section. Plug a panel to "readMe!" for more info.
        -
        Default value is 0.
        selXZ_: Connect an integer to generate a XZ section. Plug a panel to "readMe!" for more info.
        selYZ_: Connect an integer to generate a YZ section. Plug a panel to "readMe!" for more info.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        ------------------: (...)
        _runIt: Set to "True" to run the component and perform ENVI-Met data visualization.
    Returns:
        readMe!: ...
        analysisMesh: Analysis grid of ENVI-Met (XY plane, ZX plane and ZY plane).
        analysisResult: Values corrisponding to each analysis Grid.
        testPoints: Test points on grids.
        ----------------: (...)
        legend: Legend geometry of ENVI-Met Grid.
        titleLabel: Title geometry with information about project name, location, and date.
"""

ghenv.Component.Name = "Ladybug_ENVI-Met Grid"
ghenv.Component.NickName = 'ENVI-MetGrid'
ghenv.Component.Message = 'VER 0.0.63\nFEB_02_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Rhino as rc
import scriptcontext as sc
import System
import clr
clr.AddReference("Grasshopper")
import Grasshopper.Kernel as gh
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree


def checkInputs(resultFileAddress):
    if resultFileAddress == None:
        return False
    elif resultFileAddress:
        return True


def accumulate(listElm):
    total = 0
    for x in listElm:
        total +=x
        yield total


def createTitleLegend(geometry, legendValues, legendPar, titleLabelText, legendTitle):
    # this function is based on djordje example
    lb_visualization.calculateBB([geometry])
    if len(legendPar) == 0:
        lowB = "min"; highB = "max"; numSeg = None; customColors = []; legendBasePt = None; legendScale = 1; legendFont = "Verdana"; legendFontSize = None; legendBold = None; decimalPlaces = 2; removeLessThan = False
        legendPar = [lowB, highB, numSeg, customColors, legendBasePt, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan]
        if legendBasePt == None:
            legendBasePt = lb_visualization.BoundingBoxPar[0]
    lowB, highB, numSeg, customColors, legendBasePt, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar, False)
    
    # title
    titleFontSize = ((lb_visualization.BoundingBoxPar[2]/10)/3) * legendScale * 1.2
    titleLabelOrigin = lb_visualization.BoundingBoxPar[5]
    titleLabelOrigin.Y = titleLabelOrigin.Y - lb_visualization.BoundingBoxPar[2]/15
    
    titleLabelMeshes = lb_visualization.text2srf([titleLabelText], [titleLabelOrigin], legendFont, titleFontSize*1.2, legendBold, None, 6)[0]
    titleLabelMesh = rc.Geometry.Mesh()
    for mesh in titleLabelMeshes:
        titleLabelMesh.Append(mesh)
    
    # legend
    if legendBasePt == None:
        legendBasePt = lb_visualization.BoundingBoxPar[0]
    legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(legendValues, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePt, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan)
    
    # generate legend colors
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    
    # color legend surfaces
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    legendMeshes = [legendSrfs] + lb_preparation.flattenList(legendTextCrv)
    
    legendMesh = rc.Geometry.Mesh()
    for mesh in legendMeshes:
        if isinstance(mesh, rc.Geometry.Mesh):
            legendMesh.Append(mesh)
    
    return titleLabelMesh, legendMesh, legendBasePt


def createMesh(colors, surfaceList):
    # set mesh parameters
    meshParam = rc.Geometry.MeshingParameters.Default
    meshParam.GridMaxCount = 1
    meshParam.SimplePlanes = True
    meshParam.GridAmplification = 1.5
    
    # from srf to mesh
    all_mesh = []
    for srf in surfaceList:
        mesh = rc.Geometry.Mesh.CreateFromBrep(srf, meshParam)
        all_mesh.extend(mesh)
    # join mesh
    analysisMesh = rc.Geometry.Mesh()
    for m in all_mesh: analysisMesh.Append(m)
    
    # make a monotonemesh
    analysisMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.White)
    #color the mesh based on the results
    for srfCount in range (analysisMesh.Faces.Count):
        analysisMesh.VertexColors[analysisMesh.Faces[srfCount].A] = colors[srfCount]
        analysisMesh.VertexColors[analysisMesh.Faces[srfCount].B] = colors[srfCount]
        analysisMesh.VertexColors[analysisMesh.Faces[srfCount].C] = colors[srfCount]
        analysisMesh.VertexColors[analysisMesh.Faces[srfCount].D] = colors[srfCount]
    
    return analysisMesh


def main():
    
    if _selXY_ == None: selZ = 0
    else: selZ = _selXY_
    
    def xzAndyzSection(Matrix, sel, xdim, ydim, zdim, accumulateDim, currentDim, zdimA, flag):
        
        values = []
        for layer in Matrix:
            for i, rowOrColumn in enumerate(layer):
                if i == sel:
                    values.append(rowOrColumn)
        
        points = []
        surfaces = []
        analysisResult = []
        for indexZ, vList in enumerate(values):
            for index, value in enumerate(vList):
                if flag:
                    coord = ((index+1)*xdim-(xdim/2), currentDim, (zdimA[indexZ]-(zdim[indexZ]/2)))
                    point = rc.Geometry.Point3d(coord[0], coord[1], coord[2])
                    width, height = rc.Geometry.Interval(-zdim[indexZ]/2, zdim[indexZ]/2), rc.Geometry.Interval(-xdim/2, xdim/2)
                    rect = rc.Geometry.Rectangle3d(rc.Geometry.Plane(point, rc.Geometry.Vector3d.YAxis), width, height)
                else:
                    coord = (currentDim, (index+1)*ydim-(ydim/2), (zdimA[indexZ]-(zdim[indexZ]/2)))
                    point = rc.Geometry.Point3d(coord[0], coord[1], coord[2])
                    width, height = rc.Geometry.Interval(-zdim[indexZ]/2, zdim[indexZ]/2), rc.Geometry.Interval(-ydim/2, ydim/2)
                    rect = rc.Geometry.Rectangle3d(rc.Geometry.Plane(point, rc.Geometry.Vector3d.XAxis), height, width)
                
                points.append(point)
                
                surf = rc.Geometry.Brep.CreatePlanarBreps(rect.ToNurbsCurve())
                surfaces.extend(surf)
                if value == '-999.0':
                    value = 50
                analysisResult.append(float(value))
        
        return surfaces, analysisResult, points
    
    
    with open(_resultFileAddress, 'r') as f:
        completeList = f.read().split('\n')
        
        # soil data (just XY planes)
        checkSoil = _resultFileAddress.split('\\')
        
        # from xml
        legendTitle = completeList[0]
        titleLabelText = completeList[1]
        numCell = map(int,(completeList[2].replace(' ', '').split(',')))
        dimensionRaw = completeList[3:6]
        numberRaw = completeList[6:]
        print("gridSize: {0}(X), {1}(Y), {2}(Z)".format(numCell[0],numCell[1],numCell[2]))
        
        dimension = [map(float, dim.replace(' ', '').split(',')) for dim in dimensionRaw]
        
        xdim = dimension[0][0] / unitConversionFactor
        ydim = dimension[1][0] / unitConversionFactor
        zdim = [element/unitConversionFactor for element in dimension[2]]
        zdimA = list(accumulate(zdim))
        try:
            currentZ = zdimA[selZ] - zdim[selZ]/2
            
            n = numCell[0] * numCell[1]
            chunkLayers = [numberRaw[i:i+n] for i in range(0, len(numberRaw), n)]
            
            MatrixX = []
            MatrixY = []
            for l in chunkLayers:
                tx = []
                for i in range(0, numCell[0]*numCell[1], numCell[0]):
                    tx.append(l[i:i+numCell[0]])
                    ty = [list(x) for x in zip(*tx)]
                MatrixX.append(tx)
                MatrixY.append(ty)
            
            chunkRow = MatrixX[selZ]
            
            pointsZ = []
            surfacesZ = []
            analysisResultZ = []
            for indexY, vList in enumerate(chunkRow):
                for indexX, value in enumerate(vList):
                    coord = ((indexX+1)*xdim-(xdim/2), (indexY+1)*ydim-(ydim/2), currentZ)
                    
                    point = rc.Geometry.Point3d(coord[0], coord[1], coord[2])
                    width, height = rc.Geometry.Interval(-xdim/2, xdim/2), rc.Geometry.Interval(-ydim/2, ydim/2)
                    rect = rc.Geometry.Rectangle3d(rc.Geometry.Plane(point, rc.Geometry.Vector3d.ZAxis), width, height)
                    surf = rc.Geometry.Brep.CreatePlanarBreps(rect.ToNurbsCurve())
                    
                    pointsZ.append(point)
                    surfacesZ.extend(surf)
                    if value == '-999.0':
                        value = 50
                    analysisResultZ.append(float(value))
        except IndexError:
            print("gridSize has {2} XY Planes max!".format(numCell[0],numCell[1],numCell[2]))
            return -1
        
        # geometry
        if selXZ_ != None and not 'soil' in checkSoil:
            xdim = dimension[0][0] / unitConversionFactor
            ydim = [element/unitConversionFactor for element in dimension[1]]
            zdim = [element/unitConversionFactor for element in dimension[2]]
            ydimA = list(accumulate(ydim))
            try:
                currentY = ydimA[selXZ_] - ydim[selXZ_]/2
                surfacesX, analysisResultX, pointsX = xzAndyzSection(MatrixX, selXZ_, xdim, ydim, zdim, ydimA, currentY, zdimA, True)
            except IndexError:
                print("gridSize has {1} XZ Planes max!".format(numCell[0],numCell[1],numCell[2]))
                return -1
        else: surfacesX, analysisResultX, pointsX = [], [], []
        
        if selYZ_ != None and not 'soil' in checkSoil:
            xdim = [element/unitConversionFactor for element in dimension[0]]
            ydim = dimension[1][0] / unitConversionFactor
            zdim = [element/unitConversionFactor for element in dimension[2]]
            xdimA = list(accumulate(xdim))
            try:
                currentX = xdimA[selYZ_] - xdim[selYZ_]/2
                surfacesY, analysisResultY, pointsY = xzAndyzSection(MatrixY, selYZ_, xdim, ydim, zdim, xdimA ,currentX, zdimA, False)
            except IndexError:
                print("gridSize has {0} YZ Planes max!".format(numCell[0],numCell[1],numCell[2]))
                return -1
        else: surfacesY, analysisResultY, pointsY = [], [], []
        
        # bounds
        lowB, highB, numSeg, customColors, legendBasePt, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar_, False)
            
        if None in [selXZ_, selYZ_]:
            if selXZ_ != None:
                if lowB == 'min': lowB = min(analysisResultZ+analysisResultX)
                if highB == 'max': highB = max(analysisResultZ+analysisResultX)
                
            elif selYZ_ != None:
                if lowB == 'min': lowB = min(analysisResultZ+analysisResultY) 
                if highB == 'max': highB = max(analysisResultZ+analysisResultY)
                
            else:
                if lowB == 'min': lowB = min(analysisResultZ)
                if highB == 'max': highB = max(analysisResultZ)
        else:
            if lowB == 'min': lowB = min(analysisResultZ+analysisResultX+analysisResultY)
            if highB == 'max': highB = max(analysisResultZ+analysisResultX+analysisResultY)
        
        
        colorsX = lb_visualization.gradientColor(analysisResultX, lowB, highB, customColors)
        if surfacesX:
            analysisMeshX = createMesh(colorsX, surfacesX)
            print("XZ plane at {} meters from WorldXY origin.".format(currentY))
        else: analysisMeshX = None
        colorsY = lb_visualization.gradientColor(analysisResultY, lowB, highB, customColors)
        if surfacesY:
            analysisMeshY = createMesh(colorsY, surfacesY)
            print("YZ plane at {} meters from WorldXY origin.".format(currentX))
        else: analysisMeshY = None
        
        colorsZ = lb_visualization.gradientColor(analysisResultZ, lowB, highB, customColors)
        analysisMeshZ = createMesh(colorsZ, surfacesZ)
        print("XY plane at {} meters from WorldXY origin.".format(currentZ))
        
        # results
        analysisMesh = [analysisMeshX, analysisMeshY, analysisMeshZ]
        analysisResult= [analysisResultX, analysisResultY, analysisResultZ]
        testPoints = [pointsX, pointsY, pointsZ]
        
        analysisMesh = [m for m in analysisMesh if m != None]
        analysisResult = [l for l in analysisResult if l != []]
        testPoints = [l for l in testPoints if l != []]
        
        legendValues = [item for nl in analysisResult for item in nl]
        titleLabel, legend, legendBasePt = createTitleLegend(analysisMeshZ, legendValues, legendPar_, titleLabelText, legendTitle)
        
        
        analysisMeshTree, analysisResultTree, testPointsTree = DataTree[System.Object](), DataTree[System.Object](), DataTree[System.Object]()
        for i, m in enumerate(analysisMesh):
            path = GH_Path(0, i)
            analysisMeshTree.Add(m, path)
        for i, l in enumerate(analysisResult):
            path = GH_Path(0, i)
            analysisResultTree.AddRange(l, path)
        for i, l in enumerate(testPoints):
            path = GH_Path(0, i)
            testPointsTree.AddRange(l, path)
        
        return analysisMeshTree, analysisResultTree, legend, titleLabel, testPointsTree


initCheck = False
if sc.sticky.has_key('ladybug_release'):
    initCheck = True
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = True
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    lb_meshpreparation = sc.sticky["ladybug_Mesh"]()
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")


check = checkInputs(_resultFileAddress)

if check and initCheck:
    if _runIt:
        unitConversionFactor = lb_preparation.checkUnits()
        result = main()
        if result != -1:
            analysisMesh, analysisResult, legend, titleLabel, testPoints = result
        else:
            print("Something went wrong!")
    else: print("Set runIt to True.")
else:
    pass
    print("Please provide all inputs.")

ghenv.Component.Params.Output[3].Hidden = True