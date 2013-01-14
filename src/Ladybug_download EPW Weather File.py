# Open DOE website
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Open DOE website to download .epw weather file.
-
Provided by Ladybug 0.0.35

    Args:
        download: Set Boolean to True to open the website
    Returns:
        report : 'Happy downloading...' in case of success
"""
ghenv.Component.Name = "Ladybug_download EPW Weather File"
ghenv.Component.NickName = 'DownloadEPW'
ghenv.Component.Message = 'VER 0.0.35\nJAN_03_2013'

import webbrowser as wb
if download:
    url = 'http://apps1.eere.energy.gov/buildings/energyplus/cfm/weather_data.cfm'
    wb.open(url,2,True)
    print 'Happy downloading!'
else:
    print 'Set download to true...'