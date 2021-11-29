'''
Converts the air flow and temperature to heat/cooling loads on water loops 
and to electric/gas loads if it is directly to an electric/gas component
'''

from building_plus.basic.psychometric import psychometric
from building_plus.components.water_coil import water_coil
from building_plus.components.cooling_coil import cooling_coil
from building_plus.components.fan_calc import fan_calc
from building_plus.components.unitary_heat_cool import unitary_heat_cool

def sim_air_loops(building,air_nodes,mixed_air_loop,central_flow,w_loop,T_air,m_v_air,plant_nodes,e_use,fan_avail):
    supply_air = {}
    for k in mixed_air_loop:
        supply_air[k] = [j for j in mixed_air_loop[k]]
    for l in range(len(supply_air['Tdb'])):  #loop through equipment on loop
        on_loop = [i for i,x in enumerate(building['air_supply_equip']['loop']) if x==l]
        air = {}
        air['Tdb'] = supply_air['Tdb'][l]+0
        air['w'] = supply_air['w'][l]+0
        air['m_dot'] = supply_air['m_dot'][l]+0
        air['h'] = supply_air['h'][l]+0 #update intermediate air as it passes between equipment
        for j in range(len(on_loop)):
            ## making sure simulation of these components is in the order they are on the supply branch
            k = on_loop[[building['air_supply_equip']['branch_order'][on_loop[i]] for i in range(len(on_loop))].index(j)]
            name = building['air_supply_equip']['name'][k]
            out = building['air_supply_equip']['outlet'][k]
            if building['air_supply_equip']['type'][k]=='airloophvac:outdoorairsystem':
                # do nothing, already mixed air
                pass
            elif (building['air_supply_equip']['type'][k]== 'coil:cooling:water:detailedgeometry' or
                 building['air_supply_equip']['type'][k]== 'coil:cooling:water' or
                 building['air_supply_equip']['type'][k]== 'coil:heating:water'):
                air,m_w,actual_load,out = water_coil(building,name,air,air_nodes['supply_T_set'][out],plant_nodes)
                plant_nodes['demand_flow'][out] = m_w+0 #kg/s
                plant_nodes['load'][out] = actual_load+0 #load in Watts (negative for heating coil because air leaves hotter)
            elif (building['air_supply_equip']['type'][k]=='coilsystem:cooling:dx' or
                 building['air_supply_equip']['type'][k]=='dx:twospeed' or
                 building['air_supply_equip']['type'][k]=='dx:singlespeed'):
                T_wb = psychometric({'Tdp':T_air,'w':m_v_air},'Twb')
                air,P_coil = cooling_coil(building,name,air,T_air,air_nodes['supply_T_set'][out])
                e_use['cool_elec'] += P_coil
            elif (building['air_supply_equip']['type'][k]=='coil:heating:fuel' or
                 building['air_supply_equip']['type'][k]== 'coil:heating:electric'):
                spec_heat_supply = 1006 + 1860*air['w'] #J/kg*K
                Q_treat = air['m_dot']*spec_heat_supply*(air_nodes['supply_T_set'][out]-air['Tdb'])
                if Q_treat>1:
                    air['Tdb'] = air_nodes['supply_T_set'][out]+0
                    air['h'] = air['h'] + Q_treat/air['m_dot']
                    if building['air_supply_equip']['type'][k]=='coil:heating:fuel':
                        e_use['heat_gas']+= Q_treat/building['coils_heating'][name]['efficiency'] #heat added in W
                    else:
                        e_use['heat_elec']+= Q_treat/building['coils_heating'][name]['efficiency'] #heat added in W
            elif building['air_supply_equip']['type'][k][:4] == 'fan:':
                air,P_fan,_ = fan_calc(building['fans'][name],air,fan_avail[name])
                if ('end_use' in building['fans'][name] and building['fans'][name]['end_use'] == 'fan energy'):
                    e_use['fan_elec'] += P_fan
                else: # 'Unit Heater Fans', 'Zone Exhaust Fans'c
                    e_use['other_fans'] += P_fan
            elif building['air_supply_equip']['type'][k]=='humidifier:steam:electric':
                if w_loop[l]>air['w']: #see page 1250
                    #steam specific enthalpy = 2676125 J/kg
                    den_water = 995 #kg/m^3
                    m_w = (w_loop[l]-air['w'])*air['m_dot']
                    air['h'] = air['h'] + m_w/air['m_dot']*2676125
                    air['Tdb'] = psychometric(air,'Tdp')
                    ## need to check it is not over saturated
                    k =building['humidifiers']['name'].index(name)
                    e_use['heat_elec'] += m_w/(den_water*building['humidifiers']['flow_capacity'][k])*building['humidifiers']['max_power'][k] + building['humidifiers']['fan_power'][k] + building['humidifiers']['standby_power'][k]
            elif building['air_supply_equip']['type'][k]=='airloophvac:unitaryheatcool':
                air,plant_nodes,e_use = unitary_heat_cool(building,fan_avail,air,air_nodes['supply_T_set'][out],T_air,e_use,plant_nodes,building['unitary_heat_cool'][name])
            else:
                print('need to add components in sim_air_loops')
        supply_air['Tdb'][l] = air['Tdb']+0
        supply_air['w'][l] = air['w']+0
        supply_air['m_dot'][l] =air['m_dot']+0
        supply_air['h'][l] = air['h']+0 #update intermediate air as it passes between equipment

    air_density = 1.204 #kg/m^3 %standard air density (1.204 kg/m3) adjusted for the local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
    n_z = len(building['zones']['name'])
    zone_air = {}
    zone_air['Tdb'] = [0 for i in range(n_z)]
    zone_air['w'] = [0 for i in range(n_z)]
    zone_air['h'] = [0 for i in range(n_z)]
    zone_air['flow'] = [j for j in central_flow]
    zone_air['m_dot'] = [air_density*central_flow[i] for i in range(n_z)]

    for z in range(n_z):
        l = building['zones']['air_loop'][z]
        if l !=None:
            zone_air['Tdb'][z] = supply_air['Tdb'][l]+0
            zone_air['w'][z] = supply_air['w'][l]+0
            zone_air['h'][z] = supply_air['h'][l]+0

    ## exhaust fan power
    for i in building['fans']:
        if building['fans'][i]['exhaust'] and building['fans'][i]['flow_rate']!=None:
            fan_flow = building['fans'][i]['flow_rate']*fan_avail[i] #volumetric flow (m^3/s)  %See page 1601 of the reference manual
            P_fan += fan_flow*building['fans'][i]['pressure_rise']/(building['fans'][i]['fan_efficiency']) # m3/s * Pa = N*m/s = W
            if ('end_use' in building['fans'][i] and building['fans'][i]['end_use'] == 'fan energy'):
                e_use['fan_elec'] += P_fan
            else: # 'Unit Heater Fans', 'Zone Exhaust Fans'c
                e_use['other_fans'] += P_fan
    return zone_air,e_use,plant_nodes