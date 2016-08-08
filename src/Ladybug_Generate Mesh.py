#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to genrate a mesh with corresponding test points.  The resulting mesh will be in a format that the Recolor Mesh component will accept.
-
Provided by Honeybee 0.0.59
    Args:
        _testSurface: Test surface as a Brep.
        _gridSize: Size of the test grid.
        _distBaseSrf: Distance from base surface.
        moveTestMesh_: Set to 'False' if you want test mesh not to move. Default is 'True'.
    Returns:
        readMe!: ...
        testPoints: Test points
        ptsVectors: Vectors
        faceArea: Area of each mesh face
        mesh: Analysis mesh
"""

ghenv.Component.Name = "Ladybug_Generate Mesh"
ghenv.Component.NickName = 'genMesh'
ghenv.Component.Message = 'VER 0.0.62\nAUG_06_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import Rhino as rc
import Grasshopper.Kernel as gh
from itertools import chain
import System.Threading.Tasks as tasks

def createMesh(brep, gridSize):
    ## mesh breps
    def makeMeshFromSrf(i, inputBrep):
        try:
            mesh[i] = rc.Geometry.Mesh.CreateFromBrep(inputBrep, meshParam)[0]
            inputBrep.Dispose()
        except:
            print 'Error in converting Brep to Mesh...'
            pass

    # prepare bulk list for each surface
    mesh = [None] * len(brep)

    # set-up mesh parameters for each surface based on surface size
    meshParam = rc.Geometry.MeshingParameters.Default
    meshParam.MaximumEdgeLength = gridSize
    meshParam.MinimumEdgeLength = gridSize
    meshParam.GridAspectRatio = 1

    for i in range(len(mesh)): makeMeshFromSrf(i, brep[i])
    
    return mesh

def flattenList(l):return list(chain.from_iterable(l))

def getTestPts(inputMesh, movingDis, moveTestMesh= False, parallel = True):
        
        # preparing bulk lists
        testPoint = [[]] * len(inputMesh)
        srfNormals = [[]] * len(inputMesh)
        meshSrfCen = [[]] * len(inputMesh)
        meshSrfArea = [[]] * len(inputMesh)
        
        srfCount = 0
        for srf in inputMesh:
            testPoint[srfCount] = range(srf.Faces.Count)
            srfNormals[srfCount] = range(srf.Faces.Count)
            meshSrfCen[srfCount] = range(srf.Faces.Count)
            meshSrfArea[srfCount] = range(srf.Faces.Count)
            srfCount += 1

        try:
            def srfPtCalculator(i):
                # calculate face normals
                inputMesh[i].FaceNormals.ComputeFaceNormals()
                inputMesh[i].FaceNormals.UnitizeFaceNormals()
                
                for face in range(inputMesh[i].Faces.Count):
                    srfNormals[i][face] = (inputMesh[i].FaceNormals)[face] # store face normals
                    meshSrfCen[i][face] = inputMesh[i].Faces.GetFaceCenter(face) # store face centers
                    # calculate test points
                    if srfNormals[i][face]:
                        movingVec = rc.Geometry.Vector3f.Multiply(movingDis,srfNormals[i][face])
                        testPoint[i][face] = rc.Geometry.Point3d.Add(rc.Geometry.Point3d(meshSrfCen[i][face]), movingVec)
                    # make mesh surface, calculate the area, dispose the mesh and mass area calculation
                    tempMesh = rc.Geometry.Mesh()
                    tempMesh.Vertices.Add(inputMesh[i].Vertices[inputMesh[i].Faces[face].A]) #0
                    tempMesh.Vertices.Add(inputMesh[i].Vertices[inputMesh[i].Faces[face].B]) #1
                    tempMesh.Vertices.Add(inputMesh[i].Vertices[inputMesh[i].Faces[face].C]) #2
                    tempMesh.Vertices.Add(inputMesh[i].Vertices[inputMesh[i].Faces[face].D]) #3
                    tempMesh.Faces.AddFace(0, 1, 3, 2)
                    massData = rc.Geometry.AreaMassProperties.Compute(tempMesh)
                    meshSrfArea[i][face] = massData.Area
                    massData.Dispose()
                    tempMesh.Dispose()
                    
                    
        except:
            print 'Error in Extracting Test Points'
            pass
        
        # calling the function
        if parallel:
            tasks.Parallel.ForEach(range(len(inputMesh)),srfPtCalculator)
        else:
            for i in range(len(inputMesh)):
                srfPtCalculator(i)
        
        if moveTestMesh:
            # find surfaces based on first normal in srfNormals - It is a simplification we can write a better function for this later
            for meshCount, mesh in enumerate(inputMesh):
                vector = srfNormals[meshCount][0]
                vector.Unitize()
                vector = rc.Geometry.Vector3d.Multiply(movingDis, vector)
                mesh.Translate(vector.X, vector.Y, vector.Z)
                
        return flattenList(testPoint), flattenList(srfNormals), flattenList(meshSrfArea), inputMesh

ghenv.Component.Params.Input[1].Name = '_gridSize'
ghenv.Component.Params.Input[1].NickName = '_gridSize'

if _testGeometry!=None:
    inputMesh = []
    
    if type(_testGeometry) == rc.Geometry.Mesh and _distBaseSrf!=None:
        ghenv.Component.Params.Input[1].Name = '.'
        ghenv.Component.Params.Input[1].NickName = '.'
        inputMesh.append(_testGeometry)
        
    elif _gridSize!=None and _distBaseSrf!=None:
        initMesh = createMesh([_testGeometry], _gridSize)
        for m in initMesh: inputMesh.append(m)     

    if _distBaseSrf<0:
        msg = "Distance from base should be greater than 0. Flip the input surface instead of using a negative number."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    else:
        testPoints, ptsVectors, facesArea, mesh = getTestPts(inputMesh, _distBaseSrf, moveTestMesh_)