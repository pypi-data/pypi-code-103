from building_plus.components.water_equipment import water_equipment

def flow_resolver_demand(building,node,profile,l,T_mains):
    ## resolve loop flows
    #see details starting on pg 461
    d_equip = building['plant_demand_equip'] 
    on_loop = [i for i,x in enumerate(d_equip['loop']) if x == l]
    d_pump = None
    ## flow requests of water equipment first so upstream splitter is correct
    for j in on_loop:
        if d_equip['type'][j]==  'wateruse:connections':
            in_n = d_equip['inlet'][j]
            out_n = d_equip['outlet'][j]
            flow,_,_,_,_ = water_equipment(building['water_use'][d_equip['name'][j]],profile,T_mains,node['demand_temperature'][in_n]) 
            z = building['zones']['name'].index(building['water_use'][d_equip['name'][j]]['zone'])
            node['demand_flow'][out_n] = flow*building['zones']['multiplier'][z]
            node['demand_flow'][in_n] = node['demand_flow'][out_n] 
        elif d_equip['type'][j][:5]== 'coil:':
            in_n = d_equip['inlet'][j]
            out_n = d_equip['outlet'][j]
            node['demand_flow'][in_n] = node['demand_flow'][out_n] 

    ##connect flow requests from individual components
    for j in on_loop:
        in_n = d_equip['inlet'][j]
        out_n = d_equip['outlet'][j]
        if d_equip['type'][j]== 'mixer':
            if type(in_n) != list:
                node['demand_flow'][out_n] = node['demand_flow'][in_n]
            else:
                node['demand_flow'][out_n] = sum([node['demand_flow'][k] for k in in_n]) 
        elif d_equip['type'][j]== 'splitter':
            if type(out_n) != list:
                node['demand_flow'][in_n] = node['demand_flow'][out_n]
            else:
                node['demand_flow'][in_n] = sum([node['demand_flow'][k] for k in out_n]) 
        elif d_equip['type'][j][:5]== 'pump:':
            d_pump = j
        elif d_equip['type'][j][:5]== 'pipe:': 
            node['demand_flow'][out_n] = max(node['demand_flow'][in_n],node['demand_flow'][out_n]) #branch flow determined by component with largest request
            node['demand_flow'][in_n] = node['demand_flow'][out_n] 
        elif not(d_equip['type'][j][:5]== 'coil:' or d_equip['type'][j] == 'wateruse:connections'):
            node['demand_flow'][in_n] = node['demand_flow'][out_n] 
            # print(d_equip['type'][j])
        #flow is already set by component (coil or water equipment)
    loop_flow_request = node['demand_flow'][building['plant_demand_nodes']['outlet_node'][l]]/building['plant_loop']['fluid_density'][l] # convert mass flow to volumetric flow (parameters saved in building file in volumetric flow)

    #find pump & supply limits
    pump_flow = 0 
    demand_bypass_flow = 0 
    if d_pump==None:
        p = [building['plant_supply_equip']['name'][i] for i,x in enumerate(building['plant_supply_equip']['type']) if x[:5]=='pump:' and building['plant_supply_equip']['loop'][i] == l]
        p = p[0]
    else:
        p = building['plant_demand_equip']['name'][d_pump]
    if building['pump'][p]['type']=='VariableSpeed':
            if loop_flow_request>0 and loop_flow_request<building['pump'][p]['design_min_flow']:
                demand_bypass_flow = building['pump'][p]['design_min_flow'] - loop_flow_request 
                pump_flow = building['pump'][p]['design_min_flow']
            elif loop_flow_request>building['pump'][p]['design_flow']:
                pump_flow = building['pump'][p]['design_flow'] 
            else:
                pump_flow = loop_flow_request 
            PLR = pump_flow/building['pump'][p]['design_flow']
            frac_power = building['pump'][p]['c1'] + building['pump'][p]['c2']*PLR + building['pump'][p]['c3']*PLR**2 + building['pump'][p]['c4']*PLR**3 
    elif building['pump'][p]['type']=='ConstantSpeed':
        try:
            sched = profile[building['pump'][p]['schedule']] 
        except KeyError:
            if loop_flow_request>0:
                sched = 1 
            else:
                sched = 0 
        frac_power = sched 
        pump_flow = building['pump'][p]['design_flow']*sched 
        demand_bypass_flow = pump_flow - loop_flow_request 
    pump_power = building['pump'][p]['design_power']*frac_power #Watts
    shaft_power = building['pump'][p]['motor_eff']*pump_power #Watts
    pump_heat = shaft_power + (pump_power - shaft_power)*building['pump'][p]['fluid_ineff_frac'] 
    ##put correct flows on demand side branches
    node['demand_flow'][building['plant_demand_nodes']['inlet_node'][l]] = pump_flow*building['plant_loop']['fluid_density'][l] 
    for j in on_loop:
        in_n = d_equip['inlet'][j]
        out_n = d_equip['outlet'][j] 
        if d_equip['type'][j]=='mixer':
            try:
                in_n[0]
            except TypeError:
                in_n = [in_n]
            node['demand_flow'][out_n] = sum([node['demand_flow'][k] for k in in_n]) 
        elif d_equip['type'][j]=='splitter':
            try:
                out_n[0]
            except TypeError:
                out_n = [out_n]
            for j in on_loop:
                if any([d_equip['inlet'][j] == k for k in out_n]) and d_equip['bypass'][j]:
                    node['demand_flow'][d_equip['inlet'][j]] = demand_bypass_flow*building['plant_loop']['fluid_density'][l] # convert back to mass flow
                    break
        else:
            node['demand_flow'][out_n] = node['demand_flow'][in_n] 
    node['supply_flow'][building['plant_supply_nodes']['inlet_node'][l]] = node['demand_flow'][building['plant_demand_nodes']['outlet_node'][l]] # connect demand half loop to supply half loop
    return node,pump_power,pump_heat