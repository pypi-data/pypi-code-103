"""

Functions:
test_cases
disable_lb_from_group
cost_estimate
"""

from eagers.update.disable_gen import disable_gen
from eagers.solver.ecos_qp import ecos_qp
from eagers.solver.sort_solution import sort_gen_disp_step, sort_building_step, sort_eh
from eagers.solver.case_marginal import case_marginal


def test_cases(qp,gen,combinations,n_gen,c_red,stor_power,p_groups):
    n_g = len(gen)
    n_b = len(qp['organize']['building']['r'])
    n_l = len(qp['organize']['transmission'])
    n_fl = 0
    if 'cooling_water' in qp['organize']['balance']:
        n_fl = len(qp['organize']['balance']['cooling_water'])
    n_c = len(combinations)
    verified = [False for i in range(n_c)]
    cost = [float('nan') for i in range(n_c)]
    disp_comb = [[] for i in range(n_c)]
    heating = [[0 for j in range(n_b)] for i in range(n_c)]
    cooling =  [[0 for j in range(n_b)] for i in range(n_c)]
    build_temp = [[0 for j in range(n_b)] for i in range(n_c)]
    fluid_temp = [[0 for j in range(n_fl)] for i in range(n_c)]

    stor_abbrev = []
    stor_index = []
    for i in range(n_g):
        if 'stor' in gen[i]:
            f = list(gen[i]['output'].keys())
            if not f[0] in stor_abbrev:
                stor_abbrev.append(f[0])
            stor_index.append(i)
    if not stor_power is None:
        stor_offset = stor_power
    else:
        stor_offset = [0 for i in range(n_g)]

    test_more = True
    best_cost = float('inf')
    k = 0
    n = n_gen[0]
    while test_more:
        if cost[k]!=cost[k] or cost[k] < best_cost:
            disable_gen(qp, combinations[k])
            if not p_groups is None:
                for type_gen in p_groups:
                    if len(p_groups[type_gen])>0 and len(p_groups[type_gen][0])>1:
                        disable_lb_from_group(qp,combinations[k],p_groups[type_gen]) #If generators are grouped, disable the lb on generators 2-n in the most expensive active group
            x, flag1 = ecos_qp(qp['h'], qp['f'], qp['a'], qp['b'], qp['a_eq'], qp['b_eq'], qp['ub'], qp['lb'], qp['x_keep'], qp['r_keep'], qp['req_keep'])
            if flag1 == 0:
                cost[k] = sum([qp['const_cost'][i] for i in range(n_g) if combinations[k][i]])
                cost[k] += sum([0.5 * x[i]* qp['h'][i]*x[i] + x[i]*qp['f'][i] for i in range(len(x))])
                if cost[k] < best_cost:
                    best_cost = cost[k]
                sol_disp = sort_gen_disp_step(x, qp)
                stor_disch = [0 for i in range(n_g)]
                stor_pen = [0 for i in range(n_g)]
                sol_build = sort_building_step(x,qp)
                for si in stor_index:
                    s = qp['indices'][si][0][0]
                    stor_disch[si] = x[s]
                    stor_pen[si] = qp['h'][s]
                    sol_disp[si] += stor_offset[si]
                disp_comb[k] = sol_disp
                heating[k] = sol_build['heating']
                cooling[k] = sol_build['cooling']
                build_temp[k] = [x[qp['indices'][n_g+n_l+i][0][0]] for i in range(n_b)]
                fluid_temp[k] = [x[qp['indices'][n_g+n_l+n_b+i][0][0]] for i in range(n_fl)]
                eh = sort_eh(x, qp)
                if len(eh) == 0 or any([eh[i]>1e-1 for i in range(len(eh)) if isinstance(eh[i],(float,int))]):
                    v_h = False
                else:
                    v_h = True
                marginal = case_marginal(sol_disp,gen,qp,v_h)
                cost = cost_estimate(c_red,gen,cost,verified,marginal,stor_disch,stor_pen,stor_abbrev,combinations,k)
            else:
                cost[k] = float('inf')
            verified[k] = True
            

        test_more = False
        if k<n_c-1 and (n_gen[k+1]==n or n_gen[k+1]<=n_gen[0]+1):
            test_more = True
        elif k<n_c-1: #check if any possible cases with more generators could save money
            j = 1
            while k+j<n_c:
                if cost[k+j] != cost[k+j] or cost[k+j]<best_cost:
                    test_more = True
                    break
                j+=1
            n= n_gen[k+1]
        k += 1
        if all([j== float('inf') for j in cost]):
            print('no feasible solutions')
    return verified, cost,  disp_comb, heating, cooling,build_temp,fluid_temp

def disable_lb_from_group(qp,combination,groups):
    #If generators are grouped, disable the lb on generators 2-n in the most expensive active group
    if groups!=None:
        k = -1
        #find last group that has an active gen
        while k+1<len(groups) and any([j in combination for j in groups[k+1]]):
            k += 1
        if k>=0:
            #set lb on generators 2 through n to 0
            g = groups[k]
            for i in range(1,len(g)):
                states = qp['indices'][g[i]][0]
                qp['lb'][states[0]] = 0


def cost_estimate(c_red,gen,cost,verified,marginal,stor_disch,stor_pen,stor_abbrev,combinations,k):
    """Estimate the best achievable cost of an additional generator by adding
    its cost per kW at peak efficiency and subtracting the current marginal
    cost times the new generator's capacity at peak efficiency.
    """
    n_g = len(gen)
    d_cost = [0 for i in range(n_g)]
    stor_offset = {}
    stor_used = {}
    stor_cost = {}
    stor_avg_pen = {}
    for j in stor_abbrev:
        stor_used[j] = 0
        stor_cost[j] = 0
        stor_offset[j] = [0 for i in range(n_g)]
    for j in range(n_g):
        if c_red['p'][j]>0:
            d_cost[j] = - marginal[c_red['ab'][j]]*c_red['p'][j] + c_red['p'][j]*c_red['c'][j]/c_red['eff'][j]
        if stor_disch[j]>0:
            abbrev = list(gen[j]['output'].keys())[0]
            for i in range(n_g):
                if c_red['p'][i]>0:
                    if abbrev=='dc' and 'e' in gen[i]['output'] and gen[i]['output']['e'][0][0]>0:
                        abbrev2 = 'e'
                    elif abbrev=='e' and 'dc' in gen[i]['output'] and gen[i]['output']['dc'][0][0]>0:
                        abbrev2 = 'dc'
                    else:
                        abbrev2 = abbrev
                    if abbrev2 in gen[i]['output'] and gen[i]['output'][abbrev2][0][0]>0: #penalty can only be reduced by adding generators (of the correct type) if it was dawing power from the storage
                        gen_ub = gen[i]['ub']*gen[i]['output'][abbrev2][0][0]
                        stor_offset[abbrev][i] = min(stor_disch[j],gen_ub-stor_offset[abbrev][i]) #best case reduction in storage use

            stor_used[abbrev] += stor_disch[j]
            stor_cost[abbrev] += 0.5*stor_disch[j]**2*stor_pen[j]
    for abbrev in stor_abbrev:
        if stor_used[abbrev] == 0:
            stor_avg_pen[abbrev] = 0
        else:
            stor_avg_pen[abbrev] = stor_cost[abbrev]/(.5*stor_used[abbrev]**2)

    on_test = [i for i in range(len(combinations[k])) if combinations[k][i]]
    for i in range(len(combinations)):
        if not verified[i] and (cost[i] != cost[i] or cost[i]<cost[k]) and all([combinations[i][j] for j in on_test]):
            new_gen = [j for j in range(len(combinations[i])) if combinations[i][j] and not combinations[k][j]]
            # The worst best case scenario is closest to the actual best case scenario, hence using max.
            est_cost = cost[k] + sum([d_cost[j] for j in new_gen])
            for j  in stor_abbrev:
                x_new = max(0,stor_used[j]-sum([stor_offset[j][k] for k in new_gen])) #How much of the storage discharge can be offset by new generators
                pen_dif = stor_cost[j] - .5*x_new**2*stor_avg_pen[j] #difference in discharge penalty if new generators used to offset storage use
                est_cost -= pen_dif #savings by not discharging storage assets beyond expected point
            if cost[i] != cost[i]:
                cost[i] = est_cost
            else:
                cost[i] = max([cost[i],est_cost])
    return cost
