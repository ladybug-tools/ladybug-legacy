# Texture Maker
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
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
Provided by Ladybug 0.0.67
    
    Args:
        _analysisMesh: A list of colored Meshes that comes from Grasshopper OR
        .
        "radiationMesh" of "Ladybug_Radiation Analysis"
        .
        "viewStudyMesh" of "Ladybug_View Analysis"
        .
        and so on..
        transparency_: An optional number between 0 and 1 to set the opacity/transparency of the image.  Note that Rhino may not display this transparency but rendering programs like V-Ray will be able to render it.
        folder_: The folder into which you would like to write the image file. This should be a complete file path to the folder. If no folder is provided, the images will be written to C:/USERNAME/AppData/Roaming/Ladybug/LB_TextureMesh.
        name_: The file name that you would like the image to be saved as. If no input is provided it will be created automatically.
        _layerName_: An optional text string to set the name of the layer onto which the image-mapped mesh will be baked.
        softBake_: Set to "True" to run the component and bake the mesh with image material.  However, if this component runs again, the old geometry in the Rhino scene will be overwritten by new geometry, allowing you to make things like rendered animations.
        _bakeIt: Set to "True" to run the component, generate texture images, and bake the mesh into the scene with the image as a material.
    Returns:
        readMe!: ...
        imagePath: Use this image as texture for the new mesh. Connect imagePath to "DB" input of "Human Create/Modify material" and its output to "Human Create/Modify Layers" to apply material to a layer.
        mesh : A new mesh that is structured to correctly accept the image map. This has been baked into the scene for you.
"""

ghenv.Component.Name = "Ladybug_Texture Maker"
ghenv.Component.NickName = 'Texture Maker'
ghenv.Component.Message = 'VER 0.0.67\nNOV_20_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.62\nJUN_07_2016
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import Rhino as rc
import rhinoscriptsyntax as rs
import clr
import System
import math
import scriptcontext as sc
import os
import Grasshopper.Kernel as gh


def checkInputs(analysisMesh, runIt, alpha):
    if alpha == None:
        alpha = 255
    else:
        if alpha <=1 and alpha >=0:
            alpha = int((1-alpha)*255)
        else:
            warning = "opacity_ must be between 0 and 1."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
    
    if analysisMesh == [] or runIt == None or runIt == False:
        return -1
    else:
        return alpha

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

def makeTexture(size, colorTree):
    sb = size * 2 - 1
    bm = System.Drawing.Bitmap(size * 2, size * 2)
    bmb = System.Drawing.Bitmap(size * 4, size * 4)
    
    count = -1
    for x in xrange(size):
        for y in xrange(size):
            count += 1
            if count < len(colorTree):
                bm.SetPixel((x * 2) + 0, sb - ((y * 2) + 0), colorTree[count][0])
                bm.SetPixel((x * 2) + 1, sb - ((y * 2) + 0), colorTree[count][1])
                bm.SetPixel((x * 2) + 1, sb - ((y * 2) + 1), colorTree[count][2])
                bm.SetPixel((x * 2) + 0, sb - ((y * 2) + 1), colorTree[count][3])
    
    g = System.Drawing.Graphics.FromImage(bmb)
    g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor
    g.DrawImage(bm, 0, 0, size * 4 + 1, size * 4 + 1)
    
    return bmb

def vincenteBakingMesh(m, u, a, v):
    """ The author of this function is Vincente Soler. The original function is made by two VB.Net components.
    changes:
    - from VB.Net to Python
    - one component
    """
    
    m.Unweld(0, False)
    # set a tree
    colorTree = []
    c = m.Faces.Count
    f = m.Faces
    
    for i in range(c):
        colorTree.append([])
        colorTree[i].append(System.Drawing.Color.FromArgb(a, m.VertexColors[f[i].A].R, m.VertexColors[f[i].A].G, m.VertexColors[f[i].A].B))
        colorTree[i].append(System.Drawing.Color.FromArgb(a, m.VertexColors[f[i].B].R, m.VertexColors[f[i].B].G, m.VertexColors[f[i].B].B))
        colorTree[i].append(System.Drawing.Color.FromArgb(a, m.VertexColors[f[i].C].R, m.VertexColors[f[i].C].G, m.VertexColors[f[i].C].B))
        colorTree[i].append(System.Drawing.Color.FromArgb(a, m.VertexColors[f[i].D].R, m.VertexColors[f[i].D].G, m.VertexColors[f[i].D].B))
    
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
    
    # make the texture
    size = math.ceil(math.sqrt(len(colorTree)))
    bmb = makeTexture(size, colorTree)
    bmb.Save(u)
    
    # make the alpha channel.
    if a != 255:
        aColTree = []
        aColor = System.Drawing.Color.FromArgb(a, a, a)
        for count, colList in enumerate(colorTree):
            aColTree.append([])
            for val in colList:
                aColTree[count].append(aColor)
        abmb = makeTexture(size, aColTree)
        abmb.Save(v)
    
    return m


def main(analysisMesh, folder, name, layerName, alpha, softBake, softBakeMeshes):
    # make a folder for the images
    directory = mdPath(folder)
    
    #Generate the image map textures.
    special_mesh = []
    imagePath = []
    alphaPath = []
    aPath = None
    for i, m in enumerate(analysisMesh):
        if name != []:
            completePath = directory + name_[i] + '.png'
        else: completePath = directory + 'mesh_n_' + str(i) + '.png'
        if alpha != 255:
            if name != []:
                aPath = directory + name_[i] + '_alpha.png'
            else: aPath = directory + 'mesh_alpha_n_' + str(i) + '.png'
            alphaPath.append(aPath)
        
        special_mesh.append(vincenteBakingMesh(m, completePath, alpha, aPath))
        imagePath.append(completePath)
    
    # Bake the mesh into the Rhino scene and set the image map material.
    for count, mesh in enumerate(special_mesh):
        #Set up the layer to bake object onto.
        if layerName == None: layerName = 'ImageMappedMesh'
        layerT = rc.RhinoDoc.ActiveDoc.Layers #layer table
        studyLayer = rc.DocObjects.Layer()
        studyLayer.Name = layerName
        studyLayer.IsVisible = True
        studyLayerIndex = rc.DocObjects.Tables.LayerTable.Find(layerT, layerName, True)
        if studyLayerIndex < 0: studyLayerIndex = layerT.Add(studyLayer)
        
        #Set up basic object attributes
        attr = rc.DocObjects.ObjectAttributes()
        attr.LayerIndex = studyLayerIndex
        attr.ColorSource = rc.DocObjects.ObjectColorSource.ColorFromObject
        attr.PlotColorSource = rc.DocObjects.ObjectPlotColorSource.PlotColorFromObject
        
        # Set up a Material and add it to the attributes.
        materialT = rc.RhinoDoc.ActiveDoc.Materials #material table
        material = rc.DocObjects.Material()
        material.SetBitmapTexture(imagePath[count])
        if alpha != 255:
            material.SetTransparencyTexture(alphaPath[count])
        matIndex = materialT.Add(material)
        attr.MaterialSource = rc.DocObjects.ObjectMaterialSource.MaterialFromObject
        attr.MaterialIndex = matIndex
        
        #Bake the mesh into the scene.
        rhinoMesh = rc.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh, attr)
        if softBake == True:
            softBakeMeshes.append([rhinoMesh,matIndex])
    
    return imagePath, alphaPath, special_mesh


# Delete any old objects in memory
try:
    softBakeMeshes = sc.sticky["ladybug_SoftBakeMeshes"]
    for item in softBakeMeshes:
        rc.RhinoDoc.ActiveDoc.Objects.Delete(item[0], True)
        rc.RhinoDoc.ActiveDoc.Materials.DeleteAt(item[1])
except:
    sc.sticky["ladybug_SoftBakeMeshes"] = []
    softBakeMeshes = sc.sticky["ladybug_SoftBakeMeshes"]

alpha = checkInputs(_analysisMesh, _bakeIt, transparency_)
if alpha != -1:
    result = main(_analysisMesh, folder_, name_, _layerName_, alpha, softBake_, softBakeMeshes)
    if result != -1:
        imagePath, alphaPath, mesh = result
        print("Texture generated!")