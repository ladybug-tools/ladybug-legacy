# By Saeran Vasanthakumar
# saeranv@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
This component generates a Solar Envelope. The solar envelope ensures its adjacent 
neighbors (defined as anything outside of the chosen boundary) a specified minimum 
direct solar access for the user-specified time per day. Any geometry within the 
boundary, that does not exceed the Solar Envelope will therefore not cast any shadow 
for that given time period. The autumn equinox is used as the solar cutoff point.
Reference: Niemasz, J., Sargent, J., Reinhart D.F., "Solar Zoning and Energy in Detached Residential Dwellings," Proceedings of SIMAUD 2011, Boston, April 2011.

-
Provided by Ladybug 0.0.53
    
    Args:
        north_: Input a number or a vector to set north; default is set to the Y-axis
        _boundary: Input the test geometry as a closed Curve(s) 
        _latitude: Input the latitude of the location as a string
        (if you do this, you don't need to insert _location, 
        although the resulting fan will be less precise)
        _timeperiod: Input the desired guaranteed sunlight hours as a number 
        _location: [Optional] Input location from Import .epw component or constructLocation,
        (if you do this, you don't need to insert _latitude,
        and the resulting fan will be more precise)
        
    Returns:
        solarEnvelope: solar envelope
"""

ghenv.Component.Name = "Ladybug_solarEnvelope_2"
ghenv.Component.NickName = 'solarEnvelope'
ghenv.Component.Message = 'VER 0.0.53\nJAN_28_2014'

import math
import rhinoscriptsyntax as rs
import Rhino
import scriptcontext as sc
import datetime

class SunCalculation:
    """ 
    Modified from: http://michelanders.blogspot.ca/2010/12/calulating-sunrise-and-sunset-in-python.html
    Calculate sunrise and sunset based on equations from NOAA
    http://www.srrb.noaa.gov/highlights/sunrise/calcdetails.html

    typical use, calculating the sunrise at the present day:

    import datetime
    s = sun(lat=49,long=3)
    print('sunrise at ',s.sunrise(when=datetime.datetime.now())
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

# -----------------------------------------------------------

# get_max: curve -> float
# Consumes boundary curve, and returns maximum 
# bounding curve dimension
def get_max(b_):
     bbpts = rs.BoundingBox(b_)[:4]
     bbpt1 = bbpts.pop(0)
     max = 0
     for bbpt in bbpts:
         dist = rs.Distance(bbpt1,bbpt)
         if max < dist: max = dist
     return max

# int_solid: (listof pt) pt curve -> (listof solid)
def extrude_solid(pt,cp,b):
    lo_solid = []
    ptlst = rs.CurvePoints(b)
    srf = rs.AddPlanarSrf(rs.AddCurve(ptlst,1))
    # make curve and extrude
    line = rs.AddCurve([cp,pt],1)
    max = get_max(b)
    curve = rs.ExtendCurveLength(line,0,1,max*40)
    #------------ extrude surface ---------------------# using rhinocommon
    brep = rs.coercebrep(srf, True)
    curve = rs.coercecurve(curve, -1, True)
    newbrep = brep.Faces[0].CreateExtrusion(curve, True)
    if newbrep:
        rc = sc.doc.Objects.AddBrep(newbrep)
        sc.doc.Views.Redraw()
        return rc

def bool_solids(los):
    env = los.pop(0)
    for s in los:
        e = rs.BooleanIntersection(env,s,True)
        env = e
    return env

# make_zone: (listof pt), curve -> (listof solid) 
def make_zone(pts, bound):
    los = []
    # get centroid from boundary curve
    center_pt = rs.CurveAreaCentroid(boundary)[0]
    # extrude solids from sun path
    for sp in pts:
        extruded = extrude_solid(sp,center_pt,bound)
        los.append(extruded)
    # boolean interesect all
    return bool_solids(los)

def get_solarnoon(month,year,tz,d,lat,lon):
    """get_solarnoon: month -> solarnoon """ 
    date = datetime.datetime(year,month,d)
    SC = SunCalculation(lat,lon)
    snoon = SC.solarnoon(date)
    return snoon.hour + tz + snoon.minute/60.0

# -----------------------------------------------------------

# make this into a class
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
# -----------------------------------------------------------

if sc.sticky.has_key('ladybug_release'):
    lb_sunpath = sc.sticky["ladybug_SunPath"]()
    lb_preparation = sc.sticky["ladybug_Preparation"]()
else:
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")

north = north_
boundary = _boundary
timeperiod = _timeperiod


# clean curve
rs.SimplifyCurve(boundary)
# reverse curve direction
boundarybrep = rs.coercecurve(boundary)
Rhino.Geometry.Curve.Reverse(boundarybrep)
sc.doc.Objects.Replace(boundary,boundarybrep)
if not rs.IsCurveClosed(boundary):
    print "Curve is not closed"

# solar noon

if _location:
    latitude,longitude,timeZone,elevation = FL.readLocation(_location)
    year = datetime.datetime.now().year
    s_snoon = get_solarnoon(6,year,timeZone,22,latitude,longitude)
    e_snoon = get_solarnoon(9,year,timeZone,22,latitude,longitude)
else:
    latitude = float(_latitude);longitude=0;timeZone=0;elevation=0;
    s_snoon = 12.0
    e_snoon = 12.0
    print "Add the _location input for increased precision"

# variables
t = timeperiod/2.0
shourlst = [s_snoon-t,s_snoon+t]
ehourlst = [e_snoon-t,e_snoon+t]
day = 22
centerPt = rs.CurveAreaCentroid(boundary)[0]

s_sun_pts = get_sunpt(latitude,centerPt,6,day,shourlst,north_=north,lon=longitude,tZ=timeZone,scale_=100)
e_sun_pts = get_sunpt(latitude,centerPt,9,day,ehourlst,north_=north,lon=longitude,tZ=timeZone,scale_=100)

szone = make_zone(s_sun_pts,boundary)
ezone = make_zone(e_sun_pts,boundary)
solarEnvelope = rs.BooleanIntersection(szone,ezone) 