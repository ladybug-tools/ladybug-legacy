# Texture Maker
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
Use this component to generate textures from colored meshes.
In order to export model as *obj you should Bake the new mesh and apply texture to its layer material.
It is also compatible with Google Earth.
How to use it:
1) connect colored mesh which comes from LB analysis component
2) run the component
The output are: a new mesh that you have to bake and a texture that you should add to material of the layer where your mesh will be.
-
Special thanks goes to the author of the function, Vincente Soler.
.
http://www.grasshopper3d.com/forum/topics/how-to-render-mesh-colors
-
Provided by Ladybug 0.0.63
    
    Args:
        _analysisMesh: A list of colored Meshes that comes from Grasshopper OR
        .
        "radiationMesh" of "Ladybug_Radiation Analysis"
        .
        "viewStudyMesh" of "Ladybug_View Analysis"
        .
        and so on..
        folder_: The folder into which you would like to write the image file. This should be a complete file path to the folder. If no folder is provided, the images will be written to C:/USERNAME/AppData/Roaming/Ladybug/LB_TextureMesh.
        name_: The file name that you would like the image to be saved as. If no input is provided it will be created automatically.
        _runIt: Set to "True" to run the component and generate textures and meshes.
    Returns:
        readMe!: ...
        imagePath: Use this image as texture for the new mesh. Connect imagePath to "DB" input of "Human Create/Modify material" and its output to "Human Create/Modify Layers" to apply material to a layer.
        mesh : A new mesh that you have to bake.
"""

ghenv.Component.Name = "Ladybug_Texture Maker"
ghenv.Component.NickName = 'Texture Maker'
ghenv.Component.Message = 'VER 0.0.63\nOCT_12_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import Rhino as rc
import clr
import System
import math
import scriptcontext as sc
import os

clr.AddReference("Grasshopper")
import Grasshopper.Kernel as gh
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree


def mdPath(folder):
    # make a folder for the images
    if folder != None:
        directory = folder + '\\' # it work also with Desktop as folder
        if not os.path.exists(folder):
            try:
                os.mkdir(directory)
            except Exception:
                appdata = os.getenv("APPDATA")
                directory = os.path.join(appdata, "Ladybug\LB_TextureMesh\\")
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "Invalid Folder, you can find images here: {}".format(directory))
    else:
        appdata = os.getenv("APPDATA")
        directory = os.path.join(appdata, "Ladybug\LB_TextureMesh\\")
        if not os.path.exists(directory): os.makedirs(directory)
    
    return directory


def checkInputs(analysisMesh, runIt):
    if analysisMesh == [] or runIt == None:
        return False
    else:
        return True


def vincenteBakingMesh(m, u, run):
    """ The author of this function is Vincente Soler. The original function is made by two VB.Net components.
    changes:
    - from VB.Net to Python
    - one component
    """
    
    m.Unweld(0, False)
    # set a tree
    colorTree = DataTree[System.Drawing.Color]()
    c = m.Faces.Count
    f = m.Faces
    
    for i in range(c):
        path = GH_Path(i)
        colorTree.Add(System.Drawing.Color.FromArgb(m.VertexColors[f[i].A].R, m.VertexColors[f[i].A].G, m.VertexColors[f[i].A].B), path)
        colorTree.Add(System.Drawing.Color.FromArgb(m.VertexColors[f[i].B].R, m.VertexColors[f[i].B].G, m.VertexColors[f[i].B].B), path)
        colorTree.Add(System.Drawing.Color.FromArgb(m.VertexColors[f[i].C].R, m.VertexColors[f[i].C].G, m.VertexColors[f[i].C].B), path)
        colorTree.Add(System.Drawing.Color.FromArgb(m.VertexColors[f[i].D].R, m.VertexColors[f[i].D].G, m.VertexColors[f[i].D].B), path)
    
    # mod mesh
    m.TextureCoordinates.Clear()
    for i in range(0, m.Vertices.Count):
        m.TextureCoordinates.Add(0, 0)
    
    size = math.ceil(math.sqrt(c))
    count = -1
    for x in xrange(size):
        for y in xrange(size):
            count += 1
            sb = size * 2
            if count < c:
                f = m.Faces[count]
                m.TextureCoordinates[f.A] = rc.Geometry.Point2f(((x * 2) + 0.5) / sb, ((y * 2) + 0.5) / sb)
                m.TextureCoordinates[f.B] = rc.Geometry.Point2f(((x * 2) + 1.5) / sb, ((y * 2) + 0.5) / sb)
                m.TextureCoordinates[f.C] = rc.Geometry.Point2f(((x * 2) + 1.5) / sb, ((y * 2) + 1.5) / sb)
                m.TextureCoordinates[f.D] = rc.Geometry.Point2f(((x * 2) + 0.5) / sb, ((y * 2) + 1.5) / sb)
    mesh = m
    
    # make the texture
    size = math.ceil(math.sqrt(colorTree.BranchCount))
    sb = size * 2 - 1
    bm = System.Drawing.Bitmap(size * 2, size * 2)
    bmb = System.Drawing.Bitmap(size * 4, size * 4)
    
    count = -1
    for x in xrange(size):
        for y in xrange(size):
            count += 1
            if count < colorTree.BranchCount:
                bm.SetPixel((x * 2) + 0, sb - ((y * 2) + 0), colorTree.Branch(count)[0])
                bm.SetPixel((x * 2) + 1, sb - ((y * 2) + 0), colorTree.Branch(count)[1])
                bm.SetPixel((x * 2) + 1, sb - ((y * 2) + 1), colorTree.Branch(count)[2])
                bm.SetPixel((x * 2) + 0, sb - ((y * 2) + 1), colorTree.Branch(count)[3])
    
    g = System.Drawing.Graphics.FromImage(bmb)
    g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor
    g.DrawImage(bm, 0, 0, size * 4 + 1, size * 4 + 1)
    if run:
        bmb.Save(u)
    
    return mesh


def main():
    # make a folder for the images
    directory = mdPath(folder_)
    
    special_mesh = []
    imagePath = []
    for i, m in enumerate(_analysisMesh):
        if name_ != []:
            completePath = directory + name_[i] + '.png'
        else: completePath = directory + 'mesh_n_' + str(i) + '.png'
        special_mesh.append(vincenteBakingMesh(m, completePath, _runIt))
        imagePath.append(completePath)
    
    return imagePath, special_mesh


check = checkInputs(_analysisMesh, _runIt)
if check:
    result = main()
    if result != -1:
        imagePath, mesh = result
        if _runIt: print("Texture generated!")
else:
    pass
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "Please provide all inputs.")