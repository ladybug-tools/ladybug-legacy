# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to generate outline curves representing shadows cast by input _geometry for a given _sunVector.
Note that, to see shadows cast onto a ground, a surface representing the ground plane must be included in the input _geometry.
Also, please note that, for a list of input _geometry that is larger than 4 or 5 breps, the calculation time of this component can be very long.  Please keep the input geometry to small lists or be prepared to wait a long time.
WARNING: This component is a proof of concept that will not work in every situation.  It is not ideal for analyzing curved surfaces and it is not able to calculate shadows for geometries that are intersecting each other.
-
Provided by Ladybug 0.0.58
    
    Args:
        _geometry: Breps representig test geometries that will cast shadows on each other.
        _sunVector: A sun vector from the Ladybug sunPath component.
    Returns:
        readMe!: ...
        shadow: Outline curves representing the shadows cast by the individual input Breps on other input Breps.  Note that, if all input _geometry is planar, this output can be hooked up to a Grasshopper "Brep" component to give Breps representing shadows cast.
        shade: Outline curves representing the the parts of individual input Breps that are not in the sun.  In other words, this is the self-shaded part of the Breps. Note that, if all input _geometry is planar, this output can be hooked up to a Grasshopper "Brep" component to give Breps representing self-shaded areas.
"""

ghenv.Component.Name = "Ladybug_Shadow Study"
ghenv.Component.NickName = 'shadowStudy'
ghenv.Component.Message = 'VER 0.0.58\nAUG_20_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "7 | WIP"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Rhino as rc
import scriptcontext as sc
import System
import System.Threading.Tasks as tasks
import math

tol = sc.doc.ModelAbsoluteTolerance

def joinMesh(meshList):
    joinedMesh = rc.Geometry.Mesh()
    for m in meshList: joinedMesh.Append(m)
    return joinedMesh

def parallel_testPointCalculator(analysisSrfs, disFromBase, parallel = True):
        # Mesh functions should be modified and be written interrelated as a class
        movingDis = disFromBase
    
        # preparing bulk lists
        testPoint = [[]] * len(analysisSrfs)
        srfNormals = [[]] * len(analysisSrfs)
        meshSrfCen = [[]] * len(analysisSrfs)
        meshSrfEdges = [[]] * len(analysisSrfs)
        meshes = [[]] * len(analysisSrfs)        
        
        srfCount = 0
        for srf in analysisSrfs:
            testPoint[srfCount] = range(srf.Faces.Count)
            srfNormals[srfCount] = range(srf.Faces.Count)
            meshSrfCen[srfCount] = range(srf.Faces.Count)
            meshSrfEdges[srfCount] = range(srf.Faces.Count)
            meshes[srfCount] = range(srf.Faces.Count)
            srfCount += 1

        try:
            def srfPtCalculator(i):
                # calculate face normals
                analysisSrfs[i].FaceNormals.ComputeFaceNormals()
                analysisSrfs[i].FaceNormals.UnitizeFaceNormals()
                
                for face in range(analysisSrfs[i].Faces.Count):
                    srfNormals[i][face] = (analysisSrfs[i].FaceNormals)[face] # store face normals
                    meshSrfCen[i][face] = analysisSrfs[i].Faces.GetFaceCenter(face) # store face centers
                    # calculate test points
                    if srfNormals[i][face]:
                        movingVec = rc.Geometry.Vector3f.Multiply(movingDis,srfNormals[i][face])
                        testPoint[i][face] = rc.Geometry.Point3d.Add(rc.Geometry.Point3d(meshSrfCen[i][face]), movingVec)
                    # make mesh surface, calculate the area, dispose the mesh and mass area calculation
                    tempMesh = rc.Geometry.Mesh()
                    tempMesh.Vertices.Add(analysisSrfs[i].Vertices[analysisSrfs[i].Faces[face].A]) #0
                    tempMesh.Vertices.Add(analysisSrfs[i].Vertices[analysisSrfs[i].Faces[face].B]) #1
                    tempMesh.Vertices.Add(analysisSrfs[i].Vertices[analysisSrfs[i].Faces[face].C]) #2
                    tempMesh.Vertices.Add(analysisSrfs[i].Vertices[analysisSrfs[i].Faces[face].D]) #3
                    tempMesh.Faces.AddFace(0, 1, 2, 3)
                    edgesPL = tempMesh.GetNakedEdges()
                    edgesCrv = []
                    for e in edgesPL: edgesCrv.append(e.ToNurbsCurve())
                    meshSrfEdges[i][face] = rc.Geometry.Curve.JoinCurves(edgesCrv)[0]
                    meshes[i][face] = tempMesh
                    
        except:
            print 'Error in Extracting Test Points'
            pass
        
        # calling the function
        if parallel:
            tasks.Parallel.ForEach(range(len(analysisSrfs)),srfPtCalculator)
        else:
            for i in range(len(analysisSrfs)):
                srfPtCalculator(i)
    
        return testPoint, srfNormals, meshSrfEdges, meshes

def projectToPlane(geometry, plane, vector):
    
    def getTransform():
        if plane.ZAxis.IsParallelTo(vector)**2 == 1:
            x = rc.Geometry.Transform.PlanarProjection(plane)
            return x
        elif math.sin(rc.Geometry.Vector3d.VectorAngle(plane.ZAxis,vector)) == 1:
            x = rc.Geometry.Transform.Unset
            return x
        
        originalPlane = plane
        newPlane = rc.Geometry.Plane(originalPlane.Origin, -vector)
    
        z0 = originalPlane.ZAxis
        z1 = newPlane.ZAxis
        angle = rc.Geometry.Vector3d.VectorAngle(z0, z1)
        
        intersect, axis = rc.Geometry.Intersect.Intersection.PlanePlane(originalPlane, newPlane)
        
        if intersect:
            P2 = rc.Geometry.Plane(originalPlane)
            P2.XAxis = axis.UnitTangent
            P2.YAxis = rc.Geometry.Vector3d.CrossProduct(P2.XAxis, P2.ZAxis)
            
            beta = 0.5 * math.pi - angle
            factor = 1.0 / math.sin(beta)
            project = rc.Geometry.Transform.PlanarProjection(newPlane)
            rotate = rc.Geometry.Transform.Rotation(z1, z0, originalPlane.Origin)
            scale = rc.Geometry.Transform.Scale(P2, 1.0, factor, 1.0)
            x = scale * rotate * project
            return x
    
    geometry.Transform(getTransform())
    return geometry

def getMeshCenter(mesh):
    mp = rc.Geometry.AreaMassProperties.Compute(mesh)
    return mp.Centroid

def findDiscontinuity(curve, style, includeEndPts = True):
    # copied and modified from rhinoScript (@Steve Baer @GitHub)
    """Search for a derivatitive, tangent, or curvature discontinuity in
    a curve object.
    Parameters:
      curve_id = identifier of curve object
      style = The type of continuity to test for. The types of
          continuity are as follows:
          Value    Description
          1        C0 - Continuous function
          2        C1 - Continuous first derivative
          3        C2 - Continuous first and second derivative
          4        G1 - Continuous unit tangent
          5        G2 - Continuous unit tangent and curvature
    Returns:
      List 3D points where the curve is discontinuous
    """
    dom = curve.Domain
    t0 = dom.Min
    t1 = dom.Max
    points = []
    #if includeEndPts: points.append(curve.PointAtStart)
    get_next = True
    while get_next:
        get_next, t = curve.GetNextDiscontinuity(System.Enum.ToObject(rc.Geometry.Continuity, style), t0, t1)
        if get_next:
            points.append(curve.PointAt(t))
            t0 = t # Advance to the next parameter
    if includeEndPts: points.append(curve.PointAtEnd)
    return points

class pseudoFace(object):
    def __init__(self, mesh):
        self.geometry = mesh
        self.boundary = []
        polylines = self.geometry.GetNakedEdges()
        [self.boundary.append(pl.ToNurbsCurve()) for pl in polylines]
        self.boundary = self.boundary[0]

def checkReverse(shadingFace, toBeShadedFace, vector):
    res = isShadingPossible(shadingFace, toBeShadedFace, vector, count = 1)
    if res == True: return False
    elif res == False: return True
    else: return "Complicated"
    
def isShadingPossible(shadingFace, toBeShadedFace, vector, count = 0):
    
    
    # find the points of shadingFace
    crvPoints = findDiscontinuity(shadingFace.boundary, style = 4)
    
    shadingPts = []
    nonShadingPts = []
    thereIsMorePoint = True
    while len(shadingPts) * len(nonShadingPts) == 0 and thereIsMorePoint:
        # project to point
        for pt in crvPoints:
            projectedPt = projectToPlane(rc.Geometry.Point3d(pt), toBeShadedFace.plane, vector)
            pVector = rc.Geometry.Vector3d(projectedPt - pt)
            
            #print int(math.degrees(rc.Geometry.Vector3d.VectorAngle(vector, pVector)))
            if int(math.degrees(rc.Geometry.Vector3d.VectorAngle(vector, pVector))) == 0 or pVector.Length < tol:
                #print 'yup!'
                shadingPts.append(pt)
            else:
                #print 'noch!'
                nonShadingPts.append(pt)
        
        thereIsMorePoint = False
    
    if len(shadingPts) * len(nonShadingPts) != 0:
        # this is a mixed situation, I need to subdivide toBeShadedFace
        # and run the study for each part of the surface
        # the function ideally can be written as a recursive function
        # but I need to fix the rest of the code and the way I wrote the class
        # for faces which I'll do later
        count += 1
        
        # Rhino kept crashing when I wrote this function as recursive function
        # now I'm trying it in a stupid way
        res = isShadingPossible2(toBeShadedFace, shadingFace, vector)
        if res == True or res == False: return not res
        else: return 'Complicated'
        #try:
        #meshList = rc.Geometry.Mesh.Split(shadingFace.geometry, toBeShadedFace.plane)
        #if len(meshList) == 2:
        #    for m in meshList:
        #        mesh = pseudoFace(m)
        #        if isShadingPossible(mesh, toBeShadedFace, count): return True
        #        elif count > 3: return 'Complicated'
        #        else:
        #            print count
        #            count += 1
        #else:
        #return 'Complicated'
        #except Exception, e:
            
        #    print `e`
        
    
    elif len(shadingPts)!= 0: return True
    
    elif len(nonShadingPts)!=0: return False


def isShadingPossible2(shadingFace, toBeShadedFace, vector, count = 0):
    
    # the same function! just copied twice as it was making the component to crash on recursive runs
    # find the points of shadingFace
    crvPoints = findDiscontinuity(shadingFace.boundary, style = 4)
    
    shadingPts = []
    nonShadingPts = []
    thereIsMorePoint = True
    while len(shadingPts) * len(nonShadingPts) == 0 and thereIsMorePoint:
        # project to point
        for pt in crvPoints:
            projectedPt = projectToPlane(rc.Geometry.Point3d(pt), toBeShadedFace.plane, vector)
            pVector = rc.Geometry.Vector3d(projectedPt - pt)
            
            #print int(math.degrees(rc.Geometry.Vector3d.VectorAngle(vector, pVector)))
            if int(math.degrees(rc.Geometry.Vector3d.VectorAngle(vector, pVector))) == 0 or pVector.Length < tol:
                #print 'yup!'
                shadingPts.append(pt)
            else:
                #print 'noch!'
                nonShadingPts.append(pt)
        
        thereIsMorePoint = False
    
    if len(shadingPts) * len(nonShadingPts) != 0:
        # this is a mixed situation, I need to subdivide toBeShadedFace
        # and run the study for each part of the surface
        # the function ideally can be written as a recursive function
        # but I need to fix the rest of the code and the way I wrote the class
        # for faces which I'll do later
        count += 1
        #return checkReverse(shadingFace, toBeShadedFace)
        #return 'Complicated'
        #try:
        #meshList = rc.Geometry.Mesh.Split(shadingFace.geometry, toBeShadedFace.plane)
        #if len(meshList) == 2:
        #    for m in meshList:
        #        mesh = pseudoFace(m)
        #        if isShadingPossible(mesh, toBeShadedFace, count): return True
        #        elif count > 3: return 'Complicated'
        #        else:
        #            print count
        #            count += 1
        #else:
        return 'Complicated'
        #except Exception, e:
            
        #    print `e`
        
    
    elif len(shadingPts)!= 0: return True
    
    elif len(nonShadingPts)!=0: return False

class createFace(object):
    
    def __init__(self, numOfGeometry, numOfFace, mesh, boundary, centerPt, normal):
        
        self.parentID = numOfGeometry
        self.ID = numOfFace
        self.fullID = `self.parentID` + '_' + `self.ID`
        self.geometry = mesh
        self.centerPt = centerPt
        self.normal = normal
        self.boundary = boundary
        self.plane = rc.Geometry.Plane(self.centerPt, self.normal)
        self.shadedBySrfsList = []
        self.ShadingSrfsList = []
    
    def getOutlineCrvFromSun (self, sunVector):
        self.planeFromSun = rc.Geometry.Plane(self.centerPt, sunVector)
        
        self.outlineCrvFromSun = []
        polylines = self.geometry.GetOutlines(self.planeFromSun)
        [self.outlineCrvFromSun.append(pl.ToNurbsCurve()) for pl in polylines]
        
    def isShadingFaces(self, surface):
        self.shadingSrfsList.append(surface.fullID)
    
    def isShadedByFaces(self, surface):
        self.shadedSrfsList.append(surface.fullID)


# for now I copy pasted this code but it should be re-written later
# class for each surface can be made inside this function
centerPts, srfNormals, listOfBoundaryLists, meshes = parallel_testPointCalculator(_geometry, 0)

### generate faces
facesList = {}
if _sunVector!=None:
    # each geometry (closed mesh)
    for geoCount, boundaries in enumerate(listOfBoundaryLists):
        # each face curve
        for faceCount, boundary in enumerate(boundaries):
            id = `geoCount` + '_' + `faceCount`
            mesh = meshes[geoCount][faceCount]
            boundary = listOfBoundaryLists[geoCount][faceCount]
            centerPt = centerPts[geoCount][faceCount]
            normal = srfNormals[geoCount][faceCount]
            
            facesList[id] = createFace(geoCount, faceCount, mesh, boundary, centerPt, normal)
            
            # prepare data for shadow calculation
            facesList[id].getOutlineCrvFromSun(_sunVector)
    
    
    shadowCrvsCollection = []
    shaded = []
    
    
    for toBeShadedFaceID in facesList.keys():
        
        toBeShadedFace = facesList[toBeShadedFaceID]
        
        shadowCrvs = []
        
        # check if the face is facing the sun
        if rc.Geometry.Vector3d.VectorAngle(toBeShadedFace.normal, _sunVector) > math.pi/2:
            
            for shadingFaceID in facesList.keys():
                
                shadingFace = facesList[shadingFaceID]
                
                # self shading will be added later
                if shadingFace.parentID != toBeShadedFace.parentID and (toBeShadedFace.fullID not in shadingFace.shadedBySrfsList):
                    
                    shadingRelationShip = isShadingPossible(shadingFace, toBeShadedFace,  _sunVector)
                    
                    if  shadingRelationShip == 'Complicated':
                        # toBeShadedFace needs to be splitted I write this later
                        # let's just get it to work for now
                        print 'one complicated case!'
                        pass
                    
                    elif shadingRelationShip:
                        # project curve to plane
                        projectedCurve = projectToPlane(shadingFace.boundary.Duplicate(), toBeShadedFace.plane, _sunVector)
                        
                        try:
                            # find the intersection between the curve and the outline
                            shadowCrv = rc.Geometry.Curve.CreateBooleanIntersection(toBeShadedFace.boundary, projectedCurve)[0]
                            # add to shadowCrvList if any
                            shadowCrvs.append(shadowCrv)
                            toBeShadedFace.isShadedByFaces(shadingFace)
                            shadingFace.isShadingByFaces(toBeShadedFace)
                        
                        except:
                             pass
                
            # boolean union all the shadows on the same surface
            uShadowCrv = rc.Geometry.Curve.CreateBooleanUnion(shadowCrvs)
            if len(uShadowCrv)!=0:
                for c in uShadowCrv: shadowCrvsCollection.append(c)
            elif len(shadowCrvs)!=0:
                for c in shadowCrvs: shadowCrvsCollection.append(c)
                        
        else:
            # is not facing the sun
            shaded.append(toBeShadedFace.boundary)


        shadow = shadowCrvsCollection
        shade = shaded

