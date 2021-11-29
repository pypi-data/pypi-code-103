'''
Handles night cycle for HVAC system
'''

def availability_managers(building,T_zone,T_set,dt,fan_avail):
    override = False
    for i in range(len(building['hvac']['managers']['name'])):
        if building['hvac']['managers']['type'][i]=='NightCycle':
            l = building['hvac']['managers']['loop'][i]
            z_i = [z for z,x in enumerate(building['zones']['air_loop']) if x==l] #zones on this loop
            
            if 'runtime_control_type' in building['hvac']['managers'] and building['hvac']['managers']['runtime_control_type'][i]=='fixedruntime':
                uncomfortable = False
                for x in z_i:
                    if ((T_zone[x]>(T_set['cool'][x] + building['hvac']['managers']['thermostat_tolerance'][i])
                        or T_zone[x]<(T_set['heat'][x] - building['hvac']['managers']['thermostat_tolerance'][i]))
                        and T_set['no_hvac'][x]==False):
                        uncomfortable = True
                        break
                if uncomfortable: ## outside bounds, need to override
                    on_loop = [i for i,x in enumerate(building['hvac']['components']['loop']) if x==l]
                    for j in on_loop:
                        if building['hvac']['components']['type'][j][:4]=='fan:' :
                            if fan_avail[building['hvac']['components']['name'][j]] == 0:
                                fan_avail[building['hvac']['components']['name'][j]] = min(1,building['hvac']['managers']['runtime'][i]/dt)
                                override = True #turn fan on when system is off
                        elif building['hvac']['components']['type'][j]=='airloophvac:unitaryheatcool':
                            u = building['unitary_heat_cool']['name'].index(building['hvac']['components']['name'][j])
                            if fan_avail[building['unitary_heat_cool']['fan_name'][u]] == 0:
                                fan_avail[building['unitary_heat_cool']['fan_name'][u]]= min(1,building['hvac']['managers']['runtime'][i]/dt)
                                override = True #turn fan on when system is off
            else:
                print('need runtime control other than fixedruntime for night manager')

        elif building['hvac']['managers']['type'][i]=='Scheduled':
            pass
        else:
            print('need to code other types of availability managers')
    return fan_avail,override