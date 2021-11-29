'''
Run simulation of multi-zone building
Inputs are the parameters of the building in 'building'
The initial state of zone, surface temperatures and surface humidity
The weather and dates of the simulation period, and if it is a design day
'''

from building_plus.basic.leward_calc import leward_calc
from building_plus.basic.wind_speed_calc import wind_speed_calc
from building_plus.basic.thermostat_humidistat import thermostat_humidistat
from building_plus.process.load_sched import load_sched
from building_plus.process.initial_param import initial_param
from building_plus.process.reset_loop_param import reset_loop_param
from building_plus.process.update_model_states_implicit import update_model_states_implicit
from building_plus.process.zone_loads import zone_loads
from building_plus.process.ideal_hvac import ideal_hvac
from building_plus.process.sim_air_loops import sim_air_loops
from building_plus.process.manage_plant_equip import manage_plant_equip
from building_plus.components.unitary_systems import unitary_systems
from building_plus.components.air_terminals import air_terminals

def run_building(building,T_zone,T_surf,humidity,weather,date,des_day):
    air_density = 1.204  #kg/m^3 %standard air density (1.204 kg/m3) adjusted for the local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
    nz = len(building['zones']['name'])
    Q_transfer = [] #energy transfer to zone
    m_sys = [] #air mass flow to zone
    frost = [[0 for i in range(len(building['cases']))]] #need to make as initial condition that is passed from previous time step
    cat = ['net_elec','heat_elec','heat_gas','cool_elec','fan_elec','other_fans','water_gas','water_elec','tower_elec','pumps']
    e_use={}
    facility = {}
    Q_test_plots = {}
    weather_now = {}
    for i in cat:
        e_use[i] = 0
        facility[i] = []
    facility['heating_load'] = []
    facility['cooling_load'] = []
    facility['tower_load'] = []
    facility['supply'] = []
    facility['return_'] = []
    T,air_nodes,plant_nodes,T_supply0,T_return0 = initial_param(building,T_zone[0],T_surf[0])
    wh_tank = {}
    for i in building['water_heater']:
        wh_tank[i] = {}
        wh_tank[i]['T'] = load_sched(building['schedule'],building['holidays'],[date[0]],[building['water_heater'][i]['temperature_schedule']],des_day)
        wh_tank[i]['on'] = False
    w = {}
    w['zone'] = humidity[0]
    t_last = date[0]
    for t in range(len(date)-1):
        dt = (date[t+1] - t_last).seconds
        if dt <0:
            dt = dt + 24*3600 #necessary for warm-up period when date jumps back to start of day
        for i in weather:
            weather_now[i] = weather[i][t]
        leward = leward_calc(weather_now['wdir'],building['surfaces']['exterior']['normal'])
        wind_speed = wind_speed_calc(weather_now['wspd'],building['ctf']['s_height'],building['site']['terrain'])
        
        T,w,air_nodes,plant_nodes = reset_loop_param(building,T,w,air_nodes,plant_nodes,weather_now,date[t+1])
        schedules = load_sched(building['schedule'],building['holidays'],[date[t+1]],None,des_day)

        ###Load values specific to this moment in time
        T_set,w_set = thermostat_humidistat(building,schedules,T['zone']) ## HVAC temperature Schedules
        loads,gains,occupancy,mixing,infiltration,S,frost_t,T_mains,water_heat = zone_loads(building,date[t+1],schedules,weather_now,T['zone'],w['zone'],dt,frost[t])
        
        ###Determine HVAC setpoints
        air_nodes,central_flow,direct_flow,mixed_air_loop,direct_return_air,plenum,T,w,fan_avail = ideal_hvac(building,schedules,leward,wind_speed,S,air_nodes,weather_now['t_dryb'],mixing,infiltration,gains,T,w,T_set,w_set,occupancy,dt,des_day)
        if not des_day:
            ###Compute performance of HVAC system 
            for iter in range(3): #iterate to ensure water loops reach correct temperature
                for x in cat:
                    e_use[x] = 0
                plant_nodes['demand_temperature'] = [plant_nodes['demand_temperature'][building['plant_demand_nodes']['inlet_node'][building['plant_demand_nodes']['loop'][i]]] for i in range(len(building['plant_demand_nodes']['loop']))]
                supply_flow,e_use,plant_nodes = sim_air_loops(building,air_nodes,mixed_air_loop,central_flow,w['loop'],weather_now['t_dryb'],w['air'],plant_nodes,e_use,fan_avail)
                supply_flow,e_use,plant_nodes = air_terminals(building,air_nodes,supply_flow,e_use,plant_nodes,T['central'])
                supply_flow,plant_nodes,e_use = unitary_systems(building,air_nodes,supply_flow,direct_flow,direct_return_air,T['direct'],weather_now['t_dryb'],w['air'],fan_avail,plant_nodes,e_use)#zone equipment not part of central air loops
                plant_nodes,e_use,wh_tank,loop_load = manage_plant_equip(building,schedules,plant_nodes,e_use,dt,weather_now['t_dryb'],w['air'],T_mains,wh_tank,T_supply0,T_return0)
        
        e_use['water_gas'] += water_heat/building['impact_factor']['steam_efficiency'][0] ##unconnected water heat is considered purchased heat
        nonHVAC_electric = sum([loads['lighting_internal'][z]*loads['multiplier'][z] for z in range(nz)]) + sum([loads['plug_load'][z]*loads['multiplier'][z] for z in range(nz)]) + loads['exterior']['lighting'] + loads['exterior']['equipment'] + sum(loads['case']['electric']) + sum(loads['rack']['electric'])
        e_use['net_elec'] = (nonHVAC_electric + e_use['pumps'] + e_use['heat_elec'] + e_use['cool_elec'] + e_use['fan_elec'] + e_use['water_elec'] + e_use['tower_elec'])

        ## simulate a time step
        T['zone'],T['surf'],w['zone'],e_dict = update_model_states_implicit(building,T,S,wind_speed,leward,gains,dt,w,mixing,plenum,infiltration,supply_flow)
        if any([not building['zones']['air_loop'][j] is None and T['zone'][j]<T_set['heat'][j]- building['hvac']['managers']['thermostat_tolerance'][building['zones']['air_loop'][j]] and not T_set['no_hvac'][j] for j in range(len(T['zone_est']))]):
            print('investigate why building not reaching setpoint')
        frost.append(frost_t)
        ## update logging variables and move to next time step
        T_zone.append(T['zone'])
        T_surf.append(T['surf'])
        m_sys.append([air_density*(central_flow[i] + direct_flow[i]) for i in range(nz)])
        humidity.append(w['zone'])
        Q_transfer.append([air_density*(central_flow[i]*(1006 + 1860*w['central'][i])*(T['central'][i] - T['zone'][i])
                         + direct_flow[i]*(1006 + 1860*w['zone'][i])*(T['direct'][i] - T['zone'][i]) 
                         + (1006 + 1860*w['zone'][i])*(sum([plenum[i][j]*T['zone'][j] for j in range(nz)]) 
                         - sum(plenum[i])*T['zone'][i]))*building['zones']['multiplier'][i] for i in range(nz)]) #Sensible energy transfer to the zone.
        for l in range(len(building['plant_loop']['name'])):
            T_supply0[l] = plant_nodes['demand_temperature'][building['plant_demand_nodes']['inlet_node'][l]] #half loop tank temperature from previous time step (pg 468)
            T_return0[l] = plant_nodes['supply_temperature'][building['plant_supply_nodes']['inlet_node'][l]] #half loop tank temperature from previous time step (pg 468)
        for i in cat:
            facility[i].append(e_use[i])
        facility['heating_load'].append(sum(loop_load[0]))
        facility['cooling_load'].append(sum(loop_load[1]))
        facility['tower_load'].append(sum(loop_load[2]))
        facility['supply'].append(T_supply0)
        facility['return_'].append(T_return0)
        t_last = date[t+1]
    return T_zone,T_surf,humidity,frost,m_sys,Q_transfer,facility,Q_test_plots
