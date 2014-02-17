# Explode Location
# By Mostapha Sadeghipour Roudsari - based Brian Timothy Ringley suggestion
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Construct location
-
Provided by Ladybug 0.0.53

    Args:
        _locationName: Location name
        _latitude: Latitude of the location
        _longitude_: Langitude of the location
        _timeZone_: Time zone of the location
        _elevation_: Elevation of the location
    Returns:
        readMe!: ...
        location: Location data as a string
        

"""
ghenv.Component.Name = "Ladybug_Construct Location"
ghenv.Component.NickName = 'constructLocation'
ghenv.Component.Message = 'VER 0.0.54\nFEB_16_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
ghenv.Component.AdditionalHelpFromDocStrings = "3"

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

if _locationName and _latitude!=None:
    location = "Site:Location,\n" + \
            _locationName + ',\n' + \
            str(_latitude)+',      !Latitude\n' + \
            str(_longitude_)+',     !Longitude\n' + \
            str(_timeZone_)+',     !Time Zone\n' + \
            str(_elevation_) + ';       !Elevation'
else:
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "locationName or latitude is missing")