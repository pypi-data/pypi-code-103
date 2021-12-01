from eagers.basic.result_template import result_template
from eagers.basic.get_data import get_weather
from eagers.extras import bplus_building_warmup, bplus_warm_up_date


def initialize_observer(fluid_loop,market,all_data_nodes,names, zones, pl,building_observer,date):
    #operating state of generators, buildings, and fluid loops
    observer = {}
    observer['future'] = result_template(all_data_nodes,names, zones, pl)
    observer['history'] = result_template(all_data_nodes,names, zones, pl)
    observer['market'] = market
    n_g = len(names['components'])
    n_l = len(names['lines'])
    observer['timestamp'] = date
    observer['gen_names'] = names['components']
    observer['gen_state'] = [0 for i in range(n_g)]
    observer['gen_status'] = [True for i in range(n_g)]
    observer['stor_state'] = [0 for i in range(n_g)]
    observer['line_names'] = names['lines']
    observer['line_flow'] = [0 for i in range(n_l)]
    
    b_keys = list(building_observer.keys())
    for k in b_keys:
        observer[k] = building_observer[k]
    n_fl = len(fluid_loop['name'])
    observer['fluid_loop_name'] = fluid_loop['name']
    observer['fluid_loop_temperature'] = [0 for i in range(n_fl)]
    observer['fluid_loop_capacitance'] = [0 for i in range(n_fl)]
    for i in range(n_fl):
        observer['fluid_loop_temperature'][i] = fluid_loop['nominal_return_temperature'][i]
        observer['fluid_loop_capacitance'][i] = fluid_loop['fluid_capacity'][i]*fluid_loop['fluid_capacitance'][i] #Water capacity in kg and thermal capacitance in kJ/kg*K to get kJ/K
    observer['hydro_wy_timestamp'] = None
    observer['hydro_wy_soc'] = None
    return observer

def initialize_building_observer(buildings,test_weather,date):
    n_b = len(buildings)
    observer = {}
    observer['building_timestamp'] = [buildings[i]['sim_date'][0] for i in range(n_b)]
    observer['building_name'] = [buildings[i]['name'] for i in range(n_b)]
    observer['building_avg_temp'] = [0 for i in range(n_b)]
    observer['building_zone_temp'] = [[] for i in range(n_b)]
    observer['building_surf_temp'] = [[] for i in range(n_b)]
    observer['building_humidity'] = [[] for i in range(n_b)]
    observer['building_supply'] = [[] for i in range(n_b)]
    observer['building_return'] = [[] for i in range(n_b)]
    observer['building_conditioned_floor_area'] = [[] for i in range(n_b)]
    observer['building_frost'] = [[] for i in range(n_b)]
    for i in range(n_b):
        building = buildings[i]
        n = len(building['zones']['name'])
        rt = building['plant_loop']['exit_temperature']
        for j in range(len(building['plant_loop']['name'])):
            if building['plant_loop']['type'][j] == 'Heating':
                rt[j] -= building['plant_loop']['temperature_difference'][j]
            elif building['plant_loop']['type'][j] == 'Cooling':
                rt[j] += building['plant_loop']['temperature_difference'][j]
        observer['building_supply'][i] =  building['plant_loop']['exit_temperature'] #supply 'tank' temperature
        observer['building_return'][i] =  rt #return 'tank' temperature
        hvac = [0 for z in range(n)]
        for zc in list(building['zone_controls'].keys()):
            if building['zone_controls'][zc]['type'] == 'Thermostat':
                z = building['zones']['name'].index(building['zone_controls'][zc]['zone'])
                hvac[z] = 1
        observer['building_conditioned_floor_area'][i] = [building['zones']['floor_area'][z]*building['zones']['multiplier'][z]*hvac[z] for z in range(n)]
        date = bplus_warm_up_date(building,date[0])
        weather = get_weather(test_weather,date)
        weather['timestamp'] = [d for d in date]
        T_zone,T_surf,humidity,frost = bplus_building_warmup(building,weather,date[0])
        observer['building_zone_temp'][i] = T_zone[-1]
        observer['building_surf_temp'][i] =  T_surf[-1]
        observer['building_humidity'][i] =  humidity[-1] #initial humidity of each zone
        observer['building_timestamp'][i] = date[0]
        A = observer['building_conditioned_floor_area'][i]
        observer['building_avg_temp'][i] = sum([observer['building_zone_temp'][i][z]*A[z] for z in range(len(A))])/sum(A) #area_weighted_temperature %% %current average building zone temperature (used as IC in optimization)
        observer['building_frost'][i] = frost[-1]
    if n_b>0:
        zones = [len(x) for x in observer['building_zone_temp']]
        pl = [len(x) for x in observer['building_supply']]
    else:
        zones = [0]
        pl = [0]
    return observer,zones,pl

def observer_component_ic(gen,ic,stor_perc,names,observer):
    n_g = len(names['components'])
    lb =  [0 for i in range(n_g)]
    l1 = ['ElectricGenerator','CombinedHeatPower','Chiller','Heater','Electolyzer','HydrogenGenerator','CoolingTower']
    l2 = ['ElectricStorage','ThermalStorage','HydrogenStorage']
    for i in range(n_g):
        observer['gen_state'][i] = ic[i]
        if gen[i]['type'] in l1:
            states = gen[i]['states'][-1]
            for j in range(len(states)):
                lb[i] +=gen[i][states[j]]['lb'][-1]
            if ic[i]<lb[i]:
                observer['gen_status'][i] = False
        elif gen[i]['type'] in l2:
            observer['stor_state'][i] = stor_perc/100 * gen[i]['stor']['usable_size']
        elif gen[i]['type'] == 'HydroStorage':
            observer['stor_state'][i] = gen[i]['start_wy']*gen[i]['stor']['usable_size']
        else:
            observer['gen_state'][i] = ic[i]
    return observer