# Import .stat file data
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2017, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Use this component to import climate data found in the .stat file that downloads with the .epw file (in the same .zip folder).
Sepcifcally, this allows you to import the ASHRAE and Koppen climate zones as well as design temperatures representing the temperature extremes of the climate that should be used to design and size heating and cooling systems.
Lastly, this component brings in the typical and extreme weeks of the year as ladybug analysis periods that can be plugged into the other ladybug components.
-
Provided by Ladybug 0.0.65
    
    Args:
        _statFile: A .stat file path on your system from the Open STAT file component (or typed out as a string).
        
    Returns:
        readMe!: ...
        ashraeClimateZone: The estimated ASHRAE climate zone of the STAT file.  ASHRAE climate zones are frequently used to make suggestions for heating and cooling systems and correspond to recommendations for insulation levels of a building.  For more information, see this pdf: https://www.ashrae.org/File%20Library/docLib/Public/20081111_CZTables.pdf
        koppenClimateZone: The estimated Koppen climate zone of the STAT file.  The Koppen climate classification is the most widely used climate classification system and is based on the concept that native vegetation is the best expression of climate. Thus, Koppen climate zones combine average annual and monthly temperatures, precipitation, and the seasonality of precipitation.  For more information, see the wikipendia page on Koppen climate: http://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification.
        --------------------: ...
        heatingDesignTemp: The temperature in Celcius that ASHRAE recommends using to design a heating system for a building.  It rempresents the one of the coldest temperatures of the year for which only 0.4% of the hours are below.
        coolingDesignTemp: The temperature in Celcius that ASHRAE recommends using to design a cooling system for a building.  It rempresents the one of the hottest temperatures of the year for which only 0.4% of the hours are above.
        --------------------: ...
        extremeHotWeek: An analysis period representing the hottest week of the typical mean year.  If the stat file does not specify an extreme hot week, it is the most extreme week of the hottest season.
        typicalHotWeek: An analysis period representing a typical week of the hottest season in the typical mean year.  Not all stat files specify such a week and, in this case, the output here will be "Null."
        typicalWeek: An analysis period representing a typical week of the typical mean year.  If the stat file does not specify a typical week, it is the typical week of Autumn.
        typicalColdWeek: An analysis period representing a typical week of the coldest season in the typical mean year.  Not all stat files specify such a week and, in this case, the output here will be "Null."
        extremeColdWeek: An analysis period representing the coldest week of the typical mean year.  If the stat file does not specify an extreme cold week, it is the most extreme week of the coldest season.
"""
ghenv.Component.Name = "Ladybug_Import stat"
ghenv.Component.NickName = 'importSTAT'
ghenv.Component.Message = 'VER 0.0.65\nJUL_28_2017'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import Grasshopper.Kernel as gh

if _statFile and _statFile.lower().endswith(".stat"):
    # I read all the lines as a list
    try:
        with open(_statFile, 'r') as statFile:
            statFileLines = statFile.readlines()
            
            #Search the first part of the file for heating design temperatures.
            heatCount = 1
            for line in statFileLines[:26]:
                if 'Coldest' in line:
                    heatLineSplit = line.split('\t')
                    for elementCount, element in enumerate(heatLineSplit):
                        if element == 'HDB 99.6%':
                            heatCount = elementCount
                        elif element == 'DB996':
                            heatCount = elementCount
                        else: pass
                else: pass
                if 'Heating' in line:
                    heatingDesignTemp = line.split('\t')[heatCount]
                else: pass
            if heatingDesignTemp == None or heatingDesignTemp == 'Heating':
                warning = 'Failed to find a heating design temperature in the stat file.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            else: pass
            
            #Search the second part of the file for cooling design temperatures.
            coolCount = 1
            for line in statFileLines[:26]:
                if 'Hottest' in line:
                    coolLineSplit = line.split('\t')
                    for elementCount, element in enumerate(coolLineSplit):
                        if element == 'CDB .4%':
                            coolCount = elementCount
                        elif element == 'DB004':
                            coolCount = elementCount
                        else:pass
                else: pass
                if 'Cooling' in line:
                    coolingDesignTemp = line.split('\t')[coolCount]
                else: pass
            if coolingDesignTemp == None or coolingDesignTemp == 'Cooling':
                warn = 'Failed to find a cooling design temperature in the stat file.'
                print warn
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)
            else: pass
            
            
            # Search line by line  after line 220 for the climate zones.
            for line in statFileLines[220:]:
                if 'Climate type' in line:
                    # The first line is climate type based on Koppen.
                    koppenClimateZone = line.split('"')[1]
                    break
            count = 0
            for line in statFileLines[220:]:
                if 'Climate type' in line:
                    count += 1
                # the second line is climate type based on ASHRAE.
                if count == 2:
                    ashraeClimateZone = line.split('"')[1]
                    break
            
            # Search the last part of the file for typical and extreme periods.
            #First define a function that will convert the text month to a number.
            def monthNumber(month):
                if month == 'Jan': return 1
                elif month == 'Feb': return 2
                elif month == 'Mar': return 3
                elif month == 'Apr': return 4
                elif month == 'May': return 5
                elif month == 'Jun': return 6
                elif month == 'Jul': return 7
                elif month == 'Aug': return 8
                elif month == 'Sep': return 9
                elif month == 'Oct': return 10
                elif month == 'Nov': return 11
                elif month == 'Dec': return 12
            
            #Search for the extreme hot period.
            extremeHotWeek = None
            for line in statFileLines[220:]:
                if 'Extreme Hot Week Period selected' in line:
                    extHotStart = (line.split(':'))[1].split()
                    extHotEnd = (line.split(':'))[2].split(',')[0].split()
                    extremeHotWeek = ((monthNumber(extHotStart[0]), int(extHotStart[1]), 1), ((monthNumber(extHotEnd[0]), int(extHotEnd[1]), 24)))
                else: pass
            if extremeHotWeek == None:
                print 'No extreme hot week was found in the stat file.'
            else: pass
            
            #Search for the typical hot period.
            typicalHotWeek = None
            for lineCount, line in enumerate(statFileLines):
                if 'Typical Summer Week' in line:
                    hotStart =(statFileLines[lineCount+1].split(':'))[1].split()
                    hotEnd = (statFileLines[lineCount+1].split(':'))[2].split(',')[0].split()
                    typicalHotWeek = ((monthNumber(hotStart[0]), int(hotStart[1]), 1), ((monthNumber(hotEnd[0]), int(hotEnd[1]), 24)))
                else: pass
            if typicalHotWeek == None:
                print 'No typical hot week was found in the stat file.'
            else: pass
            
            #Search for the typical period.
            typicalWeek = None
            for lineCount, line in enumerate(statFileLines):
                if 'Typical Autumn Week' in line:
                    #The file contains multiple typical periods and I just want the Autumn one.
                    typStart =(statFileLines[lineCount+1].split(':'))[1].split()
                    typEnd = (statFileLines[lineCount+1].split(':'))[2].split(',')[0].split()
                    typicalWeek = ((monthNumber(typStart[0]), int(typStart[1]), 1), ((monthNumber(typEnd[0]), int(typEnd[1]), 24)))
                else: pass
            if typicalWeek == None:
                #The file contains only one typical period and I will take that one.
                for line in statFileLines:
                    if 'Typical Week Period selected' in line:
                        typStart = (line.split(':'))[1].split()
                        typEnd = (line.split(':'))[2].split(',')[0].split()
                        typicalWeek = ((monthNumber(typStart[0]), int(typStart[1]), 1), ((monthNumber(typEnd[0]), int(typEnd[1]), 24)))
                else: pass
            if typicalWeek == None:
                print 'No typical week was found in the stat file.'
            else: pass
            
            #Search for the typical cold period.
            typicalColdWeek = None
            for lineCount, line in enumerate(statFileLines):
                if 'Typical Winter Week' in line:
                    coldStart =(statFileLines[lineCount+1].split(':'))[1].split()
                    coldEnd = (statFileLines[lineCount+1].split(':'))[2].split(',')[0].split()
                    typicalColdWeek = ((monthNumber(coldStart[0]), int(coldStart[1]), 1), ((monthNumber(coldEnd[0]), int(coldEnd[1]), 24)))
                else: pass
            if typicalColdWeek == None:
                print 'No typical cold week was found in the stat file.'
            else: pass
            
            #Search for the extreme cold period.
            extremeColdWeek = None
            for line in statFileLines[220:]:
                if 'Extreme Cold Week Period selected' in line:
                    extColdStart = (line.split(':'))[1].split()
                    extColdEnd = (line.split(':'))[2].split(',')[0].split()
                    extremeColdWeek = ((monthNumber(extColdStart[0]), int(extColdStart[1]), 1), ((monthNumber(extColdEnd[0]), int(extColdEnd[1]), 24)))
                else: pass
            if extremeColdWeek == None:
                print 'No extreme cold week was found in the stat file.'
            else: pass
            
            
    except Exception, e:
        msg = "Invalid stat file path."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        pass
else:
    print "Please connect a stat file path location."