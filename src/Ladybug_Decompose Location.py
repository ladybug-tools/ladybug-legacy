# Explode Location
# By Mostapha Sadeghipour Roudsari - based on a wish from Brian Timothy Ringley
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to separate and exctract the information in the 'location' output of the importEPW or constructLocation component.
-
Provided by Ladybug 0.0.59

    Args:
        _location: The output from the importEPW or constructLocation component.  This is essentially a list of text summarizing a location on the earth.
    Returns:
        readMe! : ...
        locationName: Name of the location.
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        timeZone: Time zone of the location.
        elevation: Elevation of the location.
"""
ghenv.Component.Name = "Ladybug_Decompose Location"
ghenv.Component.NickName = 'explodeLocation'
ghenv.Component.Message = 'VER 0.0.59\nFEB_01_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass



if _location:
    locationStr = _location.split('\n')
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
    
    latitude, longitude, timeZone, elevation = float(latitude), float(longitude), float(timeZone), float(elevation)
