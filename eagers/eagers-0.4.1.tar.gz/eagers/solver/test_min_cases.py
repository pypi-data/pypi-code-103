"""Test cases with fewest number of generators, then sort others by
estimated cost.

Functions:
test_min_cases
build_cases
list_cases
validate_combinations
check_feas
group_gen
find_last_group
split_to_groups
find_avg_kWh_cost
"""

from eagers.extras import bplus_two_way_interp
from eagers.solver.test_cases import test_cases


def test_min_cases(qp, gen, options, demand, c_red, step_profile, stor_power, dt):
    """Test cases with fewest number of generators, then sort other by
    estimated cost.

    INPUTS:
    qp:             qp instance of quadratic programming matrices.
    gen:            List of generator objects.
    options:        Optimization options.
    demand:         Forecasted demand minus the forecasted renewable
                        generation plus the minimum building energy load.
    step_profile:  The first estimate of generator dispatch.
    dt:             Delta time vector.

    OUTPUTS:
    verified:       Which combination of unit commitment is verified
                        feasible.
    cost:           Vector of costs for each combination.
    combinations:      Unit commitment matrix.
    disp_comb:      
    """

    # TODO: Add parallel computing logic.
    parallel = False
    
    combinations,n_gen = build_cases(qp,gen,options,demand,step_profile,dt,c_red,stor_power,parallel)
    binary_comb = [[j>0 for j in combinations[i]] for i in range(len(combinations))]
    # if parallel and n_gen!=None:
    #     verified,cost,disp_comb,heating,cooling,build_temp,fluid_temp = test_cases_parallel(qp,gen,combinations,n_gen,c_red,stor_power,None)
    # elif n_gen!=None:
    verified,cost,disp_comb,heating,cooling,build_temp,fluid_temp = test_cases(qp,gen,combinations,n_gen,c_red,stor_power,None) 
    return verified,cost,binary_comb,disp_comb,heating,cooling,build_temp,fluid_temp


def build_cases(qp, gen, options, demand, step_profile, dt,c_red,stor_power,parallel):
    n_g = len(gen)
    always_on = []
    p_gen = {'e': [], 'h':[], 'c':[], 'cw':[], 'hy':[]}
    for i, g in enumerate(gen):
        if g['type'] in ['ElectricGenerator','CombinedHeatPower']:
            p_gen['e'].append(i)
        elif g['type'] == 'Heater':
            p_gen['h'].append(i)
        elif g['type'] in ['Chiller','AbsorptionChiller']:
            p_gen['c'].append(i)
        elif g['type'] in ['CoolingTower']:
            p_gen['cw'].append(i)
        elif g['type'] in ['HydrogenGenerator','Electrolyzer',]:
            p_gen['hy'].append(i)
        elif qp['organize']['enabled'][i]:
            always_on.append(i)
    l_type = [len(p_gen[k]) for k in p_gen]
    if any([x>4 for x in l_type]) and sum(l_type)>8:
        combinations,n_gen = group_gen(p_gen,always_on,qp,gen,options,demand,step_profile,dt,c_red,stor_power,parallel)
    else:
        combinations,n_gen = list_cases(p_gen,always_on,n_g) #a matrix of all the possible generator on/off combinations
        validate_combinations(combinations,n_gen,qp,gen,options,demand,step_profile,dt)
    return combinations, n_gen

def list_cases(p_gen,always_on,n_g):
    def mult_list(val):
        ans = 1
        for k in val:
            ans *= k
        return ans
    def binary_dispatchable(comb,k,z):
        r = 0
        while r+z <= len(comb):
            for rc in range(r,r+z):
                comb[rc][k] = True
            r += 2*z
        return comb
    def group_dispatchable(comb,k,z):
        r = 0
        n = len(k)
        while r+n*z <= len(comb):
            r+=z
            r_last = r+n*z
            for j in k:
                for rc in range(r,r_last):
                    for i in j:
                        comb[rc][i] = True
                r += z
        return comb
    c_mult =[]
    for type_gen in p_gen:
        g_list = p_gen[type_gen]
        if len(g_list)>0:
            if isinstance(g_list[0], (float,int)) or len(g_list[0])==1: #unsorted components test all combinations
                c_mult.extend([2 for i in range(len(g_list))])
            else: #sorted sequence
                c_mult.append(len(g_list)+1)
    c_len = mult_list(c_mult)
    base = [False for j in range(n_g)]
    for k in always_on:
        base[k] = True
    combinations = [[j for j in base] for i in range(c_len)]

    e = 1
    for type_gen in p_gen:
        g_list = p_gen[type_gen]
        if len(g_list)>0:
            if isinstance(g_list[0], list) and len(g_list[0])==1:
                g_list = [g[0] for g in g_list]
            if isinstance(g_list[0], (float,int)):
                for k in range(len(g_list)):
                    z = mult_list(c_mult[k+e:])
                    combinations = binary_dispatchable(combinations,g_list[k],z)
                e += len(g_list)
            else:
                z = mult_list(c_mult[e:])
                combinations = group_dispatchable(combinations,g_list,z)
                e += 1
     
    active_gen = [sum(combinations[i])-len(always_on) for i in range(c_len)]
    reorder = sorted(range(len(active_gen)), key=lambda k: active_gen[k])
    n_gen = [active_gen[i] for i in reorder]
    sorted_comb = [combinations[i] for i in reorder]
    return sorted_comb, n_gen

def validate_combinations(combinations, n_gen, qp, gen, options, demand, step_profile, dt):
    #TODO validate with node based loads and transmission limits
    ac_dc = None
    for i in range(len(gen)):
        if gen[i]['type'] == 'ACDCConverter':
            ac_dc = i
            break
    for net in list(qp['organize']['balance'].keys()):
        gen_dem = 0
        if net in demand:
            gen_dem = sum(demand[net][k] for k in demand[net])
        r_eq = qp['organize']['balance'][net] #rows of Aeq associated with electric demand

        min_prod, max_prod = check_feas(gen, qp, r_eq, step_profile, dt, net)
        if net in ['electrical','direct_current'] and not ac_dc is None:
             min_prod[i], max_prod[i] = ac_dc_prod(net, qp, r_eq[gen[ac_dc]['subnet_node'][net]], qp['indices'][ac_dc][0], ac_dc, gen, step_profile, dt)
        # Keep the rows where the ub is capable of meeting demand and
        # the lower bound is low enough to meet demand.
        r = 0
        while r<len(combinations):
            del_row = False
            if (net == 'district_heat' and options['excess_heat']) or (net == 'district_cool' and options['excess_cool']):
                pass #no lower bound constraint
            elif sum([min_prod[k] for k in range(len(gen)) if combinations[r][k]]) > gen_dem:
                del_row = True
            if del_row or sum([max_prod[k] for k in range(len(gen)) if combinations[r][k]]) < gen_dem:
                del combinations[r]
                del n_gen[r]
            else:
                r+=1
        if len(combinations)==0:
            print('Zero feasible test combinations')
    # return combinations, n_gen

def check_feas(gen, qp, r_eq, step_profile, dt, net):
    """Returns the minimum and maximum production on the network
    specified by net, for each combination of generators.
    """
    n_g = len(gen)
    min_prod = [0] * n_g
    max_prod = [0] * n_g

    for i, g in enumerate(gen):
        states = qp['indices'][i][0]
        if not states is None and net in gen[i]['subnet_node']: #any([any([qp['a_eq'][r][s]!=0 for s in states]) for r in r_eq]): #2nd condition checks for qp.a_eq at index [r_eq,states] != 0
            row_i = r_eq[gen[i]['subnet_node'][net]]
            if gen[i]['type'] == 'Utility':
                if len(states) == 2:
                    min_prod[i] = qp['a_eq'][row_i][states[1]]* qp['ub'][states[1]]
                    max_prod[i] = qp['a_eq'][row_i][states[0]]* qp['ub'][states[0]]
                else:
                    min_prod[i] = qp['a_eq'][row_i][states[0]] * qp['lb'][states[0]]
                    max_prod[i] = qp['a_eq'][row_i][states[0]] * qp['ub'][states[0]]
            elif 'Storage' in g['type']:
                s = states[0]
                min_prod[i] = -g['ramp']['b'][0]
                max_prod[i] = g['ramp']['b'][1]
                if step_profile is not None:
                    max_prod[i] = min([step_profile[i] * qp['a_eq'][row_i][s] / dt, max_prod[i]]) 
                    charging_space = (g['stor']['usable_size'] -step_profile[i])* qp['a_eq'][row_i][s]
                    min_prod[i] = max([-charging_space/dt, min_prod[i]])
            elif gen[i]['type'] == 'ACDCConverter':
                continue #done later
            elif gen[i]['type'] in ['ElectricGenerator','CombinedHeatPower','Heater','Chiller','AbsorptionChiller','CoolingTower','HydrogenGenerator','Electrolyzer']:
                if qp['a_eq'][row_i][states[0]] > 0:
                    min_prod[i] = sum([qp['a_eq'][row_i][s] * qp['lb'][s] for s in states])
                    max_prod[i] = sum([qp['a_eq'][row_i][s] * qp['ub'][s] for s in states])
                else:
                    # If it consumes this demand (i.e. a chiller when examining electrical demand) then the lower bound is -1*ub.
                    min_prod[i] = sum([qp['a_eq'][row_i][s] * qp['ub'][s] for s in states])
                    max_prod[i] = sum([qp['a_eq'][row_i][s] * qp['lb'][s] for s in states])
            if 'const_demand' in gen[i] and net in gen[i]['const_demand']:
                max_prod[i] -= gen[i]['const_demand'][net]
                min_prod[i] -= gen[i]['const_demand'][net]
    return min_prod, max_prod

def ac_dc_prod(net, qp, row, states, ac_dc, gen, step_profile, dt):
    if net == 'electrical':
        row_dc = qp['organize']['balance']['direct_current']
        _, max_prod_dc = check_feas(gen, qp, row_dc, step_profile, dt,'direct_current')
        tot_dc = sum([max_prod_dc[k] for k in range(len(gen))])
        # Capacity to convert AC to DC power.
        min_prod = -gen[ac_dc]['a']['ub']
        # Pull out the DC/AC conversion efficiency.
        max_prod = abs(qp['a_eq'][row][states[-1]]) * tot_dc
    elif net == 'direct_current':
        # Need only the row corresponding to the node that this generator is on.
        row_ac = qp['organize']['balance']['electrical']
        _, max_prod_ac = check_feas(gen, qp, row_ac, step_profile, dt,'electrical')
        tot_ac = sum([max_prod_ac[k] for k in range(len(gen))])
        # Capacity to convert DC to AC power.
        if 'b' in gen[ac_dc]:
            min_prod = -gen[ac_dc]['b']['ub']
        else:
            min_prod = gen[ac_dc]['a']['lb']
        # Pull out the AC/DC conversion efficiency.
        max_prod = qp['a_eq'][row][states[0]] * tot_ac
    return min_prod, max_prod

def group_gen(p_gen,always_on,qp,gen,options,demand,step_profile,dt,c_red,stor_power,parallel):
    ## with more than 1000 combinations, group generators to reduce the search parameters

    #group by similar average cost per kW by taking samples across range
    #when testing, the lower limit of the most expensive group gets set to
    #zero, except for the smallest lower limit in the group
    #non-electric generators (chillers) don't get grouped
    p_groups = {}
    for type_gen in p_gen:
        g_list = p_gen[type_gen]
        if len(g_list)>4:
            avg_cost_kWh = []
            for k in g_list:
                states = qp['indices'][k][0]
                h_gen = [qp['h'][s] for s in states]
                avg_cost_kWh.append(find_avg_kWh_cost(h_gen,[qp['f'][s] for s in states],[qp['lb'][s] for s in states],[qp['ub'][s] for s in states],qp['const_cost'][k],gen[k],c_red['c'][k]))
            
            gen_index = sorted(range(len(avg_cost_kWh)), key=lambda k: avg_cost_kWh[k])
            sorted_gen = [g_list[i] for i in gen_index]
            p_groups[type_gen] = split_to_groups(sorted_gen)
        else:
            p_groups[type_gen] = split_to_groups(g_list)

    #create cases with a) group 1, b) group 1 & 2, c) group 1 & 2 & 3 ....
    combinations,n_gen = list_cases(p_groups,always_on,len(gen)) #a matrix of all the possible generator on/off combinations
    validate_combinations(combinations,n_gen,qp,gen,options,demand,step_profile,dt)
    ## TODO add parallel computing for test_cases
    # if parallel and len(n_gen)>0
    #     _,cost,_,_,_,_,_  = test_cases_parallel(qp,gen,combinations,n_gen,c_red,p_groups)
    # elif  len(n_gen)>0
    _,cost,_,_,_,_,_ = test_cases(qp,gen,combinations,n_gen,c_red,stor_power,p_groups)

    #Find group that is on the bubble
    best_combo = combinations[min(range(len(cost)), key=cost.__getitem__)]
    for k in list(p_gen.keys()):
        if len(p_gen[k])>4:
            p_gen[k], always_on  = find_last_group(best_combo,p_groups[k],always_on)    
    
    #Break apart this group and make combinations based only on it
    combinations,n_gen= list_cases(p_gen,always_on,len(gen)) #a matrix of all the possible generator on/off combinations
    validate_combinations(combinations,n_gen,qp,gen,options,demand,step_profile,dt)
    return  combinations,n_gen


def find_last_group(best_combo,groups,always_on):
    #find last group that has an active gen
    k = 0
    while k<len(groups)-1 and any([best_combo[j] is True for j in groups[k+1]]):
        if k>0:
            always_on.extend(groups[k-1]) #cheaper generators are held on
        k +=1
    obj_list = []
    if k>0:
        obj_list.extend(groups[k-1])
    obj_list.extend(groups[k])
    return obj_list, always_on


def split_to_groups(obj_list):
    #split into groups
    n_inc = len(obj_list)
    if n_inc<=4:
        groups = [[x] for x in obj_list]
        # groups = obj_list
    elif n_inc<=6:
        # groups = [obj_list[:2],obj_list[2:4],obj_list[4:]]
        groups = [obj_list[:3],obj_list[3:]]
    else:
        n = 4
        n_group = round(n_inc/n)
        groups =[]
        for i in range(n_group):
            if (i+1)*n>n_inc:
                groups.append(obj_list[i*n:])
            else:
                groups.append(obj_list[i*n:(i+1)*n])
    return groups


def find_avg_kWh_cost(H,f,lb,ub,const,gen,min_load_cost):
    n = 10
    cost_kWh = []
    max_p = sum(ub)
    capacity = [lb[0]+i*(max_p-lb[0])/(n-1) for i in range(n)]
    if all([H[j]== 0 for j in range(len(H))]) and all([f[j]== 0 for j in range(len(H))]):
        load = True
    else:
        load = False
    if capacity[0] == 0:
        del capacity[0]
        n -=1
    for i in range(n):
        j = 0
        p = 0
        cost = const
        cap = capacity[i]
        while p<cap and j<len(ub):
            x = min(cap-p,ub[j])
            if load:
                eff = bplus_two_way_interp(p+x, gen['cap'], gen['eff'])
                cost += x*min_load_cost/eff
            else:
                cost += x**2*H[j] + x*f[j]
            p = p+x
            j = j+1
        cost_kWh.append(cost/capacity[i])
    avg_cost_kWh = sum(cost_kWh)/n
    return avg_cost_kWh
