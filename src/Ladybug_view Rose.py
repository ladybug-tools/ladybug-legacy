# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
ViewRose
-
Provided by Ladybug 0.0.52
    
    Args:
        _context: Context buildings as Brep or Mesh
        _plane: Test plane. Default is XY plane
        _radius: Study radius in meters
    Returns:
        readMe!: View Angles
        viewRose: The visible area
        blocked: The blocked area
        visibleAngle: Total visible angle
"""

ghenv.Component.Name = "Ladybug_view Rose"
ghenv.Component.NickName = 'viewRose'
ghenv.Component.Message = 'VER 0.0.52\nNOV_01_2013'

import Rhino as rc
import System
import scriptcontext as sc
import math

def joinMesh(meshList):
    joinedMesh = rc.Geometry.Mesh()
    for m in meshList: joinedMesh.Append(m)
    return joinedMesh
    
def castPolylineToCurve(polylineList):
    curves = []
    for pl in polylineList: curves.append(pl.ToNurbsCurve())
    return curves

def separateClosedCrvs(curves):
    closedCrvs = []
    openCrvs = []
    
    for curve in curves:
        if curve.IsClosed: closedCrvs.append(curve)
        else: openCrvs.append(curve)
    
    return closedCrvs, openCrvs

def getOutlineCrvs(closedCrvs):
    crvList = [] #create a list to convert the array to list
    outlineCrvs = rc.Geometry.Curve.CreateBooleanUnion(closedCrvs)
    if outlineCrvs: crvList.extend(outlineCrvs)
    else: crvList.extend(closedCrvs)
    return crvList

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
    if includeEndPts: points.append(curve.PointAtStart)
    get_next = True
    while get_next:
        get_next, t = curve.GetNextDiscontinuity(System.Enum.ToObject(rc.Geometry.Continuity, style), t0, t1)
        if get_next:
            points.append(curve.PointAt(t))
            t0 = t # Advance to the next parameter
    if includeEndPts: points.append(curve.PointAtEnd)
    return points

class Domain(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def length(self):
        return self.end - self.start
        
    def mergeDomain(self, otherDomain):
        if self.start > otherDomain.start:
            # change the order to have them sorted
            self, otherDomain = otherDomain, self
            
        if otherDomain.start <= self.end:
            return [Domain(self.start, max(self.end, otherDomain.end))]
        else:
            # the ranges are separated
            return [self, otherDomain]
            
    def __str__(self):
        return "%.3f"%self.start + ' To ' + "%.3f"%self.end

class Range(object):
    def __init__(self, start, mid, end, minValue = 0, maxValue = 360):
        self.start = start
        self.mid = mid
        self.end = end
        self.minValue = minValue
        self.maxValue = maxValue
        
    def analyzeRange(self):
        
        if self.start == self.end:
            return []
        elif self.start < self.mid < self.end:
            return [Domain(self.start, self.end)]
        elif self.start > self.mid > self.end:
            return [Domain(self.end, self.start)]
        else:
            return [Domain(max(self.start, self.end), self.maxValue), Domain(self.minValue, min(self.start, self.end))]

    
def sortDomains(domainsList):
    return sorted(domainsList, key = lambda x: x.start)

def mergeDomains(domainList):
    # sort the domains
    sortedDomains = sortDomains(domainList)
    
    # list for the result
    mergedDomains = []
    
    # return the list if it is a single domain
    if len(sortedDomains) == 1: return sortedDomains
    
    # start with the fist domain:
    # for dom in sortedDomains: print dom
    testDomain = sortedDomains[0]
    
    # print testDomain
    # try to merge it with the 
    for dom in sortedDomains[1:]:
        # print dom
        mergedDomain = testDomain.mergeDomain(dom)
        
        if len(mergedDomain) == 1:
            #print "merged"
            testDomain = mergedDomain[0]
        else:
            # print "separated lists"
            testDomain = mergedDomain[1]
            mergedDomains.append(mergedDomain[0])
    
    mergedDomains.append(testDomain)
    return mergedDomains

def getViewBlockedCurve(testPlane, radius, studyCircle, blockingCurve):
    
    referenceVector = testPlane.YAxis
    
    def getUnitizedMovingVector(Pt1, Pt2):
        movingVec = rc.Geometry.Vector3d(Pt2 - Pt1)
        movingVec.Unitize()
        return movingVec
    
    testPt = testPlane.Origin
    newRadius = 1.6 * radius
    
    # simplify blockingCurve
    simplifyOptions = rc.Geometry.CurveSimplifyOptions.All  
    blockingCurve = blockingCurve.Simplify(simplifyOptions, sc.doc.ModelAbsoluteTolerance, sc.doc.ModelAngleToleranceRadians)

    
    crvSegments = blockingCurve.DuplicateSegments()
    
    if crvSegments.Count == 0:
        crvSegments = [blockingCurve] # for some reason duplicate returns null for a single line
    
    triangles = []
    blockedDomains = []
    for crv in crvSegments:
        # find points of each curve
        points = findDiscontinuity(crv, 4)
        
        # make the lines between every two points
        firstPt = points[0]
        
        #print 'num of points = ' + `len(points)`
        for nextPt in points[1:]:
            #create the segment 
            vector1 = newRadius * getUnitizedMovingVector(testPt, firstPt)
            midVector = newRadius * getUnitizedMovingVector(testPt, (firstPt + nextPt)/2)
            vector2 = newRadius * getUnitizedMovingVector(testPt, nextPt)
            
            if math.degrees(rc.Geometry.Vector3d.VectorAngle(vector1, vector2, testPlane))== 180:
                #alternate method for midVector
                midVector = rc.Geometry.Vector3d(vector1)
                midVector.Rotate(math.radians(-90), testPlane.Normal)
                
            # create the arc
            pt1 = rc.Geometry.Point3d.Add(testPt, vector1)
            midPt = rc.Geometry.Point3d.Add(testPt, midVector)
            pt2 = rc.Geometry.Point3d.Add(testPt, vector2)
            
            arc = rc.Geometry.Arc(pt1, midPt, pt2).ToNurbsCurve()
            
            # create the polyline
            ptList = [pt2, testPt, pt1]
            polyline = rc.Geometry.Polyline(ptList).ToNurbsCurve()
            
            fullSegment = rc.Geometry.Curve.JoinCurves([polyline, arc])[0]
            
            # find the blocked domain
            startAngle = math.degrees(rc.Geometry.Vector3d.VectorAngle(referenceVector, vector1, testPlane))
            midAngle = math.degrees(rc.Geometry.Vector3d.VectorAngle(referenceVector, midVector, testPlane))
            endAngle = math.degrees(rc.Geometry.Vector3d.VectorAngle(referenceVector, vector2, testPlane))
            
            thisRange = Range(startAngle, midAngle, endAngle)
            blocked = thisRange.analyzeRange()
            # for dom in blocked: print dom
            # print "*****************"
            blockedDomains.extend(blocked)
            
            # part to be removed as user can see this triangle
            triangle = rc.Geometry.Polyline([firstPt, testPt, nextPt, firstPt]).ToNurbsCurve()
            
            try: blockedComponent = rc.Geometry.Curve.CreateBooleanDifference(fullSegment, [triangle])
            except: blockedComponent = [triangle] #fullSegment
            nextPt = firstPt
            triangles.extend(blockedComponent)
            
            
    return triangles, blockedDomains

def main(mesh, testPlane, radius):
    # create a plane based on test point
    # testPlane = rc.Geometry.Plane(testPt, rc.Geometry.Vector3d.ZAxis)
    
    # intersect the plane with test geometries
    polylines = rc.Geometry.Intersect.Intersection.MeshPlane(joinMesh(mesh), testPlane)
    
    if polylines:
        # join intersection curves
        outlineCurves = rc.Geometry.Curve.JoinCurves(castPolylineToCurve(polylines))
        
        # get rid of duplicate and interior curves
        # separate closed curves
        closedCrvs, openCrvs = separateClosedCrvs(outlineCurves)
        
        
        
        
        # find outline of the closed curves
        outlineClosedCrvs = getOutlineCrvs(closedCrvs)
        
        
        # put the final list of the curves together
        finalOutline = outlineClosedCrvs + openCrvs
        
        
        ################################################################################
        studyC = rc.Geometry.Circle(testPlane, radius).ToNurbsCurve()
        outlineC = rc.Geometry.Circle(testPlane, 1.05 * radius).ToNurbsCurve() 
        
        
        blockedViews = []
        outlines = []
        #print len(finalOutline)
        for crv in finalOutline:
             # At some point I should change the calculation of the blocking triangle to be based
             # blocking domain and not real geometries as it can easily fail
             # and nevertheless I need to do it for VSC
             triangles, blockedView = getViewBlockedCurve(testPlane, radius, studyC, crv)
             
             blockedViews.extend(blockedView)
             
             try:
                 uniTriangles = rc.Geometry.Curve.CreateBooleanUnion(triangles)[0]
                 
             except Exception, e:
                 try: uniTriangles = triangles[0]
                 except: pass
             
             try:
                 outlines.append(rc.Geometry.Curve.CreateBooleanIntersection(outlineC, uniTriangles)[0])
             except Exception, e:
                 print "Test point is intersecting with one of the geometries."
                 pass
                 #return outlineC, uniTriangles, []
                 #return [], [], []
        
        uOutlines = rc.Geometry.Curve.CreateBooleanUnion(outlines)
        if not uOutlines: uOutlines = outlines
        
        # print len(uOutlines)
        for ol in uOutlines: 
            try:
                studyC = rc.Geometry.Curve.CreateBooleanDifference(studyC, ol)[0]
            except Exception, e:
                print "Boolean Diffrence Failed!"
                
        viewRose = rc.Geometry.Brep.CreatePlanarBreps(studyC)
        
        mergedBlockedViews = mergeDomains(blockedViews)
        
    else:
        viewRose = rc.Geometry.Brep.CreatePlanarBreps(rc.Geometry.Circle(testPlane, 1.05 * radius).ToNurbsCurve())
        outlines = []
        mergedBlockedViews = []
        print "No block!"
        
    return viewRose, outlines, mergedBlockedViews
    
    
if _context and _radius:
    if _plane_ == None: _plane_= rc.Geometry.Plane.WorldXY
    viewRose, blocked, blockedRange = main(_context, _plane_, _radius)
    visibleAngle = 360
    if len(blockedRange)!=0: print "Blocked Angles:"
    for dom in blockedRange:
        print dom
        visibleAngle -= dom.length()
else:
    print "At least one of the inputs is missing!"