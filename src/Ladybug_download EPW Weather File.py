# Open DOE website
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to open the Department of Energy's weather database in your default web browser and download an .epw weather file.
-
Provided by Ladybug 0.0.57

    Args:
        _download: Set Boolean to True to open the website of the Department of Energy's weather database.
    Returns:
        readMe! : Will read 'Happy downloading...' in the case of successfully opening your browser
"""
ghenv.Component.Name = "Ladybug_download EPW Weather File"
ghenv.Component.NickName = 'DownloadEPW'
ghenv.Component.Message = 'VER 0.0.57\nMAR_26_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import webbrowser as wb
if _download:
    url = 'http://apps1.eere.energy.gov/buildings/energyplus/cfm/weather_data.cfm'
    wb.open(url,2,True)
    print 'Happy downloading!'
else:
    print 'Set download to true...'
