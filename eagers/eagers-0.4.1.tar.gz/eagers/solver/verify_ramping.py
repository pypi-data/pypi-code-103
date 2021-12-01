from eagers.basic.gen_limit import gen_limit
from eagers.basic.marginal_cost import piecewise_tangent

def verify_ramping(gen, subnet, qp, optimal_state, scale_cost, dt):
    #Premise, it may not be possible to follow the output from the step-by-step
    #dispatch due to ramp rate limitations. The ramp rates will limit the 
    #cumulative energy generation. Storage or spare capacity in other generators 
    #can make up the difference without turning something on. 
    #Otherwise, something must turn on.
    #
    #inputs:
    #gen        - instance of the class Generators, describing all components at the plant
    #subnet     - 
    #qp         - instance of the class QP that contains all the matrices for the quadratic programming
    #optimal_state  - dispatch setpoints for each component when optimized at inidividual timesteps
    #scale_cost     - vost for fuel/electricity at each time
    #dt         - vector of length of each timestep
    #outputs:
    #locked     - boolean matrix indicating which generators are online at each timestep updated
    #                to account for ramp rate limitations

    n_g = len(gen)
    n_s = len(dt)
    locked = [[True for t in range(n_s+1)] for i in range(n_g)]
    for i in range(n_g):
        if not qp['organize']['enabled'][i]:
            locked[i] = [False for t in range(n_s+1)]

    network_names = list(qp['organize']['balance'].keys())
    if 'hydro' in network_names:
        network_names.remove('hydro')
    # Make sure it can shut down in time from initial condition
    for i in range(n_g):
        if qp['organize']['dispatchable'][i]:
            for t in range(n_s+1):
                if optimal_state[i][t]==0:
                    locked[i][t] = False #Identify when optimal dispatch has things off
            if optimal_state[i][0]>0 and not all(locked[i]):
                d = optimal_state[i][0]
                t = 0
                while d>0:
                    r = qp['organize']['ramp_up'][i][t] #no +1 b/c indexing
                    d = d - qp['b'][r]
                    if d>0 and not locked[i][t+1]:
                        locked[i][t+1] = True
                    t = t+1
    
    # Make sure the loss of energy due to ramping constraints at starts & stops, can be made by other generators or storage
    for net in network_names:
        inc = [False for i in range(n_g)]
        stor = [False for i in range(n_g)]
        util = []
        out = subnet[net]['abbreviation']
        for i in range(n_g):
            if gen[i]['type'] == 'Solar':
                pass#don't include
            elif gen[i]['type'] == 'Utility':
                if out in gen[i]['output'] or out == 'dc' and 'e' in gen[i]['output']:
                    util.append(i)
            elif gen[i]['type'] in ['Storage','ThermalStorage','ElectricStorage']:
                if out in gen[i]['output']:
                    stor[i] = True
            elif gen[i]['type'] == 'Chiller':
                if out == 'c':
                    inc[i] = True
            elif out in gen[i]['output']:
                inc[i] = True
        
        if any(stor):
            locked = check_capacity(gen, subnet, qp, optimal_state, stor, locked, inc, out, dt)
        else:
            locked,_ = turn_gen_on(gen,subnet,qp,optimal_state,scale_cost,locked,out,net,inc,util,dt)
    
    return locked

def check_capacity(gen, subnet, qp, optimal_state, stor, locked, inc, out, dt):
    n_g = len(inc)
    n_s = len(dt)
    stored_energy = [0 for t in range(n_s)]
    charge_eff = []
    for i in range(n_g):
        if stor[i]:
            if 'buffer' in gen[i]:
                buff = gen[i]['stor']['usable_size']*(gen[i]['buffer']/100)
            else:
                buff = 0
            stored_energy = [stored_energy[t] + max([0,(optimal_state[i][t+1]-buff)*gen[i]['stor']['disch_eff']]) for t in range(n_s)]
            charge_eff.append(gen[i]['stor']['charge_eff'])
    
    avg_charge_eff = sum(charge_eff)/len(charge_eff)
    max_out, constraint,_,_ = gen_limit(gen, optimal_state, locked, dt, [out])
    if out == 'h':
        dispatch, heat_consumed = heat_disp(gen, subnet, optimal_state, locked, qp,dt)
    else:
        dispatch = optimal_state

    for i in range(len(inc)):
        if inc[i]:
            starts = [t for t in range(n_s) if locked[i][t+1] and not locked[i][t]]
            k = 0
            while k<len(starts):
                t = starts[k]
                d = [0 for t in range(n_s)]
                s = [0 for t in range(n_s)]
                new_on = []
                while t<=n_s-1 and max_out[out][i][t+1]<dispatch[i][t+1]: 
                    if t>starts[k]:
                        d[t] = d[t-1]
                    d[t] += dispatch[i][t+1] - max_out[out][i][t+1]
                    t += 1
                t_end = max([0,t-1])
                for t in range(t_end):
                    if t>0:
                        s[t] = s[t-1]
                    if out == 'h':
                        for j in range(n_g):
                            if inc[j] and j != i:
                                s[t] += max_out[out][j][t+1]
                            s[t] -= heat_consumed[t]
                    else:
                        for j in range(n_g):
                            if inc[j]:
                                s[t] +=max_out[out][j][t+1] - dispatch[j][t+1]
                if any([(d[t]-s[t])>stored_energy[t] for t in range(n_s)]) and not constraint[i][starts[k]] is None and not locked[i][constraint[i][starts[k]]+1]:
                    nw = constraint[i][starts[k]]
                    new_on.insert(0,nw)
                    locked[i][nw+1] = True
                    old_max = [max_out[out][i][t+1] for t in new_on]
                    max_out,constraint,_,_ = gen_limit(gen,optimal_state,locked,dt,[out])
                    for t in new_on:
                        optimal_state[i][t+1] = max_out[out][i][t+1]
                    if out == 'h':
                        dispatch, heat_consumed = heat_disp(gen, subnet, optimal_state, locked, qp, dt)
                    else:
                        dispatch = [[i for i in j] for j in optimal_state]
                    for j in range(len(new_on)):
                        for t in range(new_on[j],n_s):
                            stored_energy[t] += (max_out[out][i][new_on[j]+1] - old_max[j])*avg_charge_eff
                    if starts[k]>0 and locked[i][(starts[k])] == False:
                        starts[k] -= 1
                        k -= 1
                k += 1

            stops = [t for t in range(n_s) if not locked[i][t+1] and locked[i][t]]
            if len(stops) > 0 and stops[0] == 0: #Initial condition ramp down was taken care of earlier
                del stops[0]
            k = 0
            while k<len(stops):
                d = [0 for t in range(n_s)]
                s = [0 for t in range(n_s)]
                new_on = []
                next_on = [j for j in starts if j>stops[k]]
                if len(next_on) == 0:
                    next_on = n_s
                else:
                    next_on = next_on[0]
                t_start_down = 0
                while dispatch[i][t_start_down+1]<max_out[out][i][t_start_down+1] and t_start_down<stops[k]:
                    t_start_down += 1
                for t in range(next_on):
                    if t>0:
                        s[t] = s[t-1]
                        d[t] = d[t-1]
                    if t>=t_start_down:
                        d[t] = max([0,d[t]+dispatch[i][t+1]- max_out[out][i][t+1]])
                    
                    if out == 'h':
                        for j in range(n_g):
                            if inc[j] and j != i:
                                s[t] += max_out[out][j][t+1]
                        s[t] -= heat_consumed[t]
                    else:
                        for j in range(n_g):
                            if inc[j] and j != i:
                                s[t] += max_out[out][j][t+1] - dispatch[j][t+1]
                if any([(d[t]-s[t])>stored_energy[t] for t in range(n_s)]) and not constraint[i][stops[k]-1] is None and not locked[i][constraint[i][stops[k]-1]+1]:
                    nw = constraint[i][stops[k]-1]
                    new_on.insert(0,nw)
                    locked[i][nw+1] = True
                    old_max = [max_out[out][i][t+1] for t in new_on]
                    max_out,constraint,_,_ = gen_limit(gen,optimal_state,locked,dt, [out])
                    for t in new_on:
                        optimal_state[i][t+1] = max_out[out][i][t+1]
                    if out == 'h':
                        dispatch, heat_consumed = heat_disp(gen, subnet, optimal_state, locked, qp, dt)
                    else:
                        dispatch = [[i for i in j] for j in optimal_state]
                    for j in range(len(new_on)):
                        for t in range(new_on[j],n_s):
                            stored_energy[t] += (max_out[out][i][new_on[j]+1] - old_max[j])*avg_charge_eff
                    if stops[k]<n_s-1 and not locked[i][nw+2]:
                        stops[k] += 1
                        k  -= 1
                k += 1
    return locked

def turn_gen_on(gen, subnet, qp, optimal_state, scale_cost, locked, out, net, inc, util, dt):
    n_g = len(gen)
    n_s = len(dt)
    lgen = []
    net_demand =[0 for t in range(n_s)]
    for n in range(len(qp['organize']['balance'][net])):
        for t in range(n_s):
            r_eq = qp['organize']['balance'][net][n][t]
            net_demand[t] += qp['b_eq'][r_eq]
    for i in range(n_g):
        if gen[i]['type'] == 'Chiller' and ((out == 'h' and gen[i]['source'] == 'heat') or (out == 'e' and gen[i]['source'] == 'electricity')): 
            for t in range(n_s):
                net_demand[t] += gen[i]['const_demand'][net]*locked[i][t]
            lgen.append(i)
            n = gen[i]['subnet_node'][net]
            
            for t in range(n_s):
                req = qp['organize']['balance'][net][n][t]
                states = qp['indices'][i][t+1]
                if locked[i][t+1]:
                    cum = 0
                    j = 0
                    while j<len(states) and cum<optimal_state[i][t+1]:
                        s = states[j]
                        c = min([optimal_state[i][t+1]-cum,qp['ub'][s]])
                        cum += c
                        net_demand[t] -= c*qp['a_eq'][req][s]
                        j += 1
    feas = False
    while not feas:
        max_out, constraint,_,_ = gen_limit(gen, optimal_state, locked, dt, [out])
        if out == 'h':
            _,net_demand = heat_disp(gen, subnet, optimal_state, locked, qp, dt)
        constrained_gen = [sum([max_out[out][i][t+1] for i in range(n_g) if inc[i]]) for t in range(n_s)]
        if not util == []:
            constrained_gen = [constrained_gen[t] + sum([max_out[out][u][t+1] for u in util]) for t in range(n_s)]
        if all([constrained_gen[t]>= (net_demand[t]-(1e-9)) for t in range(n_s)]):
            feas = True
        else:
            t = 0
            while constrained_gen[t] >= (net_demand[t] - (1e-9)):
                t +=1
            shortfall = net_demand[t] - sum([max_out[out][i][t+1] for i in range(n_g) if inc[i]])
            if any([not constraint[i][t] is None for i in range(len(inc)) if inc[i]]):
                locked = turn_cheapest_on(gen,scale_cost,locked,inc,shortfall,constraint,t,dt,n_s)
            elif not all([locked[i][t+1] for i in range(len(inc)) if inc[i]]):
                locked = turn_cheapest_on(gen,scale_cost,locked,inc,shortfall,[],t,dt,n_s)
            elif not len(lgen) == 0 and any([locked[i][t+1] for i in lgen]):
                for i in range(len(lgen)):
                    locked[lgen[i]][t+1] = False                        
            else:
                feas = True
            
    return locked, feas

def  turn_cheapest_on(gen,scale_cost,locked,inc,shortfall,constraint,t,dt,n_s):
    n_g = len(locked)
    diff = [0 for i in range(n_g)]
    for i in range(n_g):
        if inc[i] and not locked[i][t+1]:
            if len(constraint)==0 and any(locked[i]): #turn on something else that has the same type of output
                diff[i] = min([abs(t-(x-1)) for x in range(n_s+1) if locked[i][x]])
            elif len(constraint)>0 and not constraint[i][t] is None and constraint[i][t]<n_s+1: #select apropriate one to start early or keep on later
                diff[i] = abs(constraint[i][t]-t)
            else:
                diff[i] = n_s+1
        else:
            diff[i] = float('inf')
    min_ts = min(diff)
    on_opt = []
    on_t = []
    on_dt = []
    sc = []
    for i in range(n_g):
        if diff[i] == min_ts:
            on_opt.append(i)
            if len(constraint)>0 and not constraint[i][t] is None:
                on_t.append(constraint[i][t])
            else:
                on_t.append(t)
            on_dt.append(dt[on_t[-1]])
            sc.append(scale_cost[i][on_t[-1]])
    opt_cost = cost_of_options(gen,on_opt,on_dt,shortfall,len(constraint)==0,sc)
    mi = opt_cost.index(min(opt_cost))
    locked[on_opt[mi]][on_t[mi]+1] = True
    return locked

def cost_of_options(gen,on_opt,on_dt,shortfall,new_start,sc):
    mc = []
    for k in range(len(on_opt)):
        i = on_opt[k]
        pow = min([shortfall,on_dt[k]*gen[i]['ramp']['b'][0],gen[i]['ub']])
        smc = piecewise_tangent(gen[i],pow,sc[k])
        if new_start:
            #add startup and constant cost
            mc.append((smc*pow + gen[i]['const_cost']*on_dt[k]*sc[k] + gen[i]['start_cost'])/pow)
        else:
            mc.append(smc)
    return mc

def heat_disp(gen, subnet, optimal_state, locked, qp, dt):
    n_g = len(gen)
    n_s = len(dt)
    dispatch = [[i for i in k] for k in optimal_state]
    heat_consumed = [0 for t in range(n_s)]
    for n in range(len(subnet['district_heat']['nodes'])):
        heat_consumed = [heat_consumed[t] + qp['b_eq'][qp['organize']['balance']['district_heat'][n][t]] for t in range(n_s)]
    for i in range(n_g):
        if gen[i]['type'] == 'CombinedHeatPower':
            for t in range(n_s):   
                req = qp['organize']['balance']['district_heat'][n][t]             
                if locked[i][t+1]:
                    dispatch[i][t+1] = -gen[i]['const_demand']['district_heat']
                else:
                    dispatch[i][t+1] = 0
                states = qp['indices'][i][t+1]
                cum_out = 0
                j = 0
                while j<len(states):
                    d = min([optimal_state[i][t+1] - cum_out, qp['ub'][states[j]]])
                    cum_out += d
                    dispatch[i][t+1] += d*qp['a_eq'][req][states[j]]
                    j = j + 1
        elif gen[i]['type'] == 'Heater':
            pass
        elif gen[i]['type'] == 'Chiller' and gen[i]['source']=='heat':
            dispatch[i] = [0 for t in range(n_s)]
            for n in range(len(subnet['district_heat']['nodes'])):
                heat_consumed = [heat_consumed[t] + sum([qp['const_demand']['district_heat']['load'][n][t][j]*locked[j][t+1] for j in range(n_g)]) for t in range(n_s)]
            for t in range(n_s):
                req = qp['organize']['balance']['district_heat'][n][t]     
                if locked[i][t+1]:
                    states = qp['indices'][i][t+1]
                    cum_out = 0
                    j = 0
                    while j<len(states) and cum_out<optimal_state[i][t+1]:
                        d = min([optimal_state[i][t+1] - cum_out, qp['ub'][states[j]]])
                        cum_out += d
                        heat_consumed[t] -= d*qp['a_eq'][req][states[j]]
                        j = j + 1
        elif gen[i]['type'] == 'ThermalStorage':
            if gen[i]['source']=='heat':
                for t in range(n_s):
                    if optimal_state[i][t]<optimal_state[i][t+1]:
                        heat_consumed[t] += (optimal_state[i][t+1] - optimal_state[i][t])*dt[t]/gen[i]['stor']['charge_eff']
                    else:
                        heat_consumed[t] -= (optimal_state[i][t] - optimal_state[i][t+1])*dt[t]*gen[i]['stor']['disch_eff']
            else:
                dispatch[i] = [0 for t in range(n_s)]
        else:
            dispatch[i] = [0 for t in range(n_s)]

    return dispatch, heat_consumed