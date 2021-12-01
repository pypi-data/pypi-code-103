def sort_solution(x, qp, names, gen, date, v_h):
    """
    Organizes the solution vector into a solution matrix where each column is
    for one component, and each row is for one timestep.

    INPUTS:
    qp          - instance of class QP of matrices
    x           - vector of unsorted optimal dispatch setpoints
    names       - dictionary of component, line, building and fluid_loop names
    gen         - list of generators and their attributes
    date        - list of datetime objects for the current and forecast times
    v_h         - value heat from combined heat and power generators when not excess heat

    OUTPUTS:
    solution    - sorted solution of optimal dispatch
    """

    n_s = len(date) - 1  # Numer of steps.
    n_g = len(qp['const_cost'])
    n_b = len(qp['organize']['building']['r'])
    n_l = len(qp['organize']['transmission'])
    
    solution = dict(
        timestamp = date,
        dispatch = [],
        generator_state = {},
        storage_state = {},
        excess_heat = {},
        excess_cool = {},
        line_flow = {},
        line_loss = {},
        building = {},
        fluid_loop = {},
    )
    solution['dispatch'] = sort_dispatch(x,qp)
    solution['generator_state'], solution['storage_state'] = gen_stor_state(gen,names['components'],solution['dispatch'],date)
    for i,k in enumerate(names['lines']):# Power transfer or water flow rate.
        solution['line_flow'][k] = [x[qp['indices'][n_g+i][t+1][0]] for t in range(n_s)]#flow leaving the upstream node (before losses accounted for)
        if len(qp['indices'][n_g+i][1]) > 1:
            solution['line_loss'][k] = [x[qp['indices'][n_g+i][t+1][1]] + x[qp['indices'][n_g+i][t+1][2]] for t in range(n_s)]#add loss terms in both directions
    for i,k in enumerate(names['buildings']):
        solution['building'][k] = {}
        solution['building'][k]['temperature'] = [x[qp['indices'][n_g+n_l+i][t+1][0]] for t in range(n_s)]
        solution['building'][k]['heating'] = [x[qp['indices'][n_g+n_l+i][t+1][1]] for t in range(n_s)]
        solution['building'][k]['cooling'] = [x[qp['indices'][n_g+n_l+i][t+1][2]] for t in range(n_s)]
        solution['building'][k]['heating'] = [v if abs(v)>1e-3 else 0 for v in solution['building'][k]['heating']]
        solution['building'][k]['cooling'] = [v if abs(v)>1e-3 else 0 for v in solution['building'][k]['cooling']]
    for i,k in enumerate(names['fluid_loop']):
        solution['fluid_loop'][k] = [x[qp['indices'][n_g+n_l+n_b+i][t+1][0]] for t in range(n_s)]

    sort_hydro(x,qp,solution,names['hydro'])
    for i,k in enumerate(names['heating_nodes']):
        solution['excess_heat'][k] = [x[qp['organize']['heat_vented'][i][t]] if qp['organize']['heat_vented'][i] else 0 for t in range(n_s)]
    for i,k in enumerate(names['cooling_nodes']):
        solution['excess_cool'][k] = [x[qp['organize']['cool_vented'][i][t]] if qp['organize']['cool_vented'][i] else 0 for t in range(n_s)]
    solution['value_heat'] = v_h
    return solution

def sort_hydro(x,qp,solution,names):
    n_s = qp['organize']['n_s']
    solution['hydro_soc'] = {}
    solution['hydro_spill'] =  {}
    solution['hydro_gen'] =  {}
    solution['hydro_out'] =  {}
    for i,k in enumerate(names):
    # Get SOC of each generator into a matrix for all time steps.
        solution['hydro_gen'][k] = [x[qp['organize']['ic'][qp['organize']['hydro'][i]]]]
        solution['hydro_soc'][k] = [x[qp['organize']['ic'][qp['organize']['hydro'][i]]+1]]
        solution['hydro_gen'][k].extend([x[qp['indices'][qp['organize']['hydro'][i]][t+1][0]] for t in range(n_s)])
        solution['hydro_soc'][k].extend([x[qp['indices'][qp['organize']['hydro'][i]][t+1][1]] for t in range(n_s)])
        solution['hydro_out'][k] = [x[qp['indices'][qp['organize']['hydro_dr_line']][t+1]] for t in range(n_s)]
        if 'hydro_soc_offset' in qp['organize']:
            solution['hydro_soc'][k] = [j + qp['organize']['hydro_soc_offset'][i] for j in solution['hydro_soc'][k]]
        if len(qp['indices'][qp['organize']['hydro'][i]][1]) ==3 or len(qp['indices'][qp['organize']['hydro'][i]][1]) == 5: #has spill flow
            solution['hydro_spill'][k] = [x[qp['indices'][qp['organize']['hydro'][i]][t+1][2]] for t in range(n_s)]
        else:
            solution['hydro_spill'][k] = [0 for t in range(n_s)]
        

def sort_dispatch(x,qp):
    n_g = len(qp['const_cost'])
    n_b = len(qp['organize']['building']['r'])
    n_l = len(qp['organize']['transmission'])
    n_fl = 0
    if 'cooling_water' in qp['organize']['balance']:
        n_fl = len(qp['organize']['balance']['cooling_water'])
    dispatch = [[] for i in range(n_g + n_l + n_b + n_fl)]
    if 'n_s' in qp['organize']:
        n_s = qp['organize']['n_s']
        for i in range(n_g):
            dispatch[i] = sort_gen_disp(x, qp, i)
        for i in range(n_l):# Power transfer or water flow rate.
            dispatch[n_g+i].append(0)
            dispatch[n_g+i].extend([x[qp['indices'][n_g+i][t+1][0]] for t in range(n_s)])
        for i in range(n_b):
            dispatch[n_g+n_l+i].append(0)
            dispatch[n_g+n_l+i].extend([x[qp['indices'][n_g+n_l+i][t+1][0]] for t in range(n_s)])
        for i in range(n_fl):
            dispatch[n_g+n_l+n_b+i].append(0)
            dispatch[n_g+n_l+n_b+i].extend([x[qp['indices'][n_g+n_l+n_b+i][t+1][0]] for t in range(n_s)])
    else:
        dispatch[:n_g] = sort_gen_disp_step(x, qp)
        dispatch[n_g:n_g+n_l] = [x[qp['indices'][n_g+i][0][0]] for i in range(n_l)]# Power transfer or water flow rate.
        dispatch[n_g+n_l:n_g+n_l+n_b] = [x[qp['indices'][n_g+n_l+i][0][0]] for i in range(n_b)]
        dispatch[n_g+n_l+n_b:n_g+n_l+n_b+n_fl] = [x[qp['indices'][n_g+n_l+n_b+i][0][0]] for i in range(n_fl)]
    return dispatch

def sort_gen_disp(x, qp, i):
    n_s = qp['organize']['n_s']
    dispatch = []
    if not qp['indices'][i][-1] is None and not qp['indices'][i][-1][0] is None:
        # Linear mapping between state and output.
        out_vs_state = qp['organize']['out_vs_state'][i]
        if not qp['indices'][i][0][0] is None and x[qp['indices'][i][0][0]] > 2e-4:#Initial conditions
            dispatch.append(x[qp['indices'][i][0][0]])
        else:
            dispatch.append(0)
        for t in range(n_s):
            p = sum([out_vs_state[k] * x[s] for k,s in enumerate(qp['indices'][i][t+1])])# Record this combination of outputs (SOC for storage).
            if abs(p) < 2e-4:
                p = 0  # Added to avoid rounding errors in optimization.
            dispatch.append(p)
    elif isinstance(qp['renewable'][i],(float,int)) or len(qp['renewable'][i])>0:
        dispatch.append(0)
        dispatch.extend(qp['renewable'][i])
    else:
        dispatch = [0 for t in range(n_s+1)]
    return dispatch

def sort_gen_disp_step(x, qp):
    n_g = len(qp['const_cost'])
    dispatch = []
    for i in range(n_g):
        if not qp['indices'][i][-1] is None and not qp['indices'][i][-1][0] is None:
            # Linear mapping between state and output.
            out_vs_state = qp['organize']['out_vs_state'][i]
            p = sum([out_vs_state[k] * x[s] for k,s in enumerate(qp['indices'][i][0])])# Record this combination of outputs (SOC for storage).
            if abs(p) < 2e-4:
                p = 0  # Added to avoid rounding errors in optimization.
            dispatch.append(p)
        elif isinstance(qp['renewable'][i],(float,int)) or len(qp['renewable'][i])>0:
            dispatch.append(qp['renewable'][i])
        else:
            dispatch.append(0)
    return dispatch

def sort_eh(x, qp):
    if 'n_s' in qp['organize']:
        n_s = qp['organize']['n_s']
    n_dh = len(qp['organize']['heat_vented'])
    excess_heat = [[] for n in range(n_dh)]
    for n in range(n_dh):
        if 'n_s' in qp['organize']:
            if qp['organize']['heat_vented'][n]:
                excess_heat[n] = [x[qp['organize']['heat_vented'][n][t]] for t in range(n_s)]
            else:
                excess_heat[n] = [0 for t in range(n_s)]
        else:
            if qp['organize']['heat_vented'][n]:
                excess_heat[n] = x[qp['organize']['heat_vented'][n][0]]
            else:
                excess_heat[n] = 0
    return excess_heat

def sort_ec(x,qp):
    if 'n_s' in qp['organize']:
        n_s = qp['organize']['n_s']
    n_dc = len(qp['organize']['cool_vented'])
    excess_cool = [[] for n in range(n_dc)]
    for n in range(n_dc):
        if 'n_s' in qp['organize']:
            if qp['organize']['cool_vented'][n]:
                excess_cool[n] = [x[qp['organize']['cool_vented'][n][t]] for t in range(n_s)]
            else:
                excess_cool[n] = [0 for t in range(n_s)]
        else:
            if qp['organize']['cool_vented'][n]:
                excess_cool[n] = x[qp['organize']['cool_vented'][n][0]]
            else:
                excess_cool[n] = 0
    return excess_cool


def sort_building_step(x,qp):
    n_g = len(qp['const_cost'])
    n_b = len(qp['organize']['building']['r'])
    n_l = len(qp['organize']['transmission'])
    s_build = dict(
            heating = [[] for i in range(n_b)],
            cooling = [[] for i in range(n_b)],
            temperature = [[] for i in range(n_b)],)
    for i in range(n_b):
        bs = qp['indices'][n_g+n_l+i][0]
        s_build['temperature'][i] = x[bs[0]]
        s_build['heating'][i] = x[bs[1]]
        s_build['cooling'][i] = x[bs[2]]
    return s_build

def gen_stor_state(gen,names,dispatch,date):
    n_s = len(date) -1
    dt = [(date[t+1] - date[t]).total_seconds()/3600 for t in range(n_s)]# Duration of each time segment in hours.
    gs = {}
    ss = {}
    for i,k in enumerate(names):
        if 'stor' in gen[i]:
            ss[k] = [dispatch[i][t+1] for t in range(n_s)]
            sd = soc_2_power(gen[i]['stor'],dispatch[i],dt)
            gs[k] = sd
        else:
            gs[k] = [dispatch[i][t+1] for t in range(n_s)]
    return gs,ss

def soc_2_power(gen,disp,dt):
    ss = [i for i in disp]
    sd = []
    for t in range(len(dt)):
        loss = gen['self_discharge'] * gen['usable_size']*dt[t] # %/hr * capacity (kWh) * time in hours = kWh lost
        d_soc = (ss[t+1] - ss[t]) + loss #kWh add to storage (positive is charging)
        if ss[t+1]>ss[t]:
            sd.append(-d_soc/gen['charge_eff']/dt[t]) # power in kW
        else:
            sd.append(-d_soc*gen['disch_eff']/dt[t]) # power in kW
    return sd