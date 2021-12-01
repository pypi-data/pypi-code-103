"""Update matrices.

Functions:
update_matrices
update_mat_demand
update_mat_costs
update_mat_build
update_mat_renew
update_mat_hydro
update_mat_sr
update_mat_market
"""


def update_matrices(gen, observer, subnet, options, qp, date, scale_cost,
        margin_cost, forecast, ec):
    """gen is the set of generators in the project
    building is the set of buildings in the project
    fluid_loop is the set of fluid loops, e.g. cooling tower water loop
    subnet is the agregated networks
    options are the optimization options
    qp is the optimization problem 
    date is the vector of time steps
    scale_cost is the matrix multiplier of cost for each generator at each time step
    margin_cost is the marginal cost of generation (used in the final value of the energy storage)
    forecast is the forecasted loads
    ec is the end condition for the threshold optimization"""
    
    #copy the default vectors
    qp['h'] = [i for i in qp['nom_vectors']['h']]
    qp['f'] = [i for i in qp['nom_vectors']['f']]
    qp['b'] = [i for i in qp['nom_vectors']['b']]
    qp['b_eq'] = [i for i in qp['nom_vectors']['b_eq']]
    qp['lb'] = [i for i in qp['nom_vectors']['lb']]
    qp['ub'] = [i for i in qp['nom_vectors']['ub']]
    qp['const_cost'] = [i for i in qp['nom_vectors']['const_cost']]

    n_g = len(gen)
    n_b = len(observer['building_avg_temp'])
    dt = [(date[t+1] - date[t]).total_seconds()/3600 for t in range(len(date)-1)]
    n_s = len(dt)
    n_l = len(qp['organize']['transmission'])
    n_fl = len(observer['fluid_loop_temperature'])

    #update initial condition
    for i in range(n_g):
        if 'enabled' in gen[i] and not gen[i]['enabled']:
            qp['organize']['enabled'][i] = False
        ic = None
        if gen[i]['type'] in ['ElectricGenerator','CombinedHeatPower','Chiller','Heater','Electolyzer','HydrogenGenerator','CoolingTower']:
            ic = observer['gen_state'][i]
        elif gen[i]['type'] in ['ElectricStorage','ThermalStorage','HydrogenStorage']:
            ic = observer['stor_state'][i]
        elif gen[i]['type'] == 'HydroStorage':
            ic = observer['stor_state'][i]
        if ic != None: #generators and storage devices
            qp['b_eq'][qp['organize']['ic'][i]] = ic
            qp['ub'][qp['organize']['ic'][i]] = ic+1 #+1 just to help solver find feasible
    for i in range(n_fl):
        qp['b_eq'][qp['organize']['ic'][n_g+n_l+n_b+i]] = observer['fluid_loop_temperature'][i]
        qp['ub'][qp['organize']['ic'][n_g+n_l+n_b+i]] = observer['fluid_loop_temperature'][i]+1 #+1 just to help solver find feasible
    
    update_mat_demand(qp, gen, subnet, forecast, n_s)
    update_mat_costs(qp, gen, margin_cost, scale_cost, ec, dt)
    update_mat_build(qp, observer, forecast['building'], dt)
    if 'renewable' in forecast: # subtract renewable generation 
        update_mat_renew(qp, gen, forecast)
    if 'hydro' in subnet['network_names']:
        update_mat_hydro(qp, gen, observer, subnet, forecast, date)
    if options['spin_reserve']:
        update_mat_sr(qp, options, forecast, dt, n_g)


def update_mat_demand(qp, gen, subnet, forecast, n_s):
    """Update demands and storage self-discharge."""
    g_names = [gen[i]['name'] for i in range(len(gen))]
    for net in subnet['network_names']:
        abbrev = subnet[net]['abbreviation']
        for an in range(len(subnet[net]['nodes'])):#run through all the nodes in this network
            for node in subnet[net]['nodes'][an]: #run through aggregated nodes
                if node in forecast and 'demand' in forecast[node]:# Multiple demands can be at the same node, or none.
                    for t in range(n_s):
                        r_eq = qp['organize']['balance'][net][an][t] #balance at this node
                        qp['b_eq'][r_eq] += forecast[node]['demand'][t]
            for name in subnet[net]['equipment'][an]:  #equipment at this node:
                k = g_names.index(name)
                if 'Storage' in gen[k]['type'] and abbrev in gen[k]['output']:   #if gen[k]['type'] in ['ElectricStorage','ThermalStorage','HydrogenStorage','HydroStorage']:
                    loss = gen[k]['stor']['self_discharge']*gen[k]['stor']['usable_size']*gen[k]['stor']['disch_eff']
                    for t in range(n_s):
                        r_eq = qp['organize']['balance'][net][an][t] #balance at this node
                        qp['b_eq'][r_eq] += loss #account for self-discharge losses


def update_mat_costs(qp, gen, margin_cost, scale_cost, ec, dt):
    """update costs"""
    n_g = len(gen)
    n_s = len(dt)
    for i in range(n_g):
        if not qp['indices'][i][1][0] is None:
            if gen[i]['type'] == 'Utility':
                for t in range(n_s):
                    s = qp['indices'][i][t+1]
                    if len(s)>0:
                        qp['f'][s[0]] *= scale_cost[i][t]*dt[t]
                    if len(s)>1 and gen[i]['sellback_rate'] == -1:
                        qp['f'][s[1]] *= scale_cost[i][t]*dt[t] #sellback is a fixed percent of purchase costs (percent set when building matrices)
                    else:
                        pass #gas utility or constant sellback rate was taken care of when building the matrices
            if gen[i]['type'] in ['ElectricGenerator', 'CombinedHeatPower', 'Chiller', 'Heater', 'HydrogenGenerator', 'CoolingTower', 'Electrolyzer']: #all generators 
                for t in range(n_s):
                    states = qp['indices'][i][t+1]
                    for s in states:
                        qp['h'][s] *= scale_cost[i][t]*dt[t]
                        qp['f'][s] *= scale_cost[i][t]*dt[t]
            if gen[i]['type'] in ['Storage', 'ElectricStorage', 'ThermalStorage','HydrogenStorage','HydroStorage']:
                S = list(gen[i]['output'].keys())
                est_perc_saved_by_storage_over_horizon = 0 #0.01  ## add to storage attributes or generator loading (tunable parameter?)
                val_per_kWh_per_hr = est_perc_saved_by_storage_over_horizon*(margin_cost[S[0]]['max']+margin_cost[S[0]]['min'])/2/sum(dt)
                declining_utility = [1 - t/(len(dt)-1) for t in range(len(dt))]
                if gen[i]['type'] == 'HydroStorage':
                    ss = 1#SOC is second state
                else:
                    ss = 0
                s_end = qp['indices'][i][-1][ss] 
                for t in range(n_s):
                    qp['f'][qp['indices'][i][t+1][ss]] = -val_per_kWh_per_hr*dt[t]*declining_utility[t]
                stor_size = gen[i]['stor']['usable_size']
                if 'u' in gen[i]: #has buffer
                    buff_size = gen[i]['u']['ub']
                else:
                    buff_size = 0    
                if not ec: #full forecast optimization
                    
                    max_value = 1.25*margin_cost[S[0]]['max']
                    min_value = 0.5*margin_cost[S[0]]['min']
                    a1 = -max_value # fitting C = a1*SOC + 0.5*a2*SOC^2 so that dC/dSOC @ 0 = -max & dC/dSOC @ UB = -min
                    a2 = (max_value - min_value)/(stor_size)
                    qp['h'][s_end] = a2 #quadratic final value term loaded into SOC(t=nS)  #quadprog its solving C = 0.5*x'*H*x + f'*x
                    qp['f'][s_end] = a1 #linear final value term loaded into SOC(t=nS)
                    if buff_size>0:
                        for t in range(n_s):
                            su = qp['indices'][i][t+1][-2] #upper buffer state
                            qp['f'][su] = min_value #this is the linear buffer term loaded into the lower & upper buffer
                            qp['h'][su] = (2*max_value-min_value)/buff_size #this is the quadratic buffer term loaded into the lower & upper buffer
                            qp['f'][su+1] = min_value #this is the linear buffer term loaded into the lower & upper buffer
                            qp['h'][su+1] = (2*max_value-min_value)/buff_size #this is the quadratic buffer term loaded into the lower & upper buffer
                else: #used in Online loop when there is a target EC determined by dispatch loop
                    pass
                    #final SOC deviation cost (quadratic cost for error = SOC(end) - EC
                        # if gen[i]['type'] == 'ElectricStorage':
                        #     e_type = 'electrical' 
                        # elif gen[i]['type'] == 'ThermalStorage':
                        #     if gen[i]['source'] == 'heat':
                        #         e_type = 'district_heat' 
                        #     else:
                        #         e_type = 'district_cool' 
                        # elif gen[i]['type'] == 'HydroStorage:
                        #     e_type = 'hydro' 
                        # rows = qp['organize']['inequalities'][i]
                        # n_r = len(qp['indices'][i][1])/n_s
                        # peak_charge_power = gen[i]['ramp']['b'][0]
                        # d_SOC_10_perc = .1*peak_charge_power*(date[-1]-date[0]).seconds/3600  #energy (kWh) if charging at 10#
                        # h[s_end] = -2*min(margin_cost[e_type])/d_SOC_10_perc #quadratic final value term loaded into SOC(t=nS)  #factor of 2 because its solving C = 0.5*x'*H*x + f'*x
                        # qp['f'](s_end) = -min(margin_cost[e_type]) #linear final value term loaded into SOC(t=nS)
                        # n_ic = 0
                        # for j in range(i):
                        #     if len(qp['organize']['ic'])>0:
                        #         n_ic +=1  #order in IC
                        # qp['b_eq'][n_ic] = ic[I]-ec[I]
                        # for t in range(n_s):
                        #     x_n = states[(t-1)*n_t+1] 
                        #     Rn = rows[t*n_r]
                        #     qp['lb'][Xn] = -ec[i] #change lb so that SOC = 0 coresponds to EC
                        #     qp['ub'][Xn] = stor_size - ec[i] #change ub so that SOC = 0 coresponds to EC
                        #     qp['b'][Rn-1] = -buff_size + ec[i] #change lb so that SOC = 0 coresponds to EC (adding EC because there is a -1 in front of SOC in this inequality)
                        #     qp['b'][Rn] = stor_size-buff_size - ec[i] #change lb so that SOC = 0 coresponds to EC          


def update_mat_build(qp, observer, fb, dt):
    # Within the optimization 5 states are used for a building:
    # #1 represents the air zone temperature setpoint
    # #2 represents the heating required to achieve that zone temperature setpoint
    # #3 represents the cooling required to achieve that zone temperature setpoint
    # #4 represents the temperature in excess of a comfort range (this is penalized)
    # #5 represents the temperature below a comfort range (this is penalized)

    # Building load appears in node equality equation (electric/heating/cooling)
    # 8 inequalities per building:
        #heating: 
            #heating inequality 1 additional heating at lower temp# H>=  UAl*(Th_barl - Ti) + Cap*(Ti - T(i-1))/dt where dt is in seconds
            #heating inequality 2 additional heating at higher temp# H>=  UAi*(Ti-Th_bari) + Cap*(Ti - T(i-1))/dt where dt is in seconds
            #heating inequality 3 minimum heating #  H>=Hmin (done with lower bound)
        #cooling: 
            #Cooling inequality 1 additional cooling at lower temp# C>= UAl*(Tc_barl-Ti) + Cap*(T(i-1)-Ti)/dt where dt is in seconds
            #Cooling inequality 2 additional cooling at higher temp# C>= UAi*(Ti - Tc_bari) + Cap*(T(i-1)-Ti)/dt where dt is in seconds
            #Cooling inequality 3 minimum cooling #  C>=Cmin (done with lower bound)
        #Upper bound inequality
        #Lower bound inequality
    n_s = len(dt)
    n_b = len(observer['building_zone_temp'])
    n_g = len(qp['organize']['dispatchable'])
    n_l = len(qp['organize']['transmission'])
    for i in range(n_b):
        A = observer['building_conditioned_floor_area'][i]
        temperature =  sum([observer['building_zone_temp'][i][z]*A[z] for z in range(len(A))])/sum(A) #area_weighted_temperature %% %current average building zone temperature (used as IC in optimization)
        qp['b_eq'][qp['organize']['ic'][n_g+n_l+i]] = temperature
        qp['ub'][qp['organize']['ic'][n_g+n_l+i]] = temperature+1 #+1 just to help solver find feasible

        for t in range(n_s):
            states = qp['indices'][n_g+n_l+i][t+1]
            #temperature constraint
            qp['lb'][states[0]] = fb['Tmin'][t][i] -1 #maximum deviation beyond comfort bound
            qp['ub'][states[0]] = fb['Tmax'][t][i] +1 #maximum deviation beyond comfort bound

            #electrical energy balance
            r_eq = qp['organize']['building']['electrical_req'][i][t]
            qp['a_eq'][r_eq][states[1]]= -fb['H2E'][t][i] # Electricity = E0 + H2E*Heating + C2E*Cooling
            qp['a_eq'][r_eq][states[2]] = -fb['C2E'][t][i] # Electricity = E0 + H2E*Heating + C2E*Cooling
            qp['b_eq'][r_eq] += fb['E0'][t][i] #Equipment and nominal Fan Power

            r = qp['organize']['building']['r'][i][t]
            #heating inequalities
            if t == 0 and fb['c_min'][t][i] is None: #first state is known (re-optimizing)
                qp['a'][r][states[2]] = -1
                qp['a'][r+1][states[2]] = 1
                qp['b'][r] = -fb['H0'][t][i]
                qp['b'][r+1] = fb['H0'][t][i]+1e-4
            else:
                qp['a'][r][states[0]] = -fb['ua_h'][t][i][0] + fb['Cap'][i]/(3600*dt[t])
                qp['a'][r+1][states[0]] = fb['ua_h'][t][i][1] + fb['Cap'][i]/(3600*dt[t])
                qp['a'][r][states[1]] = -1
                qp['a'][r+1][states[1]] = -1   
                states0 = qp['indices'][n_g+n_l+i][t]      
                qp['a'][r][states0[0]] = -fb['Cap'][i]/(3600*dt[t]) #T(i-1)
                qp['a'][r+1][states0[0]] = -fb['Cap'][i]/(3600*dt[t]) #T(i-1)
                qp['b'][r] = -fb['ua_h'][t][i][0]*fb['th_bar'][t][i][0]
                qp['b'][r+1] = fb['ua_h'][t][i][1]*fb['th_bar'][t][i][1] 
                qp['lb'][states[1]] = fb['h_min'][t][i]               
            
            #cooling inequalities
            if t == 0 and fb['c_min'][t][i] is None: #first state is known (re-optimizing)
                qp['a'][r+2][states[2]] = -1
                qp['a'][r+3][states[2]] = 1
                qp['b'][r+2] = -fb['C0'][t][i]
                qp['b'][r+3] = fb['C0'][t][i]+1e-4
            else:
                qp['a'][r+2][states[0]] = -fb['ua_c'][t][i][0] - fb['Cap'][i]/(3600*dt[t])
                qp['a'][r+3][states[0]] = fb['ua_c'][t][i][1] - fb['Cap'][i]/(3600*dt[t])
                qp['a'][r+2][states[2]] = -1
                qp['a'][r+3][states[2]] = -1
                states0 = qp['indices'][n_g+n_l+i][t]
                qp['a'][r+2][states0[0]] = -fb['Cap'][i]/(3600*dt[t]) #T(i-1)
                qp['a'][r+3][states0[0]] = -fb['Cap'][i]/(3600*dt[t]) #T(i-1)
                qp['b'][r+2] = -fb['ua_c'][t][i][0]*fb['tc_bar'][t][i][0] - fb['Cap'][i]/(3600*dt[t])
                qp['b'][r+3] = fb['ua_c'][t][i][1]*fb['tc_bar'][t][i][1] - fb['Cap'][i]/(3600*dt[t])
                qp['lb'][states[2]] = fb['c_min'][t][i]

            #penalty states (excess and under temperature)
            qp['b'][r+4] = fb['Tmax'][t][i] #upper buffer inequality, the longer the time step the larger the penaly cost on the state is.
            qp['b'][r+5] = -fb['Tmin'][t][i] #lower buffer inequality
            
            #Cost penalty for exceeding temperature bounds
            qp['h'][states[3]] = dt[t]*fb['Discomfort'][t][i]
            qp['h'][states[4]] = dt[t]*fb['Discomfort'][t][i]
            qp['f'][states[3]] = dt[t]*fb['Discomfort'][t][i]
            qp['f'][states[4]] = dt[t]*fb['Discomfort'][t][i]
            
            #Cost penalty for deviation if deadband in nominal temperature window
            qp['b'][r+6] = fb['T_avg'][t][i] #positive deviation inequality
            qp['b'][r+7] = -fb['T_avg'][t][i] #negative deviation inequality
            if fb['deadband'][t][i]:
                qp['f'][states[5]] = dt[t]*fb['Discomfort'][t][i]
            else:
                qp['f'][states[5]] = 0

def update_mat_renew(qp, gen, forecast):
    qp['renewable'] = [[i for i in j] for j in forecast['renewable']]
    n_g = len(gen)
    for i in range(n_g):
        if gen[i]['type'] == 'Solar':
            n_s = len(forecast['renewable'][i]) 
            if 'e' in gen[i]['output']:
                n = gen[i]['subnet_node']['electrical']
                net = 'electrical'
            elif 'dc' in gen[i]['output']:
                n = gen[i]['subnet_node']['direct_current']
                net = 'direct_current'
            for t in range(n_s):
                row = qp['organize']['balance'][net][n][t] #balance at this node (t = 1)
                qp['b_eq'][row] -= forecast['renewable'][i][t]  #put renewable generation into energy balance at correct node
                

def update_mat_hydro(qp, gen, observer, subnet, forecast, date):
    """Updating lower and upper bound for hydro resevoir SOC"""
    qp['organize']['hydro_SOC_offset'] = []
    n_g = len(gen) 
    n_s = len(date)-1 
    for n in range(len(subnet['hydro']['nodes'])): #run through all the nodes in this network
        ## Node inflows (source/sink terms and upstream flow at time t-T ago if t<T)
        #need to be able to forecast sink/source
        for t in range(n_s):
            row = qp['organize']['balance']['hydro'][n][t] #mass balance at this node (t = 1)
            qp['b_eq'][row] -= forecast['hydro']['inflow'][n][t]  #source/sink term (also previous controlled releases that precede date(1))
    for i in range(n_g): #Make sure bounds are between 0 and the maximum usable size for each generator
        if gen[i]['type'] == 'HydroStorage':
            n = gen[i]['subnet_node']['hydro'] #dam #
            if observer['wy_forecast_timestamp'] !=None and date[-1]<observer['wy_forecast_timestamp'][-1]:
                j = 0
                while j<len(observer['wy_forecast_timestamp']) and date[-1]>observer['wy_forecast_timestamp'][j]+1:
                    j+=1
                r = (observer['wy_forecast_timestamp'][j+1] - date[-1])/(observer['wy_forecast_timestamp'][j] - observer['wy_forecast_timestamp'][j])
                qp['organize']['hydro_SOC_offset'][n] = r*observer['hydro_wy_soc'][n][j] +(1-r)*observer['hydro_wy_soc'][n][j+1] # re-center so zero is actual where this target is
                curr_range = max([0.1*gen[i]['stor']['usable_size'], 1+abs(observer['stor_state'][i]-qp['organize']['hydro_SOC_offset'][n])]) 
                for t in range(n_s):
                    s = qp['indices'][i][t+1][1]  #State for Reservoirs
                    qp['ub'][s] = min(curr_range, gen[i]['stor']['usable_size']-qp['organize']['hydro_SOC_offset'][n]) 
                    qp['lb'][s] = max(-curr_range, -qp['organize']['hydro_SOC_offset'][n]) 
            soc_now = observer['stor_state'][i]-qp['organize']['hydro_SOC_offset'][n] 
            qp['b_eq'][qp['organize']['ic'][i]+1] = soc_now #SOC in reservior (2nd ic for dam)
            qp['ub'][qp['organize']['ic'][i]+1] = soc_now+1 #+1 just to help solver find feasible
            qp['lb'][qp['organize']['ic'][i]+1] = soc_now-1 #-1 just to help solver find feasible

    #Adding cost for Line Transfer Penalties to differentiate from spillway flow
    if 'electrical' in subnet and subnet['electrical']['line_names'] !=None:
        for line in range(len(subnet['electrical']['line_names'])):
            if len(qp['indices'][n_g+line][1])>1: #bi-directional transfer with penalty states
                for t in range(n_s):
                    states = qp['indices'][n_g+line][t+1]
                    s_2 = states[1] #penalty from a to b
                    s_3 = states[2] # penalty from b to a
                    qp['f'][s_2] = 0.001  #Adding .1 cent/kWhr cost to every Electric line penalty to differentiate from spill flow
                    qp['f'][s_3] = 0.001  #Adding .1 cent/kWhr cost to every Electric line penalty to differentiate from spill flow
    
    #Adding lower bounds for Hydro lines that have seasonality constraints
    if 'hydro' in subnet and subnet['hydro']['line_names'] !=None:
        for k in range(len(subnet['hydro']['lineNames'])):
            line = subnet['hydro']['lineNumber'][k]
            for t in range(n_s):
                s = qp['indices'][n_g+line][t+1]
                qp['lb'][s] = subnet['hydro']['line_minimum'][k]
                #qp['lb'][s] = subnet['hydro']['line_minimum'][k][date[t+1].month]


def update_mat_sr(qp, options, forecast, dt, n_g):
    n_s = len(dt) 
    c_max = 2 #$2 per kWh at point where shortfall = spin reserve percent*demand or $2 at 5%
    c_min = 0.05 # $0.05 per kWh
    qp['b'][qp['organize']['spin_reserve']] = -forecast['sr_target'] # -shortfall + SRancillary - SR generators - SR storage <= -SR target
    if options['spin_reserve_perc']>5: #more than 5# spinning reserve
        spin_cost = [(c_max*dt[t])/forecast['sr_target'][t] for t in range(n_s)] # -shortfall + SRancillary - SR generators - SR storage <= -SR target
    else:
        spin_cost = []
        for t in range(n_s):
            #TODO (spin reserve on specific nodes)
            r_eq = qp['organize']['balance']['electrical'][0][t]
            spin_cost.append(c_max*dt[t]/(c_min*qp['b_eq'][r_eq])) # -shortfall + SRancillary - SR generators - SR storage <= -SR target

    for t in range(n_s):
        s = qp['organize']['spin_reserve_states'][n_g][t] #cumulative spinning reserve shortfall at t = 1 --> nS
        #     sr_ancillary = qp['organize']['spin_seserve_states'][n_g+1][t] #Ancillary spinning reserve value (negative cost) at t = 1 --> nS
        qp['h'][s] = spin_cost 
        qp['f'][s] = c_min*dt[t]  


def update_mat_market(qp,gen,market,date,dt):
    #Updates the matrices to enforce any current market awards rather than bids
    n_s = len(dt)
    for i in range(len(gen)):
        if gen[i]['type'] =='Market': #update for markets to enforce awards
            if qp['indices'][i] != None:
                if market['include'] == 1: #Update all states if market is included
                    for t in range(n_s):
                        s = qp['indices'][i][t+1][0]
                        qp['ub'][s] = market['forecast']['capacity']
                        qp['lb'][s] = market['forecast']['capacity']
                elif abs(date[0]-market['award_time']).seconds<60: #If there is an award for the current time, but not including forecasted market
                    pass    
                    # award_num =??
                    # if market['award_capacity'][award_num]>=0 #update x if buying
                    #     for t in range(n_s):
                    #         qp.ub(all_states(1:2,1)) = market.award.capacity(award_num:award_num+1,:);
                    #         qp.lb(all_states(1:2,1)) = market.award.capacity(award_num:award_num+1,:);
                    # else: #update Y if selling
                    #     for t in range(n_s):
                    #         qp.ub(all_states(1:2,2)) = market.award.capacity(award_num:award_num+1,:);
                    #         qp.lb(all_states(1:2,2)) = market.award.capacity(award_num:award_num+1,:);
