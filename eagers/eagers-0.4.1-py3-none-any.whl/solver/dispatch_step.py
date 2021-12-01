from copy import copy, deepcopy

from eagers.solver.test_min_cases import test_min_cases
from eagers.basic.all_demands import all_demands, add_min_building_demand, subtract_renewable
from eagers.basic.constrain_min_max import constrain_min_max
from eagers.update.update_matrices_step import update_matrices_step
from eagers.basic.marginal_cost import net_marginal_cost
from eagers.basic.best_eff import best_eff


def dispatch_step(gen,observer, subnet, options, one_step, date, forecast, scale_cost, dt, first_profile, v_h):
    #creates step by step unit commitment for mcQP method such that N*2^G combinations are checked instead
    # of the full mixed integer approach where 2^(NG) combinations are checked and returns the generator
    #output for each step when optimized individually
    #inputs:
    #gen        - list of dictionaries that describes the components of the plant
    #observer   - current status of all generators, buildings, and fluid loops
    #subnet     - equipment at each node and connections between them
    #options    - user defined options
    #one_step   - instance of OneStep optimization matrices for individual timesteps
    #date       - timestamp for specific timesteps
    #forecast   - forecast for all timesteps
    #scale_cost - cost scale factors for all timesteps 
    #dt         - length of time for all timesteps
    #first_profile  - the dispatch from the previous dispatch horizon

    #OUTPUTS:
    #gen_output  - the solution for generator setpoints at all timesteps in horizon optimized individually
    #stor_power  - the power output of each storage device
    #binary_comb - all of the binary combinations of generators feasible at each time step
    #disp_comb   - the corresponding dispatch for each combination tested
    #cost        - the cost for each combination at each time step
    #verified    - whether a particular combination was tested or not
    #flt         - fluid loop temperature expected at each time step
    #bat         - building average temperature expected at each time step
    #flag        - errors

    # Flag values:
    #   0 -- Standard operation.
    #   1 -- No feasible combinations at one or more time steps.

    flag = 0
    flt = [j for j in observer['fluid_loop_temperature']]
    flc = observer['fluid_loop_capacitance']
    bat = [j for j in observer['building_avg_temp']]

    n_g = len(gen)
    n_s = len(date)-1 #gives number of rows
    gen_output = []
    
    ic = []
    for i in range(n_g):
        if 'Storage' in gen[i]['type']:
            ic.append(observer['stor_state'][i])
        else: 
            ic.append(observer['gen_state'][i])
        gen_output.append([ic[i]]) 
    stor_power = []
        
    i_best = []
    cost = []
    verified = []
    binary_comb = []
    disp_comb = []
    heating = []
    cooling = []
    build_temp = []
    fluid_temp = []
    
    limit = 'initially constrained'
    net_abbrev = [subnet[net]['abbreviation'] for net in subnet['network_names']]
    for t in range(n_s):
        demand = all_demands(forecast, subnet,[t])
        renewable = {}
        for j in range(len(gen)):
            if gen[j]['type'] in ['Solar','Wind']:
                renewable[gen[j]['name']] = forecast['renewable'][j][t]
        step_profile = [first_profile[i][t+1] for i in range(n_g)]
        prev_disp = [gen_output[i][t] for i in range(n_g)]
        sc = [[j[t]] if len(j)>0 else [] for j in scale_cost]
        
        stor_power.append(find_stor_power(gen,prev_disp,step_profile,dt[t]))
        marginal = net_marginal_cost(gen,net_abbrev,observer['market'],step_profile,sc,dt[t],any([v_h[n][t] for n in range(len(v_h))]))#update marginal cost
        fb = building_forecast_now(forecast['building'],t)
        min_power, max_power = constrain_min_max(gen, limit, ic, dt[t], sum(dt[0:t+1]))
        update_matrices_step(gen,observer['market'],subnet,options,one_step,fb,renewable,demand,sc,marginal,stor_power[t],dt[t],min_power, max_power,step_profile,flt,flc,bat)
        c_red = best_eff(gen,sc,marginal)  
        add_min_building_demand(forecast,subnet,demand,[t])
        subtract_renewable(renewable,subnet,demand)
        v, c, b_c, d_c,ht,cl,bt,ft = test_min_cases(one_step,gen,options,demand,c_red,step_profile,stor_power[t],dt[t])
        verified.append(v)
        cost.append(c)
        binary_comb.append(b_c)
        disp_comb.append(d_c)
        heating.append(ht)
        cooling.append(cl)
        build_temp.append(bt)
        fluid_temp.append(ft)
        if not any(verified[t]) or all([len(k)==0 for k in d_c]):
            flag = 1
            gen_output = first_profile
            print('no feasible combinations to test at step' +  str(t))
            return gen_output, stor_power, binary_comb, disp_comb, build_temp, fluid_temp, cost, verified, flag#ends the function here
        else:
            pass
            # print('Tested ' + str(sum(verified[t])) + ' combinations at step ' + str(t))
        # Update initial conditions and building temperatures.
        i_best.append(min(range(len(cost[t])), key=cost[t].__getitem__))

        best_dispatch = [j for j in d_c[i_best[t]]]
        bat = [j for j in bt[i_best[t]]]
        flt = [j for j in ft[i_best[t]]]
        disp_t = update_stor(gen,best_dispatch,prev_disp,dt[t],limit)#only updates the storage states in IC
        for i in range(n_g):
            gen_output[i].append(disp_t[i])
    return gen_output, stor_power, binary_comb, disp_comb, build_temp, fluid_temp, cost, verified, flag


def update_stor(gen, best_dispatch, prev_disp, dt, limit):
    disp_t = copy(best_dispatch)
    #update storage conditions
    n_g = len(gen)
    for i in range(n_g):
        if 'Storage' in gen[i]['type']:
            if gen[i]['type'] == 'HydroStorage':
                pass
            else:
                loss = (gen[i]['stor']['self_discharge']*gen[i]['stor']['usable_size'])
                if (disp_t[i] + loss) > 0: #discharging
                    d_soc = -(disp_t[i] + loss) * dt * gen[i]['stor']['disch_eff']
                else: #charging
                    d_soc = -(disp_t[i] + loss) * dt * gen[i]['stor']['charge_eff']   
                disp_t[i] = prev_disp[i] +d_soc
                if disp_t[i] < 0:
                    # print('Warning: '+gen[i]['name']+' is going negative by ' + str(disp_t[i]/gen[i]['stor']['usable_size']*100) +' %')
                    disp_t[i] = 0
                elif disp_t[i] > gen[i]['stor']['usable_size']:
                    # print('Warning: '+gen[i]['name']+' is exceeding max discharge by ' + str((disp_t[i]-gen[i]['stor']['usable_size'])/gen[i]['stor']['usable_size']*100) +' %')
                    disp_t[i] = gen[i]['stor']['usable_size']
    return disp_t


def find_stor_power(gen, ic, step_profile, dt):
    #find power from charging or discharging energy storage devices
    n_g = len(gen)
    stor_power =  []
    for i in range(n_g):
        if 'stor' in gen[i]:
            loss = gen[i]['stor']['self_discharge']*gen[i]['stor']['usable_size']
            d_soc = step_profile[i]-ic[i]
            if (d_soc/dt + loss)<0: #discharging
                stor_power.append(-(d_soc/dt + loss)*gen[i]['stor']['disch_eff'])
            else: #charging
                stor_power.append(-(d_soc/dt + loss)/gen[i]['stor']['charge_eff'])
        else:
            stor_power.append(None)
    return stor_power

def building_forecast_now(forecast,t):
    if forecast is None:
        fb = None
    else:
        fb = {}
        # n_b = len(fb['Cap'])
        fb['Cap'] = [i for i in forecast['Cap']]
        f_keys = ['E0','Discomfort','Tmin','Tmax','H2E','C2E','h_min','c_min','deadband','T_avg']
        for f in f_keys:
            fb[f] = copy(forecast[f][t])
        f_keys = ['th_bar','tc_bar','ua_c','ua_h']
        for f in f_keys:
            fb[f] = deepcopy(forecast[f][t])
    return fb
