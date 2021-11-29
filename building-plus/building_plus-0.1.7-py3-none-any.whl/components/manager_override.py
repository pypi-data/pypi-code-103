'''
overides temperature setpoints at specific nodes, e.g. cold air supply
'''
from building_plus.components.fan_calc import fan_calc
from building_plus.basic.psychometric import psychometric

def manager_override(building,profile,node,setpoint,air,fresh_air,fan_avail):
    k = [i for i,x in enumerate(building['manager']['node']) if x ==node]
    if len(k)>0:
        for i in k:
            if building['manager']['type'][i]=='OutdoorAirReset':
                if building['manager']['low_temp'][i]<building['manager']['high_temp'][i]:
                    if fresh_air['Tdb'] < building['manager']['low_temp'][i]:
                        setpoint = building['manager']['setpoint_at_low_temp'][i]
                    elif fresh_air['Tdb']>building['manager']['high_temp'][i]:
                        setpoint = building['manager']['setpoint_at_high_temp'][i]
                    else:
                        setpoint = building['manager']['setpoint_at_low_temp'][i] - (fresh_air['Tdb'] - building['manager']['low_temp'][i])/(building['manager']['high_temp'][i] - building['manager']['low_temp'][i])*(building['manager']['setpoint_at_low_temp'][i] - building['manager']['setpoint_at_high_temp'][i])
                else:
                    setpoint = 0.5*(building['manager']['setpoint_at_low_temp'][i] + building['manager']['setpoint_at_high_temp'][i])
            elif building['manager']['type'][i]=='Scheduled':
                setpoint = profile[building['manager']['schedule'][i]]
            elif building['manager']['type'][i]=='MixedAir':
                if air['m_dot']>0:
                    for x in building['fans']:
                        if building['fans'][x]['inlet']==building['manager']['fan_inlet_node'][i]:
                            fan_name = x
                            break
                    _,_,Q_to_air = fan_calc(building['fans'][fan_name],air,fan_avail[fan_name])
                    #cooling in zone calculation is m*Cp*dT, not h2-h1, so need to ensure sensible load = m*Cp*(Tsupply -Tzone)
                    spec_heat_supply = 1006 + 1860*air['w'] #J/kg*K
                    setpoint = setpoint - Q_to_air/(air['m_dot']*spec_heat_supply)
            elif building['manager']['type'][i]=='FollowOutdoorAirTemperature':
                if building['manager']['ref_temp_type'][i]=='OutdoorAirWetBulb' or building['manager']['ref_temp_type'][i]=='OutdoorWetBulb':
                    setpoint = psychometric(fresh_air,'Twb') + building['manager']['offset_temperature'][i]
                elif building['manager']['ref_temp_type'][i]=='OutdoorAirDryBulb' or building['manager']['ref_temp_type'][i]=='OutdoorDryBulb':
                    setpoint = fresh_air['Tdb'] + building['manager']['offset_temperature'][i]
                setpoint = max(building['manager']['min_temperature'][i],min(building['manager']['max_temperature'][i],setpoint))
            elif building['manager']['type'][i]=='SingleZone:Reheat':
                #handled elsewhere
                pass
            elif building['manager']['type'][i]=='SingleZone:Humidity:Minimum':
                #need to add for hospital see page 1396
                pass
            elif building['manager']['type'][i]=='SingleZone:Humidity:Maximum':
                #need to add for hospital
                pass
            else:
                print('need more HVAC manager types')
    return setpoint