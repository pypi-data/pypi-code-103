'''
This function runs the supply & demand sides of the plant water loops
The correct order matters so that a supply loop (chillers) puts load on ademand loop (cooling tower/condenser)
This function takes 'actual' heating and cooling and splits it among the
various heating/cooling loops in order to keep the loops as close to the
nominal supply temperature as possible
'''

from building_plus.process.flow_resolver_demand import flow_resolver_demand
from building_plus.process.demand_loop import demand_loop
from building_plus.process.flow_resolver_supply import flow_resolver_supply
from building_plus.process.supply_loop import supply_loop
from building_plus.components.half_loop_tank import half_loop_tank

def net_water_loop_supply(building,profile,dt,plant_nodes,e_use,T_mains,T_air,w_air,heating,cooling):
    cp_water = 4186  #J/kg*K
    net_pumps = 0
    nl = len(building['plant_loop']['name'])
    T_return = [0 for i in range(nl)]
    T_supply = [0 for i in range(nl)]
    T_treat = [0 for i in range(nl)]
    loop_load  = [[0 for i in range(nl)] for j in range(3)]
    sup_lv = [building['plant_loop']['loop_volume'][l]/2 for l in range(nl)] #Supply side loop volume
    hl = []
    cl = []
    for l in range(nl):
        T_supply[l] = plant_nodes['demand_temperature'][building['plant_demand_nodes']['inlet_node'][l]] #half loop tank temperature from previous time step (pg 468)
        T_return[l] = plant_nodes['supply_temperature'][building['plant_supply_nodes']['inlet_node'][l]] #half loop tank temperature from previous time step (pg 468)
        #increase tank volume if a water heater is on the loop
        if building['plant_loop']['type'][l].lower()=='heating':
            hl.append(l)
            on_loop = [i for i,x in enumerate(building['plant_supply_equip']['loop']) if x==l]
            for j in range(len(on_loop)):
                if building['plant_supply_equip']['type'][on_loop[j]]=='waterheater:mixed':
                    sup_lv[l] += building['water_heater'][building['plant_supply_equip']['name'][on_loop[j]]]['tank_volume']
        elif building['plant_loop']['type'][l].lower()=='cooling':
            cl.append(l)

        out_node = building['plant_supply_nodes']['name'][building['plant_supply_nodes']['outlet_node'][l]]
        if out_node in building['manager']['node']:
            m = building['manager']['node'].index(out_node)
            if building['manager']['type'][m]=='scheduled':
                T_treat[l] = profile[building['manager']['schedule'][m]]
            else:
                T_treat[l] = building['plant_loop']['exit_temperature'][l]
        else:
            T_treat[l] = building['plant_loop']['exit_temperature'][l]

    loop_cap = [cp_water*sup_lv[l]*building['plant_loop']['fluid_density'][l] for l in range(nl)]
    T_return0 = [j for j in T_return]
    T_treated = [j for j in T_return]
    T_supply_prev = [j for j in T_supply]
    T_supply_avg = [j for j in T_supply]
    ##Heating loops
    if len(hl)>0:
        plant_nodes,loop_load,pump_power = demand_side(building,plant_nodes,profile,T_treat,T_return0,T_mains,dt,hl,'heating',loop_load)
        tr = []
        ts = []
        ll = []
        lf = []
        tt = []
        lc = []
        for i in hl:
            flow = plant_nodes['demand_flow'][building['plant_demand_nodes']['outlet_node'][i]]
            if flow>0:
                tr.append(plant_nodes['supply_temperature'][building['plant_supply_nodes']['inlet_node'][i]])
                ts.append(T_supply[i])
                ll.append(loop_load[0][i])
                lf.append(flow)
                tt.append(T_treat[i])
                lc.append(loop_cap[i])
        if len(tr)>0:
            ttd = treat_loop(tr,ts,ll,lf,tt,lc,heating,dt,'heating')
            j = 0
            for i in hl:
                flow = plant_nodes['demand_flow'][building['plant_demand_nodes']['outlet_node'][i]]
                if flow>0:
                    T_treated[i] = ttd[j]
                    T_supply[i],T_supply_avg[i] = half_loop_tank(sup_lv[i],building['plant_loop']['fluid_density'][i],lf[j],T_supply_prev[i],0,T_treated[i],dt) # connect supply half loop to demand half loop  
                    plant_nodes['demand_temperature'][building['plant_demand_nodes']['inlet_node'][i]] = T_supply_avg[i]
                    j +=1
        else:
            for i in hl:
                T_supply[i] = T_supply_prev[i] + heating*dt/sum(loop_cap)
        net_pumps += sum(pump_power) #Watts


##Cooling loops
    if len(cl)>0:
        plant_nodes,loop_load,pump_power = demand_side(building,plant_nodes,profile,T_treat,T_return0,T_mains,dt,cl,'cooling',loop_load)
        tr = []
        ts = []
        ll = []
        lf = []
        tt = []
        lc = []
        for i in cl:
            flow = plant_nodes['demand_flow'][building['plant_demand_nodes']['outlet_node'][i]]
            if flow>0:
                tr.append(plant_nodes['supply_temperature'][building['plant_supply_nodes']['inlet_node'][i]])
                ts.append(T_supply[i])
                ll.append(loop_load[1][i])
                lf.append(flow)
                tt.append(T_treat[i])
                lc.append(loop_cap[i])
        if len(tr)>0:
            ttd = treat_loop(tr,ts,ll,lf,tt,lc,cooling,dt,'cooling')
            j = 0
            for i in cl:
                flow = plant_nodes['demand_flow'][building['plant_demand_nodes']['outlet_node'][i]]
                if flow>0:
                    T_treated[i] = ttd[j]
                    T_supply[i],T_supply_avg[i] = half_loop_tank(sup_lv[i],building['plant_loop']['fluid_density'][i],lf[j],T_supply_prev[i],0,T_treated[i],dt) # connect supply half loop to demand half loop  
                    plant_nodes['demand_temperature'][building['plant_demand_nodes']['inlet_node'][i]] = T_supply_avg[i]
                    j +=1
        else:
            for i in cl:
                T_supply[i] = T_supply_prev[i] - cooling*dt/sum(loop_cap)
        net_pumps += sum(pump_power) #Watts


    #simulate the chiller to get the load on condenser loop (ignore_use of chiller, as it may not match optimization setpoint (need to be able to override chiller setpoint?)
    for i in range(len(cl)):
        l = cl[i]
        on_loop = [i for i,x in enumerate(building['plant_supply_equip']['loop']) if x==l]
        flow = plant_nodes['demand_flow'][building['plant_demand_nodes']['outlet_node'][l]]
        plant_nodes['supply_flow'],plant_nodes['supply_temperature'] = flow_resolver_supply(building,plant_nodes['supply_temperature'],loop_load[1][l],flow,T_return[l],building['plant_loop']['load_scheme'][l],on_loop)
        plant_nodes,_,_,_,_,_,_ = supply_loop(building,profile,plant_nodes,[],T_air,w_air,l,dt)

    ## condenser loop
    for l in range(nl):
        if building['plant_loop']['type'][l].lower()=='condenser':
            #simulate cooling tower loop to get fan electric loads
            plant_nodes,loop_load,pump_power = demand_side(building,plant_nodes,profile,T_treat,T_return0,T_mains,dt,[l],'condenser',loop_load)
            T_return[l] = plant_nodes['supply_temperature'][building['plant_supply_nodes']['inlet_node'][l]]
            loop_flow_rate = plant_nodes['demand_flow'][building['plant_demand_nodes']['outlet_node'][l]]
            on_loop = [i for i,x in enumerate(building['plant_supply_equip']['loop']) if x==l]
            plant_nodes['supply_flow'],plant_nodes['supply_temperature'] = flow_resolver_supply(building,plant_nodes['supply_temperature'],loop_load[2][l],loop_flow_rate,T_return[l],building['plant_loop']['load_scheme'][l],on_loop)
            plant_nodes,_,_,_,_,_,tower_elec = supply_loop(building,profile,plant_nodes,[],T_air,w_air,l,dt)
            e_use['tower_elec'] += tower_elec
            T_treated[l] = plant_nodes['supply_temperature'][building['plant_supply_nodes']['outlet_node'][l]]
    net_pumps += sum(pump_power) #Watts
    e_use['pumps'] == net_pumps #Watts
    return e_use,plant_nodes,loop_load

def demand_side(building,plant_nodes,profile,T_treat,T_return0,T_mains,dt,loops,l_type,loop_load):
    ## Plant demand loops
    cp_water = 4186 #J/kg*K
    pump_power = []
    for l  in loops:
        plant_nodes,pp,pump_heat = flow_resolver_demand(building,plant_nodes,profile,l,T_mains) 
        pump_power.append(pp)
        plant_nodes = demand_loop(building,profile,T_mains,plant_nodes,l) 
        n = building['plant_demand_nodes']['outlet_node'][l] 
        loop_flow_rate = plant_nodes['demand_flow'][n] 
        loop_return_T = plant_nodes['demand_temperature'][n]
        if loop_flow_rate>0:
            # Update return half tank
            _,T_return_avg = half_loop_tank(building['plant_loop']['loop_volume'][l]/2,building['plant_loop']['fluid_density'][l],loop_flow_rate,T_return0[l],pump_heat,loop_return_T,dt) # connect demand half loop to supply half loop
            plant_nodes['supply_temperature'][building['plant_supply_nodes']['inlet_node'][l]] = T_return_avg
            T_supply = plant_nodes['demand_temperature'][building['plant_demand_nodes']['inlet_node'][l]]
            ## loop load (including tank back to nominal setpoint)
            if l_type=='heating':
                tank_heat = (T_treat[l] - T_supply)*cp_water*building['plant_loop']['loop_volume'][l]/2*building['plant_loop']['fluid_density'][l]#energy in J
                loop_load[0][l] = max(0,loop_flow_rate*cp_water*(T_treat[l]-loop_return_T) - pump_heat + tank_heat/dt)#power % (Watts) kg/s*J/kgK * K = J/s
            elif l_type=='cooling':
                tank_cool = (T_supply - T_treat[l])*cp_water*building['plant_loop']['loop_volume'][l]/2*building['plant_loop']['fluid_density'][l]#energy in J
                loop_load[1][l] = max(0,loop_flow_rate*cp_water*(loop_return_T-T_treat[l]) + pump_heat + tank_cool/dt)#power (Watts) kg/s*J/kgK * K = J/s
            elif l_type=='condenser':
                tank_cool = (T_supply - T_treat[l])*cp_water*building['plant_loop']['loop_volume'][l]/2*building['plant_loop']['fluid_density'][l]#energy in J
                loop_load[2][l] = max(0,loop_flow_rate*cp_water*(loop_return_T-T_treat[l]) + pump_heat + tank_cool/dt)#power % (Watts) kg/s*J/kgK * K = J/s
    return plant_nodes,loop_load,pump_power

def treat_loop(T_return,T_supply,loop_load,loop_flow_rate,T_treat,loop_cap,treatment,dt,l_type):
    ## add heat or cooling on supply side
    ## split treatment to get as close to design exit temperature on all loops
    ## constrain to +- 10 degrees to avoid errors, note the energy dump
    cp_water = 4186 #J/kg*K
    if l_type=='heating':
        tank_e_max = [(T_treat[i]+10 - T_supply[i])*loop_cap[i] for i in range(len(loop_cap))] #energy in J
        tank_e_min =  [(T_treat[i]-10 - T_supply[i])*loop_cap[i] for i in range(len(loop_cap))] #energy in J
    elif l_type=='cooling':
        tank_e_max =  [(T_supply[i] - (T_treat[i]-10))*loop_cap[i] for i in range(len(loop_cap))] #energy in J
        tank_e_min = [(T_supply[i] - (T_treat[i]+10))*loop_cap[i] for i in range(len(loop_cap))] #energy in J

    if treatment == 0:
        T_treated = [T_return[i] for i in range(len(loop_cap))]
    else:
        if treatment>sum(loop_load):
            useful_treatment = min((sum(loop_load) + sum(tank_e_max)/dt),treatment)
            perc_rest = min(1,(useful_treatment-sum(loop_load))/(sum(tank_e_max)/dt))
            e = [loop_load[i] + perc_rest*(tank_e_max[i]/dt) for i in range(len(loop_cap))]
            split = [e[i]/sum(e) for i in range(len(loop_cap))]
            e_dump = (treatment - useful_treatment)/1000 #kw that must be lost
        else:
            useful_treatment = max((sum(loop_load)+sum(tank_e_min)/dt),treatment)
            min_e = [max(0,loop_load[i]+tank_e_min[i]/dt) for i in range(len(loop_cap))]
            perc_rest = max(0,(useful_treatment-sum(min_e))/(sum(loop_load)-sum(min_e)))
            e = [min_e[i] + perc_rest*(loop_load[i]-min_e[i]) for i in range(len(loop_cap))]
            if sum(e) == 0:
                split = [0 for i in range(len(loop_cap))]
            else:
                split = [e[i]/sum(e)  for i in range(len(loop_cap))]
            e_makeup = (useful_treatment-treatment)/1000 #kw that must be made up
        if l_type=='heating':
            T_treated = [T_return[i] + useful_treatment*split[i]/(cp_water*loop_flow_rate[i]) for i in range(len(loop_cap))]
        elif l_type=='cooling':
            T_treated = [T_return[i] - useful_treatment*split[i]/(cp_water*loop_flow_rate[i]) for i in range(len(loop_cap))]
    return T_treated