def demand_loop(building,profile,T_mains,node,l):
    Cp_water = 4186  #J/kg*K
    equip = building['plant_demand_equip'] 
    on_loop = [i for i,x in enumerate(equip['loop']) if x == l] 
    for j in on_loop:
        in_n = equip['inlet'][j] 
        out_n = equip['outlet'][j] 
        if equip['type'][j]=='pipe:adiabatic':
            node['demand_temperature'][out_n] = node['demand_temperature'][in_n] 
        elif equip['type'][j]=='mixer':
            try:
                in_n[0]
            except TypeError:
                in_n = [in_n]
            if node['demand_flow'][out_n]>0:
                node['demand_temperature'][out_n] = sum([node['demand_temperature'][k]*node['demand_flow'][k]/node['demand_flow'][out_n]  for k in in_n])
            else: #avoid divide by zero
                node['demand_temperature'][out_n] = sum([node['demand_temperature'][k] for k in in_n])/len(in_n) 
        elif equip['type'][j]=='splitter':
            try:
                out_n[0]
            except TypeError:
                out_n = [out_n]
            for k in out_n:
                node['demand_temperature'][k] = node['demand_temperature'][in_n] 
        elif (equip['type'][j]=='coil:cooling:water' or
            equip['type'][j]=='coil:cooling:water:detailedgeometry' or
            equip['type'][j]=='coil:heating:water' or
            equip['type'][j]=='chiller:electric:reformulatedeir' or
            equip['type'][j]=='chiller:electric:eir'):
            if node['demand_flow'][out_n]>0:
                node['demand_temperature'][out_n] = node['demand_temperature'][in_n] + node['load'][out_n]/(Cp_water*node['demand_flow'][out_n]) 
            else:#avoid divide by zero
                node['demand_temperature'][out_n] = node['demand_temperature'][in_n] 
        elif equip['type'][j]=='wateruse:connections':
            try:
                node['demand_temperature'][out_n] = profile[building['water_use'][equip['name'][j] ]['cold_supply_temperature_schedule']]
            except KeyError:
                node['demand_temperature'][out_n] = T_mains            
        else:
            print('need additional plant demand loop component of type__' + equip['type'][j])
    return node