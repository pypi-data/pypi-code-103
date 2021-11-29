from building_plus.process.zone_loads import zone_loads
from building_plus.process.load_sched import load_sched

def load_data(building,weather,date,T_zone,w_zone):
    test_data = {}
    weather_now = {}
    test_data['date'] = []
    test_data['internal_gains'] = []
    test_data['weather'] = {}
    for i in weather:
        if i!='timestamp':
            test_data['weather'][i] = []
    dt = (date[1] - date[0]).seconds
    frost = [[0 for i in range(len(building['cases']))]] #need to make as initial condition that is passed from previous time step
    for t in range(len(date)):
        for i in weather:
            weather_now[i] = weather[i][t]
            if i!='timestamp':
                test_data['weather'][i].append(weather[i][t])
        schedules = load_sched(building['schedule'],building['holidays'],[date[t]],None,False)
        loads,gains,occupancy,mixing,infiltration,S,frost_t,T_mains,water_heat = zone_loads(building,date[t],schedules,weather_now,T_zone,w_zone,dt,frost[t])
        frost.append(frost_t)
        test_data['date'].append(date[t])
        test_data['internal_gains'].append(loads['internal_gain'])
    return test_data