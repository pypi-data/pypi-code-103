'''
Run single step forward of multi-zone building simulation
'''

from building_plus.basic.leward_calc import leward_calc
from building_plus.basic.wind_speed_calc import wind_speed_calc
from building_plus.basic.thermostat_humidistat import thermostat_humidistat
from building_plus.basic.area_weighted_temperature import area_weighted_temperature
from building_plus.process.load_sched import load_sched
from building_plus.process.reset_loop_param import reset_loop_param
from building_plus.process.update_model_states_implicit import update_model_states_implicit
from building_plus.process.zone_loads import zone_loads
from building_plus.process.ideal_hvac import ideal_hvac
from building_plus.process.sim_air_loops import sim_air_loops
from building_plus.process.net_water_loop_supply import net_water_loop_supply
from building_plus.components.unitary_systems import unitary_systems
from building_plus.components.air_terminals import air_terminals

def buildings_step(building,weather,T,w,air_nodes,plant_nodes,e_use,loads,gains,heating,cooling,T_optimal,T_nominal,schedules,frost,dt,date):
    nz = len(building['zones']['name'])
    cat = ['net_elec','heat_elec','heat_gas','cool_elec','fan_elec','other_fans','water_gas','water_elec','tower_elec','pumps']
    leward = leward_calc(weather['wdir'],building['surfaces']['exterior']['normal'])
    wind_speed = wind_speed_calc(weather['wspd'],building['ctf']['s_height'],building['site']['terrain'])
    schedules = load_sched(building['schedule'],building['holidays'],[date],None,False)
        
    ###Load values specific to this moment in time
    T_set,w_set = thermostat_humidistat(building,schedules,T['zone']) ## HVAC temperature Schedules
    _,_,occupancy,mixing,infiltration,S,frost,T_mains,water_heat = zone_loads(building,date,schedules,weather,T['zone'],w['zone'],dt,frost)

    ## extrapolate 'optimal' building temp to all zones
    T_set_mod = optim_T_set(T_set,T_optimal,T_nominal,building)
    ###Determine HVAC setpoints
    air_nodes,central_flow,direct_flow,mixed_air_loop,direct_return_air,plenum,T,w,fan_avail = ideal_hvac(building,schedules,leward,wind_speed,S,air_nodes,weather['t_dryb'],mixing,infiltration,gains,T,w,T_set_mod,w_set,occupancy,dt,False)
    j = 0
    while j <=2: #iterate to ensure water loops reach correct temperature
        j+=1
        for x in cat:
            e_use[x] = 0
        plant_nodes['demand_temperature'] = [plant_nodes['demand_temperature'][building['plant_demand_nodes']['inlet_node'][building['plant_demand_nodes']['loop'][i]]] for i in range(len(building['plant_demand_nodes']['loop']))]
        supply_flow,e_use,plant_nodes = sim_air_loops(building,air_nodes,mixed_air_loop,central_flow,w['loop'],weather['t_dryb'],w['air'],plant_nodes,e_use,fan_avail)
        supply_flow,e_use,plant_nodes = air_terminals(building,air_nodes,supply_flow,e_use,plant_nodes,T['central'])
        supply_flow,plant_nodes,e_use = unitary_systems(building,air_nodes,supply_flow,direct_flow,direct_return_air,T['direct'],weather['t_dryb'],w['air'],fan_avail,plant_nodes,e_use)#zone equipment not part of central air loops
        e_use,plant_nodes,loop_load = net_water_loop_supply(building,schedules,dt,plant_nodes,e_use,T_mains,weather['t_dryb'],w['air'],heating,cooling)

    e_use['water_gas'] += water_heat/building['impact_factor']['steam_efficiency'][0] #unconnected water heat is considered purchased heat
    nonHVAC_electric = sum([loads['lighting_internal'][z]*loads['multiplier'][z] for z in range(nz)]) + sum([loads['plug_load'][z]*loads['multiplier'][z] for z in range(nz)]) + loads['exterior']['lighting'] + loads['exterior']['equipment'] + sum(loads['case']['electric']) + sum(loads['rack']['electric'])
    e_use['net_elec'] = nonHVAC_electric + e_use['pumps'] + e_use['heat_elec'] + e_use['fan_elec'] + e_use['water_elec'] + e_use['tower_elec']

    ## simulate a time step
    T['zone'],T['surf'],w['zone'],e_dict = update_model_states_implicit(building,T,S,wind_speed,leward,gains,dt,w,mixing,plenum,infiltration,supply_flow)
    humidity = w['zone']
    return T,humidity,frost,e_use,loop_load,air_nodes,plant_nodes

def optim_T_set(T_set,T_optim,T_nom,building):
    T_set_mod = {}
    T_set_mod['no_hvac'] = [j for j in T_set['no_hvac']]
    T_set_mod['heat'] = [j for j in T_set['heat']]
    T_set_mod['cool'] = [j for j in T_set['cool']]
    T_set_mod['dual_sp'] = False
    if T_set['dual_sp']:
        T_set_mod['dual_sp'] = True
    nz = len(T_set['cool']) 
    error = 1
    T_nom1 = area_weighted_temperature(building,T_nom)
    delta =  (T_optim-T_nom1)
    while abs(error)>1e-3:
        T_set_mod['cool'] = [T_nom[z] + delta for z in range(nz)]
        T = area_weighted_temperature(building,T_set_mod['cool'])
        error = T - T_optim
        delta += error/10
    T_set_mod['heat'] = [j for j in T_set_mod['cool']]
    return T_set_mod