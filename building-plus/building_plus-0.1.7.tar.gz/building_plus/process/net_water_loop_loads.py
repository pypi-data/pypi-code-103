'''
This deviates from EnergyPlus
This collects all building heating and cooling water loops 
and converts to a load on the district heating/cooling water loops
using the district heating/cooling supply temperature
'''

from building_plus.process.flow_resolver_demand import flow_resolver_demand
from building_plus.process.demand_loop import demand_loop

def net_water_loop_loads(building,profile,plant_nodes,T_mains,T_supply,dt):   
    Cp_water = 4186  #J/kg*K
    nl = len(T_supply)
    Q_hot = [0 for i in range(nl)]
    Q_cold = [0 for i in range(nl)]
    net_pumps = 0
    for i  in range(len(building['plant_loop']['name'])):
        l = building['plant_loop']['loop_order'].index(i)
        n = building['plant_demand_nodes']['outlet_node'][l] 
        plant_nodes,pump_power,pump_heat = flow_resolver_demand(building,plant_nodes,profile,l,T_mains) 
        plant_nodes = demand_loop(building,profile,T_mains,plant_nodes,l) 
        loop_flow_rate = plant_nodes['demand_flow'][n]
        if loop_flow_rate>0:
            T_return = plant_nodes['demand_temperature'][n] + pump_heat/(Cp_water*loop_flow_rate)
            net_pumps +=pump_power
            T_treat = building['plant_loop']['exit_temperature'][l]
            if building['plant_loop']['type'][l].lower() == 'heating':
                tank_heat = (T_treat - T_supply[l])*Cp_water*building['plant_loop']['loop_volume'][l]/2*building['plant_loop']['fluid_density'][l] #energy in J
                Q_hot[l] =  max(0,loop_flow_rate*Cp_water*(T_treat-T_return) + tank_heat/dt) #power in W 
            elif building['plant_loop']['type'][l].lower() == 'cooling':
                tank_cool = (T_supply[l] - T_treat)*Cp_water*building['plant_loop']['loop_volume'][l]/2*building['plant_loop']['fluid_density'][l] #energy in J
                Q_cold[l] = max(0,loop_flow_rate*Cp_water*(T_return-T_treat) + tank_cool/dt) #power in W
    return Q_hot, Q_cold, net_pumps