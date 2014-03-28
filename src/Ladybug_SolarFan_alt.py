# By Saeran Vasanthakumar
# saeranv@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to generate a Solar Fan for a closed boundary curve and a required minimum hours of solar access to the area inside this boundary curve.  
The solar fan is used to ensure that a given property within a boundary curve is guarenteed a specified minimum hours of direct solar access for each day in a specified month range of the year.
Thus, context geometries surrounding this boundary curve that do not penetrate the Solar Fan will not cast shadows onto the boundary area for the specified hour and month range.

The start and end dates that determine the month range for solar access can be chosen from the following options:
0) Mar 21 - Jun 21
1) Mar 21 - Sep 21
2) Mar 21 - Dec 21
3) Jun 21 - Sep 21
4) Jun 21 - Dec 21
5) Sep 21 - Dec 21
The default set to 3) June 21 to September 21.

Note that extremely complicated concave shapes will take a long time to calculate a solar fan for.

-
Provided by Ladybug 0.0.57
    
    Args:
        _boundary:  closed boundary curve representing a piece of land (such as a park) or a window for which solar access is desired.
        _location: The output from the importEPW or constructLocation component.  This is essentially a list of text summarizing a location on the earth.
        _requiredHours: The number of hours of direct solar access that the property inside the boundary curve should receive during the _monthRange.
        _height: The number of Rhino model units that the solar fan should be extended above the boundary curve.
        north_: Input a vector to be used as a true North direction or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _monthRange: An optional interger value to change the month range for which solar access is being considered. The default month range is Jun 21 - Sep 21.
            Intergers input here must be between 0 - 5 and correspond to the following :
            ---
            0 = Mar 21 - Jun 21
            1 = Mar 21 - Sep 21
            2 = Mar 21 - Dec 21
            3 = Jun 21 - Sep 21
            4 = Jun 21 - Dec 21
            5 = Sep 21 - Dec 21
            ---
            Where, in the North/South Hemispheres, these dates repsectively signify:  
                Mar 21 = Vernal/Autumnal Equinox
                Jun 21 = Summer/Winter Solstice
                Sep 21 = Autumnal/Vernal Equinox
                Dec 21 = Winter/Summer Solstice
 
    Returns:
        solarFan: Brep representing a solar fan.  This volume should be clear of shading in order to ensure solar access to the area inside the boundary curve for the given number of hours.
"""

ghenv.Component.Name = "Ladybug_SolarFan_alt"
ghenv.Component.NickName = 'SolarFan Alternative'
ghenv.Component.Message = 'VER 0.0.57\nMAR_26_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import math
import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import datetime
import random
from decimal import Decimal as D
import Grasshopper.Kernel as gh

""" --------------------------3D CONVEX HULL CLASSES------------------------------"""

""" The following code class for 3D convex hull is from 
    http://michelanders.blogspot.ca/2012/02/3d-convex-hull-in-python.html
"""
debug = False
class Vector:
	def __init__(self,x,y,z):
		self.x=x
		self.y=y
		self.z=z
	
	def __str__(self):
		return str(self.x)+" "+str(self.y)+" "+str(self.z)

	def __sub__(self,other):
		return Vector(other.x-self.x,other.y-self.y,other.z-self.z)
	
	def __add__(self,other):
		return Vector(other.x+self.x,other.y+self.y,other.z+self.z)


class Vertex:
	def __init__(self,v,vnum=None,duplicate=None,onhull=False,mark=False):
		self.v = v
		self.vnum = vnum
		self.duplicate = duplicate # ref to incident cone edge (or None)
		self.onhull = onhull # T iff point on hull.
		self.mark = mark # T iff point already processed.
	
	def __str__(self):
		return str(self.v.x)+" "+str(self.v.y)+" "+str(self.v.z)
	
	def debug(self):
		return "Vertex: %d %s dup:%s onhull:%s mark:%s\n"%(self.vnum,self.v,self.duplicate,self.onhull,self.mark)
		
	@staticmethod
	def Collinear(a,b,c):
		"""
		Collinear checks to see if the three vertices given are collinear,
		by checking to see if each element of the cross product is zero.
		"""
		return ( abs(( c.v.z - a.v.z ) * ( b.v.y - a.v.y ) -
		( b.v.z - a.v.z ) * ( c.v.y - a.v.y )) <1e-4
	and abs(( b.v.z - a.v.z ) * ( c.v.x - a.v.x ) -
		( b.v.x - a.v.x ) * ( c.v.z - a.v.z )) <1e-4
	and abs(( b.v.x - a.v.x ) * ( c.v.y - a.v.y ) -
		( b.v.y - a.v.y ) * ( c.v.x - a.v.x )) <1e-4 )

class Edge:
	enum = 0
	
	def __init__(self,adjface=[None,None],endpts=[None,None],newface=None,delete=False):
		self.adjface = []
		self.adjface.extend(adjface)
		self.endpts = []
		self.endpts.extend(endpts)
		self.newface = newface # ref to incident cone face
		self.delete = delete # T iff edge should be deleted
		self.enum = Edge.enum
		Edge.enum+=1
		
	def __str__(self):
		af=[str(f.fnum) if not (f is None) else '.' for f in self.adjface]
		return "edge(%d): %s %s del: %s newf: %d adjf:%s"%(self.enum,self.endpts[0],self.endpts[1],self.delete,self.newface.fnum if not (self.newface is None) else -1," ".join(af))
		
class Face:
	fnum=0
	def __init__(self,edge=[None,None,None],vertex=[None,None,None],visible=False):
		self.edge = []
		self.edge.extend(edge)
		self.vertex = []
		self.vertex.extend(vertex)
		self.visible = visible # T iff face visible from new point
		self.fnum = Face.fnum
		Face.fnum+=1
		
	def __str__(self):
		return """facet normal 0 0 0
outer loop
vertex %s
vertex %s
vertex %s
endloop
endfacet"""%(self.vertex[0],self.vertex[1],self.vertex[2])

	def debug(self):
		return "Face(%d) visble: %s\n\t%s\t%s\t%s"%(self.fnum,self.visible,self.vertex[0].debug(),self.vertex[1].debug(),self.vertex[2].debug())
		
	def InitEdges(self, fold=None):
		v0=self.vertex[0]
		v1=self.vertex[1]
		v2=self.vertex[2]
		newedges=[]
		# Create edges of the initial triangle
		if fold is None:
			e0 = Edge()
			e1 = Edge()
			e2 = Edge()
			newedges=[e0,e1,e2]
		else: # Copy from fold, in reverse order
			e0 = fold.edge[2]
			e1 = fold.edge[1]
			e2 = fold.edge[0]
		e0.endpts[0] = v0
		e0.endpts[1] = v1
		e1.endpts[0] = v1
		e1.endpts[1] = v2
		e2.endpts[0] = v2
		e2.endpts[1] = v0
	
		self.edge[0] = e0
		self.edge[1] = e1
		self.edge[2] = e2
	
		# Link edges to face
		e0.adjface[0] = self
		e1.adjface[0] = self
		e2.adjface[0] = self

			
		return newedges
		
	def MakeCcw(f,e,p): # the customary self is called f here instead of self
		"""
		MakeCcw puts the vertices in the face structure in counterclock wise 
		order.  We want to store the vertices in the same 
		order as in the visible face.  The third vertex is always p.

		Although no specific ordering of the edges of a face are used
		by the code, the following condition is maintained for each face f:
		one of the two endpoints of f.edge[i] matches f.vertex[i]. 
		But note that this does not imply that f.edge[i] is between
		f.vertex[i] and f.vertex[(i+1)%3].  (Thanks to Bob Williamson.)
		"""
		
		# fv	The visible face adjacent to e
		# i     Index of e.endpoint[0] in fv
	
		if e.adjface[0].visible:      
			fv = e.adjface[0]
		else:
			fv = e.adjface[1]
	
		# Set vertex[0] & [1] of f to have the same orientation
		# as do the corresponding vertices of fv
		i=0
		while(fv.vertex[i] != e.endpts[0]):
			i+=1
		# Orient f the same as fv
		swap=False
		if fv.vertex[ (i+1) % 3 ] != e.endpts[1] :
			f.vertex[0] = e.endpts[1]  
			f.vertex[1] = e.endpts[0]    
		else:
			f.vertex[0] = e.endpts[0]   
			f.vertex[1] = e.endpts[1]   
			(f.edge[1], f.edge[2] ) = (f.edge[2], f.edge[1] )
			#print('swapped') 
			# This swap is tricky. e is edge[0]. edge[1] is based on endpt[0],
			# edge[2] on endpt[1].  So if e is oriented "forwards," we
			# need to move edge[1] to follow [0], because it precedes. */

		f.vertex[2] = p
		
# Define flags
ONHULL = True
REMOVED = True
VISIBLE  = True
PROCESSED = True

class Hull:
	def __init__(self,v):
		self.vertices = []
		self.edges = []
		self.faces = []
		self.ReadVertices(v)
		v=self.DoubleTriangle()
		self.ConstructHull(v)
		self.EdgeOrderOnFaces()

	def ReadVertices(self,v):
		self.vertices = [ Vertex(vc,i) for i,vc in enumerate(v) ]
		
	def EdgeOrderOnFaces(self):
		"""
		EdgeOrderOnFaces: puts e0 between v0 and v1, e1 between v1 and v2,
		e2 between v2 and v0 on each face.  This should be unnecessary, alas.
		"""
		for f in self.faces:
			for i in (0,1,2):
				if ( not (((f.edge[i].endpts[0] == f.vertex[i]) and
					(f.edge[i].endpts[1] == f.vertex[(i+1)%3])) or
					((f.edge[i].endpts[1] == f.vertex[i]) and
					(f.edge[i].endpts[0] == f.vertex[(i+1)%3])))):
					# Change the order of the edges on the face
					for j in (0,1,2):
						# find the edge that should be there
						if (((f.edge[j].endpts[0] == f.vertex[i]) and
							(f.edge[j].endpts[1] == f.vertex[(i+1)%3])) or
							((f.edge[j].endpts[1] == f.vertex[i]) and
							(f.edge[j].endpts[0] == f.vertex[(i+1)%3]))) :
							# Swap it with the one erroneously put into its place
							(f.edge[i],f.edge[j]) = (f.edge[j],f.edge[i])
	def __str__(self):
		s=["solid points"]
		for f in self.faces:
			s.append(str(f))
		s.append("endsolid points")
		return "\n".join(s)
		
	def debug(self,msg=''):
		s=[msg+'\n']
		for f in self.faces:
			s.append(f.debug())
		s.append('-'*40)
		return "".join(s)
		
	@staticmethod
	def VolumeSign(f,p):
		"""
		VolumeSign returns the sign of the volume of the tetrahedron determined by f
		and p.  VolumeSign is +1 iff p is on the negative side of f,
		where the positive side is determined by the rh-rule.  So the volume 
		is positive if the ccw normal to f points outside the tetrahedron.
		The final fewer-multiplications form is due to Bob Williamson.
		
		This implementation differs from the one in the book in that it does not assume that
		coordinates are integers.
		"""
		a=f.vertex[0].v - p.v
		b=f.vertex[1].v - p.v
		c=f.vertex[2].v - p.v
		
		vol = ( a.x * (b.y*c.z - b.z*c.y)
		+ a.y * (b.z*c.x - b.x*c.z)
		+ a.z * (b.x*c.y - b.y*c.x) )
		epsilon = 1e-7
		if abs(vol) >  epsilon:
			if vol>0 : return 1
			else : return -1
		else:
			ax=D(a.x)
			ay=D(a.y)
			az=D(a.z)
			bx=D(b.x)
			by=D(b.y)
			bz=D(b.z)
			cx=D(c.x)
			cy=D(c.y)
			cz=D(c.z)
			vol = ( ax * (by*cz - bz*cy)
			+ ay * (bz*cx - bx*cz)
			+ az * (bx*cy - by*cx) )
			if vol<D(0.0):
				return -1
			elif vol>D(0.0):
				return 1
		return 0

	def ShowEdges(self,msg=""):
		print(msg)
		for e in self.edges:
			if e.adjface[0] is None or e.adjface[1] is None :
				print(str(e))
				
	def ShowNewEdges(self,msg=""):
		print(msg,len(self.newedges))
		for e in self.newedges:
			print(str(e))
				
	def DoubleTriangle(self):
		"""
		DoubleTriangle builds the initial double triangle.  It first finds 3 
		noncollinear points and makes two faces out of them, in opposite order.
		It then finds a fourth point that is not coplanar with that face.  The  
		vertices are stored in the face structure in counterclockwise order so 
		that the volume between the face and the point is negative. Lastly, the
		3 newfaces to the fourth point are constructed and the data structures
		are cleaned up. 
		"""

		# Find 3 noncollinear points
		v0 = 0
		nv = len(self.vertices)
		while(Vertex.Collinear(self.vertices[v0%nv],self.vertices[(v0+1)%nv],self.vertices[(v0+2)%nv])):
			v0 = (v0+1)%nv
			if v0 == 0:
				raise Exception("DoubleTriangle:  All points are Collinear!")
				
		v1 = (v0+1)%nv
		v2 = (v1+1)%nv
	
		# Mark the vertices as processed
		self.vertices[v0].mark = PROCESSED
		self.vertices[v1].mark = PROCESSED
		self.vertices[v2].mark = PROCESSED

		# Create the two "twin" faces
		self.faces.append(Face(vertex=[self.vertices[v0],self.vertices[v1],self.vertices[v2]]))
		f0=self.faces[-1]
		self.edges.extend(f0.InitEdges())
		self.faces.append(Face(vertex=[self.vertices[v2],self.vertices[v1],self.vertices[v0]]))
		f1=self.faces[-1]
		self.edges.extend(f1.InitEdges(f0))

		# Link adjacent face fields.

		f0.edge[0].adjface[1] = f1
		f0.edge[1].adjface[1] = f1
		f0.edge[2].adjface[1] = f1
		f1.edge[0].adjface[1] = f0
		f1.edge[1].adjface[1] = f0
		f1.edge[2].adjface[1] = f0
	
		#Find a fourth, noncoplanar point to form tetrahedron
		v3 = (v2+1)%nv
		vol = self.VolumeSign( f0, self.vertices[v3] )
		while vol == 0:
			v3 = (v3+1)%nv
			if v3==0:
				raise Exception("DoubleTriangle:  All points are coplanar!")
			vol = self.VolumeSign( f0, self.vertices[v3] )
	
		if debug: print(self.debug('initial'))
			
		return v3
		
	def ConstructHull(self,v):
		"""
		ConstructHull adds the vertices to the hull one at a time.  The hull
		vertices are those in the list marked as onhull.
		"""

		# vertices is supposed to be a circular list that we traverse once, starting at v
		# however, the call to CleanUp may delete vertices from this list
		ev = v
		while(True):
			if not self.vertices[v].mark:
				self.vertices[v].mark = PROCESSED;
			self.AddOne(self.vertices[v]);
			ev,v=self.CleanUp(ev,v) # cleanup may delete vertices!
			if v == ev : break
			
	def AddOne(self,p):
		"""
		AddOne is passed a vertex.  It first determines all faces visible from 
		that point.  If none are visible then the point is marked as not 
		onhull.  Next is a loop over edges.  If both faces adjacent to an edge
		are visible, then the edge is marked for deletion.  If just one of the
		adjacent faces is visible then a new face is constructed.
		"""
		
		vis = False

		# Mark faces visible from p.
		for f in self.faces:
			vol = self.VolumeSign( f, p )
			if vol < 0 : 
				f.visible = VISIBLE
				vis = True;                      

		# If no faces are visible from p, then p is inside the hull
		if not vis:
			p.onhull = not ONHULL  
			return False 

		# Mark edges in interior of visible region for deletion.
		# Erect a newface based on each border edge
		self.newedges=[]
		count=0
		for e in self.edges:
			if e.adjface[0].visible and	e.adjface[1].visible:
				# e interior: mark for deletion
				e.delete = REMOVED
			elif e.adjface[0].visible or e.adjface[1].visible: 
				# e border: make a new face
				e.newface = self.MakeConeFace( e, p )
				count+=1
		self.edges.extend(self.newedges)
		if debug : print(self.debug('addone'))
		
		return True

	def MakeConeFace(self,e,p):
		"""
		MakeConeFace makes a new face and two new edges between the 
		edge and the point that are passed to it. It returns a pointer to
		the new face.
		"""
		
		new_edge=[None,None]
		dupc=0
		# Make two new edges (if it doesn't already exist)
		for i in (0,1):
			# If the edge exists, copy it into new_edge
			# Otherwise (duplicate is NULL), MakeNullEdge
			d = e.endpts[i].duplicate
			if d is None:
				new_edge[i] = Edge(endpts=[e.endpts[i],p])
				e.endpts[i].duplicate = new_edge[i]
				self.newedges.append(new_edge[i])
			else:
				new_edge[i] = d
				dupc += 1

		# Make the new face
		new_face = Face(edge=[e,new_edge[0],new_edge[1]])
		self.faces.append(new_face)
		new_face.MakeCcw( e, p )
		
		# Set the adjacent face pointers
		count=0
		for i in (0,1):
			for j in (0,1):
				# Only one None link should be set to new_face
				if new_edge[i].adjface[j] is None:
					new_edge[i].adjface[j] = new_face
					count+=1
					break
		#print(new_face.fnum,count,dupc)
		return new_face

	def CleanUp(self,ev,v):
		"""
		CleanUp goes through each data structure list and clears all
		flags and NULLs out some pointers.  The order of processing
		(edges, faces, vertices) is important.
		"""
		de=self.CleanEdges()
		if debug: print(self.debug('cleanedges '+" ".join(de)))
		self.CleanFaces()
		if debug: print(self.debug('cleanfaces'))
		ev,v=self.CleanVertices(ev,v)
		if debug: print(self.debug('cleanvertices'))
		return ev,v
		
	def CleanEdges(self):
		"""
		CleanEdges runs through the edge list and cleans up the structure.
		If there is a newface then it will put that face in place of the 
		visible face and NULL out newface. It also deletes so marked edges.
		"""
		# Integrate the newface's into the data structure
		for e in self.edges:
			if e.newface:
				if e.adjface[0].visible:
					e.adjface[0] = e.newface
					if e.newface is None: print("0 XXXXXXXXXXXXXXXXXXXX")
				else:
					e.adjface[1] = e.newface
					if e.newface is None: print("1 XXXXXXXXXXXXXXXXXXXX")
			e.newface = None

		# Delete any edges marked for deletion. */
		deleted_edges = [str(e.enum) for e in self.edges if e.delete ]
		self.edges = [e for e in self.edges if not e.delete ]
		return deleted_edges
				
	def CleanFaces(self):
		"""
		CleanFaces runs through the face list and deletes any face marked visible.
		"""

		self.faces = [f for f in self.faces if not f.visible ]
		
	def CleanVertices(self,evi,vi):
		"""
		CleanVertices runs through the vertex list and deletes the 
		vertices that are marked as processed but are not incident to any 
		undeleted edges. 
		"""
		#self.ShowNewEdges("cv in evi:"+str(evi)+" vi:"+str(vi))

		# Mark all vertices incident to some undeleted edge as on the hull
		for e in self.edges:
			e.endpts[0].onhull = ONHULL
			e.endpts[1].onhull = ONHULL
		
		# Delete all vertices that have been processed but are not on the hull
		for i,v in enumerate(self.vertices):
			if v.mark and not v.onhull:
				del self.vertices[i]
				if i<evi : evi -= 1
				if i<vi : vi -= 1
		vi = (vi+1)%len(self.vertices)

		# Reset flags
		for v in self.vertices:
			v.duplicate = None
			v.onhull = not ONHULL
		
		#self.ShowNewEdges("cv out evi:"+str(evi)+" vi:"+str(vi))
		return evi,vi

	def add_object(self):
		verts = [v.v for v in self.vertices]
		vertmap =  {v.vnum:i for i,v in enumerate(self.vertices)}
		edges = []
		faces = [ [vertmap[v.vnum] for v in f.vertex] for f in self.faces]
		mesh = bpy.data.meshes.new(name='Convex Hull')
		mesh.from_pydata(verts, edges, faces)
		add_object_data(bpy.context, mesh, operator=None)
		#f=open("file.stl","w")
		#f.write(str(self))
		#f.close()

""" --------------------------3D CONVEX HULL CLASSES------------------------------"""


class SunCalculation:
    """ 
    Modified from: http://michelanders.blogspot.ca/2010/12/calulating-sunrise-and-sunset-in-python.html
    Calculate sunrise and sunset based on equations from NOAA
    http://www.srrb.noaa.gov/highlights/sunrise/calcdetails.html
    """
    def __init__(self,lat,long): # default Amsterdam
        self.lat=lat
        self.long=long
  
    def sunrise(self,when):
        """
        return the time of sunrise as a datetime.time object
        when is a datetime.datetime object. If none is given
        a local time zone is assumed (including daylight saving
        if present)
        """
        self.__preptime(when)
        self.__calc()
        return self.__timefromdecimalday(self.sunrise_t)
  
    def sunset(self,when):
        self.__preptime(when)
        self.__calc()
        return self.__timefromdecimalday(self.sunset_t)
  
    def solarnoon(self,when):
        self.__preptime(when)
        self.__calc()
        return self.__timefromdecimalday(self.solarnoon_t)
  
    @staticmethod
    def __timefromdecimalday(day):
        """
        returns a datetime.time object.
  
        day is a decimal day between 0.0 and 1.0, e.g. noon = 0.5
        """
        hours  = 24.0*day
        h = int(hours)
        minutes = (hours-h)*60
        m = int(minutes)
        seconds = (minutes-m)*60
        s = int(seconds)
        return datetime.time(hour=h,minute=m,second=s)

    def __preptime(self,when):
        """
        Extract information in a suitable format from when, 
        a datetime.datetime object.
        """
        # datetime days are numbered in the Gregorian calendar
        # while the calculations from NOAA are distibuted as
        # OpenOffice spreadsheets with days numbered from
        # 1/1/1900. The difference are those numbers taken for 
        # 18/12/2010
        self.day = when.toordinal()-(734124-40529)
        t=when.time()
        self.time= (t.hour + t.minute/60.0 + t.second/3600.0)/24.0
  
        self.timezone=0
        offset=when.utcoffset()
        if not offset is None:
            self.timezone=offset.seconds/3600.0 + (offset.days * 24)
  
    def __calc(self):
        """
        Perform the actual calculations for sunrise, sunset and
        a number of related quantities.
  
        The results are stored in the instance variables
        sunrise_t, sunset_t and solarnoon_t
        """
        timezone = self.timezone # in hours, east is positive
        longitude= self.long     # in decimal degrees, east is positive
        latitude = self.lat      # in decimal degrees, north is positive

        time = self.time # percentage past midnight, i.e. noon  is 0.5
        day = self.day     # daynumber 1=1/1/1900
 
        Jday = day+2415018.5+time-timezone/24 # Julian day
        Jcent =(Jday-2451545)/36525 # Julian century

        Manom = 357.52911+Jcent*(35999.05029-0.0001537*Jcent)
        Mlong = 280.46646+Jcent*(36000.76983+Jcent*0.0003032)%360
        Eccent = 0.016708634-Jcent*(0.000042037+0.0001537*Jcent)
        Mobliq = 23+(26+((21.448-Jcent*(46.815+Jcent*(0.00059-Jcent*0.001813))))/60)/60
        obliq = Mobliq+0.00256*math.cos(math.radians(125.04-1934.136*Jcent))
        vary = math.tan(math.radians(obliq/2))*math.tan(math.radians(obliq/2))
        Seqcent = math.sin(math.radians(Manom))*(1.914602-Jcent*(0.004817+0.000014*Jcent))+math.sin(math.radians(2*Manom))*(0.019993-0.000101*Jcent)+math.sin(math.radians(3*Manom))*0.000289
        Struelong = Mlong+Seqcent
        Sapplong = Struelong-0.00569-0.00478*math.sin(math.radians(125.04-1934.136*Jcent))
        declination = math.degrees(math.asin(math.sin(math.radians(obliq))*math.sin(math.radians(Sapplong))))
  
        eqtime = 4*math.degrees(vary*math.sin(2*math.radians(Mlong))-2*Eccent*math.sin(math.radians(Manom))+4*Eccent*vary*math.sin(math.radians(Manom))*math.cos(2*math.radians(Mlong))-0.5*vary*vary*math.sin(4*math.radians(Mlong))-1.25*Eccent*Eccent*math.sin(2*math.radians(Manom)))

        hourangle= math.degrees(math.acos(math.cos(math.radians(90.833))/(math.cos(math.radians(latitude))*math.cos(math.radians(declination)))-math.tan(math.radians(latitude))*math.tan(math.radians(declination))))

        self.solarnoon_t=(720-4*longitude-eqtime+timezone*60)/1440
        self.sunrise_t  =self.solarnoon_t-hourangle*4/1440
        self.sunset_t   =self.solarnoon_t+hourangle*4/1440

class ConvexHull2d:
    """Modifed from: http://tomswitzer.net/2009/12/jarvis-march/"""
    def __init__(self):
        self.TURN_LEFT, self.TURN_RIGHT, self.TURN_NONE = (1, -1, 0)
 
    def turn(self,p,q,r):
        """Returns -1, 0, 1 if p,q,r forms a right, straight, or left turn."""
        return cmp((q[0] - p[0])*(r[1] - p[1]) - (r[0] - p[0])*(q[1] - p[1]), 0)
 
    def _dist(self,p,q):
        """Returns the squared Euclidean distance between p and q."""
        dx, dy = q[0] - p[0], q[1] - p[1]
        return dx * dx + dy * dy
 
    def _next_hull_pt(self,points, p):
        """Returns the next point on the convex hull in CCW from p."""
        q = p
        for r in points:
            t = self.turn(p, q, r)
            if t == self.TURN_RIGHT or \
            t == self.TURN_NONE and \
            self._dist(p, r) > self._dist(p, q):
                q = r
        return q
 
    def convex_hull(self,points):
        """Returns the points on the convex hull of points in CCW order."""
        hull = [min(points)]
        for p in hull:
            q = self._next_hull_pt(points, p)
            if q != hull[0]:
                hull.append(q)
        return hull

class Curve2ConvexHull3d:
    def __init__(self):
        pass
        
    def convert_pts(self,pt):
        rc_pt = map(lambda p: rs.coerce3dpoint(p),pt)
        return map(lambda y: Vector(y[0],y[1],y[2]),rc_pt)

    def get_brep(self,pts):
        h = Hull(pts)
        #print i,h
        F = []
        for f in h.faces:
            ptlst = map(lambda i:rs.AddPoint(i.v.x,i.v.y,i.v.z), f.vertex)
            F.append(rs.AddPlanarSrf(rs.AddCurve(ptlst+[ptlst[0]],1)))
        brepfacelst = map(lambda c: rs.coercebrep(c),F)
        brep = rs.JoinSurfaces(brepfacelst)
        return brep

    def call_convexhull(self,p,count):
        ##print 'count:', count ##for testing
        if count > 20:
            return None
        else:
            #randomize pts
            random.shuffle(p)
            brep = self.get_brep(p)
            if brep != None:
                return brep
            else:
                # dare, dare again, always dare, 
                # and France is saved!  G.Danton
                return self.call_convexhull(p,count+1)

    def get_convexhull(self,lot):
        brep_lst = []
        pt_lst = []
        rs.EnableRedraw(False)
        for T in lot:
            bound = rs.CurvePoints(T[0])[:-1]
            chull = rs.CurvePoints(T[1])[:-1]
            Rhino.Geometry.Point3d.CullDuplicates(bound,TOL)
            Rhino.Geometry.Point3d.CullDuplicates(chull,TOL)
            pts = self.convert_pts(chull + bound)
            brep = self.call_convexhull(pts,0)
            if brep == None: 'brep=none -sv'
            brep_lst.append(brep)
            pt_lst.append(bound+chull)
        rs.EnableRedraw()
        return brep_lst,pt_lst

class CleanBrep:
    def __init__(self,tol,L):
        self.tol = tol
        self.L = L
    
    def safeUnionMethod(self,solarFans):
        """From Ladybug"""
        res = []
        x = solarFans[0]
        for fanCount in range(len(solarFans[1:])):
            if gh.GH_Document.IsEscapeKeyDown():
                    print "terminated!"
                    break
            try:
                rs.EnableRedraw(False)
                #x = solarFans[fanCount]
                y = solarFans[fanCount]
                x.Faces.SplitKinkyFaces(rc.RhinoMath.DefaultAngleTolerance, False)
                y.Faces.SplitKinkyFaces(rc.RhinoMath.DefaultAngleTolerance, False)
                a = rc.Geometry.Brep.CreateBooleanUnion([x, y], sc.doc.ModelAbsoluteTolerance)
                if a == None:
                    a = [x,solarFans[fanCount]]
                rs.EnableRedraw()
            except:
                a = [x,solarFans[fanCount]]
        
            if a:
                res.extend(a)
                x = y
        return res
    
    def slowUnionMethod(self,solarFans):
        fanlst = [solarFans.pop(0)]
        rs.EnableRedraw(False)
        for next_fan in solarFans:
            if gh.GH_Document.IsEscapeKeyDown():
                print "terminated!"
                break
            breplst = [fanlst[0],next_fan]
            boolean_result = Rhino.Geometry.Brep.CreateBooleanUnion(breplst,TOL)
            if boolean_result:
                fanlst = boolean_result
            else:
                return -1
            Rhino.RhinoApp.Wait()
        rs.EnableRedraw()
        return fanlst

    def unionFans(self): 
        if len(self.L) == 1: # convex
            #print 'no union' ## for testing
            return self.L
        else:
            #print 'safeiunionmethod' ## for testing
            fanlst = self.safeUnionMethod(self.L)
        
        if len(fanlst) > 1 and len(fanlst) < 10: # safeUnionMethod has failed
            #print 'slowunionmethod' ## for testing
            slowfanlst = self.slowUnionMethod(self.L)
            if slowfanlst != -1:
                fanlst = slowfanlst
        if len(fanlst) > 1: #final check
            error_union = \
            "Sorry your boundary geometry is too complicated for\n"\
            "this component too handle cleanly. If you boolean union\n"\
            "the multiple geometries that has been outputted, it will\n"\
            "give you your Solar Fan."
            print error_union
            #ghenv.Component.AddRuntimeMessage(ERROR_W,error_union)
        return fanlst

    def mergeface(self,brplst):
        map(lambda b: b.MergeCoplanarFaces(TOL),brplst)
        return brplst
    
    def cleanBrep(self):
        blst = self.unionFans()
        return self.mergeface(blst)

def readLocation(location):
    """From Ladybug"""
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
    return float(latitude), float(longitude), float(timeZone), float(elevation)

def get_sunpt(lat,cpt,month,day,hourlst,north_=0,lon=0,tZ=0,scale_=100):
    """modifed from Ladybug"""
    lb_sunpath = sc.sticky["ladybug_SunPath"]()
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    sunpt_lst = []
    for hour in hourlst:
        centerPt = rs.coerce3dpoint(cpt)
        northAngle_, northVector = lb_preparation.angle2north(north_)
        lb_sunpath.initTheClass(lat,northAngle=northAngle_,cenPt=centerPt,\
        scale=scale_,longtitude=lon, timeZone=tZ )
        lb_sunpath.solInitOutput(month,day,hour)
        sunpt_lst.append(lb_sunpath.sunPosPt()[2]) # basePoint.Location
        #return sunSphereMesh, sunVector, basePoint.Location
    return sunpt_lst

def get_plane(b,ht):
    endpt = rs.AddPoint(0,0,ht)
    startpt = rs.AddPoint(0,0,0)
    top_vec = rs.VectorCreate(endpt,startpt)
    top_pts = rs.CurvePoints(rs.CopyObject(b,top_vec))
    return rs.PlaneFitFromPoints(top_pts)

def project_curve(sunpts,cpt,topplane,b):
    L = []
    for spt in sunpts:
        line = cpt,spt
        proj_pt = rs.LinePlaneIntersection(line,topplane)
        vec = rs.VectorCreate(proj_pt,cpt)
        topcurve = rs.CopyObject(b,vec)
        L.append(topcurve)
    return L

def get_solarnoon(month,year,tz,d,lat,lon):
    """get_solarnoon: month -> solarnoon """ 
    date = datetime.datetime(year,month,d)
    SC = SunCalculation(lat,lon)
    snoon = SC.solarnoon(date)
    return snoon.hour + tz + snoon.minute/60.0

def clean_curve(b):
    """Clean curve geometry
        1. Checks if guid or object
        2. Simplifiebs
        3. Reverse curve dirn
        4. Closes curve if not already closed
    """
    if type(b) == type(rs.AddPoint(0,0,0)): # already guid
        pass
    else:
        b = sc.doc.Objects.AddCurve(b)
    rs.SimplifyCurve(b)
    # reverse curve direction
    boundarybrep = rs.coercecurve(b)
    Rhino.Geometry.Curve.Reverse(boundarybrep)
    sc.doc.Objects.Replace(b,boundarybrep)
    if rs.IsCurveClosed(b):
        return b
    else:
        return rs.CloseCurve(b)


def getSolarData(tp,s_snoon,e_snoon):
    # solar noon
    t = tp/2.0
    shourlst = [s_snoon-t,s_snoon+t]
    ehourlst = [e_snoon-t,e_snoon+t]
    day = 21
    return shourlst,ehourlst,day

def getSolarGeom(boundary,ht,lat,shourlst,ehourlst,day,north,long,timeZ,s_mth,e_mth):
    CH = ConvexHull2d()
    boundary_pts = rs.CurvePoints(boundary) # you'll need this later
    boundary_pts.pop(-1)
    bchullpts = CH.convex_hull(boundary_pts)
    centerPt = rs.CurveAreaCentroid(rs.AddCurve(bchullpts + [bchullpts[0]],1))[0]
    #centerPt = rs.CurveAreaCentroid(boundary)[0]
    boundary_plane = rs.PlaneFitFromPoints(boundary_pts)
    top_plane = get_plane(boundary,ht)

    # project curve to user_defined height
    sun_pts = get_sunpt(lat,centerPt,s_mth,day,shourlst,north_=north,lon=long,tZ=timeZ,scale_=100)
    sun_pts.extend(get_sunpt(lat,centerPt,e_mth,day,ehourlst,north_=north,lon=long,tZ=timeZ,scale_=100))

    top_lst = project_curve(sun_pts,centerPt,top_plane,boundary)
    top_curves = map(lambda x: rs.coercecurve(x),top_lst) # temp for viz
    top_lst = map(lambda x: rs.CurvePoints(x),top_lst)
    top_pts = map(lambda x: rs.coerce3dpoint(x),\
        reduce(lambda i,j:i+j,top_lst))

    # convex hull methods
    chull_pts = CH.convex_hull(top_pts)
    chull_crv = rs.AddCurve(chull_pts + [chull_pts[0]],1)
    #chull_centerPt = rs.CurveAreaCentroid(chull_crv)[0]
    # adjust curve directions
    #if not rs.CurveDirectionsMatch(boundary,chull_crv):
    #   rs.ReverseCurve(boundary)

    #b = rs.CurvePoints(boundary) + rs.CurvePoints(chull_crv)
    #c = rs.CurvePoints(chull_crv)
    return (boundary,chull_crv),top_curves


# DECOMPOSE BOUNDARY CURVE
def mesh2curve(lof,lov):
    """convert list of face vertices into closed planar curves"""
    L = []
    for i,fv in enumerate(lof):
        if fv[2] == fv[3]:
            # triangle face
            fv = [fv[0],fv[1],fv[2],fv[0]]
        else:
            # quad face
            fv = [fv[0],fv[1],fv[2],fv[3],fv[0]]
        L.append(rs.AddCurve(map(lambda fi: lov[fi], fv),1))
    return L

def checkConcaveConvex(curve):
    CH = ConvexHull2d()
    curve_pts = rs.CurvePoints(curve)
    curve_pts.pop(-1)
    chull_pts = CH.convex_hull(curve_pts)
    
    if len(chull_pts) == len(curve_pts): # no need to mesh
        meshcurves = curve
        ##print 'is convex' ## for testing
    else:
        meshParam = Rhino.Geometry.MeshingParameters.Coarse
        mesh = Rhino.Geometry.Mesh.CreateFromPlanarBoundary(curve,meshParam)
        mesh = sc.doc.Objects.AddMesh(mesh)
        vertice_lst = rs.MeshVertices(mesh)
        face_lst = rs.MeshFaceVertices(mesh)
        meshcurves = mesh2curve(face_lst,vertice_lst)
        ## print 'is concave' ## for testing
    return meshcurves


def main(north,_boundary,timeperiod,monthRange,location,height):
    if sc.sticky.has_key('ladybug_release'):
        latitude,longitude,timeZone,elevation = readLocation(location)
        year = datetime.datetime.now().year
        day = 21
        s_mth,e_mth = MONTH_DICT[monthRange][0], MONTH_DICT[monthRange][1] 
        s_snoon = get_solarnoon(s_mth,year,timeZone,day,latitude,longitude)
        e_snoon = get_solarnoon(e_mth,year,timeZone,day,latitude,longitude)
        
        """solar variables"""
        shourlst,ehourlst,day = getSolarData(timeperiod,s_snoon,e_snoon)
    
        """work with curves"""
        
        curve_ = rs.coercecurve(_boundary, -1, True)
        boundary_lst = checkConcaveConvex(curve_)
    
        chull_lst = []
        top_lst = [] # for testing purposes
        if type(boundary_lst) != type([]):
            boundary_lst = [_boundary]
    
        for boundary_ in boundary_lst:
            boundary = clean_curve(boundary_)
            bcurve,tc = getSolarGeom(boundary,height,latitude,\
            shourlst,ehourlst,day,north,longitude,timeZone,s_mth,e_mth)
            chull_lst.append(bcurve)
            top_lst.extend(tc)
    
        b2ch = Curve2ConvexHull3d()
        breplst,ptlst = b2ch.get_convexhull(chull_lst)
    
        L = map(lambda m: rs.coercebrep(m),breplst)
        CB = CleanBrep(TOL,L)
        map(lambda id: sc.doc.Objects.Delete(id,True), breplst) #delete breplst
        return CB.cleanBrep()
        ##bcurve = boundary_lst ## for testing purposes
        ##top_curves = top_lst ## for testing purposes
    else:
        print "You should first let the Ladybug fly..."
        ghenv.Component.AddRuntimeMessage(ERROR_W, "You should first let the Ladybug fly...")

MONTH_DICT = {0:(3,6), 1:(3,9), 2:(3,12),\
              3:(6,9), 4:(6,12),\
              5:(9,12)}
TOL = sc.doc.ModelAbsoluteTolerance
ERROR_W = gh.GH_RuntimeMessageLevel.Warning

"""
Get monthrange based on month references.
Default is Jun 21 - Sep 21.
---
0 = Mar 21 - Jun 21
1 = Mar 21 - Sep 21
2 = Mar 21 - Dec 21
3 = Jun 21 - Sep 21
4 = Jun 21 - Dec 21
5 = Sep 21 - Dec 21
"""
if not _monthRange:
    _monthRange = 3
if not north_:
    north_ = 0
if _boundary and _requiredHours and _location and _height:
    solarFan = main(north_,_boundary,_requiredHours,int(_monthRange),_location,_height)
else:
    print "At least one of the inputs is missing!"

