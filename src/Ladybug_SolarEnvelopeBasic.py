#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2016, Saeran Vasanthakumar <saeranv@gmail.com> 
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
Use this component to generate a solar envelope for a closed boundary curve with minimum inputs. This component predefines monthly and hourly ranges in order to simplify the creation of useful envelope geometry.  
The solar envelope is used to ensure that its adjacent neighbors (defined as anything outside of the chosen boundary curve) will receive a specified minimum hours of direct solar access for each day in a specified month range of the year.
Any geometry built within the solar envelope boundaries will therefore not cast any shadow on adjacent property for the given hour and month range.
 
The start and end dates that determine the month range for solar access can be chosen from the following options:
0) Mar 21 - Jun 21
1) Mar 21 - Sep 21
2) Mar 21 - Dec 21
3) Jun 21 - Sep 21
4) Jun 21 - Dec 21
5) Sep 21 - Dec 21
The default set to 4) June 21 to December 21.

Reference: Niemasz, J., Sargent, J., Reinhart D.F., "Solar Zoning and Energy in 
Detached Residential Dwellings," Proceedings of SIMAUD 2011, Boston, April 2011.

-
Provided by Ladybug 0.0.62
    
    Args:
        _boundary: A closed boundary curve representing a piece of land (such as a property to be developed) for which solar access of the surrounding land is desired.
        _location: The output from the importEPW or constructLocation component.  This is essentially a list of text summarizing a location on the earth.
        _requiredHours: The number of hours of direct solar access that the property surrounding the boundary curve should receive during the _monthRange. For example an input of 4 will define the hour range roughly between 10AM and 2PM. The component will compute the hour range that will maximize the envelope volume.        
        north_: Input a vector to be used as a true North direction or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _monthRange: An optional interger value to change the month range for which solar access is being considered. The default month range is Jun 21 - Dec 21.
            Integers input here must be between 0 - 5 and correspond to the following :
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
        solarEnvelope: A Brep representing a solar envelope.  This volume should be built within in order to ensure that the surrounding property is not shaded for the given number of hours.
"""

ghenv.Component.Name = "Ladybug_SolarEnvelopeBasic"
ghenv.Component.NickName = 'SolarEnvelopeBasic'
ghenv.Component.Message = 'VER 0.0.62\nJAN_23_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "3 | EnvironmentalAnalysis"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "0"
except: pass


import math
import rhinoscriptsyntax as rs
import Rhino
import Rhino.Geometry as rc
import scriptcontext as sc
import datetime
import Grasshopper.Kernel as gh

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

# -----------------------------------------------------------

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

def get_max_side(b_):
    """
    get_max: curve -> float
    Consumes boundary curve, and returns maximum 
    bounding curve dimension
    """
    bbpts = rs.BoundingBox(b_)[:4]
    bbpt1 = bbpts.pop(0)
    max = 0
    for bbpt in bbpts:
        dist = rs.Distance(bbpt1,bbpt)
        if max < dist: max = dist
    return max

def extrude_solid(pt,cp,b):
    # int_solid: (listof pt) pt curve -> (listof solid)
    lo_solid = []
    ptlst = rs.CurvePoints(b)
    srf = rs.AddPlanarSrf(rs.AddCurve(ptlst,1))
    # make curve and extrude
    line = rs.AddCurve([cp,pt],1)

    max = get_max_side(b)
    curve = rs.ExtendCurveLength(line,0,1,max*2)
    #extrude surface
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

def make_zone(pts, bound):
    # make_zone: (listof pt), curve -> (listof solid) 
    los = []
    # get centroid from boundary curve
    center_pt = rs.CurveAreaCentroid(bound)[0]
    # extrude solids from sun path
    for p in pts:
        line = rs.AddCurve([center_pt,p],1)
        extruded = extrude_solid(p,center_pt,bound)
        los.append(extruded)
    # boolean interesect all
    los_ = map(lambda g: rs.coercegeometry(g),los)
    return bool_solids(los)

def get_solar_noon(month,year,tz,d,lat,lon):
    """get_solarnoon: month -> solarnoon """ 
    date = datetime.datetime(year,month,d)
    SC = SunCalculation(lat,lon)
    snoon = SC.solarnoon(date)
    #print 'solar noon', snoon.hour + tz + snoon.minute/60.0
    return snoon.hour + tz + snoon.minute/60.0

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

def get_sunpt(lb_sunpath,lb_preparation,lat,cpt,month,day,hourlst,north_=0,lon=0,tZ=0,scale_=100):
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

def main(north,boundary,timeperiod,monthRange,location):
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this component." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        lb_sp = sc.sticky["ladybug_SunPath"]()
        lb_prep = sc.sticky["ladybug_Preparation"]()
        
        # setting solar noon variables
        latitude,longitude,timeZone,elevation = readLocation(_location)
        year = datetime.datetime.now().year
        day = 21
        
        """
        MONTH_DICT = {0:range(3,7), 1:range(3,10), 2:range(3,13),\
              3:range(6,10), 4:range(6,13),\
              5:range(9,13)}
        """
        
        mth_lst = MONTH_DICT[monthRange]
        
        t = timeperiod/2.0
        centerPt = rs.CurveAreaCentroid(boundary)[0]
        # do geometry operations
        boundary = clean_curve(boundary)
        brep_lst = []
        for mth in mth_lst:
            solar_noon = get_solar_noon(mth,year,timeZone,day,latitude,longitude)
            hourlst = [solar_noon-t,solar_noon+t]
            #print mth
            #print 'month: ',mth,'th;', 'hours: ', hourlst
            sun_pts = get_sunpt(lb_sp,lb_prep,latitude,centerPt,mth,day,hourlst,north_=north,lon=longitude,tZ=timeZone,scale_=100)
            brep = rs.coercebrep(make_zone(sun_pts,boundary))
            brep_lst.append(brep)
        
        SE = None
        TOL = sc.doc.ModelAbsoluteTolerance
        for i in range(len(brep_lst)-1):
            brep = brep_lst[i]
            brep_ = brep_lst[i+1]
            if not SE and rs.IsBrep(brep):
                SE_ = brep
            else:
                SE_ = SE
            if rs.IsBrep(brep_):
                SE = rc.Brep.CreateBooleanIntersection(SE_,brep_,TOL)[0]
            else:
                SE = SE_
        return SE
        
    else:
        print "You should first let the Ladybug fly..."
        ghenv.Component.AddRuntimeMessage(ERROR_W, "You should first let the Ladybug fly...")


MONTH_DICT = {0:range(3,7), 1:range(3,10), 2:range(3,13),\
              3:range(6,10), 4:range(6,13),\
              5:range(9,13)}
              
ERROR_W = gh.GH_RuntimeMessageLevel.Warning
debug = []


"""
Get monthrange based on month references.
Default is Jun 21 - Dec 21.
---
0 = Mar 21 - Jun 21
1 = Mar 21 - Sep 21
2 = Mar 21 - Dec 21
3 = Jun 21 - Sep 21
4 = Jun 21 - Dec 21
5 = Sep 21 - Dec 21
"""
if not _monthRange:
    _monthRange = 4
if not north_:
    north_ = 0
if _boundary and _requiredHours and _location:
    solarEnvelope = main(north_,_boundary,_requiredHours,int(_monthRange),_location)
else:
    print "At least one of the inputs is missing!"
