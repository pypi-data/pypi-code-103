from eagers.config.network import NETWORK_ABBR_NAME_MAP


def update_matrices_step(gen, market, subnet, options, qp, fb, renewable, demand, scale_cost,
        marginal, stor_power, dt, min_power, max_power, step_profile, flt, flc, bat):
    """Update the equalities with the correct demand, and scale fuel and electric costs
     ec is the expected end condition at this time stamp (can be empty)
     stor_power is the expected output/input of any energy storage at this timestep (can be empty)
     min_power and MaxPower define the range of this generator at this timestep
     temperatures is the building and cooling tower water loop temperatures.


     flt    ---     fluid loop temperature
     flc    ---     fluid loop capacitance
     bat    ---     building average temperature
    """
    qp['h'] = [i for i in qp['nom_vectors']['h']]
    qp['f'] = [i for i in qp['nom_vectors']['f']]
    qp['b'] = [i for i in qp['nom_vectors']['b']]
    qp['b_eq'] = [i for i in qp['nom_vectors']['b_eq']]
    qp['lb'] = [i for i in qp['nom_vectors']['lb']]
    qp['ub'] = [i for i in qp['nom_vectors']['ub']]
    qp['const_cost'] = [i for i in qp['nom_vectors']['const_cost']]

    n_g = len(gen)

    # Determine which components are enabled.
    qp['organize']['enabled'] = [True for i in range(n_g)]
    for i in range(n_g):
        if 'enabled' in gen[i] and not gen[i]['enabled']:
            qp['organize']['enabled'][i] = False
    qp['renewable'] = [[] for i in range(len(gen))]
    if len(renewable)>0:
        gen_names = [k['name'] for k in gen]
        for k in renewable:
            qp['renewable'][gen_names.index(k)] = renewable[k]
    

    # Update the demands and self-discharge losses.
    update_mat_demand_step(gen, qp, subnet, options, demand, renewable, stor_power)

    # Building inequalities and equality.
    if fb != None:
        update_mat_building_step(qp, fb, bat, dt)   

    # Fluid loop equality.
    update_fluid_loop_step(flt, flc, qp, dt)

    # Update upper and lower bounds based on ramping constraint (if
    # applicable).
    
    update_gen_limit(gen, qp, min_power, max_power, market)

    # Update storage bounds.
    update_storage_bounds(gen, subnet, qp, stor_power, step_profile, dt)

    # Adding cost for Line Transfer Penalties to differentiate from spillway
    # flow.
    update_mat_hydro_step(gen, qp, subnet)

    # Update costs.
    update_mat_cost_step(gen, qp, step_profile, stor_power, scale_cost, marginal, dt)

    # Update spinning reserve.
    update_spin_reserve_step(qp, options, demand, dt)

    # update market
    update_mat_market_step(qp,options,dt)

    qp['updated_b_eq'] = [i for i in qp['b_eq']]
    qp['updated_lb'] = [i for i in qp['lb']]


def update_mat_demand_step(gen, qp, subnet, options, demand, renewable, stor_power):
    """Update demands and storage self discharge."""
    qp['network'] = {}
    gen_names = [k['name'] for k in gen]
    for net in subnet['network_names']:
        abbrev = subnet[net]['abbreviation']
        qp['network'][net] = {}
        qp['network'][net]['nodes'] = len(subnet[net]['nodes'])
        if net == 'hydro':
            # Don't do a water balance, since it depends on multiple time
            # steps. Any extra outflow at this time step is subtracted from
            # expected outflow at next step (same SOC and flows up river).
            pass
        else:
            dem = demand[net]
            for i in range(len(subnet[net]['nodes'])):
                equip = subnet[net]['equipment'][i]
                r_eq = qp['organize']['balance'][net][i]
                #TODO change to node names rather than index
                for nn in subnet[net]['nodes'][i]:
                    if nn in dem:
                        qp['b_eq'][r_eq] = dem[nn]
                for eq_name in equip:
                    k = gen_names.index(eq_name)
                    if (net == 'electrical' or net == 'direct_current') and eq_name in renewable:
                        # Subtract renewable generation. Put renewable generation into energy balance at correct node.
                        qp['b_eq'][r_eq] -= renewable[eq_name]
                    if not stor_power is None and not stor_power[k] is None:
                        if gen[k]['type'] in ['ElectricStorage', 'ThermalStorage'] and abbrev in gen[k]['output']:
                            alpha = -(1/gen[k]['stor']['charge_eff'] - gen[k]['stor']['disch_eff'])
                            if stor_power[k]>0:
                                qp['b_eq'][r_eq] -= stor_power[k]
                                qp['b'][qp['organize']['inequalities'][k][0]] = - alpha * stor_power[k] / gen[k]['stor']['disch_eff']
                            else:
                                qp['b_eq'][r_eq] -= stor_power[k] * gen[k]['stor']['charge_eff'] * gen[k]['stor']['disch_eff']
                                qp['b'][qp['organize']['inequalities'][k][0]] = - alpha * stor_power[k] * gen[k]['stor']['charge_eff']
                        elif abbrev == 'e' and gen[k]['type'] == 'HydroStorage':
                            qp['b_eq'][r_eq] -= stor_power[k]
            if net == 'electrical' and options['spin_reserve']:
                # -shortfall + SRancillary - SR generators - SR storage <= -SR target
                qp['b'][qp['organize']['spin_reserve'][0]] = -options['spin_reserve_perc']/100 * sum([dem[k] for k in dem])


def update_mat_cost_step(gen, qp, step_profile, stor_power, scale_cost, marginal, dt):    
    n_g = len(gen)
    for i in range(n_g):
        if not qp['indices'][i][0] is None:
            states = qp['indices'][i][0] #states of this generator
            if gen[i]['type'] in ['ElectricGenerator','CombinedHeatPower','Chiller','Heater','CoolingTower','Electrolyzer','HydrogenGenerator','TradePoint']:
                for s in states:
                    qp['f'][s] *= scale_cost[i][0] * dt
                    qp['h'][s] *= scale_cost[i][0] * dt
            elif gen[i]['type']  in ['Utility','Market']:
                if gen[i]['source'] == 'electricity':
                    qp['f'][states[0]] *= scale_cost[i][0] * dt
                    if len(states)>1 and (gen[i]['type'] == 'Market' or gen[i]['sellback_rate'] == -1):
                        # Sellback is a fixed percent of purchase costs (percent
                        # set when building matrices).
                        qp['f'][states[1]] *= scale_cost[i][0] * dt
                    else:
                        pass
                        # Constant sellback rate was taken care of when building
                        # the matrices.
            elif gen[i]['type'] == 'HydroStorage':
                if stor_power !=None:
                    qp['f'][states[0]] = marginal['e'] #expected generation moved to RHS, so that cost penalty can refer to deviations from that power
                    qp['h'][0] = 2*qp['f'][states[0]]/(.25*stor_power[i])  #factor of 2 because its solving C = 0.5*x'*H*x + f'*x
            elif 'stor' in gen[i]:
                stor_cat = list(gen[i]['output'].keys())
                # Penalize deviations from the expected storage output.
                a = 1  # Sets severity of quadratic penalty.
                # Scale the penalty by a) larger of 5% capcity and 2x
                # the expected change in stored capacity, b) lesser of
                # a) and remaining space in storage.
                max_charge = 0.05 * gen[i]['stor']['usable_size'] / dt
                if stor_power!=None:
                    max_charge = max([max_charge, 2 * abs(stor_power[i])])
                    us =gen[i]['stor']['usable_size']
                    fp = step_profile[i]
                    if us > fp:
                        max_charge = min([(us- fp) / dt, max_charge])
                    if fp > 0:
                        max_charge = min([0.5 * fp/ dt, max_charge])
                qp['f'][states[0]] = marginal[stor_cat[0]]
                # Factor of 2 because it's solving C = 0.5*x'*h*x + f'*x
                qp['h'][states[0]] = a * 2 * qp['f'][states[0]] / max_charge
                if len(states) > 1:
                    # Small penalty on charging state so that if there
                    # are no other generators it keeps the charging
                    # constraint as an equality.
                    qp['f'][states[1]] = 1e-6
    for i in range(len(qp['const_cost'])):
        if len(scale_cost[i])>0:
            qp['const_cost'][i] *= scale_cost[i][0] * dt


def update_spin_reserve_step(qp, options, demand, dt):
    n_g = len(qp['organize']['dispatchable'])
    if options['spin_reserve']:
        sr_short = qp['organize']['spin_reserve_states'][n_g] #cumulative spinning reserve shortfall 
        # sr_ancillary = qp['organize']['spin_reserve_states'][n_g+1] #Ancillary spinning reserve value (negative cost) 
        if all(demand['electrical'][k] == 0 for k in demand['electrical']):
            spin_cost = 0.02
            print('need building demand for spin reserve cost estimate in update_matrices_step')
        elif options['spin_reserve_perc'] > 5:
            # More than 5% spinning reserve.
            # -shortfall + sr_ancillary - sr_generators - sr_storage <= -sr_target
            spin_cost = 2 * dt / (options['spin_reserve_perc']/(100*sum([demand['electrical'][k] for k in demand['electrical']])))
        else:
            spin_cost = 2*dt/(0.05*sum(demand['e'])) #-shortfall + SRancillary - SR generators - SR storage <= -SR target
        qp['h'][sr_short] = spin_cost #effectively $2 per kWh at point where shortfall = spin reserve percent*demand or $2 at 5%
        qp['f'][sr_short] = 0.05*dt  # $0.05 per kWh.


def update_mat_building_step(qp, fb, temperatures, dt):
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
        #Positive deviation inequality
        #Negative deviation inequality
    n_b = len(temperatures)
    n_g = len(qp['organize']['dispatchable'])
    n_l = len(qp['organize']['transmission'])
    for i in range(n_b):
        states = qp['indices'][n_g+n_l+i][0]
 
        #electrical energy balance
        r_eq = qp['organize']['building']['electrical_req'][i]
        qp['a_eq'][r_eq][states[1]]= -fb['H2E'][i] # Electricity = E0 + H2E*Heating + C2E*Cooling
        qp['a_eq'][r_eq][states[2]] = -fb['C2E'][i] # Electricity = E0 + H2E*Heating + C2E*Cooling
        qp['b_eq'][r_eq] += fb['E0'][i] #Equipment and nominal Fan Power

        r = qp['organize']['building']['r'][i]
        #heating inequalities
        qp['lb'][states[1]] = fb['h_min'][i]        
        qp['a'][r][states[0]] = -fb['ua_h'][i][0] + fb['Cap'][i]/(3600*dt)
        qp['a'][r+1][states[0]] = fb['ua_h'][i][1] + fb['Cap'][i]/(3600*dt)
        qp['a'][r][states[1]] = -1
        qp['a'][r+1][states[1]] = -1
        qp['b'][r] = -fb['ua_h'][i][0]*fb['th_bar'][i][0] + fb['Cap'][i]/(3600*dt)*temperatures[i]
        qp['b'][r+1] = fb['ua_h'][i][1]*fb['th_bar'][i][1] + fb['Cap'][i]/(3600*dt)*temperatures[i]
        
        #cooling inequalities
        qp['lb'][states[2]] = fb['c_min'][i]
        qp['b'][r+2] = -fb['ua_c'][i][0]*fb['tc_bar'][i][0] - fb['Cap'][i]/(3600*dt)*temperatures[i]
        qp['a'][r+2][states[0]] = -fb['ua_c'][i][0] - fb['Cap'][i]/(3600*dt)
        qp['b'][r+3] = fb['ua_c'][i][1]*fb['tc_bar'][i][1] - fb['Cap'][i]/(3600*dt)*temperatures[i]
        qp['a'][r+3][states[0]] = fb['ua_c'][i][1] - fb['Cap'][i]/(3600*dt)
        qp['a'][r+2][states[2]] = -1
        qp['a'][r+3][states[2]] = -1
        #penalty states (excess and under temperature)
        qp['b'][r+4] = fb['Tmax'][i] #upper buffer inequality, the longer the time step the larger the penaly cost on the state is.
        qp['b'][r+5] = -fb['Tmin'][i] #lower buffer inequality
        #positive and negative deviation inequality
        qp['b'][r+6] = fb['T_avg'][i] #T deviation >= (Ti - Tnominal)
        qp['b'][r+7] = -fb['T_avg'][i] #T deviation >= (Tnominal- Ti)
        
        #Cost penalty for exceeding temperature bounds
        qp['h'][states[3]] = fb['Discomfort'][i]
        qp['h'][states[4]] = fb['Discomfort'][i]
        qp['f'][states[3]] = fb['Discomfort'][i]
        qp['f'][states[4]] = fb['Discomfort'][i]

        #Cost penalty for deviation if deadband in nominal temperature window
        if fb['deadband'][i]:
            qp['f'][states[5]] = fb['Discomfort'][i]
        else:
            qp['f'][states[5]] = 0


def update_fluid_loop_step(flt, flc, qp, dt):
    '''
    flt     ---     fluid loop temperatures
    flc     ---     fluid loop capacitance
    '''

    n_b = len(qp['organize']['building']['r'])
    n_g = len(qp['organize']['dispatchable'])
    n_l = len(qp['organize']['transmission'])
    n_fl = len(flt)
    for i in range(n_fl):
        #1st order temperature model: 0 = -T(k) + T(k-1) + dt/Capacitance*(energy balance)
        state = qp['indices'][n_g+n_l+n_b+i][0]
        r_eq = qp['organize']['balance']['cooling_water'][i]
        # Water capacity in kg and thermal capacitance in kJ/kg*K to get kJ/K.
         #energy balance for chillers & cooling tower fans already put in this row of Aeq
        qp['a_eq'][r_eq][state[0]] = -flc[i]/(3600*dt) #-T(k)
        qp['b_eq'][r_eq] = -flt[i]*flc[i]/(3600*dt) #-T(k-1)


def update_gen_limit(gen, qp, min_power, max_power, market):
    for i in range(len(gen)):
        if qp['organize']['dispatchable'][i]:
        # if gen[i]['type'] in ['ElectricGenerator','CombinedHeatPower','Chiller','Heater','CoolingTower','Electrolyzer','HydrogenGenerator'] and not qp['indices'][i][0] is None:
            states = qp['indices'][i][0]
            lb = sum([qp['lb'][s] for s in states])
            if min_power[i] > lb:
                # Raise the lower bounds.
                # qp['organize']['dispatchable'][i] = False  # Can't shut off.
                power_add = min_power[i] - lb
                for f in states:
                    # Starting with lb of 1st state in generator, then moving on.
                    gap = qp['ub'][f] - qp['lb'][f]
                    if gap > 0:
                        gap = min([gap, power_add])
                        qp['lb'][f] += gap
                        power_add -= gap
            if max_power[i] < gen[i]['ub']:
                # Lower the upper bounds.
                power_sub = gen[i]['ub'] - max_power[i]
                for f in range(len(states)-1, -1, -1):
                    # Starting with lb of 1st state in generator, then movingon.
                    if qp['ub'][states[f]] > 0:
                        gap = min(qp['ub'][states[f]], power_sub)
                        qp['ub'][states[f]] -= gap
                        power_sub -= gap
        elif gen[i]['type'] in ['HydroStorage']:
            states = qp['indices'][i][0]
            qp['lb'][states[0]] = min_power[i]
            qp['ub'][states[0]] = max_power[i]
        elif gen[i]['type'] in ['Utility','Tradepoint']:
            pass #already set, shouldn't need to update
        elif gen[i]['type'] in ['Market']:
            states = qp['indices'][i][0]
            #Set the upper and lower bounds to the awarded bid capacity to
            #avoid deviating from commitments
            if market['award']['time'] !=None:
                qp['lb'][states[0]] = 0 #initial market is 0
                qp['ub'][states[0]] = 0 
            else:
                qp['lb'][states[0]] = market['award']['capacity'][len(market['award']['capacity'])+market['award_time'][i]] #gets the award for the current time  
                qp['ub'][states[0]] = market['award']['capacity'][len(market['award']['capacity'])+market['award_time'][i]]


def update_storage_bounds(gen, subnet, qp, stor_power, step_profile, dt):
    n_g = len(gen)
    for i in range(n_g):
        states = qp['indices'][i][0]
        if gen[i]['type'] in ['ElectricStorage', 'ThermalStorage', 'HydroStorage']:
            # Update storage output range to account for what is already scheduled.
            f = list(gen[i]['output'].keys())
            net = NETWORK_ABBR_NAME_MAP[f[0]]
            n = 0
            for equip in subnet[net]['equipment']:
                if gen[i]['name'] in equip:
                    break 
                else:
                    n +=1
            r_eq = qp['organize']['balance'][net][n]#balance at correct node
            s = states[0]
            if stor_power == None: #only when solving automatic initial conditions
                qp['lb'][s] = -gen[i]['stor']['peak_charge']
                qp['ub'][s] = gen[i]['stor']['peak_disch']
                qp['f'][s] = 5*max(qp['f'])
            else:
                charging_space = max([0,(gen[i]['stor']['usable_size']-step_profile[i])*qp['a_eq'][r_eq][s]/dt]) #you can't charge more than you have space for
                qp['lb'][s] = max([qp['lb'][s]-stor_power[i], -charging_space])
                qp['ub'][s] = min([qp['ub'][s]-stor_power[i], step_profile[i]/dt])
            if not qp['organize']['spin_row'][i] is None: #update spinning reserve (max additional power from storage
                qp['b_eq'][qp['organize']['spin_row'][i]] = qp['ub'][s]
            if gen[i]['type'] == 'HydroStorage':
                if stor_power != None:
                    qp['lb'][s] -= stor_power[i]
                    qp['ub'][s] -= stor_power[i]
                    #update the equality with NewPower*conversion + spill - Outflow = nominal PowerGen Flow
                    # n = gen[i]['subnet_node']['hydro']
                    # h = qp['organize']['balance']['hydro'].index(n)
                    qp['b_eq'][qp['organize']['equalities'][i]] = -step_profile[i]*gen[i]['stor']['power_to_flow']
        if not states is None:
            for s in states:
                qp['lb'][s] = min([qp['lb'][s],qp['ub'][s]]) #fix rounding errors


def update_mat_hydro_step(gen, qp, subnet):
    """Also want to penalize spill flow to conserve water for later, spill flow
    is just to meet instream requirments when the power gen needs to be low.
    """

    if 'hydro' in subnet['network_names'] and len(subnet['electrical']['line_names']) > 0:
        n_g = len(gen)
        for k in range(0,len(subnet['electrical']['line_names'])):
            line = subnet['electrical']['line_number'][k]
            states = qp['indices'][n_g + line][0]
            if len(states)>1: #bi-directional transfer with penalty states
                # Adding .1 cent/kWhr cost to every Electric line penalty to
                # differentiate from spill flow.
                qp['f'][states[1]] = 0.001
                qp['f'][states[2]] = 0.001
        
        for i in range(n_g):
            if gen[i]['type'] == 'hydro storage' and 's' in gen[i]:
                states = qp['indices'][i][0]
                qp['f'][states[1]] = 0.0001/gen[i]['stor']['power_to_flow']

def update_mat_market_step(qp,options,dt):
    pass
    # n_g = len(qp['organize']['dispatchable'])
    # if options['market']==True:
    #     market_states = qp['organize']['market']