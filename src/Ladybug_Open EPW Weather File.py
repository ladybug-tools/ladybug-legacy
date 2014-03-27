# Open Weather data file
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to open an .epw weather file from a location on your computer.
-
Provided by Ladybug 0.0.57
    
    Args:
        _open: Set Boolean to True to browse for a weather file on your system.
    Returns:
        readMe!: ...
        fileAddress: The file path of the selected epw file.
"""
ghenv.Component.Name = "Ladybug_Open EPW Weather File"
ghenv.Component.NickName = 'Open weather file'
ghenv.Component.Message = 'VER 0.0.57\nMAR_26_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass



import rhinoscriptsyntax as rs

if _open == True:
    filter = "EPW file (*.epw)|*.epw|All Files (*.*)|*.*||"
    epwFile = rs.OpenFileName("Open .epw Weather File", filter)
    print 'Done!'
else:
    print 'Please set open to True'
