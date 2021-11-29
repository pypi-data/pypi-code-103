from copy import copy
from building_plus.components.fan_calc import fan_calc
from building_plus.basic.psychometric import psychometric
from building_plus.components.cooling_coil import cooling_coil
from building_plus.components.water_coil import water_coil

def unitary_systems(building,air_nodes,supply_flow,direct_flow,direct_return_air,T_direct,T_air,w_air,fan_avail,plant_nodes,e_use):
    ## Unitary systems (zones not on an air loop)
    r_air = {}
    c_air = {}
    air_density = 1.204
    for i in building['unitary_sys']:
        z = building['unitary_sys'][i]['zone']
        if z>=0 and direct_flow[z]>0:
            m = building['zones']['multiplier'][z]
            fan_name = building['unitary_sys'][i]['fan_name']
            for x in direct_return_air:
                r_air[x] = direct_return_air[x][z]
            c_air['Tdb'] = supply_flow['Tdb'][z]
            c_air['w'] = supply_flow['w'][z] 
            c_air['h'] = supply_flow['h'][z]
            c_air['m_dot'] = supply_flow['m_dot'][z]*m
            if 'terminal' in building['unitary_sys'][i]:
                r_air['m_dot'] = direct_flow[z]*m*air_density - c_air['m_dot'] 
                air = mix_flows(r_air,c_air) #fresh air directly to zone, not outdoor air mixing on loop
            else:
                r_air['m_dot'] = direct_return_air['m_dot'][z]*m 
                fresh_air = {}
                fresh_air['Tdb'] = T_air
                fresh_air['w'] = w_air
                fresh_air['h'] = psychometric(fresh_air,'h')
                fresh_air['m_dot'] = direct_flow[z]*m*air_density - r_air['m_dot']
                air = mix_flows(r_air,fresh_air) #fresh air directly to zone, not outdoor air mixing on loop
            air,P_fan,_ =  fan_calc(building['fans'][fan_name],air,fan_avail[fan_name])
            if ('end_use' in building['fans'][fan_name] and building['fans'][fan_name]['end_use'] == 'fan energy'):
                e_use['fan_elec'] += P_fan
            else: # 'Unit Heater Fans', 'Zone Exhaust Fans'c
                e_use['other_fans'] += P_fan

            if building['unitary_sys'][i]['type'] == 'FourPipeFanCoil':
                air,plant_nodes,e_use = unit_cool_coil(building,building['unitary_sys'][i]['cool_coil'],building['unitary_sys'][i]['cool_coil_type'],air,T_direct[z],T_air,e_use,plant_nodes,i)
                air,plant_nodes,e_use = unit_heat_coil(building,building['unitary_sys'][i]['heat_coil'],building['unitary_sys'][i]['heat_coil_type'],plant_nodes,air,T_direct[z],e_use,i)
            elif building['unitary_sys'][i]['type'] == 'PackagedTerminalAirConditioner':
                air,plant_nodes,e_use = unit_cool_coil(building,building['unitary_sys'][i]['cool_coil'],building['unitary_sys'][i]['cool_coil_type'],air,T_direct[z],T_air,e_use,plant_nodes,i)
                air,plant_nodes,e_use = unit_heat_coil(building,building['unitary_sys'][i]['heat_coil'],building['unitary_sys'][i]['heat_coil_type'],plant_nodes,air,T_direct[z],e_use,i)
            elif building['unitary_sys'][i]['type']== 'UnitHeater':
                air,plant_nodes,e_use = unit_heat_coil(building,building['unitary_sys'][i]['heat_coil'],building['unitary_sys'][i]['heat_coil_type'],plant_nodes,air,T_direct[z],e_use,i)
            elif building['unitary_sys'][i]['type'] =='WindowAirConditioner':
                    pass#not sure what to do about this (in zone, but not on air loop?)
            supply_flow['Tdb'][z] = air['Tdb']
            supply_flow['w'][z] = air['w']
            supply_flow['h'][z] = air['h']
            supply_flow['m_dot'][z] = air['m_dot']
    return supply_flow,plant_nodes,e_use

    
def unit_cool_coil(building,coil_name,coil_type,air,T_supply,T_air,e_use,plant_nodes,i):
    if (coil_type == 'coil:cooling:dx:twospeed' or coil_type == 'coil:cooling:dx:singlespeed'):
        air,P_coil = cooling_coil(building,coil_name,air,T_air,T_supply)
        e_use['cool_elec'] += P_coil
    elif (coil_type == 'coil:cooling:water:detailedgeometry' or coil_type == 'coil:cooling:water'):
        air,m_w,actual_load,out = water_coil(building,coil_name,air,T_supply,plant_nodes)
        plant_nodes['demand_flow'][out] = m_w #kg/s
        plant_nodes['load'][out] = actual_load #load in Watts (negative because air leaves hotter)
    return air,plant_nodes,e_use

def unit_heat_coil(building,coil_name,coil_type,plant_nodes,air,T_supply,e_use,i):
    if (coil_type == 'coil:heating:fuel' or coil_type == 'coil:heating:electric'):
        cp_supply = 1006 + 1860*air['w']
        load_heat = max(0,air['m_dot']*cp_supply*(T_supply-air['Tdb']))
        if load_heat>0:
            air['Tdb'] += load_heat/(cp_supply*air['m_dot'])
            air['h'] = psychometric(air,'h')
            if coil_type == 'coil:heating:fuel':
                e_use['heat_gas'] += load_heat/building['coils_heating'][coil_name]['efficiency'] #heat added in W
            else:
                e_use['heat_elec'] += load_heat/building['coils_heating'][coil_name]['efficiency'] #heat added in W
    elif coil_type == 'coil:heating:water':
        air,m_w,actual_load,out = water_coil(building,coil_name,air,T_supply,plant_nodes)
        plant_nodes['demand_flow'][out] = m_w #kg/s
        plant_nodes['load'][out] = actual_load #load in Watts (negative because air leaves hotter)
    return air,plant_nodes,e_use

def mix_flows(s1,s2):
    mixed = {}
    mixed['m_dot'] = s1['m_dot'] + s2['m_dot'] #mass flow (kg/s) :
    mixed['h'] = (s1['m_dot']*s1['h'] + s2['m_dot']*s2['h'])/mixed['m_dot']
    w_sat = psychometric({'h':mixed['h']},'w')
    mix_w = (s1['m_dot']*s1['w'] + s2['m_dot']*s2['w'])/mixed['m_dot']
    mixed['m_dot'] = mixed['m_dot']*(1 - max(0,mix_w-w_sat))
    mixed['w'] = min(w_sat,mix_w)
    mixed['Tdb'] = psychometric(mixed,'Tdb')
    return mixed
