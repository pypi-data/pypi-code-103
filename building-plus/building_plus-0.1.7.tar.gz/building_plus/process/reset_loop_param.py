from building_plus.basic.psychometric import psychometric

import numpy as np

def reset_loop_param(building,T,w,air_nodes,plant_nodes,weather,date):
    sn = len(building['plant_supply_nodes']['name'])
    dn = len(building['plant_demand_nodes']['name'])
    plant_nodes['load'] =  [0 for i in range(dn)] #reset to zero, and put in loads from demand side as you get through equipment
    plant_nodes['demand_flow'] = [0 for i in range(dn)] #reset to zero, and put in loads from demand side as you get through equipment
    plant_nodes['supply_flow'] = [0 for i in range(sn)]
    sn = len(building['air_supply_nodes']['name'])
    dn = len(building['air_demand_nodes']['name'])
    air_nodes['supply_T_set'] = [0 for i in range(sn)]
    air_nodes['supply_flow'] = [0 for i in range(sn)]
    air_nodes['demand_T_set'] = [0 for i in range(dn)]
    air_nodes['demand_flow'] = [0 for i in range(dn)]
    
    ###pre-compute some ambient conditions
    sig = 5.67e-8 # W/m^2*K^4 Stephan-Boltzman const
    sky_emissivity = (0.787 + 0.764*np.log((weather['t_dewp']+273)/273))*(1 + 0.0224*weather['opq_cld'] - 0.0035*weather['opq_cld']**2 + 0.00028*weather['opq_cld']**3)
    ir_intensity = sky_emissivity*sig*(weather['t_dryb']+273)**4 #W/m^2
    T['sky'] = (ir_intensity/sig)**.25 - 273
    T['ground'] = building['ground_temperatures'][date.month-1]
    w['air'] = psychometric({'P':weather['pres_pa'],'Tdp':weather['t_dewp']},'w')
    T['air_zone'] = [weather['t_dryb'] - 0.0065*h for h in building['ctf']['z_height']] #outdoor air temp next to each zone
    T['air_surface'] =[weather['t_dryb'] - 0.0065*h for h in building['ctf']['s_height']] #outdoor air temp next to each exterior surface
    T['exterior'] = [j for j in T['air_surface']]
    for i in range(len(building['surfaces']['exterior']['name'])):
        if building['surfaces']['exterior']['boundary'][i]=='ground':
            T['exterior'][i] = T['ground']
    return T,w,air_nodes,plant_nodes