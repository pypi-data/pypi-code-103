from building_plus.components.cooling_coil import cooling_coil
from building_plus.components.fan_calc import fan_calc
from building_plus.components.water_coil import water_coil
from building_plus.basic.psychometric import psychometric

def unitary_heat_cool(building,fan_avail,air,T_supply,T_air,e_use,plant_nodes,uhc):
    name = uhc['cool_coil']
    if air['m_dot']>1e-8:
        if 'cool_coil_type' in uhc:
            if (uhc['cool_coil_type']=='Coil:Cooling:DX:TwoSpeed' or
                uhc['cool_coil_type']=='Coil:Cooling:DX:SingleSpeed'):
                    air,P_coil = cooling_coil(building,name,air,T_air,T_supply)
                    e_use['cool_elec'] += P_coil
            elif (uhc['cool_coil_type']=='Coil:Cooling:Water:DetailedGeometry' or
                  uhc['cool_coil_type']=='Coil:Cooling:Water'):
                    air,m_w,actual_load,out = water_coil(building,name,air,T_supply,plant_nodes)
                    plant_nodes.demand_flow[out] = m_w #kg/s
                    plant_nodes.load[out] = actual_load #load in Watts (negative because air leaves hotter)
        name = uhc['heat_coil']
        c = building['coils_heating']['name'].index(uhc['heat_coil'])
        if building['coils_heating']['type'][c]=='Fuel' or building['coils_heating']['type'][c]=='Electric':
            cp_supply = 1006 + 1860*air['w']
            load_heat = max(0,air['m_dot']*cp_supply*(T_supply-air['Tdb']))
            if load_heat>0:
                air['Tdb'] += load_heat/(cp_supply*air['m_dot'])
                air['h'] = psychometric(air,'h')
                if building['coils_heating']['type'][c]=='Fuel':
                    e_use['heat_gas'] += load_heat/building['coils_heating']['efficiency'][c] #heat added in W
                else:
                    e_use['heat_elec'] += load_heat/building['coils_heating']['efficiency'][c] #heat added in W
        elif building['coils_heating']['type'][c]=='Water':
                air,m_w,actual_load,out = water_coil(building,uhc['heat_coil'],air,T_supply,plant_nodes)
                plant_nodes.demand_flow[out] = m_w #kg/s
                plant_nodes.load[out] = actual_load #load in Watts (negative because air leaves hotter)
    air,P_fan = fan_calc(building['fans'][uhc['fan_name']],air,fan_avail[uhc['fan_name']])
    e_use['fan_elec'] += P_fan
    return air,plant_nodes,e_use