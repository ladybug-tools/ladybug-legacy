# ENVI-Met Spaces
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
Use this component to generate ENVI-Met v4.0 3D geometry models.
-
Analyze parametric models with ENVI-Met!
-
Save the model in the ENVI_MET Workspace, set the simulation file with ENVI_MET ConfigWizard and run the simulation.
N.B. It can write files with equidistant grid only. If you want to visualize INX file with ENVI_MET SPACES you need to use "Open 3D view".
-
Provided by Ladybug 0.0.64
    
    Args:
        _location: The output from the importEPW or constructLocation component.  This is essentially a list of text summarizing a location on the earth.
        _north_: Input a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _numX_: Number of grid cells in base plane x direction. Default value is 20.
        _numY_: Number of grid cells in base plane y direction. Default value is 20.
        _numZ_: Number of grid cells in base plane z direction. Default value is 20.
        _dimX_: Size of grid cell in meter. Default value is 3.0.
        _dimY_: Size of grid cell in meter. Default value is 3.0.
        _dimZ_: Size of grid cell in meter. Default value is 3.0.
        --------------------: (...)
        baseSoilmaterial_: Connect a profileId that you want to use as base material of soil. If no id is provided it will be 'LO'.
        numNestingGrid_: Connect an integer to set nesting grid around main area. If no input is connected this will be 3.
        nestingGridSoil_: Connect two envimet ID soils to set soil profile for nesting grids. Use "LB ENVI-Met Read Library" for that.
        -
        If no input is connected this input will be ('LO', 'LO').
        --------------------: (...)
        _envimetBuildings: Output which comes from "LB ENVI-Met Building Terrain".
        envimetTerrain_: Output which comes from "LB ENVI-Met Building Terrain".
        envimetPlants_: Output which comes from "LB ENVI-Met Soil Plant Source".
        envimetSoils_: Output which comes from "LB ENVI-Met Soil Plant Source".
        envimetSources_: Output which comes from "LB ENVI-Met Soil Plant Source".
        --------------------: (...)
        _folder: The folder into which you would like to write the envimet model. This should be a complete file path to the folder.
        fileName_: The file name that you would like the envimet model to be saved as. Default name is "LBenvimet".
        _runIt: Set to "True" to run the component and generate the envimet model.
    Returns:
        readMe!: ...
        points: Preview of 3D grid of points.
        INXfileAddress: The file path of the inx result file that has been generated on your machine.
"""

ghenv.Component.Name = "Ladybug_ENVI-Met Spaces"
ghenv.Component.NickName = 'ENVI-MetSpaces'
ghenv.Component.Message = 'VER 0.0.64\nFEB_26_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import os
import re
import datetime
import collections
import Rhino as rc
import scriptcontext as sc
from xml.dom import minidom
import Grasshopper.Kernel as gh


def checkInputs(location, envimetBuildings, folder):
    if location == None or envimetBuildings == [] or envimetBuildings == [None] or folder == None:
        return False
    elif location and envimetBuildings and folder:
        return True


def locationDataFunction(location):
    locationStr = location.split('\n')
    newLocStr = ""
    #clean the idf file
    for line in locationStr:
        if '!' in line:
            line = line.split('!')[0]
            newLocStr  = newLocStr + line.replace(" ", "")
        else:
            newLocStr  = newLocStr + line
    newLocStr = newLocStr.replace(';', "")
    site, locationName, latitude, longitude, timeZone, elevation = newLocStr.split(',')
    
    if float(timeZone) > 0: timeZone = 'UTC' + '+' +str(int(float(timeZone)))
    elif float(timeZone) < 0: timeZone = 'UTC' + '-' +str(int(float(timeZone)))
    else: timeZone = 'GMT'
    
    return locationName, '{:f}'.format(float(latitude)), '{:f}'.format(float(longitude)), timeZone


def matrixConstruction(buildings, numX, numY, numZ, dimX, dimY, dimZ, matWall, matRoof):
    
    buildingFlagAndNr = []
    nestedLayers = []
    
    for index, building in enumerate(buildings):
        layers = []
        for k in range(numZ+5):
            columns = []
            for j in range(numY+1):
                rows = []
                for i in range(numX+1):
                    if k<5:
                        point = rc.Geometry.Point3d(i*dimX+dimX/2, j*dimY+dimY/2, k*dimZ/5+dimZ/10)
                    else:
                        point = rc.Geometry.Point3d(i*dimX+dimX/2, j*dimY+dimY/2, (k-4)*dimZ+dimZ/2)
                    if building.IsPointInside(point, sc.doc.ModelAbsoluteTolerance*10, False):
                        bNr = ','.join([str(i),str(j),str(k),'1',str(index+1)])
                        id = index+1
                        
                        buildingFlagAndNr.append(bNr)
                        rows.append(id)
                    else:
                        rows.append(0)
                  
                columns.append(rows)
            layers.append(columns)  
        nestedLayers.append(layers)
    
    buildingFlagAndNrMatrix = '\n'.join(buildingFlagAndNr)
    
    # merge Matrix
    oneMatrix = []
    for k in zip(*nestedLayers):
        columns = []
        for y in zip(*k):
            rows = []
            for x in zip(*y):
                total = sum(x)
                # overlap issue ;)
                if total > len(buildings):
                    total = 0
                rows.append(total)
            columns.append(rows)
        oneMatrix.append(columns)
    
    # spare matrix
    WallDB = []
    
    for k, layer in enumerate(oneMatrix):
        for j, column in enumerate(layer):
            for i, row in enumerate(column):
                
                if row != 0 and oneMatrix[k][j][i-1] == 0 and oneMatrix[k][j-1][i] == 0 and oneMatrix[k-1][j][i] == 0:
                    index = int(row)-1
                    WallDB.append(','.join([str(i),str(j),str(k),matWall[index],matWall[index],matRoof[index]]))
                elif row != 0 and oneMatrix[k][j][i-1] == 0 and oneMatrix[k][j-1][i] != 0 and oneMatrix[k-1][j][i] == 0:
                    index = int(row)-1
                    WallDB.append(','.join([str(i),str(j),str(k),matWall[index],'',matRoof[index]]))
                elif row != 0 and oneMatrix[k][j][i-1] != 0 and oneMatrix[k][j-1][i] == 0 and oneMatrix[k-1][j][i] == 0:
                    index = int(row)-1
                    WallDB.append(','.join([str(i),str(j),str(k),'',matWall[index],matRoof[index]]))
                
                elif row != 0 and oneMatrix[k][j][i-1] == 0 and oneMatrix[k][j-1][i] == 0 and oneMatrix[k-1][j][i] != 0:
                    index = int(row)-1
                    WallDB.append(','.join([str(i),str(j),str(k),matWall[index],matWall[index],'']))
                elif row != 0 and oneMatrix[k][j][i-1] == 0 and oneMatrix[k][j-1][i] != 0 and oneMatrix[k-1][j][i] != 0:
                    index = int(row)-1
                    WallDB.append(','.join([str(i),str(j),str(k),matWall[index],'','']))
                elif row != 0 and oneMatrix[k][j][i-1] != 0 and oneMatrix[k][j-1][i] == 0 and oneMatrix[k-1][j][i] != 0:
                    index = int(row)-1
                    WallDB.append(','.join([str(i),str(j),str(k),'',matWall[index],'']))
                elif row != 0 and oneMatrix[k][j][i-1] != 0 and oneMatrix[k][j-1][i] != 0 and oneMatrix[k-1][j][i] == 0:
                    index = int(row)-1
                    WallDB.append(','.join([str(i),str(j),str(k),'','',matRoof[index]]))
                
                # empty cells
                elif row == 0 and oneMatrix[k][j][i-1] != 0 and oneMatrix[k][j-1][i] == 0 and oneMatrix[k-1][j][i] == 0:
                    index = int(oneMatrix[k][j][i-1])-1
                    WallDB.append(','.join([str(i),str(j),str(k),matWall[index],'','']))
                elif row == 0 and oneMatrix[k][j][i-1] == 0 and oneMatrix[k][j-1][i] != 0 and oneMatrix[k-1][j][i] == 0:
                    index = int(oneMatrix[k][j-1][i])-1
                    WallDB.append(','.join([str(i),str(j),str(k),'',matWall[index],'']))
                elif row == 0 and oneMatrix[k][j][i-1] == 0 and oneMatrix[k][j-1][i] == 0 and oneMatrix[k-1][j][i] != 0:
                    index = int(oneMatrix[k-1][j][i])-1
                    WallDB.append(','.join([str(i),str(j),str(k),'','',matRoof[index]]))
                
                elif row == 0 and oneMatrix[k][j][i-1] != 0 and oneMatrix[k][j-1][i] != 0 and oneMatrix[k-1][j][i] == 0:
                    index = int(oneMatrix[k][j-1][i])-1
                    WallDB.append(','.join([str(i),str(j),str(k),matWall[index],matWall[index],'']))
                elif row == 0 and oneMatrix[k][j][i-1] != 0 and oneMatrix[k][j-1][i] == 0 and oneMatrix[k-1][j][i] != 0:
                    indexW = int(oneMatrix[k][j][i-1])-1
                    indexR = int(oneMatrix[k-1][j][i])-1
                    WallDB.append(','.join([str(i),str(j),str(k),matWall[indexW],'',matRoof[indexR]]))
                elif row == 0 and oneMatrix[k][j][i-1] == 0 and oneMatrix[k][j-1][i] != 0 and oneMatrix[k-1][j][i] != 0:
                    indexW = int(oneMatrix[k][j-1][i])-1
                    indexR = int(oneMatrix[k-1][j][i])-1
                    WallDB.append(','.join([str(i),str(j),str(k),'',matWall[indexW],matRoof[indexR]]))
                elif row == 0 and oneMatrix[k][j][i-1] != 0 and oneMatrix[k][j-1][i] != 0 and oneMatrix[k-1][j][i] != 0:
                    indexW = int(oneMatrix[k][j-1][i])-1
                    indexR = int(oneMatrix[k-1][j][i])-1
                    WallDB.append(','.join([str(i),str(j),str(k),matWall[indexW],matWall[indexW],matRoof[indexR]]))
    
    WallDBMatrix = '\n'.join(WallDB)
    
    return buildingFlagAndNrMatrix, WallDBMatrix, oneMatrix


def twoDimensionalBuilding(oneMatrix):
    buildingNr = []
    
    for k in zip(*oneMatrix):
        columns = []
        emptyColumns = []
        for y in zip(*k):
            index = sum(set(y))
            columns.append(index)
        
        linebuildingNr = ','.join(map(str, columns))
        buildingNr.append(linebuildingNr)
    
    buildingNrMatrix = '\n'.join(reversed(buildingNr))
    
    return buildingNrMatrix


def checkDistanceFromBorder(points, buildings, dimX, dimY, dimZ, numZ, maxHeight):
    
    def messageForUser():
        w = gh.GH_RuntimeMessageLevel.Warning
        message = "There is not enough space between the border and Building n{0}."
        ghenv.Component.AddRuntimeMessage(w, message.format(index))
        return False
    
    ptMin = rc.Geometry.Point3d(min(points).X, min(points).Y, 0)
    ptMax = rc.Geometry.Point3d(max(points).X, max(points).Y, 0)
    border = rc.Geometry.Rectangle3d(rc.Geometry.Plane.WorldXY, ptMin, ptMax).ToNurbsCurve()
    
    # let's check!
    cornerStyle = rc.Geometry.CurveOffsetCornerStyle.Sharp
    firstCheck = rc.Geometry.Rectangle3d(rc.Geometry.Plane.WorldXY, rc.Geometry.Point3d(ptMin.X+dimX*2, ptMin.Y+dimY*2, 0), rc.Geometry.Point3d(ptMax.X-dimX*2, ptMax.Y-dimY*2, 0)).ToNurbsCurve()
    
    for index, building in enumerate(buildings):
        bbox = building.GetBoundingBox(True).ToBrep()
        xprj = rc.Geometry.Transform.PlanarProjection(rc.Geometry.Plane.WorldXY)
        bbox.Transform(xprj)
        
        # offsets for each building
        secondCheck = border.Offset(rc.Geometry.Plane.WorldXY, -maxHeight[index], sc.doc.ModelAbsoluteTolerance, cornerStyle)[0]
        
        for v in bbox.Vertices:
            if maxHeight[index] > dimZ*numZ - dimZ*3:
                return messageForUser()
            elif secondCheck.Contains(v.Location, rc.Geometry.Plane.WorldXY) == rc.Geometry.PointContainment.Outside:
                return messageForUser()
                if firstCheck.Contains(v.Location, rc.Geometry.Plane.WorldXY) == rc.Geometry.PointContainment.Outside:
                    return messageForUser()
    return True


def digitalElevationModel3D(terrain, numX, numY, numZ, dimX, dimY, dimZ):
    
    terrainflag = []
    
    for k in range(numZ+5):
        columns = []
        for j in range(numY+1):
            rows = []
            for i in range(numX+1):
                if k<5:
                    point = rc.Geometry.Point3d(i*dimX+dimX/2, j*dimY+dimY/2, k*dimZ/5+dimZ/10)
                else:
                    point = rc.Geometry.Point3d(i*dimX+dimX/2, j*dimY+dimY/2, (k-4)*dimZ+dimZ/2)
                if terrain.IsPointInside(point, sc.doc.ModelAbsoluteTolerance*10, False):
                    tN = ','.join([str(i),str(j),str(k),str('1.00000')])
                    
                    terrainflag.append(tN)
    
    terrainFlagMatrix = '\n'.join(terrainflag)
    
    return terrainFlagMatrix


def separateData(data):
    # separate plants
    data2D = [e for e in data if e[2] == 0]
    data3D = [e for e in data if e[2] == 1]
    id = [e[1] for e in data if e[2] == 0]
    
    return data2D, data3D, id


def emptyMatrix(numX, numY):
    matrix = []
    for j in range(numY+1):
        row = []
        for i in range(numX+1):
            row.append('')
        matrix.append(','.join(row))
    matrix = '\n'.join(matrix)
    
    return matrix


def matrix2DGen(dataList, numX, numY, dimX, dimY, obj, altObj):
    
    nestedMatrix = []
    for index, d in enumerate(dataList):
        matrix = []
        for j in range(numY+1):
            row = []
            for i in range(numX+1):
                point = rc.Geometry.Point3d(i*dimX+dimX/2, j*dimY+dimY/2, 0)
                line = rc.Geometry.Line(point, rc.Geometry.Vector3d.ZAxis, dimX*2)
                if rc.Geometry.Intersect.Intersection.CurveBrep(line.ToNurbsCurve(), d[0], sc.doc.ModelAbsoluteTolerance)[2]:
                    row.append(str(obj[index]))
                else:
                    row.append('')
            matrix.append(row)
        nestedMatrix.append(matrix)
    
    # merge all!
    mergeMatrix = []
    
    for m in zip(*nestedMatrix):
        row = []
        for l in zip(*m):
            counter = collections.Counter(l)
            if len(''.join(l)) == 4:
                row.append(''.join(l)[:-2])
            elif len(counter.values()) != 1 and '' in l:
                print ''.join(l)
                row.append(''.join(l))
            elif len(''.join(l)) == 2:
                row.append(''.join(l))
            else:
                row.append(altObj)
        mergeMatrix.append(row)
    
    
    stringMatrix = []
    for line in mergeMatrix:
        lineStr = ','.join(map(str, line))
        stringMatrix.append(lineStr)
    
    finalMatrix = '\n'.join(reversed(stringMatrix))
    
    return finalMatrix


def threeDimensionalPlants(dataList, numX, numY, dimX, dimY):
    nestedMatrix = []
    for index, d in enumerate(dataList):
        curves = [c for c in d[0].DuplicateEdgeCurves()]
        closedCrv = [crv for crv in rc.Geometry.Curve.JoinCurves(curves)][0]
        
        for j in range(numY+1):
            for i in range(numX+1):
                point = rc.Geometry.Point3d(i*dimX+dimX/2, j*dimY+dimY/2, 0)
                if rc.Geometry.Curve.Contains(closedCrv, point, rc.Geometry.Plane.WorldXY, sc.doc.ModelAbsoluteTolerance) == rc.Geometry.PointContainment.Inside:
                    idAndDescription = d[1].split(',')
                    nestedMatrix.append([str(i+1),str(j+1),'0', idAndDescription[0], idAndDescription[1], '0'])
    return nestedMatrix


def generateDem2D(numX, numY, dimX, dimY, terrain):
    
    def findMaxHeight(terrain):
        bbox = terrain.GetBoundingBox(True)
        maxHeight = bbox.Max.Z
        return maxHeight
    
    altitude = findMaxHeight(terrain)
    
    terrainPattern = []
    
    for y in range(numY+1):
        rowsHeight = []
        rowsBottom = []
        for x in range(numX+1):
            line = rc.Geometry.Line(rc.Geometry.Point3d(x*dimX/2, y*dimY/2, 0), rc.Geometry.Vector3d.ZAxis, altitude*2)
            intersection = rc.Geometry.Intersect.Intersection.CurveBrep(line.ToNurbsCurve(), terrain, sc.doc.ModelAbsoluteTolerance)[2]
            if intersection:
                heightData = sorted(intersection)
                rowsHeight.append(str(int(round(max([h.Z for h in heightData]),0))))
            else:
                rowsHeight.append('0')
            line = ','.join(map(str, rowsHeight))
        terrainPattern.append(line)
    
    demPattern = '\n'.join(reversed(terrainPattern))
    
    return demPattern


def grid(numX, numY, numZ, dimX, dimY, dimZ):
    
    def prettyGridVisualization(points):
        points = [p for p in points if p.X == (numX*dimX)+dimX/2 or p.Y == (numY*dimY)+dimY/2 or p.Z == dimZ/10]
        return points
    
    points = []
    for k in range(numZ+5):
        for j in range(numY+1):
            for i in range(numX+1):
                if k<5:
                    point = rc.Geometry.Point3d(i*dimX+dimX/2, j*dimY+dimY/2, k*dimZ/5+dimZ/10)
                else:
                    point = rc.Geometry.Point3d(i*dimX+dimX/2, j*dimY+dimY/2, (k-4)*dimZ+dimZ/2)
                points.append(point)
    
    points = prettyGridVisualization(points)
    
    return points


def writeINX(fullPath, Xcells, Ycells, Zcells, Xdim, Ydim, Zdim, numNesting, matNesting, location, north, defaultMat, buildingEmptyMatrix, buildingNrMatrix, terrainFlagMatrix, buildingFlagAndNrMatrix, WallDBMatrix, ID_plants1DMatrix, threeDplants, soils2DMatrix, ID_sourcesMatrix, emptySequence, demPattern, telescopingGrid = 0, verticalStretch = 0.0, startStretch = 0.0, has3DModel = 1, isFull3DDesign = 1):
    
    # location data
    locationName, latitude, longitude, timeZone = locationDataFunction(location)
    
    
    # set grid.. It is important for future development
    if telescopingGrid == 1:
        useSplitting = 0 
    else:
        useSplitting = 1
        verticalStretch = 0     
        startStretch = 0 
        grids3DK = Zcells + 4
    
    
    def appendMultipleChild(childChild, childRoot):         
        elements = []
        for key, element in childChild.items():
            xmlElement = root.createElement(key)
            xmlElement.appendChild(root.createTextNode(element))
            elements.append(xmlElement)        
        for node in elements:
            childRoot.childNodes.append(node)
    
    
    def appendMultipleChildWithAttribute(childChild, childRoot, nameAttribute, dataAttribute): 
        elements = []
        for key, element in childChild.items():
            xmlElement = root.createElement(key)
            for name, attr in zip(nameAttribute, dataAttribute):
                xmlElement.setAttribute(name, attr)
            xmlElement.appendChild(root.createTextNode(element))
            elements.append(xmlElement)        
        for node in elements:
            childRoot.childNodes.append(node)
    
    # date
    timeTxt = datetime.datetime.now()
    timeTxt = str(timeTxt)[:-7]
    
    root = minidom.Document()
    
    # create an xml document, ENVI-MET_Datafile
    xml = root.createElement('ENVI-MET_Datafile')
    root.appendChild(xml)
    
    
    # child of root, Header
    header = root.createElement('Header')
    baseData = root.createElement('baseData')
    modelGeometry = root.createElement('modelGeometry')
    nestingArea = root.createElement('nestingArea')
    locationData = root.createElement('locationData')
    defaultSettings = root.createElement('defaultSettings')
    buildings2D = root.createElement('buildings2D')
    simpleplants2D = root.createElement('simpleplants2D')
    soils2D = root.createElement('soils2D')
    dem = root.createElement('dem')
    sources2D = root.createElement('sources2D')
    receptors2D = root.createElement('receptors2D')# empty
    additionalData = root.createElement('additionalData')# empty
    modelGeometry3D = root.createElement('modelGeometry3D')
    buildings3D = root.createElement('buildings3D')
    dem3D = root.createElement('dem3D')
    WallDB = root.createElement('WallDB')
    SingleWallDB = root.createElement('SingleWallDB')
    
    
    xml.appendChild(header)
    xml.appendChild(baseData)
    xml.appendChild(modelGeometry)
    xml.appendChild(nestingArea)
    xml.appendChild(locationData)
    xml.appendChild(defaultSettings)
    xml.appendChild(buildings2D)
    xml.appendChild(simpleplants2D)
    xml.appendChild(soils2D)
    xml.appendChild(dem)
    xml.appendChild(sources2D)
    xml.appendChild(receptors2D)
    xml.appendChild(additionalData)
    xml.appendChild(modelGeometry3D)
    xml.appendChild(buildings3D)
    xml.appendChild(dem3D)
    xml.appendChild(WallDB)
    xml.appendChild(SingleWallDB)
    
    # add child to header
    headerDict = {'filetype':'INPX ENVI-met Area Input File',
                  'version': '4',
                  'revisiondate':timeTxt,
                  'remark':'- Test version -',
                  'encryptionlevel':'0'
                  }
    baseDataDict = {'modelDescription':'DragonFly Document',
                  'modelAuthor': 'DragonFly'
                  }
    modelGeometryDict = {'grids-I': str(Xcells),
                  'grids-J': str(Ycells),
                  'grids-Z': str(Zcells),
                  'dx': '{:f}'.format(Xdim),
                  'dy': '{:f}'.format(Ydim),
                  'dz-base': '{:f}'.format(Zdim),
                  'useTelescoping_grid': str(telescopingGrid),
                  'useSplitting': str(useSplitting),
                  'verticalStretch': '{:f}'.format(verticalStretch),
                  'startStretch': '{:f}'.format(startStretch),
                  'has3DModel': str(has3DModel),
                  'isFull3DDesign': str(isFull3DDesign)
                  }
    nestingAreaDict = {'numberNestinggrids': str(numNesting),
                  'soilProfileA': matNesting[0],
                  'soilProfileB': matNesting[1]
                  }
    locationDataDict = {'modelRotation':'{:f}'.format(north),
                  'projectionSystem': '',
                  'realworldLowerLeft_X':'0.00000',
                  'realworldLowerLeft_Y':'0.00000',
                  'locationName':locationName,
                  'location_Longitude':latitude,
                  'location_Latitude':longitude,
                  'locationTimeZone_Name':timeZone,
                  'locationTimeZone_Longitude':'15.00000'
                  }
    defaultSettingsDict = {'commonWallMaterial': defaultMat[0],
                  'commonRoofMaterial': defaultMat[1]
                  }
    nameAttribute2D, dataAttribute2D = ['type', 'dataI', 'dataJ'], ['matrix-data', str(Xcells), str(Ycells)]
    buildings2DDict = {'zTop':buildingEmptyMatrix,
                  'zBottom':buildingEmptyMatrix,
                  'buildingNr':buildingNrMatrix,
                  'fixedheight':buildingEmptyMatrix
                  }
    simpleplants2DDict = {'ID_plants1D':ID_plants1DMatrix
                  }
    soils2DDict = {'ID_soilprofile':soils2DMatrix
                  }
    demDict = {'terrainheight':demPattern
                  }
    sources2DDict = {'ID_sources':ID_sourcesMatrix
                  }
    receptors2DDict = {'ID_receptors':emptySequence
                  }# empty
    additionalDataDict = {'db_link_point':emptySequence,
                  'db_link_area':emptySequence
                  }# empty
    modelGeometry3DDict = {'grids3D-I': str(Xcells),
                  'grids3D-J': str(Ycells),
                  'grids3D-K': str(grids3DK)
                  }
    nameAttribute3Dbuilding, dataAttribute3Dbuilding = ['type', 'dataI', 'dataJ', 'zlayers', 'defaultValue'], ['sparematrix-3D', str(Xcells), str(Ycells), str(grids3DK), '0']
    buildings3DDict = {'buildingFlagAndNr':buildingFlagAndNrMatrix
                  }
    nameAttribute3DTerrain, dataAttribute3DTerrain = ['type', 'dataI', 'dataJ', 'zlayers', 'defaultValue'], ['sparematrix-3D', str(Xcells), str(Ycells), str(grids3DK), '0.00000']
    dem3DDict = {'terrainflag':terrainFlagMatrix
                  }
    nameAttributeWallDB, dataAttributeWallDB = ['type', 'dataI', 'dataJ', 'zlayers', 'defaultValue'], ['sparematrix-3D', str(Xcells), str(Ycells), str(grids3DK), '']
    WallDBDict = {'ID_wallDB':WallDBMatrix
                  }
    nameAttributeSingleWallDB, dataAttributeSingleWallDB = ['type', 'dataI', 'dataJ', 'zlayers', 'defaultValue'], ['sparematrix-3D', str(Xcells), str(Ycells), str(grids3DK), '']
    SingleWallDBDict = {'ID_singlewallDB':''
                  }
    
    # appendChild!
    appendMultipleChild(headerDict, header)
    appendMultipleChild(baseDataDict, baseData)
    appendMultipleChild(modelGeometryDict, modelGeometry)
    appendMultipleChild(nestingAreaDict, nestingArea)
    appendMultipleChild(locationDataDict, locationData)
    appendMultipleChild(defaultSettingsDict, defaultSettings)
    appendMultipleChildWithAttribute(buildings2DDict, buildings2D, nameAttribute2D, dataAttribute2D)
    appendMultipleChildWithAttribute(simpleplants2DDict, simpleplants2D, nameAttribute2D, dataAttribute2D)
    if threeDplants:
        for plant in threeDplants:
            plants3D = root.createElement('3Dplants')
            xml.appendChild(plants3D)
            plants3DDict = {'rootcell_i': str(plant[0]),
                          'rootcell_j': str(plant[1]),
                          'rootcell_k': str(plant[2]),
                          'plantID': str(plant[3]),
                          'name': str(plant[4]),
                          'observe': str(plant[5])
                          }
            appendMultipleChild(plants3DDict, plants3D)
    appendMultipleChildWithAttribute(soils2DDict, soils2D, nameAttribute2D, dataAttribute2D)
    appendMultipleChildWithAttribute(demDict, dem, nameAttribute2D, dataAttribute2D)
    appendMultipleChildWithAttribute(sources2DDict, sources2D, nameAttribute2D, dataAttribute2D)
    appendMultipleChildWithAttribute(receptors2DDict, receptors2D, nameAttribute2D, dataAttribute2D)
    appendMultipleChildWithAttribute(additionalDataDict, additionalData, nameAttribute2D, dataAttribute2D)
    appendMultipleChild(modelGeometry3DDict, modelGeometry3D)
    appendMultipleChildWithAttribute(buildings3DDict, buildings3D, nameAttribute3Dbuilding, dataAttribute3Dbuilding)
    appendMultipleChildWithAttribute(dem3DDict, dem3D, nameAttribute3DTerrain, dataAttribute3DTerrain)
    appendMultipleChildWithAttribute(WallDBDict, WallDB, nameAttributeWallDB, dataAttributeWallDB)
    appendMultipleChildWithAttribute(SingleWallDBDict, SingleWallDB, nameAttributeSingleWallDB, dataAttributeSingleWallDB)
    
    # pass xml in xml string
    xml_str = root.toprettyxml(indent="  ")
    
    with open(fullPath, "w") as f:
        f.write(xml_str[23:])


def main():
    
    # default values
    if _numX_ == None:
        numX = 19
    else:
        numX = _numX_ - 1 
    if _numY_ == None:
        numY = 19
    else:
        numY = _numY_ - 1 
    if _numZ_ == None:
        numZ = 19
    else:
        numZ = _numZ_ - 1 
    
    if _dimX_ == None:
        dimX = 3.0
    else:
        dimX = _dimX_ 
    if _dimY_ == None:
        dimY = 3.0
    else:
        dimY = _dimY_
    if _dimZ_ == None:
        dimZ = 3.0
    else:
        dimZ = _dimZ_ 
    
    if _north_ == None:
        north = 0.00
    else: north = _north_
    
    if numNestingGrid_ == None:
        numNestingGrid = 3
    else:
        numNestingGrid = numNestingGrid_
    if nestingGridSoil_ == []:
        nestingGridSoil = ['LO', 'LO']
    elif len(nestingGridSoil_) == 1:
        nestingGridSoil = nestingGridSoil_*2
    else:
        nestingGridSoil = nestingGridSoil_
    
    if fileName_ == None:
        fileName = 'LBenvimet.INX'
    else:
        fileName = fileName_ + '.INX'
    
    if baseSoilmaterial_ == None:
        baseSoilmaterial = 'LO'
    else:
        baseSoilmaterial = baseSoilmaterial_
    
    # name of file
    if not os.path.exists(_folder):
        os.makedirs(_folder)
    fileAddress = _folder + '\\' + fileName
    
    # location
    locationName, latitude, longitude, timeZone = locationDataFunction(_location)
    
    # generate pretty grid visualization
    points = grid(numX, numY, numZ, dimX, dimY, dimZ)
    
    if _runIt:
        # read buildingData
        buildings = [buildingData[2] for buildingData in _envimetBuildings]
        wallMaterials = [buildingData[0] for buildingData in _envimetBuildings]
        roofMaterials = [buildingData[1] for buildingData in _envimetBuildings]
        defaultMaterials = [[buildingData[3] for buildingData in _envimetBuildings][0], [buildingData[4] for buildingData in _envimetBuildings][0]]
        maxHeight = [buildingData[5] for buildingData in _envimetBuildings]
        
        checkBorder = checkDistanceFromBorder(points, buildings, dimX, dimY, dimZ, numZ, maxHeight)
        
        if checkBorder:
            # move building up
            copyBuildings = [b.DuplicateBrep() for b in buildings]
            [b.Translate(rc.Geometry.Vector3d.ZAxis*(dimZ/10)) for b in copyBuildings]
            
            # create building matrix
            buildingFlagAndNrMatrix, WallDBMatrix, oneMatrix = matrixConstruction(copyBuildings, numX, numY, numZ, dimX, dimY, dimZ, wallMaterials, roofMaterials)
            
            # 2D building stuff
            buildingNrMatrix = twoDimensionalBuilding(oneMatrix)
            buildingEmptyMatrix = re.sub('\d+','0',buildingNrMatrix)
        else:
            return -1
        
        emptySequence = emptyMatrix(numX, numY)
        # dem
        if envimetTerrain_:
            terrainFlagMatrix = digitalElevationModel3D(envimetTerrain_, numX, numY, numZ, dimX, dimY, dimZ)
            demPattern = generateDem2D(numX, numY, dimX, dimY, envimetTerrain_)
        else:
            terrainFlagMatrix = ''
            demPattern = buildingEmptyMatrix
        # plants
        if envimetPlants_:
            plants2D, plants3D, idPlants = separateData(envimetPlants_)
            if len(plants2D) != 0:
                ID_plants1DMatrix = matrix2DGen(plants2D, numX, numY, dimX, dimY, idPlants, '')
            else: ID_plants1DMatrix = emptySequence
            if len(plants3D) != 0:
                threeDplants = threeDimensionalPlants(plants3D, numX, numY, dimX, dimY)
            else: threeDplants = []
        else: ID_plants1DMatrix, threeDplants = emptySequence, []
        # soil
        if envimetSoils_:
            soil2D, empty, idSoild = separateData(envimetSoils_)
            soils2DMatrix = matrix2DGen(soil2D, numX, numY, dimX, dimY, idSoild, baseSoilmaterial)
            print soils2DMatrix
        else: soils2DMatrix = re.sub(r'', baseSoilmaterial, emptySequence)
        # source
        if envimetSources_:
            source2D, empty, idSource = separateData(envimetSources_)
            ID_sourcesMatrix = matrix2DGen(source2D, numX, numY, dimX, dimY, idSource, '')
        else: ID_sourcesMatrix = emptySequence
        
        # write file
        writeINX(fileAddress, numX+1, numY+1, numZ+1, dimX, dimY, dimZ,
                str(numNestingGrid), nestingGridSoil, _location,
                north, defaultMaterials, buildingEmptyMatrix, buildingNrMatrix,
                terrainFlagMatrix, buildingFlagAndNrMatrix, WallDBMatrix, ID_plants1DMatrix, 
                threeDplants, soils2DMatrix, ID_sourcesMatrix, emptySequence, demPattern)
        
        if os.path.exists(fileAddress):
            print("INX file successfully created!")
            return points, fileAddress
        else:
            warning = "Something went wrong, please try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        
    else:
        print("Set runIt to True.")
    
    return points, None


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
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")


check = checkInputs(_location, _envimetBuildings, _folder)

if check and initCheck:
    result = main()
    if result != -1:
        points, INXfileAddress = result
else:
    print("Please provide all _inputs.")