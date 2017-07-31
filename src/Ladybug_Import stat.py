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
ghenv.Component.Message = 'VER 0.0.65\nAUG_01_2017'
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
            
            # Add climate definition for koppenClimate types
            # Climate definitions mentioned below are taken from following two links
            # http://bigladdersoftware.com/epx/docs/8-3/auxiliary-programs/koppen-climate-classification.html
            # https://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification
            koppenClimateName = {
            "af" : [
                    "Tropical Rainforest Climate",
                    "This type of climate has every month of the year with an average temperature of 18 C (64.4 F) or higher, with precipitation all year long. Monthly temperature variations in this climate are less than 3 degrees Celsius. Because of intense surface heating and high humidity cumulus and cumulonimbus clouds form early in the afternoons almost every day. Daily highs are about 32 degrees Celsius while night time temperatures average 22 degrees Celsius.",
                    "Examples;",
                    "Singapore",
                    "West Palm Beach, Florida, USA",
                    "Hilo, Hawai, USA"
                    ],
            "am" : [
                    "Tropical monsoon climate",
                    "This type of climate has every month of the year with an average temperature of 18 C (64.4 F) or higher, with substantial rainfall during the 7 to 9 hottest months of the year. During the dry months, very little rainfall occurs.",
                    "Examples;",
                    "Maimi ,Florida, USA"
                    ],
             "aw" : [
                    "Tropical wet and dry or Savanna climate",
                    "This type of climate has every month of the year with an average temperature of 18 C (64.4 F) or higher. This climate has a pronounced dry season during the winter months with the driest month having precipitation less than 60mm (2.4 in) and less than 4% of the total annual precipitation.",
                    "Examples;",
                    "Mumbai, India",
                    "Key West, Florida, USA",
                    "Naples, Florida, USA",
                    "Panama City",
                    "Rio de Janeiro, Rio de Janeiro, Brazil"
                    ],
             "as" : [
                    "Tropical wet and dry or Savanna climate",
                    "This type of climate has every month of the year with an average temperature of 18 C (64.4 F) or higher. This climate has a pronounced dry season during the winter months with the driest month having precipitation less than 60mm (2.4 in) and less than 4% of the total annual precipitation.",
                    "Examples;",
                    "Mumbai, India",
                    "Key West, Florida, USA",
                    "Naples, Florida, USA",
                    "Panama City",
                    "Rio de Janeiro, Rio de Janeiro, Brazil"
                    ],
            "bwh" : [
                    "Dry climate with a little precipitation throughout most of the year.",
                    "This is hot and arid desert climate and is often dominated by xerophytic vegetation (The vegetation that has adapted to survive in an environment with little liquid water).",
                    "Examples;",
                    "Doha, Qatar",
                    "Riyadh, Saudi Arabia",
                    "Dubai, UAE",
                    "Las Vegas, Nevada, USA",
                    "Phoenix, Arizona, USA"
                    ],
            "bwk" : [
                    "Dry climate with a little precipitation throughout most of the year.",
                    "This is cold and arid desert climate and is often dominated by xerophytic vegetation (The vegetation that has adapted to survive in an environment with little liquid water).",
                    "Examples;",
                    "Turpan, Xinjiang, China"
                    ],
            "bwn" : [
                    "Dry climate with a little precipitation throughout most of the year.",
                    "This is mild and arid desert climate and is often dominated by xerophytic vegetation (The vegetation that has adapted to survive in an environment with little liquid water).",
                    "Examples;",
                    "Lima, Peru"
                    ],
            "bsh" : [
                    "Dry climate with a little precipitation throughout most of the year.",
                    "This is hot semi-arid climate. It receives a little more precipitation than the arid (desert) climate. This climate receives this precipitation from the ITCZ (inter-tropical convergence zone) or from mid-latitude cyclones.",
                    "Examples;",
                    "Lahore, Pakistan",
                    "Odessa, Texas, USA",
                    "Yuanjian, Yunnan, China"
                    ],
            "bsk" : [
                    "Dry climate with a little precipitation throughout most of the year.",
                    "This is cold semi-arid climate. It receives a little more precipitation than the arid (desert) climate. This climate receives this precipitation from the ITCZ (inter-tropical convergence zone) or from mid-latitude cyclones.",
                    "Examples;",
                    "Denver, Colorado, USA",
                    "Tabriz, East Azerbaijan Province, Iran",
                    "Brooks, Alberta, Canada",
                    "Shijiazhuang, Hebel, China",
                    ],
            "bsn" : [
                    "Dry climate with a little precipitation throughout most of the year.",
                    "This is mild semi-arid climate. It receives a little more precipitation than the arid (desert) climate. This climate receives this precipitation from the ITCZ (inter-tropical convergence zone) or from mid-latitude cyclones.",
                    "Examples;",
                    "Sanaa, Yemen"
                    ],
            "cfa" : [
                    "Moist mid-latitude climate with mild winters.",
                    "This is a temperate climate without dry season and a hot summer.", 
                    "Examples;",
                    "Sao Paulo, Brazil",
                    "Brisbane, Australia",
                    "Sydney, Australia",
                    "Orlando, Florida, USA",
                    "New Orleans, Florida, USA",
                    "Washington D.C. USA",
                    "Dallas, Texas, USA",
                    "Srinagar, India",
                    "Shanghai, China",
                    "Nanjing, China",
                    "Tokyo, Japan",
                    "Osaka, Japan",
                    "Milan, Italy",
                    "Durban, South Africa"
                    ],
            "cfb" : [
                    "Moist mid-latitude climate with mild winters.",
                    "This is a temperate climate without dry season and a warm summer.  This climate is also known as the oceanic (marine) climate. Heavy precipitation occurs during the mild winters because of continuous presence of mid-latitude cyclones.",
                    "Examples;",
                    "Mexico City, Mexico"
                    ],
            "cfc" : [
                    "Moist mid-latitude climate with mild winters.",
                    "This is a temperate climate without dry season and a cold summer. This climate is also known as the subpolar oceanic climate.",
                    "Examples;",
                    "Mount Read, Tasmania, Australia",
                    "Punta Arenas, Chile",
                    ],
            "csa" : [
                    "Moist mid-latitude climate with mild winters.",
                    "This is a temperate climate with dry and hot summer. This climate is also known as the Mediterranean climate.",
                    "Examples;",
                    "Beirut, Lebanon",
                    "Tel Aviv, Israel",
                    "Los Angeles, California, USA",
                    "Perth, Australia",
                    "Tangier, Morocco",
                    "Rome, Italy",
                    "Seville, Spain",
                    "Madrid, Spain",
                    "Marseille, France",
                    "Athens, Greece"
                    ],
            "csb" : [
                    "Moist mid-latitude climate with mild winters.",
                    "This is a temperate climate with dry and warm summer.", 
                    "Examples;",
                    "San Francisco, California, USA",
                    "Seattle, Washington, USA",
                    "Cape Town, South Africa",
                    "Kington SE, Australia"
                    ],
            "csc" : [
                    "Moist mid-latitude climate with mild winters.",
                    "This is a temperate climate with dry and cold summer. This is apparently a rare climate type.",
                    "Examples;",
                    "Balmaceda, Chile",
                    "Haleakala Summit, Hawaii, USA",
                    ],
            "cwa" : [
                    "Moist mid-latitude climate with mild winters.",
                    "This is a temperate climate with dry winter and hot summer. This climate has a classic dry winter / wet summer pattern associated with tropical monsoonal climates.",
                    "Examples;",
                    "Islamabad, Pakistan",
                    "New Delhi, India",
                    "Zhengzhou, China",
                    "Hong Kong",
                    "Hanoi, Vietnam"
                    ],
            "cwb" : [
                    "Moist mid-latitude climate with mild winters.",
                    "This is a temperate climate with dry winter and warm summer. In this climate winters are noticeable and dry, and summers can be very rainy.",
                    "Examples;",
                    "Nairobi, Kenya",
                    "Mexico City, Mexico",
                    "Johannesburg, South Africa",
                    "Kunming, China"
                    ],
            "cwc" : [
                    "Moist mid-latitude climate with mild winters.",
                    "This is a temperate climate with dry winter and cold summer.", 
                    "Examples;",
                    "EI Alto, Bolivia"
                    ],
            "dsa" : [
                    "Moist mid-latitude climate with cold winters.",
                    "This is a cold climate with dry and hot summer.", 
                    "Examples;",
                    "Saqqez, Iran",
                    "Cambridge, Idaho, USA"
                    ],
            "dsb" : [
                    "Moist mid-latitude climate with cold winters.",
                    "This is a cold climate with dry and warm summer.", 
                    "Examples;",
                    "South Lake Tahoe, California, USA",
                    "Bridgeport, California, USA"
                    ],
            "dsc" : [
                    "Moist mid-latitude climate with cold winters.",
                    "This is a cold climate with dry and cold summer.", 
                    "Examples;",
                    "Homer, Alaska, USA",
                    "Brian Head, Utah, USA"
                    ],
            "dsd" : [
                    "Moist mid-latitude climate with cold winters.",
                    "This is a cold climate with dry summer and very cold winter."
                    ],
            "dwa" : [
                    "Moist mid-latitude climate with cold winters.",
                    "This is a cold climate with dry winter and hot summer.", 
                    "Examples;",
                    "Beijing, China",
                    "Seoul, South Korea",
                    ],
            "dwb" : [
                    "Moist mid-latitude climate with cold winters.",
                    "This is a cold climate with dry winter and warm summer.", 
                    "Examples;",
                    "Pembina, North Dakota, USA",
                    "Heihe, China"
                    ],
            "dwc" : [
                    "Moist mid-latitude climate with cold winters.",
                    "This is a cold climate with dry winter and cold summer.", 
                    "Examples;",
                    "Mohe County, Heliongjiang, China",
                    "Yushu City, Qinghai, China"
                    ],
            "dwd" : [
                    "Moist mid-latitude climate with cold winters.",
                    "This is a cold climate with dry and very cold winter.", 
                    "Examples;",
                    "Seymchan, Magadan Oblast, Russia",
                    "Oymyakon, Sakha Republic, Russia"
                    ],
            "dfa" : [
                    "Moist mid-latitude climate with cold winters.",
                    "This is a cold climate without dry season and hot summer.", 
                    "Examples;",
                    "Chicago, Illinois, USA",
                    "Columbus, Ohio, USA",
                    "Boston, Massachusetts, USA",
                    "Omaha, Nebraska, USA",
                    "Minneapolis, Minnesota, USA",
                    "Windsor, Ontario, Canada"
                    ],
            "dfb" : [
                    "Moist mid-latitude climate with cold winters.",
                    "This is a cold climate without dry season and warm summer.", 
                    "Examples;",
                    "Calgary, Alberta, Canada", 
                    "Winnipeg, Manitoba, Canada", 
                    "Ottawa, Ontario, Canada", 
                    "Toronto Islands, Ontario, Canada", 
                    "London, Ontario, Canada", 
                    "Kiev, Ukraine", 
                    "Moscow, Russia", 
                    "Saint Petersburg, Russia", 
                    "Stockholm, Sweden", 
                    "Oslo, Norway", 
                    "Lillehammer, Norway", 
                    "Portland, Maine, USA",
                    "Montpelier, Vermont, USA",
                    "Binghamton, New York, USA",
                    ],
            "dfc" : [
                    "Moist mid-latitude climate with cold winters.",
                    "This is a cold climate without dry season and cold summer.", 
                    "Examples;",
                    "Fraser, Colorado, USA",
                    "Fairbanks, Alaska, USA", 
                    "Whitehorse, Yukon, Canada", 
                    "Churchill, Manitoba, Canada"
                    ],
            "dfd" : [
                    "Moist mid-latitude climate with cold winters.",
                    "This is a cold climate without dry season and very cold winter.", 
                    "Examples;",
                    "Yakutsk, Sakha Republic, Russia", 
                    "Verkhoyansk, Sakha Republic, Russia"
                    ],
             "et" : [
                    "Polar climate with extremely cold winters and summers",
                    "Polar climates have year-round cold temperatures with warmest month less than 10 C. Polar climates are found on the northern coastal areas of North America and Europe, Asia and on the landmasses of Greenland and Antarctica. Two minor climate types exist. ET or polar tundra is a climate where the soil is permanently frozen to depths of hundreds of meters, a condition known as permafrost. Vegetation is dominated by mosses, lichens, dwarf trees and scattered woody shrubs.",
                    "Examples;",
                    "Mount Rainier, Washington, USA",
                    "Macquarie Island",
                    "Nagqu, Tibet, China"
                    ],
             "ef" : [
                    "Polar climate with extremely cold winters and summers",
                    "Polar climates have year-round cold temperatures with warmest month less than 10 C. Polar climates are found on the northern coastal areas of North America and Europe, Asia and on the landmasses of Greenland and Antarctica. Two minor climate types exist. EF or polar ice caps has a surface that is permanently covered with snow and ice.",
                    "Examples;",
                    "Mount Ararat, Turkey",
                    "Grossglockner, Carinthia, Austria",
                    "Mount Everest, Nepal",
                    "Summit Camp, Greenland",
                    "Scott Base, Antarctica",
                    "Vostok Station, Antarctica, location of the lowest air temperature ever recorded on Earth.",
                    "McMurdo Station, Antarctica",
                    "Byrd Station, Antarctica"
                    ],
              "h" : [
                    "Highland areas due to mountainous areas. This classification can encompass any of the climate type",
                    "Highland areas can encompass any of the previously mentioned major categories  the determining factor is one of altitude (temperature decreases roughly 2 C for every increase of 305 m). This is a complex climate zone. Highland regions roughly correspond to the major categories change in temperature with latitude - with one important exception. Seasons only exist in highlands if they also exist in the nearby lowland regions. For example, although A climates have cooler temperatures at higher elevations, the seasonal changes of C, D and E climates are not present."
                    ]
            }
            if koppenClimateZone.lower() in koppenClimateName.keys():
                key = koppenClimateZone.lower()
                koppenClimateZone = [koppenClimateZone] + koppenClimateName[key]
            else:
                pass

            count = 0
            for line in statFileLines[220:]:
                if 'Climate type' in line:
                    count += 1
                # the second line is climate type based on ASHRAE.
                if count == 2:
                    ashraeClimateZone = line.split('"')[1]
                    break
            
            # Add the ASHRAE climate name for the climate number
            # Following climate names are taken from https://www.ashrae.org/File%20Library/docLib/Public/20081111_CZTables.pdf
            climateName = {
            "1A" : " | Very Hot - Humid",
            "1B" : " | Dry",
            "2A" : " | Hot - Humid",
            "2B" : " | Dry",
            "3A" : " | Warm - Humid",
            "3B" : " | Dry",
            "3C" : " | Warm - Marine",
            "4A" : " | Mixed - Humid",
            "4B" : " | Dry",
            "4C" : " | Mixed - Marine",
            "5A" : " | Cold - Humid",
            "5B" : " | Dry",
            "5C" : " | Marine",
            "6A" : " | Cold - Humid",
            "6B" : " | Dry",
            "7" : " | Very Cold",
            "8" : " | Subarctic",
            }
            if ashraeClimateZone in climateName.keys():
                ashraeClimateZone += climateName[ashraeClimateZone]
            else:
                pass
            
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