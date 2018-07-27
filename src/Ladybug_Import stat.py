# Import .stat file data
#
# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Ladybug.
# 
# Copyright (c) 2013-2018, Chris Mackey <Chris@MackeyArchitecture.com> 
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
Provided by Ladybug 0.0.66
    
    Args:
        _statFile: A .stat file path on your system from the Open STAT file component (or typed out as a string).
    Returns:
        readMe!: The description of ASHRAE anf koppen climate zones. For more information on ASHRAE climate names, please see the PDF at https://www.ashrae.org/File%20Library/docLib/Public/20081111_CZTables.pdf. To know more about koppen climate zones and their definitions, please visit, http://bigladdersoftware.com/epx/docs/8-3/auxiliary-programs/koppen-climate-classification.html and https://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification
        ashraeClimateZone: The estimated ASHRAE climate zone of the STAT file.  ASHRAE climate zones are frequently used to make suggestions for heating and cooling systems and correspond to recommendations for insulation levels of a building.
        koppenClimateZone: The estimated Koppen climate zone of the STAT file.  The Koppen climate classification is the most widely used climate classification system and is based on the concept that native vegetation is the best expression of climate. Thus, Koppen climate zones combine average annual and monthly temperatures, precipitation, and the seasonality of precipitation.  For more information, see the wikipendia page on Koppen climate: http://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification.
        ---------------: ...
        heatingDesignDay: An analysis period that represents the day of the year that should be used to size the heating system.
        coolingDesignDay: An analysis period that represents the day of the year that should be used to size the cooling system.
        heatingDesignTemps: The temperatures in celcius that ASHRAE recommends using to size a heating system to meet a building's sensible heating demand.  The two values output here represent some of the coldest temperatures of the year for which only 0.4% and 1.0% of the hours are below (respectively).
        coolingDesignTemps: The temperatures in celcius that ASHRAE recommends using to size a cooling system to meet a building's sensible cooling demand.  The two values output here represent some of the hottest temperatures of the year for which only 0.4% and 1.0% of the hours are above (respectively).
        coolingDayTempRange: The temperature difference between the hottest and coolest outdoor temperatures on the cooling design day.  This is used on conjunction with the warmest temperature (above) and a "Daily Temperature Range Profile" defined by ASHRAE to produce hourly temperatures for a cooling system sizing calculation.
        monthlyTauBeam: Values representing the monthly optical sky depth for beam (direct) solar radiation.  These can be used with the "Ladybug_Design Day Sky" component to create ASHRAE Tau design day solar radiation values.  These values can then be used for sizing HVAC cooling systems.
        monthlyTauDiffuse: Values representing the monthly optical sky depth for diffuse solar radiation.  These can be used with the "Ladybug_Design Day Sky" component to create ASHRAE Tau design day solar radiation values.  These values can then be used for sizing HVAC cooling systems.
        ---------------:...
        extremeHotWeek: An analysis period representing the hottest week of the typical meteorological year.  If the stat file does not specify an extreme hot week, it is the most extreme week of the hottest season.
        typicalSummerWeek: An analysis period representing a typical week of the hottest season in the typical meteorological year.  Not all stat files specify such a week and, in this case, the output here will be "Null."
        typicalAutumnWeek: An analysis period representing a typical autumn week of the typical meteorological year.
        typicalWinterWeek: An analysis period representing a typical week of the coldest season in the typical meteorological year.  Not all stat files specify such a week and, in this case, the output here will be "Null."
        extremeColdWeek: An analysis period representing the coldest week of the typical meteorological year.  If the stat file does not specify an extreme cold week, it is the most extreme week of the coldest season.
"""
ghenv.Component.Name = "Ladybug_Import stat"
ghenv.Component.NickName = 'importSTAT'
ghenv.Component.Message = 'VER 0.0.66\nJUL_26_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import Grasshopper.Kernel as gh

if _statFile != None and _statFile.lower().endswith(".stat"):
    # I read all the lines as a list
    try:
        with open(_statFile, 'r') as statFile:
            statFileLines = statFile.readlines()
            
            #Search the first part of the file for heating design temperatures.
            heatingDesignTemps = []
            htrigger = False
            heatCount1 = 4
            heatCount2 = 3
            for line in statFileLines:
                if 'Coldest' in line:
                    htrigger = True
                    heatLineSplit = line.split('\t')
                    for elementCount, element in enumerate(heatLineSplit):
                        if element == 'HDB 99.6%':
                            heatCount1 = elementCount
                        elif element == 'DB996':
                            heatCount1 = elementCount
                        elif element == 'HDB 99%':
                            heatCount2 = elementCount
                        elif element == 'DB990':
                            heatCount2 = elementCount
                if 'Heating' in line and htrigger == True and not 'Heating DB' in line:
                    htrigger = False
                    heatingDesignTemps.append(line.split('\t')[heatCount1].strip())
                    heatingDesignTemps.append(line.split('\t')[heatCount2].strip())
                    try:
                        heatingDesignTemps = [float(x) for x in heatingDesignTemps]
                        heatingDesignTemps.sort()
                    except:
                        pass
            if heatingDesignTemps == None or heatingDesignTemps == 'Heating':
                warning = 'Failed to find a heating design temperature in the stat file.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            
            #Search the second part of the file for cooling design temperatures.
            coolingDesignTemps = []
            ctrigger = False
            coolCount1 = 4
            coolCount2 = 6
            coolCount3 = 3
            for line in statFileLines:
                if 'Hottest' in line:
                    ctrigger = True
                    coolLineSplit = line.split('\t')
                    for elementCount, element in enumerate(coolLineSplit):
                        if element == 'CDB .4%':
                            coolCount1 = elementCount
                        elif element == 'DB004':
                            coolCount1 = elementCount
                        elif element == 'CDB 1%':
                            coolCount2 = elementCount
                        elif element == 'DB010':
                            coolCount2 = elementCount
                        elif 'Avg DB Range' in element:
                            coolCount3 = elementCount
                        elif element == 'DBR':
                            coolCount3 = elementCount
                if 'Cooling' in line and ctrigger == True and not 'Cooling DB' in line:
                    ctrigger = False
                    coolingDesignTemps.append(line.split('\t')[coolCount1].strip())
                    coolingDesignTemps.append(line.split('\t')[coolCount2].strip())
                    coolingDayTempRange = line.split('\t')[coolCount3].strip()
            if coolingDesignTemps == None or coolingDesignTemps == 'Cooling':
                warn = 'Failed to find a cooling design temperature in the stat file.'
                print warn
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warn)
            
            # Search for the Monthly Optical Sky Depth.
            location = statFileLines[2].split('-- ')[-1].strip()
            monthlyTauBeam = ["key:location/dataType/units/frequency/startsAt/endsAt", location, 'Clear Sky Optical Depth for Beam Irradiance', 'Continuous', 'Monthly', (1, 1, 1), (12, 31, 24)]
            monthlyTauDiffuse = ["key:location/dataType/units/frequency/startsAt/endsAt", location, 'Clear Sky Optical Depth for Diffuse Irradiance', 'Continuous', 'Monthly', (1, 1, 1), (12, 31, 24)]
            for line in statFileLines:
                if 'taub (beam)' in line:
                    beamLineSplit = line.split('\t')
                    beamVals = [float(i) if 'N' not in i else None for i in beamLineSplit[2:14]]
                    avgOptDepth = sum(filter(None, beamVals))/len(filter(None, beamVals))
                    beamVals = [i if i != None else avgOptDepth for i in beamVals]
                    monthlyTauBeam.extend(beamVals)
                elif 'taud (diffuse)' in line:
                    diffLineSplit = line.split('\t')
                    diffVals = [float(i) if 'N' not in i else None for i in diffLineSplit[2:14]]
                    avgOptDepth = sum(filter(None, diffVals))/len(filter(None, diffVals))
                    diffVals = [i if i != None else avgOptDepth for i in diffVals]
                    monthlyTauDiffuse.extend(diffVals)
            if len(monthlyTauBeam) == 7:
                monthlyTauBeam = []
            if len(monthlyTauDiffuse) == 7:
                monthlyTauDiffuse = []
            
            # Figure out the design days from the monthly average temperatures.
            heatingDesignDay = []
            coolingDesignDay = []
            daytrigger = False
            for line in statFileLines[:63]:
                if 'Drybulb 0.4%' in line and not '=' in line and not 'Monthly Design Drybulb Temperature' in line:
                    designLineSplit = line.split('\t')[2:14]
                    designLineSplit = [float(i) for i in designLineSplit]
                    designLineSplit, designMonths = zip(*sorted(zip(designLineSplit, range(1,12))))
                    heatingDesignDay = [(designMonths[0], 21, 1),(designMonths[0], 21, 24)]
                    coolingDesignDay = [(designMonths[-1], 21, 1),(designMonths[-1], 21, 24)]
                elif 'Monthly Statistics for Dry Bulb temperatures' in line and heatingDesignDay == [] and coolingDesignDay == []:
                    daytrigger = True
                elif daytrigger == True and 'Daily Avg' in line:
                    daytrigger = False
                    designLineSplit = line.split('\t')[2:14]
                    designLineSplit = [float(i) for i in designLineSplit]
                    designLineSplit, designMonths = zip(*sorted(zip(designLineSplit, range(1,12))))
                    heatingDesignDay = [(designMonths[0], 21, 1),(designMonths[0], 21, 24)]
                    coolingDesignDay = [(designMonths[-1], 21, 1),(designMonths[-1], 21, 24)]
            
            # Search line by line  after line 220 for the climate zones.
            for line in statFileLines[220:]:
                if 'Climate type' in line:
                    # The first line is climate type based on Koppen.
                    koppenClimateZone = line.split('"')[1]
                    break
            
            # Add climate definition for koppenClimate types
            # Climate descriptions mentioned below are taken from following two links;
            # http://bigladdersoftware.com/epx/docs/8-3/auxiliary-programs/koppen-climate-classification.html
            # https://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification
            koppenClimateName = {
            "af" : "Tropical Rainforest Climate\n" + \
                    "This type of climate has every month of the year with an average temperature of 18 C (64.4 F) or higher, with precipitation all year long. Monthly temperature variations in this climate are less than 3 degrees Celsius. Because of intense surface heating and high humidity cumulus and cumulonimbus clouds form early in the afternoons almost every day. Daily highs are about 32 degrees Celsius while night time temperatures average 22 degrees Celsius.\n" + \
                    "Examples;\n" + \
                    "Singapore\n" + \
                    "West Palm Beach, Florida, USA\n" + \
                    "Hilo, Hawai, USA"
                    ,
            "am" : "Tropical monsoon climate\n" + \
                    "This type of climate has every month of the year with an average temperature of 18 C (64.4 F) or higher, with substantial rainfall during the 7 to 9 hottest months of the year. During the dry months, very little rainfall occurs.\n" + \
                    "Examples;\n" + \
                    "Maimi ,Florida, USA"
                    ,
             "aw" : "Tropical wet and dry or Savanna climate\n" + \
                    "This type of climate has every month of the year with an average temperature of 18 C (64.4 F) or higher. This climate has a pronounced dry season during the winter months with the driest month having precipitation less than 60mm (2.4 in) and less than 4% of the total annual precipitation.\n" + \
                    "Examples;\n" + \
                    "Mumbai, India\n" + \
                    "Key West, Florida, USA\n" + \
                    "Naples, Florida, USA\n" + \
                    "Panama City\n" + \
                    "Rio de Janeiro, Rio de Janeiro, Brazil"
                    ,
             "as" : "Tropical wet and dry or Savanna climate\n" + \
                    "This type of climate has every month of the year with an average temperature of 18 C (64.4 F) or higher. This climate has a pronounced dry season during the winter months with the driest month having precipitation less than 60mm (2.4 in) and less than 4% of the total annual precipitation.\n" + \
                    "Examples;\n" + \
                    "Mumbai, India\n" + \
                    "Key West, Florida, USA\n" + \
                    "Naples, Florida, USA\n" + \
                    "Panama City\n" + \
                    "Rio de Janeiro, Rio de Janeiro, Brazil"
                    ,
            "bwh" : "Dry climate with a little precipitation throughout most of the year.\n" + \
                    "This is hot and arid desert climate and is often dominated by xerophytic vegetation (The vegetation that has adapted to survive in an environment with little liquid water).\n" + \
                    "Examples;\n" + \
                    "Doha, Qatar\n" + \
                    "Riyadh, Saudi Arabia\n" + \
                    "Dubai, UAE\n" + \
                    "Las Vegas, Nevada, USA\n" + \
                    "Phoenix, Arizona, USA"
                    ,
            "bwk" : "Dry climate with a little precipitation throughout most of the year.\n" + \
                    "This is cold and arid desert climate and is often dominated by xerophytic vegetation (The vegetation that has adapted to survive in an environment with little liquid water).\n" + \
                    "Examples;\n" + \
                    "Turpan, Xinjiang, China"
                    ,
            "bwn" : "Dry climate with a little precipitation throughout most of the year.\n" + \
                    "This is mild and arid desert climate and is often dominated by xerophytic vegetation (The vegetation that has adapted to survive in an environment with little liquid water).\n" + \
                    "Examples;\n" + \
                    "Lima, Peru"
                    ,
            "bsh" : "Dry climate with a little precipitation throughout most of the year.\n" + \
                    "This is hot semi-arid climate. It receives a little more precipitation than the arid (desert) climate. This climate receives this precipitation from the ITCZ (inter-tropical convergence zone) or from mid-latitude cyclones.\n" + \
                    "Examples;\n" + \
                    "Lahore, Pakistan\n" + \
                    "Odessa, Texas, USA\n" + \
                    "Yuanjian, Yunnan, China"
                    ,
            "bsk" : "Dry climate with a little precipitation throughout most of the year.\n" + \
                    "This is cold semi-arid climate. It receives a little more precipitation than the arid (desert) climate. This climate receives this precipitation from the ITCZ (inter-tropical convergence zone) or from mid-latitude cyclones.\n" + \
                    "Examples;\n" + \
                    "Denver, Colorado, USA\n" + \
                    "Tabriz, East Azerbaijan Province, Iran\n" + \
                    "Brooks, Alberta, Canada\n" + \
                    "Shijiazhuang, Hebel, China"
                    ,
            "bsn" : "Dry climate with a little precipitation throughout most of the year.\n" + \
                    "This is mild semi-arid climate. It receives a little more precipitation than the arid (desert) climate. This climate receives this precipitation from the ITCZ (inter-tropical convergence zone) or from mid-latitude cyclones.\n" + \
                    "Examples;\n" + \
                    "Sanaa, Yemen"
                    ,
            "cfa" : "Moist mid-latitude climate with mild winters.\n" + \
                    "This is a temperate climate without dry season and a hot summer.\n" + \
                    "Examples;\n" + \
                    "Sao Paulo, Brazil\n" + \
                    "Brisbane, Australia\n" + \
                    "Sydney, Australia\n" + \
                    "Orlando, Florida, USA\n" + \
                    "New Orleans, Florida, USA\n" + \
                    "Washington D.C. USA\n" + \
                    "Dallas, Texas, USA\n" + \
                    "Srinagar, India\n" + \
                    "Shanghai, China\n" + \
                    "Nanjing, China\n" + \
                    "Tokyo, Japan\n" + \
                    "Osaka, Japan\n" + \
                    "Milan, Italy\n" + \
                    "Durban, South Africa"
                    ,
            "cfb" : "Moist mid-latitude climate with mild winters.\n" + \
                    "This is a temperate climate without dry season and a warm summer.  This climate is also known as the oceanic (marine) climate. Heavy precipitation occurs during the mild winters because of continuous presence of mid-latitude cyclones.\n" + \
                    "Examples;\n" + \
                    "Mexico City, Mexico"
                    ,
            "cfc" : "Moist mid-latitude climate with mild winters.\n" + \
                    "This is a temperate climate without dry season and a cold summer. This climate is also known as the subpolar oceanic climate.\n" + \
                    "Examples;\n" + \
                    "Mount Read, Tasmania, Australia\n" + \
                    "Punta Arenas, Chile"
                    ,
            "csa" : "Moist mid-latitude climate with mild winters.\n" + \
                    "This is a temperate climate with dry and hot summer. This climate is also known as the Mediterranean climate.\n" + \
                    "Examples;\n" + \
                    "Beirut, Lebanon\n" + \
                    "Tel Aviv, Israel\n" + \
                    "Los Angeles, California, USA\n" + \
                    "Perth, Australia\n" + \
                    "Tangier, Morocco\n" + \
                    "Rome, Italy\n" + \
                    "Seville, Spain\n" + \
                    "Madrid, Spain\n" + \
                    "Marseille, France\n" + \
                    "Athens, Greece"
                    ,
            "csb" : "Moist mid-latitude climate with mild winters.\n" + \
                    "This is a temperate climate with dry and warm summer.\n" + \
                    "Examples;\n" + \
                    "San Francisco, California, USA\n" + \
                    "Seattle, Washington, USA\n" + \
                    "Cape Town, South Africa\n" + \
                    "Kington SE, Australia"
                    ,
            "csc" : "Moist mid-latitude climate with mild winters.\n" + \
                    "This is a temperate climate with dry and cold summer. This is apparently a rare climate type.\n" + \
                    "Examples;\n" + \
                    "Balmaceda, Chile\n" + \
                    "Haleakala Summit, Hawaii, USA"
                    ,
            "cwa" : "Moist mid-latitude climate with mild winters.\n" + \
                    "This is a temperate climate with dry winter and hot summer. This climate has a classic dry winter / wet summer pattern associated with tropical monsoonal climates.\n" + \
                    "Examples;\n" + \
                    "Islamabad, Pakistan\n" + \
                    "New Delhi, India\n" + \
                    "Zhengzhou, China\n" + \
                    "Hong Kong\n" + \
                    "Hanoi, Vietnam"
                    ,
            "cwb" : "Moist mid-latitude climate with mild winters.\n" + \
                    "This is a temperate climate with dry winter and warm summer. In this climate winters are noticeable and dry, and summers can be very rainy.\n" + \
                    "Examples;\n" + \
                    "Nairobi, Kenya\n" + \
                    "Mexico City, Mexico\n" + \
                    "Johannesburg, South Africa\n" + \
                    "Kunming, China"
                    ,
            "cwc" : "Moist mid-latitude climate with mild winters.\n" + \
                    "This is a temperate climate with dry winter and cold summer.\n" + \
                    "Examples;\n" + \
                    "EI Alto, Bolivia"
                    ,
            "dsa" : "Moist mid-latitude climate with cold winters.\n" + \
                    "This is a cold climate with dry and hot summer.\n" + \
                    "Examples;\n" + \
                    "Saqqez, Iran\n" + \
                    "Cambridge, Idaho, USA"
                    ,
            "dsb" : "Moist mid-latitude climate with cold winters.\n" + \
                    "This is a cold climate with dry and warm summer.\n" + \
                    "Examples;\n" + \
                    "South Lake Tahoe, California, USA\n" + \
                    "Bridgeport, California, USA"
                    ,
            "dsc" : "Moist mid-latitude climate with cold winters.\n" + \
                    "This is a cold climate with dry and cold summer.\n" + \
                    "Examples;\n" + \
                    "Homer, Alaska, USA\n" + \
                    "Brian Head, Utah, USA"
                    ,
            "dsd" : "Moist mid-latitude climate with cold winters.\n" + \
                    "This is a cold climate with dry summer and very cold winter."
                    ,
            "dwa" : "Moist mid-latitude climate with cold winters.\n" + \
                    "This is a cold climate with dry winter and hot summer.\n" + \
                    "Examples;\n" + \
                    "Beijing, China\n" + \
                    "Seoul, South Korea"
                    ,
            "dwb" : "Moist mid-latitude climate with cold winters.\n" + \
                    "This is a cold climate with dry winter and warm summer.\n" + \
                    "Examples;\n" + \
                    "Pembina, North Dakota, USA\n" + \
                    "Heihe, China"
                    ,
            "dwc" : "Moist mid-latitude climate with cold winters.\n" + \
                    "This is a cold climate with dry winter and cold summer.\n" + \
                    "Examples;\n" + \
                    "Mohe County, Heliongjiang, China\n" + \
                    "Yushu City, Qinghai, China"
                    ,
            "dwd" : "Moist mid-latitude climate with cold winters.\n" + \
                    "This is a cold climate with dry and very cold winter.\n" + \
                    "Examples;\n" + \
                    "Seymchan, Magadan Oblast, Russia\n" + \
                    "Oymyakon, Sakha Republic, Russia"
                    ,
            "dfa" : "Moist mid-latitude climate with cold winters.\n" + \
                    "This is a cold climate without dry season and hot summer.\n" + \
                    "Examples;\n" + \
                    "Chicago, Illinois, USA\n" + \
                    "Columbus, Ohio, USA\n" + \
                    "Boston, Massachusetts, USA\n" + \
                    "Omaha, Nebraska, USA\n" + \
                    "Minneapolis, Minnesota, USA\n" + \
                    "Windsor, Ontario, Canada"
                    ,
            "dfb" : "Moist mid-latitude climate with cold winters.\n" + \
                    "This is a cold climate without dry season and warm summer.\n" + \
                    "Examples;\n" + \
                    "Calgary, Alberta, Canada\n" + \
                    "Winnipeg, Manitoba, Canada\n" + \
                    "Ottawa, Ontario, Canada\n" + \
                    "Toronto Islands, Ontario, Canada\n" + \
                    "London, Ontario, Canada\n" + \
                    "Kiev, Ukraine\n" + \
                    "Moscow, Russia\n" + \
                    "Saint Petersburg, Russia\n" + \
                    "Stockholm, Sweden\n" + \
                    "Oslo, Norway\n" + \
                    "Lillehammer, Norway\n" + \
                    "Portland, Maine, USA\n" + 
                    "Montpelier, Vermont, USA\n" + \
                    "Binghamton, New York, USA"
                    ,
            "dfc" : "Moist mid-latitude climate with cold winters.\n" + \
                    "This is a cold climate without dry season and cold summer.\n" + \
                    "Examples;\n" + \
                    "Fraser, Colorado, USA\n" + \
                    "Fairbanks, Alaska, USA\n" + \
                    "Whitehorse, Yukon, Canada\n" + \
                    "Churchill, Manitoba, Canada"
                    ,
            "dfd" : "Moist mid-latitude climate with cold winters.\n" + \
                    "This is a cold climate without dry season and very cold winter.\n" + \
                    "Examples;\n" + \
                    "Yakutsk, Sakha Republic, Russia\n" + \
                    "Verkhoyansk, Sakha Republic, Russia"
                    ,
             "et" : "Polar climate with extremely cold winters and summers\n" + \
                    "Polar climates have year-round cold temperatures with warmest month less than 10 C. Polar climates are found on the northern coastal areas of North America and Europe, Asia and on the landmasses of Greenland and Antarctica. Two minor climate types exist. ET or polar tundra is a climate where the soil is permanently frozen to depths of hundreds of meters, a condition known as permafrost. Vegetation is dominated by mosses, lichens, dwarf trees and scattered woody shrubs.\n" + \
                    "Examples;\n" + \
                    "Mount Rainier, Washington, USA\n" + \
                    "Macquarie Island\n" + \
                    "Nagqu, Tibet, China"
                    ,
             "ef" : "Polar climate with extremely cold winters and summers\n" + \
                    "Polar climates have year-round cold temperatures with warmest month less than 10 C. Polar climates are found on the northern coastal areas of North America and Europe, Asia and on the landmasses of Greenland and Antarctica. Two minor climate types exist. EF or polar ice caps has a surface that is permanently covered with snow and ice.\n" + \
                    "Examples;\n" + \
                    "Mount Ararat, Turkey\n" + \
                    "Grossglockner, Carinthia, Austria\n" + \
                    "Mount Everest, Nepal\n" + \
                    "Summit Camp, Greenland\n" + \
                    "Scott Base, Antarctica\n" + \
                    "Vostok Station, Antarctica, location of the lowest air temperature ever recorded on Earth.\n" + \
                    "McMurdo Station, Antarctica\n" + \
                    "Byrd Station, Antarctica"
                    ,
              "h" : "Highland areas due to mountainous areas. This classification can encompass any of the climate type\n" + \
                    "Highland areas can encompass any of the previously mentioned major categories  the determining factor is one of altitude (temperature decreases roughly 2 C for every increase of 305 m). This is a complex climate zone. Highland regions roughly correspond to the major categories change in temperature with latitude - with one important exception. Seasons only exist in highlands if they also exist in the nearby lowland regions. For example, although A climates have cooler temperatures at higher elevations, the seasonal changes of C, D and E climates are not present."
            }
            
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
            "1A" : "Very Hot - Humid",
            "1B" : "Dry",
            "2A" : "Hot - Humid",
            "2B" : "Dry",
            "3A" : "Warm - Humid",
            "3B" : "Dry",
            "3C" : "Warm - Marine",
            "4A" : "Mixed - Humid",
            "4B" : "Dry",
            "4C" : "Mixed - Marine",
            "5A" : "Cold - Humid",
            "5B" : "Dry",
            "5C" : "Marine",
            "6A" : "Cold - Humid",
            "6B" : "Dry",
            "7" : "Very Cold",
            "8" : "Subarctic"
            }
            
            
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
            if extremeHotWeek == None:
                print 'No extreme hot week was found in the stat file.'
            else: pass
            
            #Search for the typical hot period.
            typicalSummerWeek = None
            for lineCount, line in enumerate(statFileLines):
                if 'Typical Summer Week' in line:
                    hotStart =(statFileLines[lineCount+1].split(':'))[1].split()
                    hotEnd = (statFileLines[lineCount+1].split(':'))[2].split(',')[0].split()
                    typicalSummerWeek = ((monthNumber(hotStart[0]), int(hotStart[1]), 1), ((monthNumber(hotEnd[0]), int(hotEnd[1]), 24)))
            if typicalSummerWeek == None:
                print 'No typical Summer week was found in the stat file.'
                ghenv.Component.Params.Output[10].NickName = "."
                ghenv.Component.Params.Output[10].Name = "."
                ghenv.Component.Params.Output[10].Description = " "
            else:
                ghenv.Component.Params.Output[10].NickName = "typicalSummerWeek"
                ghenv.Component.Params.Output[10].Name = "typicalSummerWeek"
                ghenv.Component.Params.Output[10].Description = "An analysis period representing a typical week of the hottest season in the typical meteorological year.  Not all stat files specify such a week and, in this case, the output here will be 'Null.'"
            
            #Search for the typical autumn period.
            typicalAutumnWeek = None
            for lineCount, line in enumerate(statFileLines):
                ghenv.Component.Params.Output[11].NickName = "typicalAutumnWeek"
                ghenv.Component.Params.Output[11].Name = "typicalAutumnWeek"
                ghenv.Component.Params.Output[11].Description = "An analysis period representing a typical Autumn week of the typical meteorological year."
                if 'Typical Autumn Week' in line:
                    #The file contains multiple typical periods and I just want the Autumn one.
                    typStart =(statFileLines[lineCount+1].split(':'))[1].split()
                    typEnd = (statFileLines[lineCount+1].split(':'))[2].split(',')[0].split()
                    typicalAutumnWeek = ((monthNumber(typStart[0]), int(typStart[1]), 1), ((monthNumber(typEnd[0]), int(typEnd[1]), 24)))
            if typicalAutumnWeek == None:
                ghenv.Component.Params.Output[11].NickName = "typicalWeek"
                ghenv.Component.Params.Output[11].Name = "typicalWeek"
                ghenv.Component.Params.Output[11].Description = "An analysis period representing a typical week of the typical meteorological year."
                #The file contains only one typical period and I will take that one.
                for line in statFileLines:
                    if 'Typical Week Period selected' in line:
                        typStart = (line.split(':'))[1].split()
                        typEnd = (line.split(':'))[2].split(',')[0].split()
                        typicalWeek = ((monthNumber(typStart[0]), int(typStart[1]), 1), ((monthNumber(typEnd[0]), int(typEnd[1]), 24)))
            
            typicalSpringWeek = None
            for lineCount, line in enumerate(statFileLines):
                if 'Typical Spring Week' in line:
                    #The file contains multiple typical periods and I just want the Spring one.
                    typStart =(statFileLines[lineCount+1].split(':'))[1].split()
                    typEnd = (statFileLines[lineCount+1].split(':'))[2].split(',')[0].split()
                    typicalSpringWeek = ((monthNumber(typStart[0]), int(typStart[1]), 1), ((monthNumber(typEnd[0]), int(typEnd[1]), 24)))
            if typicalSpringWeek == None:
                print 'No typical Spring week was found in the stat file.'
                ghenv.Component.Params.Output[12].NickName = "."
                ghenv.Component.Params.Output[12].Name = "."
                ghenv.Component.Params.Output[12].Description = " "
            else:
                ghenv.Component.Params.Output[12].NickName = "typicalSpringWeek"
                ghenv.Component.Params.Output[12].Name = "typicalSpringWeek"
                ghenv.Component.Params.Output[12].Description = "An analysis period representing a typical Spring week of the typical meteorological year.  Not all stat files specify such a week and, in this case, the output here will be 'Null.'"
            
            
            #Search for the typical cold period.
            typicalWinterWeek = None
            for lineCount, line in enumerate(statFileLines):
                if 'Typical Winter Week' in line:
                    coldStart =(statFileLines[lineCount+1].split(':'))[1].split()
                    coldEnd = (statFileLines[lineCount+1].split(':'))[2].split(',')[0].split()
                    typicalWinterWeek = ((monthNumber(coldStart[0]), int(coldStart[1]), 1), ((monthNumber(coldEnd[0]), int(coldEnd[1]), 24)))
                else: pass
            if typicalWinterWeek == None:
                print 'No typical Winter week was found in the stat file.'
                ghenv.Component.Params.Output[13].NickName = "."
                ghenv.Component.Params.Output[13].Name = "."
                ghenv.Component.Params.Output[13].Description = " "
            else:
                ghenv.Component.Params.Output[13].NickName = "typicalWinterWeek"
                ghenv.Component.Params.Output[13].Name = "typicalWinterWeek"
                ghenv.Component.Params.Output[13].Description = "An analysis period representing a typical week of the coldest season in the typical meteorological year.  Not all stat files specify such a week and, in this case, the output here will be 'Null.'"
            
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
            
            
            # This is the list container for koppenZoneDescription output from this component.
            koppenZoneDescription = []
            if koppenClimateZone.lower() in koppenClimateName.keys():
                key = koppenClimateZone.lower()
                koppenZoneDescription = koppenClimateName[key]
                print'Koppen Zone Description:\n' + koppenZoneDescription
            else:
                pass
            
            # This is the string variable for the output of ashraeClimateZoneName on this component.
            ashraeZoneDescription = ""
            if ashraeClimateZone in climateName.keys():
                ashraeZoneDescription = climateName[ashraeClimateZone]
                print 'ASHRAE Zone Description:\n' + ashraeZoneDescription
            else:
                pass
            
    except Exception, e:
        msg = "Failed to parse stat file." + str(e)
        print msg
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
elif _statFile != None:
    warning = '_statFile is not a valid .stat file.'
    print warning
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
else:
    print "Please connect a stat file path location."