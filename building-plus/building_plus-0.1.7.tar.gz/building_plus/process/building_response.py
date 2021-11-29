from building_plus.process.buildings_step import optim_T_set
from building_plus.basic.leward_calc import leward_calc
from building_plus.basic.wind_speed_calc import wind_speed_calc
from building_plus.basic.thermostat_humidistat import thermostat_humidistat
from building_plus.basic.area_weighted_temperature import area_weighted_temperature
from building_plus.process.load_sched import load_sched
from building_plus.process.initial_param import initial_param
from building_plus.process.reset_loop_param import reset_loop_param
from building_plus.process.update_model_states_implicit import update_model_states_implicit
from building_plus.process.zone_loads import zone_loads
from building_plus.process.ideal_hvac import ideal_hvac
from building_plus.process.sim_air_loops import sim_air_loops
from building_plus.process.net_water_loop_supply import net_water_loop_supply
from building_plus.components.unitary_systems import unitary_systems
from building_plus.components.air_terminals import air_terminals

def building_response(buildings,observer,weather_now,actual_build,dt,setpoint,date):
    #use the temperature setpoints from the optimization to find the actual zone temperatures
    n_b = len(buildings)
    net_electric = [0 for i in range(n_b)]
    cat = ['heat_elec','heat_gas','cool_elec','fan_elec','water_gas','water_elec','tower_elec','pumps','other_fans',]
    e_use = {}
    w = {}
    for i in range(len(cat)):
        e_use[cat[i]] = 0
    for k in range(n_b):
        building = buildings[k]
        heating = None
        if 'district_heat' in setpoint:
            heating = setpoint['district_heat'][k]
        cooling = None
        if 'district_cool' in setpoint:
            cooling = setpoint['district_cool'][k]
        T_optim = setpoint['temperature'][k]
        nz = len(building['zones']['name'])
        w['zone'] = observer['building_humidity'][k]
        frost = observer['building_frost'][k]
        T,air_nodes,plant_nodes,_,_= initial_param(building,observer['building_zone_temp'][k],observer['building_surf_temp'][k])
        for l in range(len(building['plant_loop']['name'])):
            plant_nodes['demand_temperature'][building['plant_demand_nodes']['loop'] == l] = observer['building_supply'][k][l]
            plant_nodes['supply_temperature'][building['plant_supply_nodes']['inlet_node'][l]] = observer['building_return'][k][l]
        leward = leward_calc(weather_now['wdir'],building['surfaces']['exterior']['normal'])
        wind_speed = wind_speed_calc(weather_now['wspd'],building['ctf']['s_height'],building['site']['terrain'])
        
        T,w,air_nodes,plant_nodes = reset_loop_param(building,T,w,air_nodes,plant_nodes,weather_now,observer['building_timestamp'][k])

        #parameters that could be overridden by 'actual' measurements
        if 'schedules' in actual_build:
            schedules = actual_build['schedules'][k]
        else:
            schedules = load_sched(building['schedule'],building['holidays'],[date],None,False)
        T_set,w_set = thermostat_humidistat(building,schedules,T['zone']) ## HVAC temperature Schedules
        if 'T_set' in actual_build:
            T_set = actual_build['T_set'][k]
        if 'w_set' in actual_build:
            w_set = actual_build['w_set'][k]
        ## extrapolate 'optimal' building temp to all zones
        T_set_mod = optim_T_set(T_set,T_optim,actual_build['Tz_nominal'][k],building)
        
        ###Load values specific to this moment in time
        loads,gains,occupancy,mixing,infiltration,S,frost,T_mains,water_heat = zone_loads(building,date,schedules,weather_now,T['zone'],w['zone'],dt,frost)
        if 'loads' in actual_build:
            loads = actual_build['loads'][k]
        if 'gains' in actual_build:
            gains = actual_build['gains'][k]
        if 'occupancy' in actual_build:
            occupancy = actual_build['occupancy'][k]
        if 'mixing' in actual_build:
            mixing = actual_build['mixing'][k]
        if 'infiltration' in actual_build:
            infiltration = actual_build['infiltration'][k]
        if 'T_mains' in actual_build:
            T_mains = actual_build['T_mains'][k]
        if 'water_heat' in actual_build:
            water_heat = actual_build['water_heat'][k]
        if 'S' in actual_build:
            S = actual_build['S'][k]
        ###Determine HVAC setpoints
        air_nodes,central_flow,direct_flow,mixed_air_loop,direct_return_air,plenum,T,w,fan_avail = ideal_hvac(building,schedules,leward,wind_speed,S,air_nodes,weather_now['t_dryb'],mixing,infiltration,gains,T,w,T_set_mod,w_set,occupancy,dt,False)
        for iter in range(3): #iterate to ensure water loops reach correct temperature
            for x in cat:
                e_use[x] = 0
            plant_nodes['demand_temperature'] = [plant_nodes['demand_temperature'][building['plant_demand_nodes']['inlet_node'][building['plant_demand_nodes']['loop'][i]]] for i in range(len(building['plant_demand_nodes']['loop']))]
            supply_flow,e_use,plant_nodes = sim_air_loops(building,air_nodes,mixed_air_loop,central_flow,w['loop'],weather_now['t_dryb'],w['air'],plant_nodes,e_use,fan_avail)
            supply_flow,e_use,plant_nodes = air_terminals(building,air_nodes,supply_flow,e_use,plant_nodes,T['central'])
            supply_flow,plant_nodes,e_use = unitary_systems(building,air_nodes,supply_flow,direct_flow,direct_return_air,T['direct'],weather_now['t_dryb'],w['air'],fan_avail,plant_nodes,e_use)#zone equipment not part of central air loops
            e_use,plant_nodes,loop_load = net_water_loop_supply(building,schedules,dt,plant_nodes,e_use,T_mains,weather_now['t_dryb'],w['air'],heating,cooling)
            
        e_use['water_gas'] += water_heat/building['impact_factor']['steam_efficiency'][0] #unconnected water heat is considered purchased heat
        nonHVAC_electric = sum([loads['lighting_internal'][z]*loads['multiplier'][z] for z in range(nz)]) + sum([loads['plug_load'][z]*loads['multiplier'][z] for z in range(nz)]) + loads['exterior']['lighting'] + loads['exterior']['equipment'] + sum(loads['case']['electric']) + sum(loads['rack']['electric'])
        e_use['net_elec'] = nonHVAC_electric + e_use['pumps'] + e_use['heat_elec'] + e_use['fan_elec'] + e_use['water_elec'] + e_use['tower_elec']

        ## simulate a time step & update observer
        observer['building_zone_temp'][k],observer['building_surf_temp'][k],observer['building_humidity'][k],e_dict = update_model_states_implicit(building,T,S,wind_speed,leward,gains,dt,w,mixing,plenum,infiltration,supply_flow)
        for l in range(len(building['plant_loop']['name'])):
            observer['building_supply'][k][l] = plant_nodes['demand_temperature'][building['plant_demand_nodes']['inlet_node'][l]]
            observer['building_return'][k][l] = plant_nodes['supply_temperature'][building['plant_supply_nodes']['inlet_node'][l]]
        A = observer['building_conditioned_floor_area'][k]
        observer['building_avg_temp'][k] =  sum([observer['building_zone_temp'][k][z]*A[z] for z in range(len(A))])/sum(A) #area_weighted_temperature %% %current average building zone temperature (used as IC in optimization)
        observer['building_timestamp'][k] = date #weather_now['timestamp']
        net_electric[k] = e_use['net_elec']/1000 #kW
    return observer,net_electric