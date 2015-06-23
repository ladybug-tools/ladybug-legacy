# Comfort Parameters
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to set PMV comfort parameters for the PMV comfort calculator or the Psychrometric Chart.  
_
Parameters include whether comfort is defined by 80 or 90 percent of the occupants comfortable as well as maximum and minimum acceptable humidity ratios.  Note that the applied science and engineering community differs widely on its inderstanding of these parameters.
_
The air conditioning industy set out with the goal of satisfying 80% of the occupants (assuming they all had similar clothing and metabolic rates) but many today set 90% as their benchmark.  Also note that, if you try to restrict everyone's clothing and metabolic rate as the PMV model assumed, you can never make 100% of the people comfortable.
_
Further note that cultures differ widely in terms of their treatment of humidity at cooler temperatures and lack of humidity.
-
Provided by Ladybug 0.0.59
    
    Args:
        PPDComfortThreshold_: A number between 5 and 100 that represents the percent of people dissatisfied (PPD) at which point a given set of conditions are outside of a comfortable range.  The default is set to 10 percent, which is the typical criteria for both US and European (ISO) standards. However, both of these standards allow an expanded range for infrequenlty-occupied buildings (20% in the US and 15% in Europe) and the European standard requires 6% for 'Class I' buildings.  Note that, if you try to restrict everyone's clothing and metabolic rate as the PMV model assumes, you can never make 100% of the people comfortable.  This is why the smallest acceptable input here is 5%.
        humidRatioUpBound_: An optional number between 0.012 and 0.030 that limits the maximum humidity ratio acceptable for comfort.  In many cultures and to many people, humidity in conditions of no thermal stress is not considered a source of discomfort and, accordingly, this component does not set an upper limit on humidity by default.  However, for some people, stickyness from humidity in cool conditons is considered uncomfortable and, if you want to account for such a situation, you may want to set an upper limit on the acceptable humidity ratio here.  The ASHRAE 55 PMV comfort standard recommends a maximum humidity of 0.012 kg water/kg air.
        humidRatioLowBound_: An optional number between 0.000 and 0.005 that limits the minimum humidity ratio acceptable for comfort.  In many cultures, a lack of humidity is not considred uncomfortable since people compensate for its effects by using chap stick and lotions.  Accordingly, this component does not set a lower limit on humidity by default.  However, in some more tropical where people are not accustomed to very dry environments, chaping of lips and drying of skin can occur more easily and, if you want to account for such a situation, you may want to set a lower limit on the acceptable humidity ratio here. The ASHRAE 55 PMV comfort recommends no lower limit on humidity.
        
    Returns:
        comfortPar: Comfort parameters that you can plug into either the "Ladybug_PMV Comfort Calculator" or the "Ladybug_Psychrometric Chart."
"""
ghenv.Component.Name = "Ladybug_PMV Comfort Parameters"
ghenv.Component.NickName = 'ComfortPar'
ghenv.Component.Message = 'VER 0.0.59\nJUN_23_2015'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "4 | Extra"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import Grasshopper.Kernel as gh

comfortPar = []

if PPDComfortThreshold_ != None:
    if PPDComfortThreshold_ <= 100 and PPDComfortThreshold_ >= 5:
        comfortPar.append(PPDComfortThreshold_)
    else:
        comfortPar.append(10.0)
        warning = 'The PPDComfortThreshold_ must be a number between 5 and 100.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
else:
    comfortPar.append(10.0)

if humidRatioUpBound_ != None:
    if humidRatioUpBound_ <= 0.03 and humidRatioUpBound_ >= 0.012:
        comfortPar.append(humidRatioUpBound_)
    else:
        comfortPar.append(0.03)
        warning = 'The humidityRatioUpBound_ must be a number between 0.012 and 0.030.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
else:
    comfortPar.append(0.03)

if humidRatioLowBound_ != None:
    if humidRatioLowBound_ <= 0.005 and humidRatioLowBound_ >= 0.0:
        comfortPar.append(humidRatioLowBound_)
    else:
        comfortPar.append(0.0)
        warning = 'The humidRatioLowBound_ must be a number between 0.012 and 0.030.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
else:
    comfortPar.append(0.0)
