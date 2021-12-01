def disable_gen(qp, locked):
    # indices is the record of which indicies are associated with each generator
    #locked is the specific combination of generators being tested
    n_g = len(qp['organize']['dispatchable']) #just generators
    qp['x_keep'] = [True for i in range(len(qp['lb']))]
    qp['r_keep'] = [True for i in range(len(qp['a']))]
    qp['req_keep'] = [True for i in range(len(qp['a_eq']))]
    subnet_names = list(qp['const_demand'].keys())
    if not 'n_s' in qp['organize']:
        #single time step optimization
        for i in range(n_g):
            if not qp['organize']['enabled'][i]:
                locked[i] = False
            if not locked[i]:
                # Generator offline; remove states.
                for s in qp['indices'][i][0]:
                    qp['x_keep'][s] = False
                # Remove any associated equality constraints.
                if not qp['organize']['equalities'][i] is None:
                    # Equality constraints.
                    for req in qp['organize']['equalities'][i]:
                        qp['req_keep'][req] = False
                if not qp['organize']['spin_row'][i] is None:
                    # Spinning reserve equality constraint.
                    qp['req_keep'][qp['organize']['spin_row'][i]] = False
                if not qp['organize']['inequalities'][i] is None:
                    # Inequality constraints.
                    for r in qp['organize']['inequalities'][i]:
                        qp['r_keep'][r] = False
        #add in constant electric loads from chillers/pumps in FitB
        qp['b_eq'] = [i for i in qp['updated_b_eq']]#restore values to last time update_matrices_step was called
        qp['lb'] = [i for i in qp['updated_lb']] #might get modified in disable_lb_from_group
        for net in subnet_names:
            if qp['const_demand'][net]['r_eq'] is not None:
                for node in range(qp['network'][net]['nodes']):
                    r_eq = qp['const_demand'][net]['r_eq'][node]
                    qp['b_eq'][r_eq] += sum([qp['const_demand'][net]['load'][node][i] for i in range(n_g) if locked[i]])
    else:
        #multi-timestep optimization
        n_s = qp['organize']['n_s']
        #add in constant electric loads from chillers/pumps in FitB
        if not locked is None:
            for net in subnet_names:
                for node in range(qp['network'][net]['nodes']):
                    for t in range(n_s):
                        r_eq = qp['const_demand'][net]['r_eq'][node][t]
                        qp['b_eq'][r_eq] += sum([qp['const_demand'][net]['load'][node][t][i] for i in range(n_g) if locked[i][t+1]])

        if not locked is None:
            for i in range(n_g):
                if not qp['organize']['enabled'][i]:
                    locked[i] = [False for t in range(len(locked[i]))]
        
            ramp_up = qp['organize']['ramp_up']
            ramp_down = qp['organize']['ramp_down']
            spin_row = qp['organize']['spin_row']
            #deal with initial condition first
            for i in range(n_g):
                if locked[i][0]==False:
                    state = qp['indices'][i][0][0]
                    
                    if locked[i][1]==False or ramp_up[i] is None:#if locked off
                        qp['x_keep'][state] = False
                        qp['req_keep'][qp['organize']['ic'][i]] = False
                    else:
                        #if it turns on right away keep ic = 0 constraint, but change ramping constraints
                        qp['r_keep'][ramp_down[i][0]] = False #eliminate ramp down constraint
                        qp['b'][ramp_up[i][0]] = max([qp['b'][ramp_up[i][0]],-1.001*qp['a'][ramp_up[i][0]][state]*qp['lb'][qp['indices'][i][1][0]]]) #ramp up constraint
                        qp['b_eq'][qp['organize']['ic'][i]] = 0
                for t in range(n_s):
                    if not locked[i][t+1]: #if its offline
                        for s in qp['indices'][i][t+1]:
                            qp['x_keep'][s] = False
                        if (t == n_s-1 and not locked[i][t]) or (not locked[i][t] and not locked[i][t+2]) or qp['organize']['ramp_up'][i] is None:
                            #completely remove all generator states and ramping constraints at this time step if
                            # a) it was off previously & is the last time step, b) was off previously and will remain off at next step, c) has no ramping constraint (shuts off instantly)
                            #remove the ramping constraints
                            s1 = None
                            if not ramp_up[i] is None:
                                qp['r_keep'][ramp_up[i][t]] = False #ramp up constraint
                                qp['r_keep'][ramp_down[i][t]] = False #ramp down constraint
                                if t<n_s-1:
                                    qp['r_keep'][ramp_up[i][t+1]] = False #ramp up constraint
                                    qp['r_keep'][ramp_down[i][t+1]] = False #ramp down constraint
                        else:
                            #keep the first state for ramping constraint to zero
                            s1 = qp['indices'][i][t+1][0]
                            qp['x_keep'][s1] = True
                            #simplify the ramping constraint when ramping to/from offline
                            qp['r_keep'][ramp_up[i][t]] = False #ramp up constraint from previous condition
                            r_down0 = ramp_down[i][t]
                            if not locked[i][t]:
                                qp['r_keep'][r_down0] = False #ramp down constraint
                            else:
                                qp['b'][r_down0] = max([qp['b'][r_down0],-1.001*qp['a'][r_down0][s1]*qp['lb'][s1]]) #ramp down constraint
                            #there is no ramping constraint to next step to remove if it is the last timestep
                            if t==n_s-1:
                                pass
                            #if you are offline in the next step, remove ramp up and ramp down constraint
                            elif not locked[i][t+2]:
                                qp['r_keep'][ramp_up[i][t+1]] = False #ramp up constraint to next time
                                qp['r_keep'][ramp_down[i][t+1]] = False #ramp down constraint to next time
                            else:
                                qp['r_keep'][ramp_down[i][t+1]] = False #amp down constraint to next time
                                r_up2 = ramp_up[i][t+1]
                                qp['b'][r_up2] = max([qp['b'][r_up2],-1.001*qp['a'][r_up2][s1]*qp['lb'][s1]])

                        # Eliminate the spinning reserve state for the individual generator.
                        if not qp['organize']['spin_reserve_states'][i] is None:
                            qp['x_keep'][qp['organize']['spin_reserve_states'][i][t]] = False
                        # Remove any associated equality constraints.
                        if not qp['organize']['equalities'][i] is None:
                            # Equality constraints.
                            qp['req_keep'][qp['organize']['equalities'][i][t]] = False
                        if not s1 is None:
                            qp['ub'][s1] = 0 #Constrained to be off
                            qp['lb'][s1] = 0 #Constrained to be off
                        if not qp['organize']['inequalities'][i] is None:
                            # Inequality constraints.
                            qp['r_keep'][qp['organize']['inequalities'][i][t]] = False
                        if not spin_row[i] is None:
                            # Spinning reserve equality constraint.
                            qp['req_keep'][spin_row[i][t]] = False
        qp['f'] = check_stor_penalty(qp['organize'],qp['indices'],qp['a_eq'],qp['f'],n_g,n_s)

def check_stor_penalty(organize,indices,a_eq,f,n_g,n_s):
    ## small penalty on charging state so that if there are no other generators active at a particular timestep to apply a cost it keeps the charging constraint as an equality
    for i in range(n_g):
        if organize['storage_w_penalty'][i]:
            f_name = list(organize['balance'].keys())
            for k in f_name:
                for n in range(len(organize['balance'][k])):
                    r_eq = organize['balance'][k][n][0]
                    states = indices[i][1]
                    if a_eq[r_eq][states[1]] !=0: #storage is in this energy balance
                        for t in range(n_s):
                            r_eq = organize['balance'][k][n][t]
                            other_gen = [i for i, val in enumerate(a_eq[r_eq]) if val!=0] 
                            if all([f[ind]==0 for ind in other_gen]):
                                f[indices[i][t+1][1]]= 1e-6
    return f