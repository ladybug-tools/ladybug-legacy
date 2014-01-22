# import .epw file data
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Import weather data to Grasshopper from a standard .epw file.
For detailed information about the structure of an epw file, you may want to read the
"Weather Converter Program" section in "Auxiliary EnergyPlus Programs" document.
All the output definitions are borrowed from the same document.
The document is available online at this address:
"http://apps1.eere.energy.gov/buildings/energyplus/pdfs/auxiliaryprograms.pdf"
-
Provided by Ladybug 0.0.53
    
    Args:
        _epwFile: epw file location on your system as a string
        
    Returns:
        readMe!: ...
        latitude: Latitude of the location. Useful to draw the sunpath.
        location: Summary of location data
        dryBulbTemperature: "This is the dry bulb temperature, in C, at the time indicated. Note that this is a full numeric field (i.e. 23.6) and not an integer representation with tenths. Valid values range from 70 C to 70 C. Missing value for this field is 99.9."
        dewPointTemperature: "This is the dew point temperature, in C, at the time indicated. Note that this is a full numeric field (i.e. 23.6) and not an integer representation with tenths. Valid values range from 70 C to 70 C. Missing value for this field is 99.9."
        relativeHumidity: "This is the Relative Humidity in percent at the time indicated. Valid values range from 0% to 110%. Missing value for this field is 999."
        windSpeed: "This is the wind speed in m/sec (wind speed at time indicated). Values can range from 0 to 40. Missing value is 999."
        windDirection: "This is the Wind Direction in degrees where the convention is that North=0.0, East=90.0, South=180.0, West=270.0. (Wind direction in degrees at the time indicated. If calm, direction equals zero.) Values can range from 0 to 360. Missing value is 999."
        directNormalRadiation: "This is the Direct Normal Radiation in Wh/m2. (Amount of solar radiation in Wh/m2 received directly from the solar disk on a surface perpendicular to the sun's rays, during the number of minutes preceding the time indicated.) If the field is missing ( 9999) or invalid (<0), it is set to 0. Counts of such missing values are totaled and presented at the end of the runperiod."
        diffuseHorizontalRadiation: "This is the Diffuse Horizontal Radiation in Wh/m2. (Amount of solar radiation in Wh/m2 received from the sky (excluding the solar disk) on a horizontal surface during the number of minutes preceding the time indicated.) If the field is missing ( 9999) or invalid (<0), it is set to 0. Counts of such missing values are totaled and presented at the end of the runperiod."
        globalHorizontalRadiation: "This is the Global Horizontal Radiation in Wh/m2. (Total amount of direct and diffuse solar radiation in Wh/m2 received on a horizontal surface during the number of minutes preceding the time indicated.) It is not currently used in EnergyPlus calculations. It should have a minimum value of 0; missing value for this field is 9999."
        directNormalIlluminance: "This is the Direct Normal Illuminance in lux. (Average amount of illuminance in hundreds of lux received directly from the solar disk on a surface perpendicular to the sun's rays, during the number of minutes preceding the time indicated.) It is not currently used in EnergyPlus calculations. It should have a minimum value of 0; missing value for this field is 999999 and will be considered missing of >= 999900."
        diffuseHorizontalIlluminance: "This is the Diffuse Horizontal Illuminance in lux. (Average amount of illuminance in hundreds of lux received from the sky (excluding the solar disk) on a horizontal surface during the number of minutes preceding the time indicated.) It is not currently used in EnergyPlus calculations. It should have a minimum value of 0; missing value for this field is 999999 and will be considered missing of >= 999900."
        globalHorizontalIlluminance: "This is the Global Horizontal Illuminance in lux. (Average total amount of direct and diffuse illuminance in hundreds of lux received on a horizontal surface during the number of minutes preceding the time indicated.) It is not currently used in EnergyPlus calculations. It should have a minimum value of 0; missing value for this field is 999999 and will be considered missing of >= 999900."
        totalSkyCover: "This is the value for total sky cover (tenths of coverage). (i.e. 1 is 1/10 covered. 10 is total coverage). (Amount of sky dome in tenths covered by clouds or obscuring phenomena at the hour indicated at the time indicated.) Minimum value is 0; maximum value is 10; missing value is 99."
        liquidPrecipitationDepth: "The amount of liquid precipitation(mm) observed at the indicated time for the period indicated in the liquid precipitation quantity field. If this value is not missing, then it is used and overrides the precipitation flag as rainfall.  Conversely, if the precipitation flag shows rain and this field is missing or zero, it is set to 1.5 (mm)."
        barometricPressure: "This is the station pressure in Pa at the time indicated. Valid values range from 31,000 to 120,000... Missing value for this field is 999999."
"""
ghenv.Component.Name = "Ladybug_Import epw"
ghenv.Component.NickName = 'importEPW'
ghenv.Component.Message = 'VER 0.0.53\nJan_22_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "0 | Ladybug"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh

def main(_epw_file):
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        
        locationData = lb_preparation.epwLocation(_epw_file)
        weatherData = lb_preparation.epwDataReader(_epw_file, locationData[0])
        
        return locationData, weatherData
    
    else:
        warningM = "First please let the Ladybug fly..."
        print warningM
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warningM)
        return -1
    


# Collecting Data
if _epwFile and _epwFile.endswith('.epw'):
    result = main(_epwFile)
    if result!= -1:
        location, locName, latitude = result[0][-1], result[0][0], result[0][1]
        dryBulbTemperature, dewPointTemperature, relativeHumidity, windSpeed, windDirection, directNormalRadiation, diffuseHorizontalRadiation, globalHorizontalRadiation, directNormalIlluminance, diffuseHorizontalIlluminance, globalHorizontalIlluminance, totalSkyCover, liquidPrecipitationDepth, barometricPressure = result[1][:]
        print 'Hourly weather data for ' + locName + ' is imported successfully!'
else:
    print "Please connect a valid epw file address to _epw_file input..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "Please connect a valid epw file address to _epw_file input...")