from building_plus.basic.eval_curve import eval_curve

def flow_resolver_supply(building,supply_temperature,load,flow,T_return,method,on_loop):
    ##supply side
    ##Pump at start of supply side
    supply_flow = [0 for x in range(len(building['plant_supply_nodes']['name']))]
    for j in on_loop:
        in_n = building['plant_supply_equip']['inlet'][j] 
        out_n = building['plant_supply_equip']['outlet'][j] 
        if building['plant_supply_equip']['type'][j]=='mixer':
            if type(in_n) != list:
                supply_flow[out_n] = supply_flow[in_n]
            else:
                supply_flow[out_n] = sum([supply_flow[k] for k in in_n]) 
        elif building['plant_supply_equip']['type'][j]=='splitter':
            dist,supply_temperature = load_distribution(building,supply_temperature,out_n,supply_flow[in_n],T_return,load,method) 
            if type(out_n) != list:
                supply_flow[out_n] = dist[0]
            else:
                for i in range(len(out_n)):
                    supply_flow[out_n[i]] = dist[i]
        elif building['plant_supply_equip']['type'][j]=='pump:variablespeed' or building['plant_supply_equip']['type'][j]=='pump:constantspeed':
            supply_flow[out_n] = flow 
        else:
            supply_flow[out_n] = supply_flow[in_n] 
    return supply_flow, supply_temperature

def load_distribution(building,supply_temperature,out,flow_in,T_in,net_load,method):
    ## need equipment on the loop to add up to the load
    ## equipment + bypass flows = flow in
    #not doing anything if equipment is in series on a supply branch (not sure if this is ever a problem)
    names = []
    bypass = None
    for j in range(len(building['plant_supply_equip']['name'])):
        for k in range(len(out)):
            if (type(building['plant_supply_equip']['inlet'][j]) == list and out[k] == building['plant_supply_equip']['inlet'][j][0]) or out[k] == building['plant_supply_equip']['inlet'][j]:
                names.append(building['plant_supply_equip']['name'][j]) 
                if building['plant_supply_equip']['bypass'][j]:
                    bypass = len(names) 
                    break
    n = len(names) 
    flow_out = [0 for i in range(n)]
    #first distribution of flow
    if method =='optimal':
        if bypass==None or bypass !=0:
            flow_out[0] = flow_in 
        else:
            flow_out[1] = flow_in 
    elif method =='uniformload':
        #split evenly amongst non-bypass branches
        if bypass == None: #no bypass branch
            flow_out = [flow_in/n for i in range(n)]
        else:
            flow_out = [flow_in/(n-1) for i in range(n)]
            flow_out[bypass-1] = 0 
    elif method =='sequentialload':
        if bypass==None or bypass !=1:
            k=0
        else:
            k=1
        flow_out[k] = flow_in 
    elif method =='uniformplr':
        print('need work in load_distribution of UniformPLR')
    elif method =='sequentialuniformplr':
        print('need work in load_distribution of SequentialUniformPLR')
    else:
        print('need work in load_distribution of manage_plant_equip')

    ## Re-distribution of flow
    error_load = 1 
    tol = 1e-2 
    if net_load>0:
        while abs(error_load)>tol:
            supply_temperature,PLR,load,flow_max,PLR_opt = PLR_load(building,supply_temperature,names,flow_out,T_in,net_load) 
            flow_out = min(flow_max,flow_out) 
            if load == None: #cooling tower, cant calculate load yet
                error_load = 0 
            else:
                error_load = (net_load - sum(load))/net_load 
                sys_with_spare_cap = [i for i in range(len(load)) if load[i]>0 and flow_out[i]<flow_max[i]] 
                if error_load>0 and len(sys_with_spare_cap)==0:
                    error_load = 0 
            if method=='optimal':
                if error_load>tol and any([PLR[i]<PLR_opt[i] for i in range(len(PLR))]):
                    #increase load up to PLR_opt in order of equipment 
                    for j in range(n):
                        if PLR[j]<PLR_opt[j]:
                            flow_out[j] = flow_out[j]*min(PLR_opt[j]/PLR[j],(load[j]+error_load*net_load)/load[j]) 
                            break 
                elif error_load<-tol and any([True for i in range(len(PLR)) if PLR[i]>PLR_opt[i]]):
                    #decrease load to PLR_opt
                    for j in range(n):
                        if PLR[j]>PLR_opt[j]:
                            flow_out[j] = flow_out[j]*min(PLR_opt[j]/PLR[j],(load[j]+error_load*net_load)/load[j]) 
                            break 
                elif abs(error_load)>tol:
                    #distrubte error in load uniformly
                    sys_with_spare_cap = [i for i in range(len(load)) if load[i]>0 and flow_out[i]<flow_max[i]] 
                    for j in sys_with_spare_cap:
                        flow_out[j] = flow_out[j]*(load[j] + (net_load - sum(load))/len(sys_with_spare_cap))/load[j]
            elif method=='uniformload':
                for j in sys_with_spare_cap:
                    flow_out[j] = flow_out[j]*(load[j] + (net_load - sum(load))/len(sys_with_spare_cap))/load[j] 
                flow_out = [f*flow_in/sum(flow_out) for f in flow_out]  #normalize to correct total mass flow
                error_load = 0 
            elif method=='sequentialload':
                if error_load>tol:
                #increase load up to max PLR in order of equipment 
                    if flow_out[k]<flow_max[k]:
                        flow_out[k] = min(flow_max[k],flow_out[k]*(load[k]+error_load*net_load)/load[k]) 
                    else:
                        k += 1 
                        if k == bypass-1:
                            k += 1 
                        if k<=n:
                            flow_out[k] = 0.5*flow_max[k] 
                elif error_load<-tol:
                    #decrease load 
                    flow_out[k] = max(0,flow_out[k]*(load[k]+error_load*net_load)/load[k]) 
                    if flow_out[k] == 0:
                        k -= 1 
                        if k == bypass-1:
                            k -= 1 
            elif method=='uniformplr':
                print('need work in load_distribution of UniformPLR')
            elif method=='sequentialuniformplr':
                print('need work in load_distribution of SequentialUniformPLR')
            else:
                print('need work in load_distribution of manage_plant_equip')
            if bypass!=None:
                flow_out[bypass-1] = max(0,flow_in - (sum(flow_out)- flow_out[bypass-1])) 
    return flow_out, supply_temperature


def PLR_load(building,supply_temperature,names,flow,T_in,net_load):
    Cp_water = 4186  #J/kg*K
    n = len(names) 
    PLR = [0 for i in range(n)]
    load = [flow[i]*net_load/sum(flow) for i in range(n)]
    flow_max = [0 for i in range(n)]
    PLR_opt = [0 for i in range(n)]
    for j in range(n):
        k = building['plant_supply_equip']['name'].index(names[j])
        den = building['plant_loop']['fluid_density'][building['plant_supply_equip']['loop'][k]]
        if (building['plant_supply_equip']['type'][k]=='chiller:electric:reformulatedeir' or
            building['plant_supply_equip']['type'][k]=='chiller:electric:eir' or
            building['plant_supply_equip']['type'][k]=='chiller:constantcop'):
            T_out = T_in - load[j]/(flow[j]*Cp_water)
            PLR[j],load[j],T_out,Q_avail,c = chiller_PLR(building,names[j],flow[j],T_in,T_out)  
            if PLR[j]*Q_avail/(Cp_water*(T_in - T_out))<flow[j]:
                flow_max[j] = PLR[j]*Q_avail/(Cp_water*(T_in - T_out)) 
            else:
                flow_max[j] = building['chiller'][c]['chilled_water_flow_ref']*den #max flow in kg/s
            PLR_opt[j] = building['chiller'][c]['opt_part_load']
            out = building['plant_supply_equip']['outlet'][building['plant_supply_equip']['name'].index(names[j])]
            supply_temperature[out] = T_out
        elif building['plant_supply_equip']['type'][k]=='boiler:hotwater':
            T_out = T_in + load[j]/(flow[j]*Cp_water)
            PLR[j],load[j],T_out,b = boiler_PLR(building,names[j],flow[j],T_in,T_out) 
            if load[j]/(Cp_water*(T_out - T_in))<flow[j]:
                flow_max[j] = load[j]/(Cp_water*(T_out - T_in)) 
            else:
                flow_max[j] = building['boiler'][b]['design_flow_rate']*den #max flow in kg/s
            PLR_opt[j] = building['boiler'][b]['optimal_part_load']
            out = building['plant_supply_equip']['outlet'][building['plant_supply_equip']['name'].index(names[j])]
            supply_temperature[out] = T_out
        elif building['plant_supply_equip']['type'][k]=='coolingtower:singlespeed':
            load = [] 
            PLR[j] = 1 
            PLR_opt[j] = 1 
            flow_max[j] = building['cooling_tower'][names[j]]['water_flow']*den
        elif building['plant_supply_equip']['type'][k]=='waterheater:mixed':
            load = [] 
            PLR[j] = 1 
            PLR_opt[j] = 1 
            flow_max[j] = building['plant_loop']['max_flow_rate'][building['plant_supply_equip']['loop'][k]]*den
        elif (building['plant_supply_equip']['type'][k]=='chiller:enginedriven' or
              building['plant_supply_equip']['type'][k]=='chiller:absorption' or 
              building['plant_supply_equip']['type'][k]=='chiller:absorption:indirect' or 
              building['plant_supply_equip']['type'][k]=='chiller:combustionturbine' or
              building['plant_supply_equip']['type'][k]=='chillerheater:absorption:directfired' or
              building['plant_supply_equip']['type'][k]=='chillerheater:absorption:doubleeffect' or
              building['plant_supply_equip']['type'][k]=='coolingtower:twospeed' or
              building['plant_supply_equip']['type'][k]=='coolingtower:variablespeed:merkel'):
            print('need examples of these types of equipment__' + building['plant_supply_equip']['type'][k])
        elif  building['plant_supply_equip']['bypass'][k]:
            flow_max[j] = sum(flow) 
    return supply_temperature,PLR,load,flow_max,PLR_opt

def boiler_PLR(building,b,flow,T_in,T_out):
    Cp_water = 4186  #J/kg*K
    load = flow*Cp_water*(T_out- T_in) 
    PLR = min(load/building['boiler'][b]['capacity'],building['boiler'][b]['max_part_load']) 
    if load>0 and PLR<building['boiler'][b]['min_part_load']:
        PLR = building['boiler'][b]['min_part_load']
    load = PLR*building['boiler'][b]['capacity']
    return PLR,load,T_out,b

def chiller_PLR(building,c,flow,T_in,T_out):
    ##see pg 763 about standard IPLV values
    Cp_water = 4186  #J/kg*K
    Q_evap = flow*Cp_water*(T_in - T_out) # (Watts) kg/s*J/kgK * K = J/s
    #need to update with actual condenser water outlet temperature
    CCFT = eval_curve(building['curves'],building['chiller'][c]['capacity_temperature_curve'],[T_out,building['chiller'][c]['condenser_water_temperature_ref']]) 
    Q_avail = building['chiller'][c]['capacity']*CCFT #(Watts)
    if flow>0:
        min_T_out = T_in - Q_avail/(Cp_water*flow) 
        T_out = max(T_out,min_T_out) 
        PLR = min(Q_evap/Q_avail,building['chiller'][c]['max_part_load']) 
    else: 
        PLR = 0
    load = PLR*Q_avail
    return PLR,load,T_out,Q_avail,c