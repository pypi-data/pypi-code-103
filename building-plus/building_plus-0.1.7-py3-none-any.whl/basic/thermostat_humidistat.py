def thermostat_humidistat(building,profile,T_zone):
    ## HVAC temperature Schedules
    T_set = {}
    T_set['heat'] = [T_zone[i] for i in range(len(T_zone))]
    T_set['cool'] = [T_zone[i] for i in range(len(T_zone))]
    w_set = {}
    w_set['humidify'] = [0 for i in range(len(T_zone))]
    w_set['dehumidify'] = [1 for i in range(len(T_zone))]
    T_set['no_hvac'] = [True for i in range(len(building['zones']['name']))]
    for i in building['zone_controls']:
        z = building['zones']['name'].index(building['zone_controls'][i]['zone'])
        if building['zone_controls'][i]['type']=='Thermostat':
                T_set['no_hvac'][z] = False
                ct_now = profile[building['zone_controls'][i]['control_type_schedule']]
                c_avail = building['zone_controls'][i]['control_type']
                c_type = []
                for j  in c_avail:
                    if j=='thermostatsetpoint:singleheating':
                            c_type.append(1)
                    elif j=='thermostatsetpoint:singlecooling':
                            c_type.append(2)
                    elif j=='thermostatsetpoint:singleheatingorcooling':
                            c_type.append(3)
                    elif j=='thermostatsetpoint:dualsetpoint':
                            c_type.append(4)
                k = c_type.index(ct_now)
                c = building['zone_controls'][i]['control_name'][k]
                if  c_avail[k]== 'thermostatsetpoint:singleheating':
                        T_set['heat'][z] = profile[building['thermostat'][c]['heating']]
                elif c_avail[k] == 'thermostatsetpoint:singlecooling':
                        T_set['cool'][z] = profile[building['thermostat'][c]['cooling']]
                elif c_avail[k] == 'thermostatsetpoint:singleheatingorcooling':
                        T_set['heat'][z] = profile[building['thermostat'][c]['heating']]
                        T_set['cool'][z] = profile[building['thermostat'][c]['heating']]
                elif c_avail[k] == 'thermostatsetpoint:dualsetpoint':
                        T_set['heat'][z] = profile[building['thermostat'][c]['heating']]
                        T_set['cool'][z] = profile[building['thermostat'][c]['cooling']]
        elif building['zone_controls'][i]['type']=='Humidistat':
            w_set['humidify'][z] = profile[building['zone_controls'][i]['humidify_schedule'][0]]
            w_set['dehumidify'][z] = profile[building['zone_controls'][i]['dehumidify_schedule'][0]]
    T_set['dual_sp'] = False
    for i in range(len(T_zone)):
        if T_set['heat'] < T_set['cool']:
            T_set['dual_sp'] = True
    return T_set,w_set