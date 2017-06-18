# Open epwmap
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
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
Use this component to open the epwmap page in your default web browser and download an .epw weather file.
-
Provided by Ladybug 0.0.64

    Args:
        _download: Set Boolean to True to open the epw map page
    Returns:
        readMe! : Will read 'Happy downloading...' in the case of successfully opening your browser
"""
ghenv.Component.Name = "Ladybug_download EPW Weather File"
ghenv.Component.NickName = 'DownloadEPW'
ghenv.Component.Message = 'VER 0.0.64\nAPR_25_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import webbrowser as wb
if _download:
    url = 'http://www.ladybug.tools/epwmap/'
    wb.open(url,2,True)
    print 'Happy downloading!'
else:
    print 'Set download to true...'
