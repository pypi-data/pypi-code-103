"""Logic for loading matrices.
"""

def load_matrices(gen, b_names, fluid_loop, market, subnet, options, op, dt):
    """This function builds constant matrices for multi-time-step optimization
    demands, initial conditions, and utility costs must be updated prior to
    optimization.

    INPUTS:
    gen        -list of components in the plant
    b_names    -list of building names
    fluid_loop -list of cooling tower fluid loops
    subnet     -description of each energy network in the optimizing
    options    -options specifying simulation parameters
    op         -string designation for which efficiency fit curves to use
                (op_mat_a: continuous, op_mat_b: discontinuous but more
                accurate)
    dt         -vector of timestep differences

    OUTPUTS:
    qp         -qp dictionary which includes all the optimization matrices
    """

    n_g = len(gen)
    n_b = len(b_names)
    n_fl = len(fluid_loop)
    n_m = len(market)
    # Count number of lines for each network.
    n_l = sum([len(subnet[net]['line']['node1']) for net in subnet['network_names']])

    qp = {}
    qp['organize'] = {}
    qp['organize']['names'] = [gen[i]['name'] for i in range(n_g)]
    for net in subnet['network_names']:
        qp['organize']['names'].extend([subnet[net]['line']['node1'][i] +'_to_' + subnet[net]['line']['node2'][i] for i in range(len(subnet[net]['line']['node1']))])
    qp['organize']['names'].extend(b_names)
    qp['organize']['names'].extend([fluid_loop[i]['name'] for i in range(n_fl)])

    if dt !=None:
        n_s = len(dt)
        qp['organize']['n_s'] = n_s
        qp['organize']['ic'] = [None for i in range(n_g+n_l+n_b+n_fl)]
    else:
        n_s = 0
    qp['organize']['dispatchable'] = [False for i in range(n_g)]
    qp['organize']['storage_w_penalty'] = [False for i in range(n_g)]
    qp['organize']['enabled'] =  [True for i in range(n_g)]
    qp['organize']['ramp_up'] = [None for i in range(n_g)]
    qp['organize']['ramp_down'] = [None for i in range(n_g)]
    qp['organize']['spin_reserve_states'] = [None for i in range(n_g)]
    qp['organize']['transmission'] = [None for i in range(n_l)]
    qp['organize']['hydro'] = []
    qp['organize']['hydro_dr_line'] = []
    qp['organize']['building'] = {}
    qp['organize']['building']['r'] = [None for i in range(n_b)]
    qp['organize']['building']['electrical_req'] = [None for i in range(n_b)]
    qp['organize']['building']['district_heat_req'] = [None for i in range(n_b)]
    qp['organize']['building']['district_cool_req'] = [None for i in range(n_b)]
    qp['organize']['dt'] = dt
    qp['organize']['market'] = [None for i in range(n_m)]
    qp['organize']['out_vs_state'] = [None for i in range(n_g+n_l+n_b+n_fl)]
    qp['indices'] = [[None] for j in range(n_g+n_l+n_b+n_fl)]
    qp['excess_heat'] = options['excess_heat']
    qp['excess_cool'] = options['excess_cool']
    qp['const_cost'] = [0 for i in range(n_g)]
    qp['organize']['equalities'] = [None for i in range(n_g)]
    qp['organize']['inequalities'] = [None for i in range(n_g)]
    qp['organize']['spin_row'] = [None for i in range(n_g)] 
    qp['organize']['balance'] = {}
    qp['network'] = {}
    qp['const_demand'] = {}
    for net in subnet['network_names']:
        qp['organize']['balance'][net] = [None for i in range(len(subnet[net]['nodes']))]
        nn = len(subnet[net]['nodes'])
        qp['network'][net] = {}
        qp['network'][net]['nodes'] = nn
        qp['network'][net]['node_names'] = [subnet[net]['nodes'][j][0] for j in range(nn)]
        qp['const_demand'][net] = {}
        qp['const_demand'][net]['r_eq'] = [[] for n in range(nn)]
        qp['const_demand'][net]['load'] = [[] for n in range(nn)]
    

    if dt !=None:
        qp, n_ic = count_ic(gen, qp, n_g, n_b, n_l, n_fl) # n_ic is an number, anywhere it is used in an index, requires a -1
    else:
        n_ic = 0

    qp, lb, ub = count_states(gen, subnet, options, n_g, n_b, n_l, fluid_loop, dt, n_ic, op, qp)
    if dt !=None:
        for i in range(n_g+n_l+n_b+n_fl):
            qp['indices'][i].insert(0,[qp['organize']['ic'][i]])
    
    # Expand by number of time steps.
    # Number of states per time step is x_l.
    # Order of states will repeat for n_s timesteps.
    t1s = len(lb)
    if dt !=None:
        total_states = n_s * t1s + n_ic
        for n in range(len(qp['indices'])):
            if not qp['indices'][n][1] is None:
                for t in range(1, n_s):
                    qp['indices'][n].append([k + t1s for k in qp['indices'][n][t]])      
            else:
                qp['indices'][n] = [[None] for t in range(n_s+1)]
        h = [0 for i in range(total_states)]
        qp['f'] = [0 for i in range(total_states)]
        qp['lb'] = [0 for i in range(n_ic)]
        qp['ub'] = [0 for i in range(n_ic)]
        for t in range(n_s):
            qp['lb'].extend(lb)
            qp['ub'].extend(ub)
    else:
        h = [0 for i in range(len(lb))]
        qp['f'] = [0 for i in range(len(lb))]
        qp['lb'] = lb
        qp['ub'] = ub
        
    qp['organize'], n_eq, ec = count_equalities(gen, subnet, options['spin_reserve'], qp['organize'], n_ic, options['end_soc'],dt)
    qp['organize'], n_ineq = count_inequalities(gen, subnet, options['spin_reserve'], qp['organize'], n_b, dt)
    if dt !=None:
        qp['organize'] = expand_organize(qp['organize'],subnet,n_s,n_eq,n_ineq,t1s)
        total_equalities = n_s*n_eq + n_ic + len(ec)
        qp['a_eq'] = [[0 for i in range(total_states)] for j in range(total_equalities)]
        qp['b_eq'] = [0 for j in range(total_equalities)]
        # Initial condition identity matrix.
        for i in range(n_ic):
            qp['a_eq'][i][i] = 1
        total_inequalities = n_s*n_ineq
        qp['a'] = [[0 for i in range(total_states)] for j in range(total_inequalities)]
        qp['b'] = [0 for j in range(total_inequalities)]
    else:
        qp['a_eq'] = [[0 for i in range(t1s)] for j in range(n_eq)]
        qp['b_eq'] = [0 for j in range(n_eq)]
        
        qp['a'] = [[0 for i in range(t1s)] for j in range(n_ineq)]
        qp['b'] = [0 for j in range(n_ineq)]

    # Call sub functions to fill in these matrices now that they are
    # sized.
    if dt !=None:
        qp['a_eq'], qp['b_eq'], h, qp['f'] = generator_equalities(gen, subnet, qp['a_eq'], qp['b_eq'], h, qp['f'], qp['organize'], qp['indices'], dt, op)
        qp['a_eq'], qp['b_eq'] = end_state_constraint(gen, options['end_soc'], qp['a_eq'], qp['b_eq'], qp['indices'], ec)
        qp['a'], qp['b'] = generator_inequalities(gen, qp['a'], qp['b'], qp['organize'], qp['indices'], dt)
        qp['a'], qp['b'] = spin_reserve_inequalities(gen, subnet, options['spin_reserve'], qp['a'], qp['b'], qp['organize'], qp['indices'], dt)
    else:
        qp, h = equality_constraints_step(gen, subnet, qp, h)
        qp['a'] = storage_inequalities_step(gen, qp['a'], qp['organize'], qp['indices'])
        qp['a_eq'] = hydro_equalities_step(gen, subnet, qp['a_eq'], qp['organize'], qp['indices'])
        qp['a_eq'], qp['b_eq'], qp['a'] = spin_reserve_constraints_step(gen, subnet, options['spin_reserve'], qp['a_eq'], qp['b_eq'], qp['a'], qp['organize'], qp['indices'])
    
    qp['a_eq'] = line_equalities(subnet, qp['a_eq'], qp['organize'], qp['indices'], n_s, n_g)
    qp['a'] = line_inequalities(subnet, qp['a'], qp['organize'], qp['indices'], n_s, n_g)
    qp['a_eq'], qp['a'], h, qp['f'], qp['organize'] = building_constraints(b_names,subnet, qp['a_eq'], qp['a'], h, qp['f'], qp['organize'], qp['indices'], dt, n_g, n_l, n_s)
    qp['a_eq'], qp['a'], h, qp['f'], qp['organize'] = fluid_loop_constraints(gen, fluid_loop, subnet, qp['a_eq'], qp['a'], h, qp['f'], qp['organize'], qp['indices'], dt, n_l, n_b, n_s)
    qp['h'] = h
    if op == 'b': #when using fit B record the constant load demands
        qp['const_demand'] = load_const_demand(qp['const_demand'], qp, gen, subnet,  n_s)

    #copy these defaults to refer to later whenever they need to be reset
    qp['nom_vectors'] = {}
    qp['nom_vectors']['h'] = [i for i in qp['h']]
    qp['nom_vectors']['f'] = [i for i in qp['f']]
    qp['nom_vectors']['b'] = [i for i in qp['b']]
    qp['nom_vectors']['b_eq'] = [i for i in qp['b_eq']]
    qp['nom_vectors']['lb'] = [i for i in qp['lb']]
    qp['nom_vectors']['ub'] = [i for i in qp['ub']]
    qp['nom_vectors']['const_cost'] = [i for i in qp['const_cost']]
    return qp

def expand_organize(organize,subnet,n_s,n_eq,n_ineq,t1s):
    #expand out by timestep for disable_generators
    for net in subnet['network_names']:
        for i in range(len(subnet[net]['nodes'])):
            organize['balance'][net][i] = [organize['balance'][net][i] + t*n_eq for t in range(n_s)]
    for n in range(len(organize['heat_vented'])):
        if organize['heat_vented'][n]:
            organize['heat_vented'][n].extend([organize['heat_vented'][n][0] + t*t1s for t in range(1,n_s)])
    for n in range(len(organize['cool_vented'])):
        if organize['cool_vented'][n]:
            organize['cool_vented'][n].extend([organize['cool_vented'][n][0] + t*t1s for t in range(1,n_s)])
    for n in range(len(organize['spin_reserve_states'])):
        if organize['spin_reserve_states'][n]:
            organize['spin_reserve_states'][n] = [organize['spin_reserve_states'][n] + t*t1s for t in range(n_s)]
    if 'spin_reserve' in organize:
        organize['spin_reserve'] = [organize['spin_reserve'] + t*n_ineq for t in range(n_s)]
    for n in range(len(organize['equalities'])):
        if organize['equalities'][n]:
            organize['equalities'][n] = [[eq + t*n_eq for eq in organize['equalities'][n]] for t in range(n_s)]
    for n in range(len(organize['inequalities'])):
        if organize['inequalities'][n]:
            organize['inequalities'][n] = [[ineq + t*n_ineq for ineq in organize['inequalities'][n]] for t in range(n_s)]
    for n in range(len(organize['building']['r'])):
        organize['building']['r'][n] = [organize['building']['r'][n] + t*n_ineq for t in range(n_s)]
    for n in range(len(organize['transmission'])):
        if organize['transmission'][n] is None:
            organize['transmission'][n] = [None for t in range(n_s)]
        else:
            organize['transmission'][n] = [organize['transmission'][n] + t*n_ineq for t in range(n_s)]
    return organize

def count_ic(gen, qp, n_g, n_b, n_l, n_fl):
    """Initial condition for each generator and storage."""
    n_ic = 0
    for i in range(n_g):
        if 'ramp' in gen[i]:
            qp['organize']['ic'][i] = n_ic
            n_ic += 1
        if gen[i]['type'] =='HydroStorage':
            qp['organize']['hydro'].append(i)
            n_ic += 1#second initial condition for the SOC fo the resrvior (1st was for power output)
    for i in range(n_b):#all buildings have an initial temperature state
        qp['organize']['ic'][n_g+n_l+i] = n_ic 
        n_ic += 1#initial condition state
    for i in range(n_fl): #all fluid water loops have an initial temperature state
        qp['organize']['ic'][n_g+n_l+n_b+i] = n_ic 
        n_ic += 1 #initial condition state
    return qp, n_ic


def count_states(gen_all, subnet, options, n_g, n_b, n_l, fluid_loop, dt, x_l, op, qp):
    #organize the order of non-initial condition states
    #states for each generator/storage at t=1
    #spinning reserve for generator/storage at t=1 if option is selected
    #states for each transmission line/pipe at t=1
    #state or power loss in heating and cooling energy balances
    #state for spinning reserve shortfall (target - cumulative of all active generators) 
    #repeat order of generators and lines for t = 2:n_s
    lb = []
    ub = []
    n_fl = len(fluid_loop)
    n_ic = x_l+0
    for i in range(n_g):
        gen = gen_all[i]
        if dt == None and gen['type'] =='HydroStorage':
            s = 1  # Storage treated as generator with 1 state.
            lb.append(gen['x']['lb'])
            ub.append(gen['x']['ub'])
            if 's' in gen_all[i]:  # Spill flow.
                s = 2
                lb.append(gen['s']['lb'])
                ub.append(gen['s']['ub'])
        elif dt == None and gen['type'] in ['Storage','ThermalStorage','ElectricStorage','HydrogenStorage']:
            # Ideal storage is treated as generator with 1 state
            # (additional power output relative to 1st dispatch).
            s = 1
            lb.append(-gen['ramp']['b'][0])
            ub.append(gen['ramp']['b'][1])
            if 'y' in gen:
                # Storage treated as generator with 2 states (additional
                # power output relative to 1st dispatch and charging
                # penalty).
                s = 2
                lb.append(0)
                ub.append((1/gen['stor']['charge_eff'] - gen['stor']['disch_eff']) * gen['ramp']['b'][1])
        elif gen['type'] in ['ElectricGenerator','CombinedHeatPower','Chiller','Heater','CoolingTower','Electrolyzer','HydrogenGenerator']:
            if op=='b':
                f=1
            else:
                f=0
            states = gen['states'][f]
            s = len(states)
            for k in states:
                lb.append(gen[k]['lb'][f])
                ub.append(gen[k]['ub'][f])
            qp['const_cost'][i] = gen['const_cost']
            if gen['start_cost'] > 0:
                qp['organize']['dispatchable'][i] = True
            elif 'const_demand' in gen and len(list(gen['const_demand'].keys()))>0 and any([gen['const_demand'][n]!=0 for n in gen['const_demand']]):
                qp['organize']['dispatchable'][i] = True
            elif qp['const_cost'][i] > 0 or gen[states[0]]['lb'][1]>0:
                # First state has a non-zero lower bound for
                # second optimization or a non-zero cost at an
                # output of 0.
                qp['organize']['dispatchable'][i] = True
            elif gen['type'] in ['ElectricStorage','ThermalStorage','HydrogenStorage'] and 'y' in gen:
                qp['organize']['storage_w_penalty'][i] = True
        else: #Utilities, Market, Tradepoint, ACDCconverter,...
            states = gen['states'][0]
            s = len(states)
            for k in states:
                lb.append(gen[k]['lb'])
                ub.append(gen[k]['ub'])
                
        # Output is sum of multiple states at each timestep.
        if s>0:
            qp['indices'][i][0] =  [x_l + k for k in range(s)]

        
        if gen['type'] == 'Utility' and gen['source']=='electricity' and s == 2:
            qp['organize']['out_vs_state'][i] = [1,-1]
        elif gen['type'] == 'ACDCConverter':
            # Value is the total transfer from AC to DC.
            if len(gen['output']['e'][0])==1:
                qp['organize']['out_vs_state'][i] = [1]
            else:
                qp['organize']['out_vs_state'][i] = [1,-1]
        elif gen['type'] in ['Storage','ThermalStorage','ElectricStorage','HydrogenStorage']:
            # Output state for storage is only state of charge
            # (power in the case of hydro).
            qp['organize']['out_vs_state'][i] = [1]
            qp['organize']['out_vs_state'][i].extend([0 for s in range(len(qp['indices'][i][0])-1)])
        else:
            qp['organize']['out_vs_state'][i] = [1 for k in range(s)]
        x_l += s
        if options['spin_reserve']:
            if gen['type'] == 'HydroStorage':
                lb.append(0)
                ub.append(gen['max_gen_capacity'])
            elif gen['type'] == 'ElectricStorage':
                lb.append(-gen['stor']['peak_charge'])
                ub.append(gen['stor']['peak_disch'])
            elif gen['type'] in ['ElectricGenerator', 'CombinedHeatPower', 'HydrogenGenerator']:
                lb.append(0)
                ub.append(gen['ub'])
            qp['organize']['spin_reserve_states'][i] = x_l
            x_l = x_l+1 

    qp, x_l, lb, ub = count_trans_lines(subnet, qp, x_l, lb, ub, n_g, gen_all)
    if options['spin_reserve'] and any([not qp['organize']['spin_reserve_states'][i] is None for i in range(n_g)]):
        qp['organize']['spin_reserve_states'].append(x_l) #spinning reserve shortfall at t=1
        qp['organize']['spin_reserve_states'].append(x_l+1) #spinning reserve provided as ancillary service at t=1
        x_l += 2
        lb.extend([0,0])
        ub_sr = 0
        for i in range(n_g):
            if qp['organize']['spin_reserve_states'][i] !=None:
                ub_sr += ub[qp['organize']['spin_reserve_states'][i]-n_ic]
        ub.extend([ub_sr,ub_sr])
    qp['organize']['heat_vented'], x_l, lb, ub = vented_energy(gen_all, subnet, options['excess_heat'], x_l, lb, ub, 'h')
    qp['organize']['cool_vented'], x_l, lb, ub = vented_energy(gen_all, subnet, options['excess_cool'], x_l, lb, ub, 'c')
    
    # All buildings have an initial temperature state.
    for i in range(n_b):
        # Output state for building is temperature.
        qp['indices'][n_g+n_l+i][0] = [x_l, x_l+1, x_l+2, x_l+3, x_l+4, x_l+5]
        qp['organize']['out_vs_state'][n_g+n_l+i] = [1,0,0,0,0,0]
        # Add 6 states: temperature, heating, cooling, exceeding upper
        # comfort zone, exceeding lower comfort zone, deviation from last temperature.
        x_l += 6
        # Don't let building below 10 degrees C.
        lb.extend([10, 0, 0, 0, 0, 0])
        # Building stays below 35 degrees C, and excess temperature is
        # less than 10 degrees.
        ub.extend([35, 1e5, 1e5, 10, 10, 10])
    for i in range(n_fl):  #all fluid loops have 1 state
        # qp['organize']['states'][n_g+n_l+n_b+i] = [x_l+1]
        qp['indices'][n_g+n_l+n_b+i][0] = [x_l] #output state for fluid loop is temperature
        qp['organize']['out_vs_state'][n_g+n_l+n_b+i] = [1]
        x_l += 1 # 1 states: Temperature of return water
        lb.append(fluid_loop[i]['nominal_return_temperature']-fluid_loop[i]['temperature_range']) #Temperature in C
        ub.append(fluid_loop[i]['nominal_return_temperature']+fluid_loop[i]['temperature_range']) #Temperature in C
    return qp, lb, ub


def count_trans_lines(subnet, qp, x_l, lb, ub, n_g, gen):
    # States for transmission lines.
    for net in subnet['network_names']:
        if len(subnet[net]['line']['node1'])>0:
            limit = subnet[net]['line']['limit']
            if net == 'Hydro':
                eff = []
                minimum = subnet[net]['line']['minimum']
            else:
                eff = subnet[net]['line']['eff']
                minimum =[0 for i in range(len(limit))]
            for i in range(len(limit)):
                line = subnet[net]['line']['number'][i]
                qp['indices'][n_g+line][0] = [x_l] #no +1 because index
                if eff == [] or len(eff[i])==1: #uni-directional transfer, or river segment, 1 state for each line
                    qp['indices'][n_g+line][0] = [x_l]
                    lb.append(minimum[i])
                    ub.append(limit[i][0])
                    x_l += 1
                else: #bi-directional transfer, 3 states for each line(state of the line and penalty term in each direction)
                    qp['indices'][n_g+line][0] = [x_l, x_l+1, x_l+2]
                    lb.extend([-limit[i][1],0,0])
                    ub.extend([limit[i][0],limit[i][0]*(1-eff[i][0]), limit[i][1]*(1-eff[i][1])])
                    x_l = x_l+3                  
    return qp, x_l, lb, ub


def vented_energy(generators, subnet, vent, x_l, lb, ub, param):
    """This function adds states at each node to allow purposeful energy
    discharge (venting heat or cooling). Returns a list of vent states.

    Positional arguments:
    generators - (list of Component) List of components in the plant.
    subnet 
    vent - (bool) Whether venting is allowed.
    x_l - (int) Index of last state x.
    lb - (list of float) Lower bound for each state so far.
    ub - (list of float) Upper bound for each state so far.
    param - (str) 'h' or 'c', indicating which type of thermal energy is
        being vented.
    """
    if param == 'h':
        net = 'district_heat'
    elif param == 'c':
        net = 'district_cool'
    gen_names = [generators[i]['name'] for i in range(len(generators))]
    
    if net in subnet['network_names']:
        n_nodes = len(subnet[net]['nodes'])
        energy_vented = [[] for i in range(n_nodes)]
        if vent:
            # Find maximum heat production possible.
            max_gen = 0
            for gen in generators:
                if param in gen['output']:
                    if gen['type'] in ['Storage','ThermalStorage','ElectricStorage','HydrogenStorage']:
                        max_gen = max_gen + gen['stor']['peak_disch']
                    else:
                        if param == 'h' and gen['type'] == 'CombinedHeatPower':
                            max_gen += gen['max_heat']
                        elif param in gen['output'] and gen['output'][param][-1][0] > 0:
                            max_gen += gen['ub']
            # Assume heat can be lost at any node in the network that has a
            # device producing heat.
            
            vent_nodes = 0
            # Matrix for the state associated with venting heat at each
            # district heating node, at each timestep.
            for i_node in range(n_nodes):
                # Identify generators at this node.
                for g_name in subnet[net]['equipment'][i_node]:
                    i_gen = gen_names.index(g_name)
                    if 'h' in generators[i_gen]['output']:
                        # Add single state for heat that is vented to make
                        # energy equality true.
                        energy_vented[i_node].append(x_l + vent_nodes)
                        vent_nodes += 1
                        break
            x_l += vent_nodes
            lb.extend([0 for i in range(vent_nodes)])
            ub.extend([max_gen for i in range(vent_nodes)])
    else:
        energy_vented = []
    return energy_vented, x_l, lb, ub


def count_equalities(gen, subnet, sr, organize, ic, end_soc, dt):
    """Equality constraints:
    initial conditions for each generator and storage device
    electric energy balance at each electric subnet node at t=0, including transmission lines
    heat balance at each district heat subnet node at t=0
    any generator link equalitites (linking states within a generator)
    repeat power balance equalities and link equalities at each step

    INPUTS: 
    gen       -list of generator components
    subnet    -sub network object
    sr        -boolean indicating if you have spinning reserve requirements
    ic        -vector of initial conditions
    end_soc   -desired state of charge for storage at the end of the horizon
    dt        -Time interval of each step

    OUTPUTS:
    organize  -updated qp['organize'] structure
    ec        -end conditions vector
    """

    r_eq = ic #row index of the a_eq matrix and b_eq vector

    #the following puts together the energy balance equations
    # 1 energy/mass balance equation for each subnet node
    # nodes were agregated if their line efficiencies were 1
    for net in subnet['network_names']:
        n = len(subnet[net]['nodes'])
        for i in range(n):
            organize['balance'][net][i] = r_eq
            # Note any demands at this node.
            # organize['demand'][net].append(subnet[net]['load'][i])
            r_eq += 1 # There is an energy/mass balance at this node.

    n_g = len(gen)
    ec = []
    for i in range(n_g):
        #link is a field if there is more than one state and the states are linked by an inequality or an equality
        if 'link' in gen[i] and 'eq' in gen[i]['link']:
            m = len(gen[i]['link']['beq'])  # only hydro has an equality constraint (flow to power conversion)
            organize['equalities'][i] = [r_eq+j for j in range(m)]
            r_eq += m
        if dt is None:
            if gen[i]['type'] == 'HydroStorage':
                organize['hydro'].append(i)
                organize['hydro_dr_line'].append(gen[i]['hydro']['down_river'])
            if 'electrical' in subnet['network_names'] and sr and gen['type'] in ['ElectricGenerator', 'CombinedHeatPower', 'HydrogenGenerator', 'ElectricStorage', 'HydroStorage']:
                organize['spin_row'][i] = r_eq
                r_eq = r_eq+1
        elif not end_soc=='flexible':
            if 'stor' in gen[i]:
                ec.append(i) #special case of final state-of-charge equal to initial state or fixed value
    n_eq = r_eq -ic
    return organize, n_eq, ec
#end of function equality_constraints

def count_inequalities(gen, subnet, sr, organize, n_b, dt):
    ## inequality constraints:
    # 2 ramping constriants for each generator at each timestep (ramp up, ramp down)
    # constraints for each energy storage
    # 2 constraints for each bi-directional transmission line to prevent negative losses
    # repeat all of the above for each time
    #INPUTS:
    #gen        -list of generator components
    #subnet     -sub network
    #sr         -boolean indicating if you include spinning reserve
    #organize   -the organization of matrices from within qp
    #n_b         -integer number of buildings
    #dt          -time interval of each step
    #OUTPUTS:
    #organize   -updated ogranization indices of matrices
    n_g = len(gen)
    r = 0 # row index of the A matrix and b vector
    ramping = [None for i in range(n_g)]
    spin_row = [None for i in range(n_g)]
    #agregate spinning reserve shortfall
    #currently only implemented for electric power
    if 'electrical' in subnet['network_names'] and sr:
        organize['spin_reserve'] = r
        r = r+1 #inequality for net spinning reserve (total of all individual generator spinning reserves)
    if not dt is None:
        #ramping and generator inequalities        
        for i in range(n_g):
            if 'ramp' in gen[i]:
                ramping[i] = r
                r = r+2
            if 'link' in gen[i] and 'ineq' in gen[i]['link']:
                m = len(gen[i]['link']['bineq'])
                organize['inequalities'][i] = [r+j for j in range(m)]
                r += m
            if 'electrical' in subnet['network_names'] and sr and gen['type'] in ['ElectricGenerator', 'CombinedHeatPower', 'HydrogenGenerator', 'ElectricStorage', 'HydroStorage']:
                spin_row[i] = r# constraints, ramping, capacity
                r = r+2
    else: #single timestep matrices
        #charging penalty eqn
        for i in range(n_g):
            if 'stor' in gen[i] and not gen[i]['type'] == 'HydroStorage':
                organize['inequalities'][i] = [r]
                r = r+1
    #transmission line inequalities (penalty terms)
    for net in subnet['network_names']:
        if 'line_eff' in subnet[net]:
            eff = subnet[net]['line']['eff']
            for i in range(len(eff)):
                if len(eff[i]) == 1 or eff[i][1] == 0: #uni-directional transfer, 1 state for each line
                    #do noting, no ineqaulities linking penalty states
                    pass
                else: #bidirectional power transfer
                    organize['transmission'][subnet[net]['line']['number'][i]] = r
                    r = r+2
    
    for i in range (n_b):
        organize['building']['r'][i] = r
        r = r+8 # 8 total ineqaulities per building plus two handled with lb & ub

    #number of generator inequality constraints and energy imbalances at each time step will be r
    # there are 2 ramping constraints on each generator/storage
    for n in range(n_g):
        if not ramping[n] is None:
            organize['ramp_up'][n] = [ramping[n]+t*r  for t in range(len(dt))]
            organize['ramp_down'][n] = [ramping[n]+t*r+1  for t in range(len(dt))]
        if not spin_row[n] is None:
            if dt is None:
                organize['spin_row'][n] = spin_row[n]
            else:
                organize['spin_row'][n] = [spin_row[n]+t*r for t in range(len(dt))]
    return organize, r


def generator_equalities(gen_all, subnet, a_eq, b_eq, h, f, organize, indices, dt, op):
    #this function loads generators/chillers/other components into the appropriate energy balance of a_eq
    #INPUTS:
    #gen_all        -list of generators and components
    #subnet         -the subnetwork you are working with
    #a_eq           -the Aeq matrix
    #b_eq           -the b_eq matrix in Aeq*x = b_eq
    #h              -a diagonal matrix of quadratic costs
    #f              -a matrix of linear costs
    #organize       -organization of constriants
    #dt             -vector of delta time
    #op             -string denoting which optimization fit curves are used ('a' or 'b')
    #OUPUTS:
    #a_eq           -a_eq matrix with equality constraints filled in
    #b_eq           -b_eq matrix with equality constraints filled in
    #h              -diagonal matrix with some cost constraints filled in
    #f              -linear cost matrix with some values filled in
    n_s = len(dt)
    gen_names = [gen_all[i]['name'] for i in range(len(gen_all))]
    for net in subnet['network_names']:
        out = subnet[net]['abbreviation']
        if net == 'hydro':
            a_eq = hydro_equalities(gen_all, subnet, a_eq, organize, indices, dt)
        else:
            for n in range(len(subnet[net]['nodes'])):
                r_eq = organize['balance'][net][n]
                # Only things in equip should have an output or input in this
                # network (electric, heating, cooling).
                equip = subnet[net]['equipment'][n]
                for e_name in equip:
                    k = gen_names.index(e_name)
                    gen = gen_all[k]
                    # link is a field if there is more than one state and the
                    # states are linked by an inequality or an equality.
                    if 'link' in gen and 'eq' in gen['link']:
                        for t in range(n_s):
                            for j in organize['equalities'][k][t]:
                                for z in range(len(gen['link']['eq'][j])):
                                    a_eq[j][indices[k][t+1][z]] = gen['link']['eq'][j][z]
                                b_eq[j] = gen['link']['b_eq'][j]
                    if 'stor' in gen and not gen['type'] == 'HydroStorage':
                        eff = gen['stor']['disch_eff']
                        for t in range(n_s):
                            r_eq = organize['balance'][net][n][t]
                            a_eq[r_eq][indices[k][t+1][0]] = -eff/dt[t]  # State of charge at t.
                            if 'y' in gen['states'][0]:
                                a_eq[r_eq][indices[k][t+1][1]] = -1/dt[t]  # Charging penalty at t.
                            soc_prev = indices[k][t][0]# State of charge at IC.
                            a_eq[r_eq][soc_prev] = eff/dt[t]  # State of charge at t-1.
                    elif not indices[k][1][0] is None:
                        if len(gen['output'][out])>1 and op == 'b':
                            gen_output = gen['output'][out][1]
                        else:
                            gen_output = gen['output'][out][0]

                        if len(gen['states'])>1 and op == 'b':
                            state_names = gen['states'][1]
                        else: 
                            state_names = gen['states'][0]
                        if gen['type'] in ['ElectricGenerator','CombinedHeatPower','Chiller','Heater','CoolingTower','Electrolyzer','HydrogenGenerator']:
                            fit=0
                            if op=='b':
                                fit=1
                            if len(gen['output'][out])>1:
                                gen_output = gen['output'][out][fit]
                            else:
                                gen_output = gen['output'][out][0]
                            state_names = gen['states'][fit]
                            for j in range(len(state_names)):
                                z = min([j,len(gen_output)-1])
                                for t in range(n_s):
                                    r_eq = organize['balance'][net][n][t]
                                    h[indices[k][t+1][j]] = gen[state_names[j]]['h'][fit]
                                    f[indices[k][t+1][j]] =  gen[state_names[j]]['f'][fit]
                                    a_eq[r_eq][indices[k][t+1][j]] = gen_output[z]
                        else:
                            for t in range(n_s):
                                states = indices[k][t+1]
                                for j in range(len(states)):
                                    z = min([j,len(gen_output)])
                                    r_eq = organize['balance'][net][n][t]
                                    h[states[j]] = gen[gen['states'][0][j]]['h']
                                    f[states[j]] =  gen[gen['states'][0][j]]['f']
                                    a_eq[r_eq][states[j]] = gen_output[z]

                # Any heating loss term to balance equality.
                if net == 'district_heat' and organize['heat_vented'][n]:
                    for t in range(n_s):
                        a_eq[organize['balance'][net][n][t]][organize['heat_vented'][n][t]] = -1
                # Any cooling loss term to balance equality.
                if net == 'district_cool' and organize['cool_vented'][n]:
                    for t in range(n_s):
                        a_eq[organize['balance'][net][n][t]][organize['cool_vented'][n][t]] = -1                
    return a_eq, b_eq, h, f
#end of function generator_equalities

def hydro_equalities(gen, subnet, a_eq, organize, indices, dt):
    """This function loads the mass and energy balances of the hydro network"""
    n_s = len(dt)
    n_g = len(gen)
    downriver = subnet['hydro']['line']['node2'] #node names of the downriver node
    for i in range(n_g):
        if gen[i]['type'] == 'HydroStorage':
            n = gen[i]['subnet_node']['hydro']
            index_dr = gen[i]['hydro']['down_river'] #lines leaving this node, i.e. this node is the upriver node (should be at most 1)
            if subnet['hydro']['nodes'][n] in downriver:
                index_ur = subnet['hydro']['line']['number'][subnet['hydro']['up_river'][n]]
            else:
                index_ur = [] #no upstream nodes
            for t in range(n_s):
                ## Mass balance
                req = organize['balance']['hydro'][n][t]
                a_eq[req][indices[i][t+1][1]] = -12.1/dt[t] #SOC at t in acre-ft / hours converted to ft^3/s:  43560 ft^3/acre-ft * 1 hr / 3600s = 12.1 cfs per acre-ft/hr
                if t==0:
                    a_eq[req][organize['ic'][i]+1] = 12.1/dt[t]#SOC at IC is 1 after dam power IC
                else:
                    a_eq[req][indices[i][t][1]] = 12.1/dt[t]
                #river segments flowing into this node
                for j in range(len(index_ur)):
                    T = subnet['hydro']['line']['time'][subnet['hydro']['up_river'][n][j]]
                    tt = sum(dt[0:t])
                    if tt<=T:                           
                        pass
                        #Do nothing; the inflow rate will be updated in update_matrices
                    elif tt>T and tt<=T+dt[0]:#between initial condition & first step
                        frac = (tt-T)/dt[0] #portion of flow from step 1, remainder from  SourceSink + (1-frac)*Inflow(t=1) : subtracted from beq in update matrices
                        a_eq[req][indices[n_g+index_ur[j]][1]]= frac # Qupriver at step 1, 
                    else:
                        step = 1
                        while tt>(T+sum(dt[0:step])):
                            step = step+1
                        frac = (tt-(T+sum(dt[0:step-1])))/dt[step] #portion of flow from step, remainder from previous step
                        a_eq[req][indices[n_g+index_ur[j]][step]]= frac # Qupriver at t - floor(T)
                        a_eq[req][indices[n_g+index_ur[j]][step-1]]= (1-frac) # Qupriver at t - ceil(T)
                #water flow out of the node
                a_eq[req][indices[n_g+index_dr][t+1]]= -1 #Qdownriver,  
                ## convert power to outflow (other part of balance is done in Generator Equalities when doing the electric network, this is the - Qdownriver
                a_eq[organize['equalities'][i][t]][indices[n_g+index_dr][t+1]]= -1 # Power/(eff*head*84.76) + Spill - Qdownriver = 0
        else:
            pass
            ## add water district here
    return a_eq

def end_state_constraint(all_gen, end_soc, a_eq, b_eq, indices, ec):
    #INPUTS:
    #end_soc        -the state of charge for storage at the last timestep
    #ec             -end condition indices
    #OUTPUTS:
    #a_eq            -equality matrix in Aeq*x = b_eq
    #b_eq            -equality matrix in Aeq*x = b_eq

    n = len(b_eq)-len(ec)
    for j in range(len(ec)):
        i = ec[j]
        if not isinstance(end_soc, str):
            a_eq[n][indices[i][-1]] = 1
            b_eq[n] = end_soc[i]
        elif end_soc=='initial':
            b_eq[n] = 0
            if all_gen[i]['type'] == 'HydroStorage':
                a_eq[n][indices[i][0]+1] = 1
                a_eq[n][indices[i][-1]+1] = -1
            else:
                a_eq[n][indices[i][0]] = 1
                a_eq[n][indices[i][-1]] = -1
        n +=1
    return a_eq, b_eq

def generator_inequalities(gen_all, amat, bmat, organize, indices, dt):
    #this function adds the generator state inequality constraints
    n_g = len(gen_all)
    n_s = len(dt)
    for i in range(n_g):
        gen = gen_all[i]
        #ramping
        if not organize['ramp_up'][i] is None:
            for t in range(n_s):
                up = organize['ramp_up'][i][t]
                down = organize['ramp_down'][i][t]
                #if storage, ramping only affects 1st states
                ramp_states = indices[i][t+1]
                if gen['type'] in ['Storage','ThermalStorage','ElectricStorage','HydrogenStorage']:
                    ramp_states = [ramp_states[0]]
                for s in ramp_states:
                    amat[up][s] = 1/dt[t] #ramp up
                    amat[down][s] = -1/dt[t] #ramp down
                if t==0:  # Ramping from initial condition.
                    amat[up][organize['ic'][i]] = -1/dt[t]  # Ramp up.
                    amat[down][organize['ic'][i]] = 1/dt[t]  # Ramp down.
                else: #condition at previous time step
                    ramp_states0 = indices[i][t]
                    if gen['type'] in ['Storage','ThermalStorage','ElectricStorage','HydrogenStorage']:
                        ramp_states0 = [ramp_states0[0]]
                    for s in ramp_states0:
                        amat[up][s] = -1/dt[t] #ramp up
                        amat[down][s] = 1/dt[t] #ramp down
                bmat[up] = gen['ramp']['b'][0] #ramp up
                bmat[down] = gen['ramp']['b'][1] #ramp down
        #inequality constraints
        if not organize['inequalities'][i] is None:
            
            for t in range(n_s):
                ineq_row = organize['inequalities'][i][t]
                for k in range(len(ineq_row)):
                    if k == 0 and gen_all[i]['type'] in ['ThermalStorage','ElectricStorage'] and 'y' in gen_all[i]['states'][0]:
                        amat[ineq_row[k]][indices[i][t+1][0]] = gen['link']['ineq'][0][0] #soc at t
                        amat[ineq_row[k]][indices[i][t+1][1]] = gen['link']['ineq'][0][1] #charging state at t (-1)
                        if t == 0: #state of charge change from initial condition
                            amat[ineq_row[k]][organize['ic'][i]] = -gen['link']['ineq'][0][0]
                        else:
                            amat[ineq_row[k]][indices[i][t][0]] = -gen['link']['ineq'][0][0] #soc at t-1
                        loss = gen['stor']['self_discharge'] * gen['stor']['usable_size']
                        bmat[ineq_row[k]] = gen['link']['bineq'][k] - loss*(1-gen['stor']['charge_eff'])
                    else:
                        for s in range(len(indices[i][t+1])):
                            amat[ineq_row[k]][indices[i][t+1][s]] = gen['link']['ineq'][k][s] #typically buffer on soc
                        bmat[ineq_row[k]] = gen['link']['bineq'][k]
    return amat, bmat


def spin_reserve_inequalities(gen, subnet, sr, amat, bmat, organize, indices, dt):
    #this function adds spinning reserve inequalities to the A and b matrices (Ax<b)
    #spinning reserve inequalities sum all spinning reserves and individual spinning reserves
    #currently only implemented for electric power
    if 'electrical' in subnet['network_names'] and sr:
        n_g = len(gen)
        n_s = len(dt)
        #total spinning reserve shortfall at each time step
        for t in range(n_s):
            sr_states = [organize['spin_reserve_states'][i][t] for i in range(n_g+1)]
            sr_ancillary = organize['spin_reserve_states'][n_g+1][t]
            for s in sr_states:
                amat[organize['spin_reserve'][t]][s] = -1 #inequality for spinning reserve shortfall: -(shortfall) -sum(sr(i)) + sr_ancillary <= -sr target
            amat[organize['spin_reserve'][t]][sr_ancillary] = 1 #inequality for spinning reserve shortfall: -(shortfall) -sum(sr(i)) +sr_ancillary <= -sr target
        #individual spinning reserve at each time step (limited by ramp rate and peak gen capacity)
        for i in range(n_g):
            if gen[i]['type'] in ['ElectricGenerator', 'CombinedHeatPower', 'HydroStorage', 'HydrogenGenerator']:
                
                for t in range(n_s):
                    states = indices[i][t+1]
                    if gen[i]['type'] == 'HydroStorage':
                        states = states[0]
                    sr_state = organize['spin_reserve_states'][i][t]
                    r = organize['spin_row'][i][t]
                    amat[r][sr_state] = 1/dt[t] #sr+power[t] -power[t-1] <= ramprate*dt
                    for s in states:
                        amat[r][s] = 1/dt[t] 
                    if t==0: #ramping from ic
                        amat[r][organize['ic'][i]] = -1/dt[t] #power at t-1
                    else:
                        states0 = indices[i][t]
                        if gen[i]['type'] == 'HydroStorage':
                            states0 = states0[0]
                        for s in states0:
                            amat[r][s] = -1/dt[t] #power at t-1
                    bmat[r] = gen[i]['ramp']['b'][0] #ramp up constraint
                    amat[r][sr_state] = 1#sr +power <=size
                    amat[r][states] = 1
                    bmat[r] = gen[i]['ub'] #max capacity constraint
        #individual spinning reserve at each time step (limited by discharge rate and storage capacity)
        for i in range(n_g):
            if gen[i]['type'] == 'ElectricStorage':
                for t in range(n_s):
                    sr_state = organize['spin_reserve_states'][i][t] 
                    states = indices[i][t+1]
                    soc = states[0]
                    r = organize['spin_row'][i][t]
                    eff = gen[i]['stor']['dicheff']
                    amat[r][sr_state] = 1 #sr +eff*(soc[t-1] -soc[t])/dt <= peak discharge
                    amat[r][soc] = -eff/dt[t]
                    amat[r+1][sr_state] = 1
                    if t==0: #soc change from ic
                        amat[r][organize['ic'][i]] = eff/dt[t]
                        amat[r+1][organize['ic'][i]] = -eff/dt[t]
                    else:
                        states0 = indices[i][t]
                        soc0 = states0[0]
                        amat[r][soc0] = eff/dt[t] #soc at t-1
                        amat[r+1][soc0] = -eff/dt[t] #soc at t-1
                    bmat[r] = gen[i]['ramp']['b'][2] #peak discharge constraint
    return amat, bmat

def equality_constraints_step(gen, subnet, qp, h):
    #this function loads generators/chiller etc into the appropriate energy balance of a_eq
    organize = qp['organize']
    gen_names = [gen[i]['name'] for i in range(len(gen))]
    for net in subnet['network_names']:
        if not net == 'hydro':
            out = subnet[net]['abbreviation']
            for n in range(len(subnet[net]['nodes'])):
                r_eq = organize['balance'][net][n]
                equip = subnet[net]['equipment'][n]
                for e_name in equip:
                    i = gen_names.index(e_name)
                    gen_i = gen[i]
                    states = qp['indices'][i][0]
                    if 'stor' in gen_i:
                        if out in gen_i['output']:
                            qp['a_eq'][r_eq][states[0]] = gen_i['output'][out][0][0]
                            if not gen_i['type'] == 'HydroStorage'and 'y' in gen_i:# Charging penalty.
                                qp['a_eq'][r_eq][states[0]+1] = -1
                    else:
                        # link is a field for if there is more than one state
                        # and the states are linked by an inequality or an
                        # equality.
                        if 'link' in gen_i and 'eq' in gen_i['link']:
                            req2 = organize['equalities'][i]
                            for j in range(len(req2)):
                                for k in range(len(states)):
                                    qp['a_eq'][req2[j]][states[k]] = gen_i['link']['eq'][j][k]
                                qp['b_eq'][req2[j]] = gen_i['link']['b_eq'][j]
                        if len(gen_i['states']) > 0:
                            if gen_i['type'] in ['ElectricGenerator','CombinedHeatPower','Chiller','Heater','CoolingTower','Electrolyzer','HydrogenGenerator']:
                                gen_output = gen_i['output'][out][-1]
                                state_names = gen_i['states'][-1]
                                for j in range(len(state_names)):
                                    z = min([j,len(gen_output)-1])
                                    h[states[j]] = gen_i[state_names[j]]['h'][-1]
                                    qp['f'][states[j]] = gen_i[state_names[j]]['f'][-1]
                                    qp['a_eq'][r_eq][states[j]] = gen_output[z]
                            else:
                                gen_output = gen_i['output'][out][-1]
                                state_names = gen_i['states'][-1]
                                for j in range(len(state_names)):
                                    z = min([j,len(gen_output)])
                                    h[states[j]] = gen_i[state_names[j]]['h']
                                    qp['f'][states[j]] = gen_i[state_names[j]]['f']
                                    qp['a_eq'][r_eq][states[j]] = gen_output[z]

                # Any heat loss term to balance equality.
                if net == 'district_heat' and qp['excess_heat']==1 and organize['heat_vented'][n]:
                    qp['a_eq'][r_eq][organize['heat_vented'][n][0]] = -1
                if net == 'district_cool' and qp['excess_cool']==1 and organize['cool_vented'][n]:
                    qp['a_eq'][r_eq][organize['cool_vented'][n][0]] = -1    
    return qp, h

def storage_inequalities_step(gen, amat, organize, indices):
    n_g = len(gen)
    for i in range(n_g):
        if 'stor' in gen[i] and not gen[i]['type'] == 'HydroStorage':
            states = indices[i][0]
            r = organize['inequalities'][i][0]
            amat[r][states[0]] = -(1/gen[i]['stor']['charge_eff'] - gen[i]['stor']['disch_eff'])
            amat[r][states[1]] = -1
    return amat

def hydro_equalities_step(gen, subnet, a_eq, organize, indices):
    if 'hydro' in subnet['network_names']:
        n_g = len(gen)
        upriver = subnet['hydro']['line']['node1'] #node names of the downriver node
        uplines = [i for i in range(len(upriver))]

        #equality: additional power/ (hd*eff*84.67) +spillflow - outflow = nominal power flow (from 1st dispatch)
        #this will allow imposition of instream flow constraints later
        for n in range(len(subnet['hydro']['nodes'])):
            i = subnet['hydro']['equipment'][n]
            index_ur = uplines[upriver.index(subnet['hydro']['nodes'][n])] #lines leaving this node, ie this node is the upriver node (should be at most 1)
            line_out = subnet['hydro']['line']['number'][index_ur]
            if gen[i]['type'] == 'HydroStorage':
                r_eq = organize['equalities'][i]
                # states = organize['states'][i]
                # a_eq[r_eq][states[0]] = gen[i]['stor']['power_2_flow']
                a_eq[r_eq][indices[n_g+line_out][0]] = -1 #qdown river (in excess of original solution from multi-time step)
                # if 's' in gen[i]: #spill flow
                #     a_eq[r_eq][states[1]] = 1
    return a_eq
#end of function hydro_equalities_step

def spin_reserve_constraints_step(gen, subnet, sr, a_eq, b_eq, amat, organize, indices):
    #spinning reserve equalities: individual spinning reserves
    #currently only implemented for electric power
    if 'electrical' in subnet['network_names'] and sr==True:
        n_g = len(gen)
        #individual spinning reserve at each time step (limited by ramp rate and peak gen capacity)
        for i in range(n_g):
            if gen[i]['type'] in ['ElectricGenerator', 'CombinedHeatPower', 'HydroStorage', 'ElectricStorage', 'HydrogenGenerator']:
                states = indices[i][0]
                if gen[i]['type'] == 'HydroStorage':
                    states = states[0] #power output only associated with 1st state
                r_eq = organize['spin_row'][i]
                for s in states:
                    a_eq[r_eq][s] = 1
                b_eq[r_eq] = sum(gen[i]['ub']) #max power
        for i in organize['spin_reserve_states'][:n_g+1]:
            if i != None:
                amat[organize['spin_reserve']][i] = -1#inequality for spinning reserve shortfall: -shortfall - sum(sr(i)) + sr(ancillary) <= -sr target
        amat[organize['spin_reserve']][organize['spin_reserve_states'][n_g+1]] = 1 #inequality for spinning reserve shortfall: -shortfall - sum(sr(i)) + sr(ancillary) <= -sr target
    return a_eq, b_eq, amat
#end of function spin_reserve_constraints_step

def line_equalities(subnet, a_eq, organize, indices, n_s, n_g):
    #this function loads generators/chillers etc into the appropriate energy balance of Aeq
    for net in subnet['network_names']:
        if not net== 'Hydro':
            for k in range(len(subnet[net]['line']['node1'])):
                for n in range(len(subnet[net]['nodes'])):
                    if subnet[net]['line']['node1'][k] in subnet[net]['nodes'][n]:
                        n1 = n
                    if subnet[net]['line']['node2'][k] in subnet[net]['nodes'][n]:
                        n2 = n
                line_num = subnet[net]['line']['number'][k]
                direction = subnet[net]['line']['dir'][k]
                if n_s == 0:
                    line_states = indices[n_g+line_num][0]
                else:
                    line_states = indices[n_g+line_num][1]
                if direction == 'dual':
                    if n_s == 0:
                        line_states = indices[n_g+line_num][0]
                        r_eq = organize['balance'][net][n1]
                        a_eq[r_eq][line_states[0]] = -1 #sending node  (this node, i)-->(connected node), is positive, thus positive transmission is power leaving the node, the penalty from b->a is power not seen at a
                        a_eq[r_eq][line_states[1]] = 0
                        a_eq[r_eq][line_states[2]] = -1
                        r_eq2 = organize['balance'][net][n2]
                        a_eq[r_eq2][line_states[0]] = 1 #receiving node (connected node)-->(this node, i), is positive, thus positive power is power entering the node, the penalty from a->b is power not seen at b                
                        a_eq[r_eq2][line_states[1]] = -1
                        a_eq[+r_eq2][line_states[2]] = 0
                    else:
                        for t in range(n_s):
                            line_states = indices[n_g+line_num][t+1]
                            r_eq = organize['balance'][net][n1][t]
                            a_eq[r_eq][line_states[0]] = -1 #sending node  (this node, i)-->(connected node), is positive, thus positive transmission is power leaving the node, the penalty from b->a is power not seen at a
                            a_eq[r_eq][line_states[1]] = 0
                            a_eq[r_eq][line_states[2]] = -1
                            r_eq2 = organize['balance'][net][n2][t]
                            a_eq[r_eq2][line_states[0]] = 1 #receiving node (connected node)-->(this node, i), is positive, thus positive power is power entering the node, the penalty from a->b is power not seen at b                
                            a_eq[r_eq2][line_states[1]] = -1
                            a_eq[+r_eq2][line_states[2]] = 0
                elif direction == 'forward' or direction == 'reverse':#uni-directional transfer
                    if n_s == 0:
                        line_states = indices[n_g+line_num][0]
                        r_eq = organize['balance'][net][n1]
                        a_eq[r_eq][line_states[0]] = -1
                        r_eq2 = organize['balance'][net][n2]
                        a_eq[r_eq2][line_states[0]] = subnet[net]['line']['eff'][k][0]
                    else:
                        for t in range(n_s):
                            line_states = indices[n_g+line_num][t+1]
                            r_eq = organize['balance'][net][n1][t]
                            a_eq[r_eq][line_states[0]] = -1
                            r_eq2 = organize['balance'][net][n2][t]
                            a_eq[r_eq2][line_states[0]] = subnet[net]['line']['eff'][k][0]                        
    return a_eq
#end of function line_equalities

def line_inequalities(subnet, amat, organize, indices, n_s, n_g):
    #transmission:no connection to previous or later time steps, and no dependence on step size
    for net in subnet['network_names']:
        if 'line' in subnet[net] and not len(subnet[net]['line']['eff']) >0:
            eff = subnet[net]['line']['eff']
            for i in range(len(eff)):
                direction = subnet[net]['line']['dir'][i]
                line = subnet[net]['line']['number'][i]
                if direction == 'dual':
                    for t in range(max([n_s,1])):
                        if n_s == 0:
                            states = indices[n_g+line][0]
                            line_row = organize['transmission'][line]
                        else:
                            states = indices[n_g+line][t+1]
                            line_row = organize['transmission'][line][t]
                        amat[line_row][states[0]] = 1-eff[i][0]
                        amat[line_row][states[1]] = -1
                        amat[line_row][states[2]] = 0 #Pab*(1-efficiency) < penalty a to b
                        amat[line_row+1][states[0]] = -(1-eff[i][1])
                        amat[line_row+1][states[1]] = 0
                        amat[line_row+1][states[2]] = -1 #-Pab*(1-efficiency) < penalty b to a
    return amat


def building_constraints(b_names,subnet, a_eq, amat, h, f, organize, indices, dt, n_g, n_l, n_s):
    #States representing building are: Tzone, Heating, Cooling, Excess T, shortfall T, T deviation
    n_b = len(b_names)
    for i in range(n_b):
        e_n = [n for n in range(len(subnet['electrical']['nodes'])) if i in subnet['electrical']['buildings'][n]][0]
        h_n = [n for n in range(len(subnet['district_heat']['nodes'])) if i in subnet['district_heat']['buildings'][n]][0]
        c_n = [n for n in range(len(subnet['district_cool']['nodes'])) if i in subnet['district_cool']['buildings'][n]][0]
        if n_s>0:
            #electric equality            
            organize['building']['electrical_req'][i] = organize['balance']['electrical'][e_n]
            #heating equality
            organize['building']['district_heat_req'][i] = organize['balance']['district_heat'][h_n]
            for t in range(n_s):
                r_eq = organize['building']['district_heat_req'][i][t]
                a_eq[r_eq][indices[n_g+n_l+i][t+1][1]] = -1 #subtract building heating needs from heating energy balance
            #cooling equality
            organize['building']['district_cool_req'][i] = organize['balance']['district_cool'][c_n]
            for t in range(n_s):
                r_eq = organize['building']['district_cool_req'][i][t]
                a_eq[r_eq][indices[n_g+n_l+i][t+1][2]] = -1 #subtract building cooling needs from cooling energy balance
            for t in range(n_s):
                r = organize['building']['r'][i][t]
                #upper bound inequality
                amat[r+4][indices[n_g+n_l+i][t+1][0]] = 1 #upper buffer >= Ti - (Tset + comfort width/2)
                amat[r+4][indices[n_g+n_l+i][t+1][3]] = -1 #upper buffer >= Ti - (Tset + comfort width/2)
                #lower bound inequality
                amat[r+5][indices[n_g+n_l+i][t+1][0]] = -1 #lower buffer >= (Tset - comfort width/2) -Ti
                amat[r+5][indices[n_g+n_l+i][t+1][4]] = -1 #lower buffer >= (Tset - comfort width/2) -Ti
                #positive deviation inequality
                amat[r+6][indices[n_g+n_l+i][t+1][0]] = 1 #T deviation >= (Ti - Tnominal)
                amat[r+6][indices[n_g+n_l+i][t+1][5]] = -1 #T deviation >= (Ti - Tnominal)
                #negative deviation inequality
                amat[r+7][indices[n_g+n_l+i][t+1][0]] = -1 #T deviation >= (Tnominal- Ti)
                amat[r+7][indices[n_g+n_l+i][t+1][5]] = -1 #T deviation >= (Tnominal- Ti)
        else:
            states = indices[n_g+n_l+i][0]
            #electric equality: put demands into electrical (heating and cooling) balances
            r_eq = organize['balance']['electrical'][e_n]
            organize['building']['electrical_req'][i] = r_eq
            #heating equality
            r_eq = organize['balance']['district_heat'][h_n]
            organize['building']['district_heat_req'][i] = r_eq
            a_eq[r_eq][states[1]] = -1 #subtract building heating needs from heating energy balance
            #cooling equality
            r_eq = organize['balance']['district_cool'][c_n]
            organize['building']['district_cool_req'][i] = r_eq
            a_eq[r_eq][states[2]] = -1 #subtract building cooling needs from cooling energy balance
            r = organize['building']['r'][i]
            #upper bound inequality
            amat[r+4][states[0]] = 1 #upper buffer >= Ti - (Tset+comfort width/2)
            amat[r+4][states[3]] = -1 #upper buffer >= Ti - (Tset + comfort width/2)
            #lower bound inequality
            amat[r+5][states[0]] = -1 #lower buffer >= (Tset - comfort width/2) -Ti
            amat[r+5][states[4]] = -1 #lower buffer >= (Tset - comfort width/2) -Ti
            #positive deviation inequality
            amat[r+6][states[0]] = 1 #T deviation >= (Ti - Tnominal)
            amat[r+6][states[5]] = -1 #T deviation >= (Ti - Tnominal)
            #negative deviation inequality
            amat[r+7][states[0]] = -1 #T deviation >= (Tnominal- Ti)
            amat[r+7][states[5]] = -1 #T deviation >= (Tnominal- Ti)
    return a_eq, amat, h, f, organize


def fluid_loop_constraints(gen, fluid_loop, subnet, a_eq, amat, h, f, organize, indices, dt, n_l, n_b, n_s):
    n_g = len(gen)
    n_fl = len(fluid_loop)
    if n_fl>0:
        equip_names = [gen[i]['name'] for i in range(len(gen))]
    
    for i in range(n_fl):
        #first order temperature model: 0 = -T(k) +T(k-1) +dt/capacitance*(energy balance)
        capacitance = fluid_loop[i]['fluid_capacity']*fluid_loop[i]['fluid_capacitance'] #water capacity in kg and thermal capacitance in kJ/kgK to get kJ/K
        delta_temperature = fluid_loop[i]['nominal_supply_temperature'] - fluid_loop[i]['nominal_return_temperature']
        pump_power = fluid_loop[i]['pump_power_per_kgs']/(delta_temperature*fluid_loop[i]['fluid_capacitance']) # (kW_e/kgs) / (K *  (kJ_t/kg*K)) = kW_e/kW_t 
        c_list = [equip_names.index(equip) for equip in subnet['cooling_water']['equipment'][i] if gen[equip_names.index(equip)]['type'] == 'Chiller']
        if n_s>0:
            for t in range(n_s):
                r_eq = organize['balance']['cooling_water'][i][t]
                a_eq[r_eq][indices[n_g+n_l+n_b+i][t+1][0]] = -capacitance/(3600*dt[t]) #-T(k)
                a_eq[r_eq][indices[n_g+n_l+n_b+i][t][0]] = capacitance/(3600*dt[t]) #T(k-1)
                for k in c_list:
                    e_r_eq = organize['balance']['electrical'][gen[k]['subnet_node']['electrical']][t] #electric equality
                    for s in indices[k][t+1]:
                        a_eq[e_r_eq][s] -= pump_power #add water pumping load to electric 'cost' of chiller
                        a_eq[r_eq][s] += pump_power #add water pumping heat to fluid loop
        else:
            #single step optimization
            # Temperature state done in update_1step because of dt: # Aeq(r_eq,chiller/ fan states) = (HeatRejected)/Building(i)['Cap*dt
            r_eq = organize['balance']['cooling_water'][i]
            for k in c_list:
                e_r_eq = organize['balance']['electrical'][gen[k]['subnet_node']['electrical']] #electric equality
                for s in indices[k][0]:
                    a_eq[e_r_eq][s] -= pump_power #add water pumping load to electric 'cost' of chiller
                    a_eq[r_eq][s] += pump_power #add water pumping heat to fluid loop
    return a_eq, amat, h, f, organize
#end of function fluid_loop_constraints


def load_const_demand(const_demand, qp, gen, subnet,  n_s):
    """Update demands and storage self-discharge."""
    n_g = len(gen)
    gen_names = [gen[i]['name'] for i in range(n_g)]
    for net in subnet['network_names']:
        for n in range(qp['network'][net]['nodes']): #run through all the nodes in this network
            equip = subnet[net]['equipment'][n]  #equipment at this node
            c_load = [0 for i in range(n_g)]
            for e_name in equip:
                k = gen_names.index(e_name)
                if 'const_demand' in gen[k]  and net in gen[k]['const_demand']:
                    c_load[k] = gen[k]['const_demand'][net]
            if n_s == 0:
                const_demand[net]['r_eq'][n] =  qp['organize']['balance'][net][n] #balance at this node 
                const_demand[net]['load'][n] = c_load 
            else:
                const_demand[net]['r_eq'][n] =  qp['organize']['balance'][net][n]  #balance at this node (t = 1:nS)
                const_demand[net]['load'][n] = [c_load for t in range(n_s)]
    return const_demand