'''
Run a simulation with forecasting and actual data
'''
from building_plus.read.get_data import get_data
from building_plus.process.load_sched import load_sched
from building_plus.process.initial_param import initial_param
from building_plus.process.reset_loop_param import reset_loop_param
from building_plus.process.zone_loads import zone_loads
from building_plus.process.forecast_dr_capacity import forecast_dr_capacity
from building_plus.process.buildings_step import buildings_step
from building_plus.process.load_actual_building_data import update_real_gains

import datetime

def run_sim(building,test_data,weather,T_zone,T_surf,humidity,date,horizon):
    facility = {}
    e_use = {}
    weather_now = {}
    weather_forecast = {}
    frost = [[0 for i in range(len(building['cases']))]]
    net_elec = []
    heat_absorbed_by_loop = []
    cooling_absorbed_by_loop = []
    w = {}
    w['zone'] = humidity[0]
    f_cat = ['net_elec','heat_elec','heat_gas','cool_elec','fan_elec','other_fans','water_gas','water_elec','tower_elec','pumps','heating_load','cooling_load','tower_load','supply_T','return_T']
    for i in f_cat:
        facility[i] = []
    T,air_nodes,plant_nodes,T_supply,T_return = initial_param(building,T_zone[0],T_surf[0])
    facility['supply_T'].append(T_supply)
    facility['return_T'].append(T_return)
    t_last = date[0]
    for t in range(len(date)-1):#number of simulation steps
        dt = (date[t+1] - t_last).seconds# resolution in seconds
        d_now = date[t+1] 
        d_forecast = [d_now + datetime.timedelta(hours=i) for i in range(horizon+1)]
        for i in weather:
            weather_now[i] = weather[i][t]
            weather_forecast[i] = [weather[i][t+j] for j in range(horizon+1)]

        observer = {}
        observer['building_humidity'][0] = w['zone']
        observer['building_zone_temp'][0] = T_zone[t]
        observer['building_surf_temp'][0] = T_surf[t]
        observer['building_supply'][0] = T_supply[t]
        forecast,T_building_effective,heating_t,cooling_t = forecast_dr_capacity([building],observer,weather_forecast,d_forecast)
        Tz_nominal = forecast['Tz_nominal']
        ## compute vertices

        ## receive heating/cooling and 'optimal' building temperature values from transactive optimization
        n0 = int((len(heating_t[0][0])-1)/2)
        heating = heating_t[0][0][n0]
        cooling = cooling_t[0][0][n0]
        T_optimal = T_building_effective[0][0][n0]
        
        ##Update actual data
        actual_data = get_data(test_data,[d_now])[0]
        T,w,air_nodes,plant_nodes = reset_loop_param(building,T,w,air_nodes,plant_nodes,weather_now,d_now)
        schedules = load_sched(building['schedule'],building['holidays'],[d_now],None,False)
        loads,gains,_,_,_,_,_,_,_ = zone_loads(building,d_now,schedules,actual_data['weather'],T_zone[t],humidity[t],dt,frost[t])
        new_loads,new_gains,_ = update_real_gains(building,actual_data['weather'],loads,gains,d_now,actual_data['internal_gains'])
        ##simulate building forward in time
        T, humid_t1, frost_t, e_use, loop_load, air_nodes, plant_nodes = buildings_step(building,actual_data['weather'],T,w,air_nodes,plant_nodes,e_use,new_loads,new_gains,heating,cooling,T_optimal,Tz_nominal,schedules,frost[t],dt,d_now)

        ##Collect and organize
        frost.append(frost_t)
        T_zone.append(T['zone'])
        T_surf.append(T['surf'])
        humidity.append(humid_t1)
        for i in range(10):
            facility[f_cat[i]].append(e_use[f_cat[i]])
        facility['heating_load'].append(sum(loop_load[0]))
        facility['cooling_load'].append(sum(loop_load[1]))
        facility['tower_load'].append(sum(loop_load[2]))
        T_supply = []
        T_return = []
        for l in range(len(building['plant_loop']['name'])):
            T_return.append(plant_nodes['supply_temperature'][building['plant_supply_nodes']['inlet_node'][l]])
            T_supply.append(plant_nodes['demand_temperature'][building['plant_demand_nodes']['inlet_node'][l]])
        facility['supply_T'].append(T_supply)
        facility['return_T'].append(T_return)
        net_elec.append((facility['net_elec'][t] - facility['cool_elec'][t])/1000) #kW
        heat_absorbed_by_loop.append(heating - facility['heating_load'][t]/1000)
        cooling_absorbed_by_loop.append(cooling - facility['cooling_load'][t]/1000)
        t_last = date[t+1]
    return facility, net_elec