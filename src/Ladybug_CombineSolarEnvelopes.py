# Combine Solar Envelopes
# Combine two or more solar envelopes from Ladybug_SolarEnvelope component
# Applicable to solar rights and solar access.
# A typical use could be to create nultiple envelopes by various filter parameters for different facades in the surrounding 
# and combining them to one. For instance choosing morning hours to apply for east facades, noon for south and after noon 
# for west to ensure solar access to each orientation on critical times.


# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Boris Plotnikov <pborisp@gmail.com> 
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
Use this component to combine two or more solar envelopes from Ladybug_SolarEnvelope component

-
Provided by Ladybug 0.0.62
    
    Args:
        _baseSrf: A surface representing the area for which you want to create the solar envelope (could also be a closed planer curve). Must be the same as the _BaseSrf connected to the solar Envelope component.
        _envelopePts: A list of 3d points representing the heights to which the solar envelope reaches. Use the envelopePts output from the solar envelope component.
        HighestEnv_: if HighestEnv_ is True we'll take the highest points and if it's False we'll take the lowest ones. Default value is True
        _gridSize: A numeric value inidcating the gird size of the analysis in Rhino model units. Muse be the same as the gridSize_ value connected to the solar Envelope component.
    Returns:
        newEnvPoints: A list of 3d points representing the heights to which the solar envelope reaches.  Plug into a native GH 'Delunay Mesh' component to visualize the full solar envelope.
        envelopeBrep: Brep representing the envelope.
"""

ghenv.Component.Name = 'Ladybug_CombineSolarEnvelopes'
ghenv.Component.NickName = 'CombineEnvelopes'
ghenv.Component.Message = 'VER 0.0.62\nAUG_08_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "5 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass

import Rhino
import Grasshopper.Kernel as gh

def issueWarning(message,boolToReturn = False):
    print message
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, message)
    return boolToReturn

allDataProvided = True
if not _baseSrf :
    allDataProvided = issueWarning("Base surface must be provided")
if not _envelopePts:
    allDataProvided = issueWarning("Envelope points must be provided")
if not _gridSize:
    allDataProvided = issueWarning("Grid size must be provided")

if allDataProvided:
    if HighestEnv_ is None: HighestEnv_ = True
    
    #a weird way of determining how many solar envelope points we have - should probably get the lists as tree branches or something
    numOfEnvelopes = len(ghenv.Component.Params.Input[1].Sources)
    totalPoints = len(_envelopePts)
    pointsPerEnv = int(totalPoints/numOfEnvelopes)
    
    #convert the base surface to a mesh
    regionMeshPar = Rhino.Geometry.MeshingParameters.Default
    regionMeshPar.MinimumEdgeLength = regionMeshPar.MaximumEdgeLength = _gridSize/2
    regionMesh = Rhino.Geometry.Mesh.CreateFromBrep(_baseSrf, regionMeshPar)[0]
    
    #loop through all the points in all the envelopes and populate a list of the highest or lowest points
    newEnvPoints = []
    for i in range(0,pointsPerEnv,1):
        val = _envelopePts[i]
        for j in range(0,numOfEnvelopes - 1, 1):
            if HighestEnv_:
                if _envelopePts[i + (j + 1) * pointsPerEnv].Z > val.Z:
                    val = _envelopePts[i + (j + 1) * pointsPerEnv]
            else:
                if _envelopePts[i + (j + 1) * pointsPerEnv].Z < val.Z:
                    val = _envelopePts[i + (j + 1) * pointsPerEnv]
        newEnvPoints.append(val)
    
    #set the new height of all the points constructing the envelope brep
    for vertexCount, gridPt in enumerate(newEnvPoints):
        regionMesh.Vertices[vertexCount] = Rhino.Geometry.Point3f(gridPt.X,gridPt.Y, gridPt.Z)
        finalEnvelopeBrep = Rhino.Geometry.Brep.CreateFromMesh(regionMesh,True)
    envelopeBrep = finalEnvelopeBrep
