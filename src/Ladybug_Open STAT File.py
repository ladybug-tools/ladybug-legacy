# Open Weather data file
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to open a .stat file, which downloads with the .epw weather file and contains information such as the climate zone and maximum temperatures for designing heating/cooling systems.
This component opens the file from a location on your computer.
-
Provided by Ladybug 0.0.59
    
    Args:
        _open: Set Boolean to True to browse for a .stat file on your system.
    Returns:
        readMe!: ...
        statFile: The file path of the selected .stat file.
"""
ghenv.Component.Name = "Ladybug_Open STAT File"
ghenv.Component.NickName = 'Open stat file'
ghenv.Component.Message = 'VER 0.0.59\nFEB_01_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass



import rhinoscriptsyntax as rs

if _open == True:
    filter = "STAT file (*.stat)|*.stat|All Files (*.*)|*.*||"
    statFile = rs.OpenFileName("Open .stat File", filter)
    print 'Done!'
else:
    print 'Please set open to True'
