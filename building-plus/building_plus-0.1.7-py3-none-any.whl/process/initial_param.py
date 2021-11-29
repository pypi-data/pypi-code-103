from building_plus.process.load_sched import load_sched

def initial_param(building,T_zone1,T_surf1):
    '''
    initial conditions for some more state variables
    '''
    T ={}
    air_nodes ={}
    plant_nodes={}
    nl = len(building['plant_loop']['name'])
    T_supply = [[] for i in range(nl)]
    T_return = [[] for i in range(nl)]
    T['zone'] = T_zone1
    T['surf'] = T_surf1
    n_win = len(building['windows']['name'])
    T['windows'] = [[300,300,300,300] for i in range(n_win)]
    T['windows_int'] = [300 for i in range(n_win)]
    for i in range(n_win):
        if building['windows']['type'][i]=='SimpleGlazingSystem':
            T['windows'][i][2:] = [0,0]
    
    sn = len(building['plant_supply_nodes']['name'])
    dn = len(building['plant_demand_nodes']['name'])
    plant_nodes['demand_temperature'] = [0 for i in range(dn)]
    plant_nodes['demand_flow'] = [0 for i in range(dn)]
    plant_nodes['supply_temperature'] = [0 for i in range(sn)]
    for i in range(len(building['plant_loop']['name'])):
        T_supply[i] = building['plant_loop']['exit_temperature'][i]
        if building['plant_loop']['type'][i].lower()=='heating': #heating loop, water comes back cooler
            T_return[i] = building['plant_loop']['exit_temperature'][i]-building['plant_loop']['temperature_difference'][i]
        else:
            T_return[i] = building['plant_loop']['exit_temperature'][i]+building['plant_loop']['temperature_difference'][i]
    air_nodes['supply_T_set'] = [0 for i in range(sn)]
    air_nodes['supply_w_set'] = [0 for i in range(sn)]
    air_nodes['supply_flow'] = [0 for i in range(sn)]
    air_nodes['demand_T_set'] = [0 for i in range(dn)]
    air_nodes['demand_w_set'] = [0 for i in range(dn)]
    air_nodes['demand_flow'] = [0 for i in range(dn)]
    return T,air_nodes,plant_nodes,T_supply,T_return
