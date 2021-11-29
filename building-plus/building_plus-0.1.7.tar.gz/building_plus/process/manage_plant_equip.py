'''
Run all water plant lops between demand side coils and supply side boilers/chillers
'''
from building_plus.process.flow_resolver_demand import flow_resolver_demand
from building_plus.process.demand_loop import demand_loop
from building_plus.process.flow_resolver_supply import flow_resolver_supply
from building_plus.process.supply_loop import supply_loop
from building_plus.components.half_loop_tank import half_loop_tank

def manage_plant_equip(building,profile,plant_nodes,e_use,dt,T_air,w_air,T_mains,wh_tank,T_supply0,T_return0):   
    ##This function runs the plant water loop supply and demand side 
    ##The correct order matters so that a supply loop (chillers) puts load on a demand loop (cooling tower/condenser)
    ##This function determines 'ideal' heating and cooling and simulates supply
    ##equipment settings (PLR) to provide this amount of heating/cooling
    cp_water = 4186  #J/kg*K
    nl = len(building['plant_loop']['name'])
    loop_load  = [[0 for i in range(nl)] for j in range(3)]
    T_supply_avg = [j for j in T_supply0]
    for i  in range(nl):
        l = building['plant_loop']['loop_order'].index(i)
        n_d_in = building['plant_demand_nodes']['inlet_node'][l]
        n_d_out = building['plant_demand_nodes']['outlet_node'][l]
        n_s_in = building['plant_supply_nodes']['inlet_node'][l]
        n_s_out = building['plant_supply_nodes']['outlet_node'][l]
        sup_lv = building['plant_loop']['loop_volume'][l]/2
        on_loop = [i for i,x in enumerate(building['plant_supply_equip']['loop']) if x==l]
        for j in on_loop:
            if building['plant_supply_equip']['type'][j]== 'waterheater:mixed':
                sup_lv += building['water_heater'][building['plant_supply_equip']['name'][j]]['tank_volume']

        ## Plant demand loops
        plant_nodes,pump_power,pump_heat = flow_resolver_demand(building,plant_nodes,profile,l,T_mains) 
        plant_nodes = demand_loop(building,profile,T_mains,plant_nodes,l) 
        loop_flow_rate = plant_nodes['demand_flow'][n_d_out] 
        loop_return_T = plant_nodes['demand_temperature'][n_d_out]
        T_return,T_return_avg = half_loop_tank(building['plant_loop']['loop_volume'][l]/2,building['plant_loop']['fluid_density'][l],loop_flow_rate,T_return0[l],pump_heat,loop_return_T,dt) # connect demand half loop to supply half loop
        plant_nodes['supply_temperature'][n_s_in] = T_return_avg+0
        plant_nodes['supply_flow'][n_s_in] = loop_flow_rate+0

        ## loop load (including tank back to nominal setpoint)
        if building['plant_supply_nodes']['name'][n_s_out] in building['manager']['node']:
            m = building['manager']['node'].index(building['plant_supply_nodes']['name'][n_s_out])
            if building['manager']['type'][m] == 'Scheduled':
                T_treat = profile[building['manager']['schedule'][m]]
            else:
                T_treat = building['plant_loop']['exit_temperature'][l]
        else:
            T_treat = building['plant_loop']['exit_temperature'][l]

        if building['plant_loop']['type'][l].lower()=='heating':
            if loop_flow_rate>0:
                tank_heat = (T_treat - T_supply_avg[l])*cp_water*building['plant_loop']['loop_volume'][l]/2*building['plant_loop']['fluid_density'][l]#energy in J
            else: 
                tank_heat = 0
            loop_load[0][l] = max(0,loop_flow_rate*cp_water*(T_treat-T_return_avg) - pump_heat + tank_heat/dt)#power % (Watts) kg/s*J/kgK * K = J/s
            supply_load = loop_load[0][l]
        else:
            if loop_flow_rate>0:
                tank_cool = (T_supply_avg[l] - T_treat)*cp_water*building['plant_loop']['loop_volume'][l]/2*building['plant_loop']['fluid_density'][l]#energy in J
            else: 
                tank_cool = 0
            if building['plant_loop']['type'][l].lower()=='cooling':
                loop_load[1][l] = max(0,loop_flow_rate*cp_water*(T_return_avg-T_treat) + pump_heat + tank_cool/dt)#power (Watts) kg/s*J/kgK * K = J/s
                supply_load = loop_load[1][l]
            elif building['plant_loop']['type'][l].lower()=='condenser':
                loop_load[2][l] = max(0,loop_flow_rate*cp_water*(T_return_avg-T_treat) + pump_heat + tank_cool/dt)#power % (Watts) kg/s*J/kgK * K = J/s
                supply_load = loop_load[2][l]

        ## Plant supply loops        
        plant_nodes['supply_flow'],plant_nodes['supply_temperature'] = flow_resolver_supply(building,plant_nodes['supply_temperature'],supply_load,loop_flow_rate,T_return_avg,building['plant_loop']['load_scheme'][l],on_loop) 
        plant_nodes,wh_tank,cool_elec,heat_gas,water_gas,water_elec,tower_elec = supply_loop(building,profile,plant_nodes,wh_tank,T_air,w_air,l,dt) 
        treated_T = plant_nodes['supply_temperature'][n_s_out]
        T_supply_new,T_avg = half_loop_tank(sup_lv,building['plant_loop']['fluid_density'][l],plant_nodes['supply_flow'][n_s_out],T_supply0[l],0,treated_T,dt) # connect supply half loop to demand half loop  
        T_supply_avg[l] = .15*T_supply_avg[l] + .85*T_avg
        plant_nodes['demand_temperature'][n_d_in] = T_supply_avg[l]+0

        e_use['pumps'] += pump_power #Watts
        e_use['cool_elec'] += cool_elec #Watts
        e_use['heat_gas'] += heat_gas #Watts
        e_use['water_gas'] +=water_gas
        e_use['water_elec'] += water_elec
        e_use['tower_elec'] += tower_elec#Watts
        plant_nodes['demand_temperature'][n_d_in] = T_avg+0
    return plant_nodes,e_use,wh_tank,loop_load