# import .stat file data
# By Chris MAckey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to import climate data that can only be found in the .stat file that downloads in the .zip folder with the .epw file.
Sepcifcally, this includes the ASHRAE and Koppen climate zones as well as design temperatures representing the temperature extremes of the climate that should be used to design and size heating and cooling systems.
-
Provided by Ladybug 0.0.57
    
    Args:
        _statFile: A .stat file path on your system from the Open STAT file component (or typed out as a string).
        
    Returns:
        readMe!: ...
        ashraeClimateZone: The estimated ASHRAE climate zone of the STAT file.  ASHRAE climate zones are frequently used to make suggestions for heating and cooling systems and correspond to recommendations for insulation levels of a building.  For more information, see this pdf: https://www.ashrae.org/File%20Library/docLib/Public/20081111_CZTables.pdf
        koppenClimateZone: The estimated Koppen climate zone of the STAT file.  The Koppen climate classification is the most widely used climate classification system and is based on the concept that native vegetation is the best expression of climate. Thus, Koppen climate zones combine average annual and monthly temperatures, precipitation, and the seasonality of precipitation.  For more information, see the wikipendia page on Koppen climate: http://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification.
        heatingDesignTemp: The temperature in Celcius that ASHRAE recommends using to design a heating system for a building.  It rempresents the one of the coldest temperatures of the year for which only 0.4% of the hours are below.
        coolingDesignTemp: The temperature in Celcius that ASHRAE recommends using to design a cooling system for a building.  It rempresents the one of the hottest temperatures of the year for which only 0.4% of the hours are above.
"""
ghenv.Component.Name = "Ladybug_Import stat"
ghenv.Component.NickName = 'importSTAT'
ghenv.Component.Message = 'VER 0.0.57\nMAR_31_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import Grasshopper.Kernel as gh

if _statFile and _statFile.lower().endswith(".stat"):
    # I read all the lines as a list
    try:
        with open(_statFile, 'r') as statFile:
            statFileLines = statFile.readlines()
            
            #Search the first part of the file for heating and then cooling design temperatures.
            heatCount = 1
            for line in statFileLines[:30]:
                if 'ColdestMonth' or 'Coldest Month' in line:
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
            
            coolCount = 1
            for line in statFileLines[:30]:
                if 'HottestMonth' or 'Hottest Month' in line:
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
    except Exception, e:
        #print `e`
        msg = "Invalid stat file path."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        pass
else:
    print "Please connect a stat file path location."