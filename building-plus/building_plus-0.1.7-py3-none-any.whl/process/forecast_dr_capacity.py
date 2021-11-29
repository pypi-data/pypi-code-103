'''
Run 2*n+1 simulations of multi-zone building at each step in forecast horizon
to determine the heating/cooling/electric load deviation from the nominal operation.
'''


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
from building_plus.process.net_water_loop_loads import net_water_loop_loads
from building_plus.process.lin_load_increase import lin_load_increase
from building_plus.components.unitary_systems import unitary_systems
from building_plus.components.air_terminals import air_terminals

import datetime

def forecast_dr_capacity(buildings,observer,weather,date):
    n_b = len(buildings)
    if n_b==0:
        forecast = None
        T_building_effective = None
        heating = None
        cooling = None
    else:
        n = 3 #resolution for linear interpolation
        order = [j for j in range(n,0,-1)]
        order.append(0)
        order.extend([j for j in range(n+1,2*n+1)])
        if len(date) == 1:
            date = [date[0] - datetime.timedelta(hours=1),date[0]]
        forecast = {}
        n_s = len(date)-1
        # m_param = ['schedules','T_set','w_set','loads','gains','occupancy','mixing','infiltration','T_mains','water_heat','S'] #parameters that could be overridden by 'actual' measurements
        # forecast['m_param'] = [[{} for k in range(n_b)] for t in range(n_s)]
        f_keys = ['E0','C0','H0','T_avg','Tzone','Discomfort','Tmin','Tmax','H2E','C2E','th_bar','tc_bar','ua_c','ua_h','h_min','c_min','internal_gain']
        for f in f_keys:
            forecast[f] = [[0 for b in range(n_b)] for t in range(n_s)]
        forecast['Cap'] = [[] for b in range(n_b)]
        forecast['deadband'] = [[False for b in range(n_b)] for t in range(n_s)]
        forecast['Tz_nominal'] = [[] for b in range(n_b)]
        heating = [[[0 for j in range(2*n+1)] for b in range(n_b)] for t in range(n_s)]
        cooling=  [[[0 for j in range(2*n+1)] for b in range(n_b)] for t in range(n_s)]
        air_density = 1.204 #kg/m^3 #standard air density (1.204 kg/m3) adjusted for the local barometric pressure (standard barometric pressure corrected for altitude, ASHRAE 1997 HOF pg. 6.1).
        cat = {'heat_elec''heat_gas''cool_elec''fan_elec''water_gas''water_elec''tower_elec''pumps''other_fans'}
        default = {}
        default['Tzone'] = []
        T_building_effective = [[[0 for i in range(2*n+1)] for k in range(n_b)] for j in range(n_s)]
        hvac_elec = [0 for i in range(2*n+1)]
        Tzone_dr = [[0 for i in range(2*n+1)] for j in range(n_s)]
        Tsurf_dr = [[0 for i in range(2*n+1)] for j in range(n_s)]
        humidity_dr = [[0 for i in range(2*n+1)] for j in range(n_s)]
        flow_param = {} #output for debugging
        flow_param['zone_flow'] = [[0 for i in range(2*n+1)] for j in range(n_s)]
        flow_param['zone_temp'] = [[0 for i in range(2*n+1)] for j in range(n_s)]
        flow_param['zone_transfer'] = [[0 for i in range(2*n+1)] for j in range(n_s)]
        cat = ['heat_elec','heat_gas','cool_elec','fan_elec','other_fans','water_gas','water_elec','tower_elec','pumps']
        e_use={}
        weather_now = {}
        w = {}

    for k in range(n_b):
        building = buildings[k]
        nz = len(building['zones']['name'])
        frost = [[0 for i in range(len(building['cases']))]] #need to make as initial condition that is passed from previous time step
        
        Tz0 = [Tz for Tz in observer['building_zone_temp'][k]]
        Ts0 = [Ts for Ts in observer['building_surf_temp'][k]]
        w0 = [j for j in observer['building_humidity'][k]]
        T_supply = observer['building_supply'][k]  #hot and cold water half loop tank temperature

        air_flow = [[0 for i in range(len(building['zones']['name']))] for j in range(2*n+1)]
        Tcentral_supply = [[0 for i in range(len(building['zones']['name']))] for j in range(2*n+1)]

        electric = [[0 for i in range(2*n+1)] for i in range(n_s)]
        ## need a multiplier on capacitance to acccount for walls
        forecast['Cap'][k] = sum([air_density*(1006 + 1860*w0[z])*building['zones']['volume'][z]*building['zones']['multiplier'][z]/1000 for z in range(nz)])#kJ/K
        T,air_nodes,plant_nodes,_,_ = initial_param(building,Tz0,Ts0)
        for l in range(len(building['plant_loop']['name'])):
            plant_nodes['demand_temperature'][building['plant_demand_nodes']['inlet_node'][l]] = T_supply[l]
        
        t_last = date[0]
        for t in range(n_s):
            dt = (date[t+1] - t_last).seconds
            if dt <0:
                dt = dt + 24*3600 #necessary for warm-up period when date jumps back to start of day
            for i in weather:
                if len(weather[i])== len(date):
                    weather_now[i] = weather[i][t+1]
                else:
                    weather_now[i] = weather[i][t]
            leward = leward_calc(weather_now['wdir'],building['surfaces']['exterior']['normal'])
            wind_speed = wind_speed_calc(weather_now['wspd'],building['ctf']['s_height'],building['site']['terrain'])
            schedules = load_sched(building['schedule'],building['holidays'],[date[t+1]],None,False)
            
            ###Load values specific to this moment in time
            T_set,w_set = thermostat_humidistat(building,schedules,Tz0) ## HVAC temperature Schedules
            loads,gains,occupancy,mixing,infiltration,S,frost_t,T_mains,water_heat = zone_loads(building,date[t+1],schedules,weather_now,Tz0,w0,dt,frost[t])

            forecast['Tmin'][t][k] = area_weighted_temperature(building,T_set['heat'])-1
            forecast['Tmax'][t][k] = max(forecast['Tmin'][t][k]+1,area_weighted_temperature(building,T_set['cool']))+1
            
            Qheat = [[] for j in range(2*n+1)]
            Qcool = [[] for j in range(2*n+1)]
            for j in range(2*n+1):
                T['zone'] = [Tz for Tz in Tz0]
                T['surf'] = [Ts for Ts in Ts0]
                w['zone'] = [wz for wz in w0]
                T,w,air_nodes,plant_nodes = reset_loop_param(building,T,w,air_nodes,plant_nodes,weather_now,date[t+1])
                for x in cat:
                    e_use[x] = 0
                T_set_mod = modify_T_set(T_set,j,n,Tzone_dr[t][order[0]])

                ###Determine HVAC setpoints
                air_nodes,central_flow,direct_flow,mixed_air_loop,direct_return_air,plenum,T,w,fan_avail = ideal_hvac(building,schedules,leward,wind_speed,S,air_nodes,weather_now['t_dryb'],mixing,infiltration,gains,T,w,T_set_mod,w_set,occupancy,dt,False)
                #no iteration, because we are holding the supply temperature fixed during the forecast
                supply_flow,e_use,plant_nodes = sim_air_loops(building,air_nodes,mixed_air_loop,central_flow,w['loop'],weather_now['t_dryb'],w['air'],plant_nodes,e_use,fan_avail)
                supply_flow,e_use,plant_nodes = air_terminals(building,air_nodes,supply_flow,e_use,plant_nodes,T['central'])
                supply_flow,plant_nodes,e_use = unitary_systems(building,air_nodes,supply_flow,direct_flow,direct_return_air,T['direct'],weather_now['t_dryb'],w['air'],fan_avail,plant_nodes,e_use)#zone equipment not part of central air loops
                # Collect loads to create vertices
                Qheat[order[j]], Qcool[order[j]],e_use['pumps']  = net_water_loop_loads(building,schedules,plant_nodes,T_mains,T_supply,dt)
                e_use['water_gas'] += water_heat/building['impact_factor']['steam_efficiency'][0] ##unconnected water heat is considered purchased heat
                hvac_elec[j] = e_use['pumps'] + e_use['heat_elec'] + e_use['cool_elec'] + e_use['fan_elec']#net_water_loop loads did not simulate chillers, so this is cool elec not from chillers

                nonHVAC_electric = sum([loads['lighting_internal'][z]*loads['multiplier'][z] for z in range(nz)]) + sum([loads['plug_load'][z]*loads['multiplier'][z] for z in range(nz)]) + loads['exterior']['lighting'] + loads['exterior']['equipment'] + sum(loads['case']['electric']) + sum(loads['rack']['electric'])
                electric[t][order[j]] = (nonHVAC_electric + e_use['pumps'] + e_use['heat_elec'] + e_use['cool_elec'] + e_use['fan_elec'] + e_use['water_elec'] + e_use['tower_elec'])
                ## Simulate step forward in time   
                Tzone_dr[t][order[j]],Tsurf_dr[t][order[j]],humidity_dr[t][order[j]],e_dict = update_model_states_implicit(building,T,S,wind_speed,leward,gains,dt,w,mixing,plenum,infiltration,supply_flow)              
                T_building_effective[t][k][order[j]] = area_weighted_temperature(building,Tzone_dr[t][order[j]])
                air_flow[j] = [supply_flow['flow'][z]*building['zones']['multiplier'][z] for z in range(nz)] #useful to compare total treated air flows
                Tcentral_supply[j] = supply_flow['Tdb']
                flow_param['zone_flow'][t][order[j]] = supply_flow['m_dot']
                flow_param['zone_temp'][t][order[j]] = supply_flow['Tdb']
                n_z = len(supply_flow['Tdb'])
                cp_zone = [(1006 + 1860*supply_flow['w'][z])*air_density for z in range(n_z)] #Specific heat in J/m^3
                flow_param['zone_transfer'][t][order[j]] = [supply_flow['m_dot'][z]*cp_zone[z]*(supply_flow['Tdb'][z] - T_set_mod['cool'][z]) for z in range(n_z)]

            forecast['tc_bar'][t][k],forecast['ua_c'][t][k],forecast['c_min'][t][k],forecast['C2E'][t][k] = lin_load_increase(T_building_effective[t][k],[sum(Qcool[j])/1000 for j in range(2*n+1)],[hvac_elec[j]/1000 for j in range(2*n+1)])
            forecast['th_bar'][t][k],forecast['ua_h'][t][k],forecast['h_min'][t][k],forecast['H2E'][t][k] = lin_load_increase(T_building_effective[t][k],[sum(Qheat[j])/1000 for j in range(2*n+1)],[hvac_elec[j]/1000 for j in range(2*n+1)])
            flat_start = max([forecast['tc_bar'][t][k][0],forecast['th_bar'][t][k][0]])
            flat_end = min([forecast['tc_bar'][t][k][1],forecast['th_bar'][t][k][1]])
            if (flat_start>forecast['Tmin'][t][k] or flat_end<forecast['Tmax'][t][k]) and flat_start<flat_end:
                forecast['deadband'][t][k] = True

            Tz0 = [Tz for Tz in Tzone_dr[t][order[0]]]
            Ts0 = [Ts for Ts in Tsurf_dr[t][order[0]]]
            w0 = [j for j in humidity_dr[t][order[0]]]
            heating[t][k] = [sum(Qheat[j]) for j in range(2*n+1)]
            cooling[t][k] = [sum(Qcool[j]) for j in range(2*n+1)]

            forecast['Discomfort'][t][k] = sum([max([1,occupancy[z]]) * building['zones']['multiplier'][z] for z in range(nz)]) # how many people are made uncomfortable
            forecast['E0'][t][k] = electric[t][order[0]]/1000 #kW
            forecast['C0'][t][k] = sum(Qcool[order[0]])/1000 #kW
            forecast['H0'][t][k] = sum(Qheat[order[0]])/1000 #kW
            forecast['Tzone'][t][k] = [tz for tz in Tzone_dr[t][order[0]]]
            forecast['T_avg'][t][k] = area_weighted_temperature(building,Tzone_dr[t][order[0]])
            #ensure when heating = H0, & cooling = C0 that there is no change in electrical demand
            forecast['E0'][t][k] = max([0,forecast['E0'][t][k]- forecast['C0'][t][k]*forecast['C2E'][t][k] - forecast['H0'][t][k]*forecast['H2E'][t][k]])
            frost.append(frost_t)
            t= t+1
            t_last = date[t]
        forecast['Tz_nominal'][k] = Tzone_dr[0][order[0]]
    return forecast,T_building_effective,heating,cooling


def modify_T_set(T_set,j,n,T0):
    T_set_mod = {}
    T_set_mod['no_hvac'] = [j for j in T_set['no_hvac']]
    T_set_mod['heat'] = [j for j in T_set['heat']]
    T_set_mod['cool'] = [j for j in T_set['cool']]
    T_set_mod['dual_sp'] = True
    if j>0:
        for z in range(len(T_set['cool'])):
            if not T_set['no_hvac'][z] :
                r = 2 #degrees it varies +,- from default
                if j<=n:
                    T_set_mod['cool'][z] = T0[z] - j/n*r
                else:
                    T_set_mod['cool'][z] = T0[z] + (j-n)/n*r
                T_set_mod['heat'][z] = T_set_mod['cool'][z]
        T_set_mod['dual_sp'] = False
    return T_set_mod