"""Heuristics for minimizing generator startup costs.

Functions:
minimize_start_costs
update_storage
avoid_generation
find_case
move_generation
alt_generation
spare_storage_check
leave_gen_on
seg_length
slack_cap
stor_state
turndown_capacity
turndown_now
stor_add
test_more_cases
mp_test_more_cases
"""

from eagers.basic.gen_limit import gen_limit, chp_heat
from eagers.basic.marginal_cost import gen_marginal_cost, sort_mc, net_marginal_cost
from eagers.update.disable_gen import disable_gen
from eagers.solver.ecos_qp import ecos_qp
from eagers.solver.sort_solution import sort_gen_disp_step
from eagers.solver.dispatch_step import building_forecast_now
from eagers.basic.all_demands import all_demands
from eagers.basic.constrain_min_max import constrain_min_max
from eagers.update.update_matrices_step import update_matrices_step


def minimize_start_costs(qp, gen, market, subnet, options, forecast, first_profile, scale_cost, 
                        gen_output_w_starts, stor_power, binary_comb, disp_comb, build_temp, 
                        fluid_temp, cost_comb, verified, observer, dt, v_h):
    '''
    this function finds the unit commitment which minimizes startup costs, it relies on heuristic rules
    #the heuristic rules are present in the sub functions. It is called within dispatch_loop
    #this function finds the n shortest segments of time the generator is on/off, and compares the
    #startup cost to the alternative configuration that avoids the start or re-start
    
    #INPUTS:
    #qp         - dictionary which contains the optimization matrices
    #gen        - dictionary holding relevant information for all generation/load assets
    #market
    #subnet
    #options
    #forecast
    #first_profile  - dispatch from entire horizon optimization without lower bound constraints
    #scale_cost - list of scaling factors for fuel or electricity cost at ach time step
    #gen_output_w_starts - matrix of generator setpoints when timesteps are optimized individually
    #stor_power - power from storage components
    #binary_comb- list of identified feasible unit commitment combinations 
    #disp_comb  - Optimal setpoint for each unit commitment combination
    #cost_comb  -  cost for each combination
    #verified   - binary vector indicating if a combinations has been verified feasible
    #observer   - 
    #dt         - vector of length of each timestep
    #vh         - value heat from CHP generators
    

    #OUTPUTS:
    #gen_output - matrix of generator setpoints when timesteps are optimized individually, and startup cost is minimized
    #i_best     - 
    '''
    n_s = len(dt)
    n_g = len(gen)
    include = ['ElectricGenerator','CombinedHeatPower','Heater','Electrolyzer','HydrogenGenerator','CoolingTower','Chiller']
    skip_on = {'gen':[],'start':[],'stop':[],'duration':[]}
    skip_off = {'gen':[],'start':[],'stop':[],'duration':[]}
    locked = [[True for j in range(n_s+1)] for i in range(n_g)]
    max_start_cost = max([gen[k]['start_cost'] for k in range(n_g) if 'start_cost' in gen[k]])
    gen_output = [[i for i in j] for j in gen_output_w_starts]
    inc = [False for i in range(n_g)]
    for i in range(n_g):
        if gen[i]['type'] in include:
            locked[i] = [gen_output[i][t]>0 for t in range(n_s+1)]
            inc[i] = True
    if 'renewable' in forecast:
        for i in range(n_g):
            if len(forecast['renewable'][i])>0:
                for j in range(len(dt)):
                    gen_output[i][j+1] += forecast['renewable'][i][j]
    i_best = [min(range(len(cost_comb[t])), key=cost_comb[t].__getitem__)for t in range(n_s)] #find i_best(t), index that results in lowest cost once start-up is considered
    
    bat = [[j for j in observer['building_avg_temp']]]
    flt = [[j for j in observer['fluid_loop_temperature']]]
    flc = observer['fluid_loop_capacitance']
    
    bat.extend([build_temp[t][i_best[t]] for t in range(n_s)])
    flt.extend([fluid_temp[t][i_best[t]] for t in range(n_s)])

    seg = 1 #track the shortest ___ segments, currently set to 20. If fewer than 20 segments it ends early
    while seg < 20:
        #try and remove the shortest segment with generator on, and if there are multiple segments 
        #of equal length, start with highest startup cost.
        #if the segments are equal length and same generator, then start with the first segment
        on_seg, off_seg = seg_length(locked, gen, dt, skip_on, skip_off, inc)
        if on_seg['gen'] == [] and off_seg['gen'] == []:
            seg = float('inf')
        else:
            osl = len(on_seg['gen'])
            weighted_value = [on_seg['duration'][i]-gen[on_seg['gen'][i]]['start_cost']/(2*max_start_cost)+on_seg['start'][i]/n_s for i in range(osl)]
            weighted_value.extend([off_seg['duration'][i]-gen[off_seg['gen'][i]]['start_cost']/(2*max_start_cost)+off_seg['start'][i]/n_s for i in range(len(off_seg['gen']))])
            i_seg = min(range(len(weighted_value)), key=weighted_value.__getitem__)
            if i_seg<osl:
                k = on_seg['gen'][i_seg]
                t1 = on_seg['start'][i_seg]
                t2 = on_seg['stop'][i_seg]
                i_best, locked, no_alt, disp_comb, cost_comb, verified = alt_generation(
                    qp, gen, market, subnet, options, first_profile, stor_power, forecast, scale_cost,
                    i_best, k, t1, t2, binary_comb, disp_comb, cost_comb, verified, flt, flc, bat, gen_output, locked, dt, v_h)
                if no_alt:
                    #second, can it get close to the final storage capacity without this on-segment
                    binary_comb, disp_comb, cost_comb, verified, i_best, locked, must_replace = avoid_generation(
                        qp, gen, market, subnet, options, first_profile, stor_power, forecast, scale_cost,
                        i_best, k, t1, t2, binary_comb, disp_comb, cost_comb, verified, flt, flc, bat, gen_output, locked, dt, v_h)
                    if must_replace:
                        #third try moving generation earlier or later with same generator (if there is storage)
                        binary_comb, disp_comb, cost_comb, verified, i_best, locked, cant_move = move_generation(
                            qp, gen, market, subnet, options, first_profile, stor_power, forecast, scale_cost,
                            i_best, k, t1, t2, binary_comb, disp_comb, cost_comb, verified, flt, flc, bat, gen_output, locked, inc, dt, v_h) 
                        if cant_move:#add to list of segments to avoid
                            skip_on['gen'].append(on_seg['gen'][i_seg])
                            skip_on['start'].append(on_seg['start'][i_seg])
                            skip_on['stop'].append(on_seg['stop'][i_seg])
                            skip_on['duration'].append(on_seg['duration'][i_seg])
            else:
                i = i_seg - osl
                k = off_seg['gen'][i]
                t1 = off_seg['stop'][i]
                t2 = off_seg['start'][i]
                i_best, locked, cant_keep_on, disp_comb, cost_comb, verified = leave_gen_on(
                    qp, gen, market, subnet, options, first_profile, stor_power, forecast, scale_cost,
                     i_best, k, t1, t2, binary_comb, disp_comb, cost_comb, verified, flt, flc, bat, gen_output, locked, dt, v_h)
                if cant_keep_on:#add to list of segments to avoid
                    skip_off['gen'].append(off_seg['gen'][i])
                    skip_off['start'].append(off_seg['start'][i])
                    skip_off['stop'].append(off_seg['stop'][i])
                    skip_off['duration'].append(off_seg['duration'][i])
            update_gen_output(gen, gen_output, disp_comb, i_best, dt)
            seg = seg+1
    return gen_output, i_best


def update_gen_output(gen, gen_output, disp_comb, i_best, dt):
    #pull the corresponding best dispatches with the start-cost considered
    for t in range(len(dt)):
        status = [gen_output[i][t] for i in range(len(gen_output))]
        new_status = [j for j in disp_comb[t][i_best[t]]]
        for i in range(len(gen)):
            if gen[i]['type'] in ['ElectricStorage', 'ThermalStorage']:
                loss = gen[i]['stor']['self_discharge']*gen[i]['stor']['usable_size']
                if (new_status[i] +loss) > 0: #discharging
                    d_soc = -(new_status[i] + loss)*dt[t]/gen[i]['stor']['disch_eff']
                else: #charging
                    d_soc = -(new_status[i] + loss)*dt[t]*gen[i]['stor']['charge_eff']
                new_status[i] = max([min([status[i] + d_soc,gen[i]['stor']['usable_size']]),0])
        for i in range(len(gen_output)):
            gen_output[i][t+1] = new_status[i]


def avoid_generation(qp, gen, market, subnet, options, first_profile, stor_power, forecast, scale_cost, 
                    i_best, k, t1, t2, binary_comb, disp_comb, cost_comb, 
                    verified, flt, flc, bat, gen_output, locked, dt, v_h):
    #TODO validate for variable time steps
    '''
    Find the cheapest feasible alternative dispatch without this generator
    # only use generators that were on previously or will be on
    #look for enough slack in other generators to avoid the overdepleating
    #storage at the minimum and to get to the same final state
    '''
    from eagers.basic.component_output import eff_interp

    n_s = len(dt)
    must_replace = True
    cap = gen[k]['cap']
    eff = gen[k]['eff']
    stor_energy, _, stor, _, _ = stor_state(gen, gen_output, dt)
    out = None
    if gen[k]['type'] == 'Chiller':
        out = 'c'
    elif gen[k]['type'] == 'Heater':
        out = 'h'
    elif gen[k]['type'] in ('CombinedHeatPower', 'ElectricGenerator'):
        if 'dc' in stor:
            out = 'dc'
        elif 'e' in stor:
            out = 'e'
    #TODO add other dispatchable components
    if not out is None and out in stor and any([j>0 for j in stor_energy[out]]):
        _, _, spare_capacity, _ = gen_limit(gen, gen_output, locked, dt,[out])
        rmv_cost = 0
        margin_cost = gen_marginal_cost(gen, gen_output, scale_cost, dt)
        rem_gen = [0 for t in range(n_s)]
        rem_heat = [0 for t in range(n_s)]
        for t in range(t1,t2,1):
            #need to replace this energy in the storage by the end and 
            #replace enough early so that UsefulStoredEnergy - remStor + makeup does not go negative
            eff_t =eff_interp(cap,eff,gen_output[k][t+1])
            rem_gen[t:] = [rem_gen[tt] + gen_output[k][t+1]*dt[t] for tt in range(t,len(dt))]
            if gen[k]['type'] == 'CombinedHeatPower':
                rem_heat[t:] = [rem_heat[tt] + chp_heat(gen[k],[gen_output[k][t+1]])[0]*dt[t] for tt in range(t,len(dt))]
            rmv_cost += scale_cost[k][t+1]*gen_output[k][t+1]/eff_t*dt[t]
            if 'const_cost' in gen[k]:
                rmv_cost += gen[k]['const_cost'] * scale_cost[k][t+1] * dt[t]
            if gen[k]['type'] == 'Chiller' and 'electrical' in gen[k]['const_demand']:
                rmv_cost +=  (gen[k]['const_demand']['electrical'] + (gen_output[k][t+1]/eff_t))*min(margin_cost['e']['cost']['spin_reserve'][k][t])*dt[t]
        if gen[k]['type'] == 'CombinedHeatPower' and not 'h' in stor:
            stor_energy['h'] = [0 for j in range(n_s)]
            
        possible_to_avoid = True    
        if (sum(spare_capacity[out])+0.5*stor_energy[out][-1])<0: #it can reach at least half the planned final SOC
            possible_to_avoid = False
        for t in range(n_s):
            if (sum(spare_capacity[out][:t+1]) - sum(rem_gen[:t+1]))<-stor_energy[out][t]: #storage never lets the SOC dip below 0
                possible_to_avoid = False
            if gen[k]['type'] == 'CombinedHeatPower' and (sum(spare_capacity['h'][:t+1]) - sum(rem_heat[:t+1]))<-stor_energy['h'][t]:
                possible_to_avoid = False
        if possible_to_avoid:
            for t in range(t1,t2):
                new_comb = [locked[j][t+1] for j in range(len(locked))]
                new_comb[k] = False #turn off
                new_case = find_case(binary_comb[t], new_comb)#find indicies of all combinations that include locked[t+1,:]
                if not new_case is None:
                    if not verified[t][new_case]:
                        cost_comb[t], verified[t], disp_comb[t] = test_more_cases(
                            qp, [new_case], cost_comb[t], verified[t], disp_comb[t], stor_power[t], flt[t], flc, bat[t], binary_comb[t],
                            gen, market, subnet, options, first_profile, forecast, scale_cost, dt, t, any([v_h[n][t] for n in range(len(v_h))]))
                    if not cost_comb[t][new_case] == float('inf'):
                        i_best[t] = new_case
                    else:
                        possible_to_avoid = False
                else:
                    disp_comb[t].append([j for j in disp_comb[t][i_best[t]]])
                    binary_comb[t].append([j for j in binary_comb[t][i_best[t]]])
                    cost_comb[t].append(cost_comb[t][i_best[t]]-0.001) #make the other combos barely cheaper than the standard
                    verified[t].append(False)
                    i_best[t] = len(verified[t]) - 1 # -1 because it is an index
                    binary_comb[t][i_best[t]][k] = False #set output of this generator to zero
                    disp_comb[t][i_best[t]],exceeding_charge_limit = stor_add(gen, disp_comb[t][i_best[t]], -disp_comb[t][i_best[t]][k], k)
                    disp_comb[t][i_best[t]][k] = 0 #set output of this generator to zero
            if possible_to_avoid:
                must_replace = False
                for t in range(t1,t2):
                    locked[k][t+1] = False
        #try and replace the generation with the cheapest generation from any other spare capacity
        #otherwise storage at end of horizon drops
        if possible_to_avoid:
            #need to make up generation before storage would go negative
            t_limit = 0
            neg_stor = [j for j in range(n_s) if rem_gen[j]>stor_energy[out][j]]
            if len(neg_stor)>0:
                t_limit = neg_stor[0]
            else:
                t_limit = n_s
            make_up_gen = 0
            rem_e = max(rem_gen) #removed energy (maximum = sum of generator output that is turned off * dt)
            sorted_mc = sort_mc(margin_cost, out, t_limit, k, dt)
            if not sorted_mc is None and sorted_mc['cumulative_energy'][-1] >= rem_e:
                j = 0
                while sorted_mc['cumulative_energy'][j]<rem_e:
                    j+=1
                if j>0:
                    make_up_cost = sorted_mc['cumulative_cost'][j-1] + sorted_mc['marginal_cost'][j]*(rem_e - sorted_mc['cumulative_energy'][j-1])
                else:
                    make_up_cost = sorted_mc['marginal_cost'][0]*rem_e
                if (make_up_cost-rmv_cost)<gen[k]['start_cost']: #if spare_gen is less than start_cost
                    r=0
                    while make_up_gen<rem_e and r<len(sorted_mc['cumulative_energy'])-1:
                        t = int(sorted_mc['timestep'][r])
                        add_gen_energy = min([sorted_mc['capacity'][r]*dt[t],rem_e-make_up_gen])
                        disp_comb[t][i_best[t]][sorted_mc['generator'][r]] = disp_comb[t][i_best[t]][sorted_mc['generator'][r]] + add_gen_energy/dt[t]
                        #edit storage dispatch at this timestep so that update_storate_state works correctly
                        disp_comb[t][i_best[t]],exceeding_charge_limit = stor_add(gen, disp_comb[t][i_best[t]], add_gen_energy, k)
                        make_up_gen += (add_gen_energy - exceeding_charge_limit)
                        r+=1    
    return binary_comb, disp_comb, cost_comb, verified, i_best, locked, must_replace


def find_case(binary_comb,case):
    k = None
    for i in range(len(binary_comb)):
        if binary_comb[i] == case:
            k = i
            break
    return k


def move_generation(qp, gen, market, subnet, options, first_profile, stor_power,
    forecast,  scale_cost, i_best, k, t1, t2, binary_comb, 
    disp_comb, cost_comb, verified, flt, flc, bat, gen_output, locked, inc, dt, v_h):
    #TODO validate for variable timestep
    stor_energy, _, _, spare_stor_cap, _ = stor_state(gen, gen_output,dt)
    out = None
    if gen[k]['type'] in ['CombinedHeatPower','ElectricGenerator']:
        if 'dc' in stor_energy:
            out = 'dc'
        elif 'e' in stor_energy:
            out = 'e'
    elif gen[k]['type'] == 'Chiller':
        out = 'c'
    elif gen[k]['type'] == 'Heater':
        out = 'h'
    elif gen[k]['type'] == 'CoolingTower':
        out = 'cw'
    else: 
        out = None
    ##TODO add more dispatchable components

    n_s = len(disp_comb)
    cant_move = True
    i_best_alt = [j for j in i_best]

    if out in stor_energy and any([x>0 for x in stor_energy[out]]):
        add_stor = [0 for t in range(n_s)]
        rem_stor = [0 for t in range(n_s)]
        stops = [t for t in range(n_s) if not locked[k][t+1] and locked[k][t]]
        n= t2-t1 #number of steps generator is on for
        pre_stops = [j for j in stops if j<t1]
        if len(pre_stops)>0:
            #it was on previously, try to move earlier if storage permits
            t_stop = pre_stops[-1]
            #check if there is a feasible option to leave this generator on at earlier time steps
            for j in range(n):
                tj = t_stop+j
                opt = binary_comb[tj] #all feasible options tested at this time
                locked_now = opt[i_best_alt[tj]]
                locked_now[k] = True
                new_locked = find_case(opt,locked_now)
                if not new_locked is None:
                    if not verified[tj][new_locked]:
                        cost_comb[tj],verified[tj],disp_comb[tj] = test_more_cases(
                            qp,[new_locked],cost_comb[tj],verified[tj],disp_comb[tj], stor_power[tj], flt[tj], flc, bat[tj], opt,
                            gen, market, subnet, options, first_profile, forecast, scale_cost, dt, tj, any([v_h[n][tj] for n in range(len(v_h))]))
                        if not cost_comb[tj][new_locked] == float('inf'):
                            i_best_alt[tj] = new_locked
                for ts in range(t1-t_stop):
                    add_stor[t_stop+ts+j] += gen_output[k][t1+j+1]
            if not any([i_best_alt[ts] == i_best[ts] for ts in range(t_stop,t_stop+n)]) and all([add_stor[t]<spare_stor_cap[out][t] for t in range(n_s)]):
                cant_move = False
                for kg in inc:
                    for j in range(n):
                        locked[kg][t_stop+j+1] = binary_comb[t_stop+j][i_best_alt[t_stop+j]][kg]
                for t in range(t_stop+n,t2):
                    new_comb = [locked[j][t+1] for j in range(len(locked))]
                    new_comb[k] = False
                    new_case = find_case(opt,new_comb)
                    if not new_case is None:
                        if not verified[t][new_case]:
                            cost_comb[t],verified[t],disp_comb[t] = test_more_cases(
                                qp,[new_case],cost_comb[t],verified[t],disp_comb[t],stor_power[t], flt[t], flc, bat[t],binary_comb[t], 
                                gen, market, subnet, options, first_profile, forecast, scale_cost, dt, t, any([v_h[n][t] for n in range(len(v_h))]))
                        if not cost_comb[t][new_case] == float('inf'):
                            i_best_alt[t] = new_case
                        else:
                            cant_move = True
                    else:
                        disp_comb[t].append(disp_comb[t][i_best_alt[t]])
                        binary_comb[t].append(binary_comb[t][i_best_alt[t]])
                        cost_comb[t].append(cost_comb[t][i_best_alt[t]]-0.001) #make the other combos barely cheaper than the standard
                        verified[t].append(False)
                        i_best_alt[t] = len(verified[t]) - 1 # -1 because it is an index
                        disp_comb[t][i_best_alt[t]][k] = 0 #set output of this generator to zero
                        binary_comb[t][i_best_alt[t]][k] = False #set output of this generator to zero
                if not cant_move:
                    for t in range(t_stop+n,t2):
                        locked[k][t+1] = False
                    i_best = [j for j in i_best_alt]
                
        if cant_move:
            starts = [t for t in range(n_s) if locked[k][t+1] and not locked[k][t]]
            t_start = [j for j in starts if j>t2]
            if len(t_start) == 0:
                t_start = n_s -n
            else:
                t_start = t_start[0]-n
            for j in range(n):
                if t_start+j<n_s:
                    opt = binary_comb[t_start+j] #all feasible options tested at this time
                    locked_now = opt[i_best_alt[t_start+j]]
                    locked_now[k] = True
                    new_locked = find_case(opt,locked_now)
                    if not new_locked is None:
                        i_best_alt[t_start+j] = new_locked
                    #need to hold this shifted energy in the storage from the previous time the generator shut down until it had come on before     
                    for ts in range(t_start-t1-1):
                        rem_stor[t1+j+ts] += gen_output[k][t1+j+1]
            if not any([i_best_alt[ts] == i_best[ts] for ts in range(t_start,t_start+n)]) and all([rem_stor[t]>stor_energy[out][t] for t in range(n_s)]):
                i_best = [j for j in i_best_alt]
                for j in range(n):
                    for kg in inc:
                        locked[kg][t_start+j+1] = binary_comb[t_start+j][i_best[t_start+j]][inc]
                    disp_comb[t_start+j][i_best[t_start+j]][k] = gen_output[k][t1+j+1]
                for t in range(t1,t_start):
                    locked[k][t+1] = False
                    disp_comb[t][i_best[t]][k] = 0 #set output of this generator to zero
                cant_move = False

    return binary_comb, disp_comb, cost_comb, verified, i_best, locked, cant_move


def alt_generation(qp, gen, market, subnet, options, first_profile, stor_power,
    forecast, scale_cost, i_best, k, t1, t2, binary_comb, 
    disp_comb, cost_comb, verified, flt, flc, bat, gen_output, locked, dt, v_h):
    '''
    #determine any possible subsitute generators
    '''
    stor_energy, stor_gen_avail, _, _, _  = stor_state(gen, gen_output, dt)
    no_alt = True
    n_g = len(gen)
    inc = [False for i in range(n_g)]
    acdc = False
    for i in range(n_g):
        if gen[i]['type'] == 'ACDCConverter':
            acdc = True
            dc_ac = abs(gen[i]['output']['e'][0][-1])
            ac_dc = gen[i]['output']['dc'][0][0]
    if gen[k]['type'] == 'Chiller':
        out = 'c'
        for i in range(n_g):
            if gen[i]['type'] == 'Chiller' or (gen[i]['type'] == 'ThermalStorage' and gen[i]['source'] == 'cooling'):
                inc[i] = True
    if gen[k]['type'] == 'CoolingTower':
        out = 'cw'
        for i in range(n_g):
            if gen[i]['type'] == 'CoolingTower':
                inc[i] = True
    if gen[k]['type'] == 'Heater':
        out = 'h'
        for i in range(n_g):
            if gen[i]['type'] in ['Heater', 'CombinedHeatPower'] or (gen[i]['type'] == 'ThermalStorage' and gen[i]['source']=='heat'):
                inc[i] = True
    if gen[k]['type'] in ['CombinedHeatPower', 'ElectricGenerator']:
        if 'dc' in gen[k]['output']:
            out = 'dc'
        elif 'e' in gen[k]['output']:
            out = 'e'
        for i in range(n_g):
            if gen[i]['type'] in ['CombinedHeatPower', 'ElectricGenerator', 'ElectricStorage']:
                inc[i] = True
            if gen[k]['type'] == 'CombinedHeatPower' and (gen[i]['type'] == 'Heater' or (gen[i]['type'] == 'ThermalStorage' and gen[i]['source'] == 'heat')):
                inc[i] = True
    #TODO add other dispatchable components
    if not out in stor_energy:
        stor_energy[out] = [0 for t in range(len(dt))]
        stor_gen_avail[out] = [0 for t in range(len(dt))]
    if 'dc' in stor_energy and acdc and out == 'e':
        stor_energy['e'] = [stor_energy['e'][t] + stor_energy['dc'][t]*dc_ac for t in range(len(dt))]
        stor_gen_avail['e'] = [stor_gen_avail['e'][t] + stor_gen_avail['dc'][t]*dc_ac for t in range(len(dt))]
    elif 'e' in stor_energy and acdc and out == 'dc':
        stor_energy['dc'] = [stor_energy['e'][t] + stor_energy['dc'][t]*ac_dc for t in range(len(dt))]
        stor_gen_avail['dc'] = [stor_gen_avail['dc'][t] + stor_gen_avail['e'][t]*dc_ac for t in range(len(dt))]
    
    i_best_alt = [j for j in i_best]
    d_cost = [0 for t in range(t2-t1)]
    d_gen = [0 for t in range(t2-t1)]
    alt_locked = [[i for i in j] for j in locked]
    #for the time that the generator in question is on, try combinations that don't have it on
    for t in range(t1,t2,1):
        opt = binary_comb[t] #all options at this time
        #run all unverified cases that replace he generator in question with either 1 or 2 or 3 others that are:
        #a) running within (t2-t1) steps before/after and have a marginal cost less than starting the generator in question
        #b) have a marginal cost + start-up cost less than starting the generator in question
        need_test = []
        for c in range(len(opt)):
            if not verified[t][c] and not opt[c][k]:
                new_on = [i for i in range(n_g) if opt[c][i] and not opt[i_best[t]][i]]
                d_c = cost_comb[t][c] - cost_comb[t][i_best[t]]
                if len(new_on)<=3 and all([inc[j] for j in new_on]):
                    for j in range(len(new_on)):
                        if not any(locked[new_on[j]]):
                            d_c += gen[new_on[j]]['start_cost']
                    if d_c<gen[k]['start_cost']:
                        need_test.append(c)
        cost_comb[t], verified[t], disp_comb[t] = test_more_cases(
            qp, need_test, cost_comb[t], verified[t], disp_comb[t], stor_power[t], flt[t], flc, bat[t], opt,
            gen, market, subnet, options, first_profile, forecast,  scale_cost, dt, t, any([v_h[n][t] for n in range(len(v_h))]))

        #determine the marginal cost of switching to the best possible option that doesn't use the generator in question
        cost2 = []
        for c in range(len(cost_comb[t])):
            if opt[c][k] or not verified[t][c]:
                cost2.append(float('inf')) #make the cost infinite for all combinations with generator i or untested combinations
            else:
                cost2.append(cost_comb[t][c] - cost_comb[t][i_best[t]])#cost for these options
       
        frac_time = dt[t]/sum(dt[t1:t2])
        for j in range(n_g):
            if 'start_cost' in gen[j] and gen[j]['start_cost']>0:
                for c in range(len(cost2)):
                    if (not cost2[c] == float('inf') 
                        and (not any([locked[j][t] for t in range(t1,t2+2)]) and opt[c][j])
                        or (all([locked[j][t] for t in range(t1,t2+2)]) and not opt[c][j])):#would be adding a startup or a temporary shutdown
                        cost2[c] += gen[j]['start_cost']*frac_time 
        if not all([cost2[c] == float('inf') for c in range(len(cost2))]):
            i_best_alt[t] = min(range(len(cost2)), key=cost2.__getitem__)
            d_cost[t-t1] = cost2[i_best_alt[t]]
            d_gen[t-t1] = disp_comb[t][i_best[t]][k] - disp_comb[t][i_best_alt[t]][k]
            for i in range(n_g):
                alt_locked[i][t+1] = binary_comb[t][i_best_alt[t]][i]
        else:
            #no feasible combinations without turning on a different generator, so don't make changes to this segment
            d_cost = [float('inf')]
            break
    #if it wants to swap to have a different generator on now, don't constrain its maximum output by shutting it down immediately
    for i in range(n_g):
        if all([binary_comb[t][i_best_alt[t]][i] and not binary_comb[t][i_best[t]][i] for t in range(t1,t2,1)]) and gen[i]['start_cost']>0:
            alt_locked[i][t2:] = [True for j in range(len(alt_locked[i])-t2)]
    #check if the alternate operation strategy is feasible when put in sequence
    _,_,_,spare_gen = gen_limit(gen,gen_output,alt_locked,dt, [out])
    spare_storage = spare_storage_check(spare_gen[out][t1:t2],stor_gen_avail[out][t1:t2],stor_energy[out][t1:t2],dt[t1:t2])
    if sum(d_cost)<gen[k]['start_cost'] and spare_storage:
        spare_heat_storage = True
        if gen[k]['type'] == 'CombinedHeatPower' and 'h' in stor_energy:
            spare_heat_storage = spare_storage_check(spare_gen['h'][t1:t2],stor_gen_avail['h'][t1:t2],stor_energy['h'][t1:t2],dt[t1:t2])
        if spare_heat_storage:
            i_best = [j for j in i_best_alt] #use the alternative index
            for t in range(t1,t2,1):
                for i in range(n_g):
                    locked[i][t+1] = binary_comb[t][i_best[t]][i]
            no_alt = False
    return i_best, locked, no_alt, disp_comb, cost_comb, verified


def spare_storage_check(spare_gen,stor_gen,stored_energy,dt):
    spare_storage = True
    if any([(spare_gen[j]+stor_gen[j])<0 for j in range(len(spare_gen))]):
        spare_storage = False #there is insufficient spare capacity in the other generators & storage at any moment
    else:
        for i in range(len(spare_gen)):
            if sum([spare_gen[j]*dt[j] for j in range(i+1)])+stored_energy[i]<0:
                spare_storage = False #the cumulative loss of generation would deplete the storage
    return spare_storage


def leave_gen_on(qp, gen, market, subnet, options, first_profile, stor_power,
    forecast, scale_cost, i_best, k, t1, t2, binary_comb,
     disp_comb, cost_comb,  verified, flt, flc, bat, gen_output, locked, dt, v_h):
    '''
    find the cheapest feasible alternative dispatch that keeps this generator on
    only use generators that were on previously or will be on
    '''
    n_g = len(gen)
    _, _, _, spare_stor_cap, stor_slack_avail = stor_state(gen, gen_output, dt)
    out = None
    if gen[k]['type'] in ['CombinedHeatPower', 'ElectricGenerator']:
        if 'dc' in spare_stor_cap:
            out = 'dc'
        elif 'e' in spare_stor_cap:
            out = 'e'
        else:
            out = None
    elif gen[k]['type'] == 'Chiller':
        out = 'c'
    elif gen[k]['type'] == 'Heater':
        out = 'h'
    elif gen[k]['type'] == 'CoolingTower':
        out = 'cw'
    turndown = turndown_capacity(gen,gen_output,k)
    cant_keep_on = True
    #only allow generators that are on at beginning or end to be involved or that have smaller start-up cost
    i_best_alt = [j for j in i_best]
    has_changed = False
    d_cost = [0 for t in range(t2-t1)]
    d_gen = [0 for t in range(t2-t1)]
    slack_gen = [0 for t in range(t2-t1)]
    if t1 == 0:
        prev = [gen_output[i][0] for i in range(n_g)]
    else:
        prev = disp_comb[t1-1][i_best[t1-1]]
    for t in range(t1,t2,1):
        opt = binary_comb[t] #all feasible options tested at this time
        #run unverified cases that just add the generator in question
        locked_now = opt[i_best_alt[t]]
        locked_now[k] = True
        new_locked = find_case(opt,locked_now)
        if not new_locked is None:
            if not verified[t][new_locked]:
                cost_comb[t], verified[t], disp_comb[t] = test_more_cases(
                    qp, [new_locked], cost_comb[t], verified[t], disp_comb[t], stor_power[t], flt[t], flc, bat[t], opt,
                    gen, market, subnet, options, first_profile, forecast, scale_cost, dt, t, any([v_h[n][t] for n in range(len(v_h))]))
            if not cost_comb[t][new_locked] == float('inf'):
                i_best_alt[t] = new_locked
                has_changed = True
                d_cost[t-t1] = cost_comb[t][i_best_alt[t]]-cost_comb[t][i_best[t]]
                d_gen[t-t1], slack_gen[t-t1] = slack_cap(gen, disp_comb[t][i_best[t]], disp_comb[t][i_best_alt[t]], prev, k, sum(dt[t1:t+1]))
        else:
            #no feasible combinations keeping this generator active
            #don't make changes to this segment
            d_cost = [float('inf')]
            break
    if has_changed:
        useful1 = [0 for t in range(t2-t1)]
        useful2 = 0
        if out in spare_stor_cap:
            useful1 = stor_slack_avail[out][t1:t2]
            useful2 = min(spare_stor_cap[out][t1:])
        #sum of the marginal increase in cost is less than the start-up cost, there is spare capacity in the other generators and storage
        #and the cumulative loss of generation does not deplete the storage
        
        if sum(d_cost)<gen[k]['start_cost'] and all([d_gen[t]<(slack_gen[t]+useful1[t]/dt[t1+t]) for t in range(len(d_gen))]) and (sum(d_gen)-sum(slack_gen))<useful2+sum(turndown):
            i_best = [j for j in i_best_alt]
            for t in range(t1, t2, 1):
                #best alternative option tested at this time
                for i in range(n_g):
                    locked[i][t+1] = binary_comb[t][i_best[t]][i]
            cant_keep_on = False
    return i_best, locked, cant_keep_on, disp_comb, cost_comb, verified


def seg_length(locked, gen, dt, skip_on, skip_off, inc):
    on_seg = {'gen':[],'start':[],'stop':[],'duration':[]}
    off_seg = {'gen':[],'start':[],'stop':[],'duration':[]}
    def check_seg_list(gen_i,stop,start,skip_off):
        same = False
        for i in range(len(skip_off['gen'])):
            if skip_off['gen'][i] == gen_i and skip_off['stop'][i] == stop and skip_off['start'][i] == start:
                same = True
                break
        return same

    n_g = len(gen)
    n_s = len(dt)
     #find length of segments that a generator is on or off
    for i in range(n_g):
        if inc[i] and gen[i]['start_cost']>0 and sum(locked[i])<len(locked[i]):
            starts = [t for t in range(n_s) if locked[i][t+1] and not locked[i][t]]
            stops = [t for t in range(n_s) if not locked[i][t+1] and locked[i][t]]
            n_on = len(starts)
            n_off = len(stops)
            #only look at generators that turn both on and off during the window
            if n_on>0 and n_off>0:
                #generator is off for a segment
                if stops[0]<starts[0]:
                    if not check_seg_list(i,stops[0],starts[0],skip_off): 
                        off_seg['gen'].append(i)
                        off_seg['stop'].append(stops[0])
                        off_seg['start'].append(starts[0])
                        off_seg['duration'].append(sum(dt[stops[0]:starts[0]+1]))
                    del stops[0]
                    n_off -= 1
                j = 0
                while j<n_off:
                    #index of generator, start index, stop index, duration of segment
                    if not check_seg_list(i,stops[j],starts[j],skip_on): 
                        on_seg['gen'].append(i)
                        on_seg['start'].append(starts[j])
                        on_seg['stop'].append(stops[j])
                        on_seg['duration'].append(sum(dt[starts[j]:stops[j]+1]))
                    j+=1
                    if j<n_on: 
                        if not check_seg_list(i,stops[j-1],starts[j],skip_off): 
                            off_seg['gen'].append(i)
                            off_seg['stop'].append(stops[j-1])
                            off_seg['start'].append(starts[j])
                            off_seg['duration'].append(sum(dt[stops[j-1]:starts[j]+1]))
    return on_seg, off_seg


def slack_cap(gen, original, new, prev, k, dt):
    n_g = len(gen)
    d_gen = gen[k]['a']['lb'][-1]
    if gen[k]['type'] == 'Chiller':
        include = 'Chiller'
    elif gen[k]['type'] == 'Heater':
        include = 'Heater'
    elif gen[k]['type'] in ['CombinedHeatPower', 'ElectricGenerator']:
        include = ['CombinedHeatPower','ElectricGenerator']
    slack_gen = 0
    for i in range(n_g):
        if i!=k and gen[i]['type'] in include:
            if original[i]>0 and new[i]>0:
                slack_gen += min([original[i]-gen[i]['a']['lb'][-1], original[i]-(prev[i]-gen[i]['ramp']['b'][1]*dt)])# capacity to ramp down from the original set point is constrained by the ramp rate from the previous setpoint and the lower bound
            elif original[i]>0:
                slack_gen += original[i]
            elif new[i]>0:
                slack_gen -= new[i]
    return d_gen, slack_gen


def stor_state(gen, gen_output, dt):
    n_g = len(gen)
    n_s = len(dt)
    stored_energy = {}
    stor_gen_avail = {}
    spare_stor_cap = {}
    stor_slack_avail = {}
    stor = {}
    for i in range(n_g):
        if 'stor' in gen[i] and not gen[i]['type'] == 'HydroStorage':
            outs = list(gen[i]['output'].keys()) #find outputs of storage from possible outs
            for out in outs:
                if not out in stored_energy:
                    stored_energy[out] = [0 for t in range(n_s)]
                    stor_gen_avail[out] = [0 for t in range(n_s)]
                    spare_stor_cap[out] = [0 for t in range(n_s)]
                    stor_slack_avail[out] = [0 for t in range(n_s)]
                    stor[out] = []
                buff = 0
                if 'buffer' in gen[i]:
                    buff = gen[i]['stor']['usable_size']*(gen[i]['buffer']/100)
                for t in range(n_s):
                    stored_energy[out][t] += (gen_output[i][t+1]-buff)*gen[i]['stor']['disch_eff']
                    stor_gen_avail[out][t] += min([(gen_output[i][t+1]-buff)*gen[i]['stor']['disch_eff']/dt[t], gen[i]['stor']['peak_disch']])
                    spare_stor_cap[out][t] += (gen[i]['stor']['usable_size']-buff-gen_output[i][t+1]/gen[i]['stor']['charge_eff'])
                    stor_slack_avail[out][t] += min([(gen[i]['stor']['usable_size']-buff-gen_output[i][t+1])/(gen[i]['stor']['charge_eff']*dt[t]), gen[i]['stor']['peak_charge']])
                stor[out].append(i)
    return stored_energy, stor_gen_avail, stor, spare_stor_cap, stor_slack_avail


def turndown_capacity(gen,gen_output,k):
    n_g = len(gen)
    n_s = len(gen_output[0])-1
    turndown = [0 for i in range(n_s)]
    ac_dc = False
    for i in range(n_g):
        if gen[i]['type'] == 'ACDCConverter':
            ac_dc = True
    for i in range(n_g):
        if gen[k]['type'] in ['CombinedHeatPower','ElectricGenerator'] and gen[i]['type'] in ['CombinedHeatPower','ElectricGenerator']:
            out = gen[i]['output']
            if ac_dc or  ('dc' in out and 'dc' in gen[k]['output']) or ('e' in out and 'e' in gen[k]['output']):
                turndown = turndown_now(gen[i],gen_output[i],turndown) 
        elif gen[k]['type'] == 'Chiller' and gen[i]['type'] == 'Chiller':
            turndown = turndown_now(gen[i],gen_output[i],turndown) 
        elif gen[k]['type'] == 'Heater':
            if gen[i]['type'] == 'CombinedHeatPower':
                lb = turndown_now(gen[i],gen_output[i],'lb')  
                set_heat = chp_heat(gen[i],gen_output[i][1:])
                min_heat = chp_heat(gen[i],lb)
                turndown = [turndown[j] + max([0,set_heat[j] - min_heat[j]]) for j in range(n_s)]
            elif gen[i]['type'] == 'Heater':
                turndown = turndown_now(gen[i],gen_output[i],turndown)
        elif gen[k]['type'] == 'CoolingTower' and gen[i]['type'] == 'CoolingTower':
            turndown = turndown_now(gen[i],gen_output[i],turndown)  
    return turndown


def turndown_now(gen,output,turndown):
    n_s = len(output) - 1
    lb = []
    for t in range(n_s-1):
        s = gen['states'][1][0]
        lb.append(max([gen[s]['lb'][-1],output[t]-gen['ramp']['b'][1],output[t+2]-gen['ramp']['b'][1]]))
    lb.append(max([gen[s]['lb'][-1],output[t]-gen['ramp']['b'][1]]))
    if isinstance(turndown,list):
        turndown = [turndown[i] + max([0,output[i+1]-lb[i]]) for i in range(n_s)]
        return turndown
    else:
        return lb
        

def stor_add(gen, prev, add_gen, k):
    def stor_add2(gen,prev,add_gen):
        change = max(-gen['peak_disch']+prev, min(add_gen, gen['peak_charge']+prev))
        add_gen -= change
        dispatch = prev-change
        return dispatch,add_gen
    n_g = len(gen)
    dispatch = [j for j in prev]
    for i in range(n_g):
        if gen[k]['type'] == 'Chiller' and gen[i]['type'] == 'ThermalStorage' and gen[i]['source'] == 'cooling':
            dispatch[i],add_gen = stor_add2(gen[i]['stor'],prev[i],add_gen)
        if gen[k]['type'] == 'Heater' and gen[i]['type'] == 'ThermalStorage' and gen[i]['source'] == 'heat':
            dispatch[i],add_gen = stor_add2(gen[i]['stor'],prev[i],add_gen)
        if gen[k]['type'] in ['CombinedHeatPower', 'ElectricGenerator'] and gen[i]['type'] == 'ElectricStorage':
            dispatch[i],add_gen = stor_add2(gen[i]['stor'],prev[i],add_gen)
    return dispatch,add_gen


def test_more_cases(qp, need_test, cost_comb, verified, disp_comb, stor_power, flt, flc, bat, opt, gen, market, subnet, options, first_profile, forecast, scale_cost, dt, t, v_h):
    parallel = False
    if not need_test == []:
        n_g = len(gen)
        demand = all_demands(forecast, subnet,[t])
        net_abbrev = [subnet[net]['abbreviation'] for net in subnet['network_names']]
        step_profile = [first_profile[i][t+1] for i in range(n_g)]
        sc = [[j[t]] if len(j)>0 else [] for j in scale_cost]
        marginal = net_marginal_cost(gen,net_abbrev,market,step_profile,sc,dt[t],v_h)#update marginal cost
        fb = building_forecast_now(forecast['building'],t)
        renewable = {}
        for j in range(len(gen)):
            if gen[j]['type'] in ['Solar','Wind']:
                renewable[gen[j]['name']] = forecast['renewable'][j][t]
        min_power, max_power = constrain_min_max(gen, 'initially constrained', [first_profile[i][0] for i in range(n_g)], dt[t], sum(dt[0:t+1]))
        update_matrices_step(gen,market,subnet,options,qp,
            fb,renewable,demand,sc,marginal,stor_power,
            dt[t],min_power, max_power,step_profile,flt,flc,bat)

        if parallel:
            pass
            # cost_par= [cost_comb[n] for n in need_test]
            # disp_comb_par = [disp_comb[n] for n in need_test]
            # opt_par = [opt[n] for n in need_test]
            # qp_par = qp
            # with multiprocessing.Pool() as pool:
            #     #variables in n_test long list, acting as parfor in matlab
            #     a = pool.starmap(mp_test_more_cases,zip(cost_par,disp_comb_par, opt_par, qp_par))
            # unzip_a = zip(*a)
            # for n in need_test:
            #     cost_comb[n] = next(unzip_a)
            #     verified[n] = True
            #     disp_comb[n] = next(unzip_a)
        else:
            for c in need_test:
                disable_gen(qp, opt[c])
                x, flag1 = ecos_qp(qp['h'], qp['f'], qp['a'], qp['b'], qp['a_eq'], qp['b_eq'], qp['ub'], qp['lb'], qp['x_keep'], qp['r_keep'], qp['req_keep'])
                if flag1 == 0:
                    cost_comb[c] = sum([0.5 * x[i] * qp['h'][i] * x[i] + x[i] * qp['f'][i] for i in range(len(x))]) + sum([qp['const_cost'][j] * opt[c][j] for j in range(len(opt[c]))])
                    verified[c] = True
                    disp_comb[c] = sort_gen_disp_step(x, qp)
                else:
                    cost_comb[c] = float('inf')
    return cost_comb, verified, disp_comb


def mp_test_more_cases(cost_par, disp_comb_par, opt_par, qp):
    # Multiprocessing for test_more_cases
    disable_gen(qp, opt_par)
    x_par, flag1 = ecos_qp(qp['h'], qp['f'], qp['a'], qp['b'], qp['a_eq'], qp['b_eq'], qp['ub'], qp['lb'], qp['x_keep'], qp['r_keep'], qp['req_keep'])
    n_g = len(qp['const_cost'])
    if flag1 == 0:
        cost_par = sum([0.5*x_par[i]*qp['h'][i]*x_par[i] + x_par[i]*qp['f'] for i in range(len(x_par))]) + sum([qp['const_cost'][j] * opt_par[j] for j in range(n_g)])
        disp_comb_par = sort_gen_disp_step(x_par, qp)
    else:
        cost_par = float('inf')
    return [cost_par, disp_comb_par]
