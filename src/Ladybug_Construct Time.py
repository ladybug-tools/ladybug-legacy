# Construct Time
# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to construct a specific hour from corresponding time in hours, minutes and seconds.  The output can be plugged into the analysisPeriod or sunPath components.
-
Provided by Ladybug 0.0.57

    Args:
        _hour_: A number between 1 and 23 representing the hour of the day.
        _minutes_: A number between 1 and 60 representing the minute of the hour.
        _seconds_: A number between 1 and 60 representing the second of the minute.
    Returns:
        hour: An output hour that an be plugged into the analysisPeriod or sunPath components.

"""
ghenv.Component.Name = "Ladybug_Construct Time"
ghenv.Component.NickName = 'constructTime'
ghenv.Component.Message = 'VER 0.0.57\nMAR_26_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

hour = _hour_ + _minutes_/60 + _seconds_/3600