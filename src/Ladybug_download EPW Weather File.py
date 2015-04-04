# Open epwmap
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to open the epwmap page in your default web browser and download an .epw weather file.
-
Provided by Ladybug 0.0.59

    Args:
        _download: Set Boolean to True to open the epw map page
    Returns:
        readMe! : Will read 'Happy downloading...' in the case of successfully opening your browser
"""
ghenv.Component.Name = "Ladybug_download EPW Weather File"
ghenv.Component.NickName = 'DownloadEPW'
ghenv.Component.Message = 'VER 0.0.59\nMAR_02_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import webbrowser as wb
if _download:
    url = 'http://mostapharoudsari.github.io/epwmap'
    wb.open(url,2,True)
    print 'Happy downloading!'
else:
    print 'Set download to true...'
