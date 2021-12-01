from eagers.basic.gen_limit import gen_limit
from eagers.config.simulation import CHP_HEAT_VALUE

def gen_marginal_cost(gen, dispatch, scale_cost, dt):
    ''' Finds the capacity and marginal cost for each generation component 
    in three categories: spinning reserve, non-spinning reserve, and demand response
    These categories can be thought of as a: turning up a generator already on,
    b: turning on an inactive generator, and c: turning down an active generator'''
    n = 4 #breaks remaining generator capacity into n segments
    n_s = len(dt)
    n_g = len(gen)
    include = ['ElectricGenerator','CombinedHeatPower','Heater','Electrolyzer','HydrogenGenerator','CoolingTower','Chiller']
    locked = [[True for j in range(n_s+1)] for i in range(n_g)]
    for i in range(n_g):
        if gen[i]['type'] in include:
            locked[i] = [dispatch[i][t]>0 for t in range(n_s+1)]
    margin_cost = {}
    s = {'e':['CombinedHeatPower', 'ElectricGenerator'],'h':['Heater'], 'c':['Chiller']}
    #TODO add other dispatchable components
    for i in range(n_g):
        if gen[i]['type'] in ['CombinedHeatPower', 'ElectricGenerator', 'HydrogenGenerator'] and 'dc' in gen[i]['output']:
            s['dc'] = ['CombinedHeatPower', 'ElectricGenerator']
            # Marginal costs of 'electricity' and 'direct_current' will be lumped together.
            break
    max_out,_,_,_ = gen_limit(gen,dispatch,locked,dt,list(s.keys()))
    for k in list(s.keys()):
        inc = [False for i in range(n_g)]
        # Include the Component at i if its primary output is the type
        # of energy we're finding the marginal cost of.
        for i in range(n_g):
            if gen[i]['type'] in s[k]:
                inc[i] = True
        if any(inc):
            margin_cost[k] = {}
            margin_cost[k]['capacity'] = {}
            margin_cost[k]['cost'] = {}
            margin_cost[k]['capacity']['spin_reserve'] = [[[0 for j in range(n)] for t in range(n_s)] for i in range(n_g)]
            margin_cost[k]['capacity']['non_spin'] = [[[0 for j in range(n)] for t in range(n_s)] for i in range(n_g)]
            margin_cost[k]['capacity']['demand_response'] = [[[0 for j in range(n)] for t in range(n_s)] for i in range(n_g)]
            margin_cost[k]['cost']['spin_reserve'] = [[[0 for j in range(n)] for t in range(n_s)] for i in range(n_g)]
            margin_cost[k]['cost']['non_spin'] = [[[0 for j in range(n)] for t in range(n_s)] for i in range(n_g)]
            margin_cost[k]['cost']['demand_response'] = [[[0 for j in range(n)] for t in range(n_s)] for i in range(n_g)]
            for i in range(n_g):
                if inc[i]:
                    sr = [max_out[k][i][t+1] - dispatch[i][t+1] for t in range(n_s)]
                    for t in range(n_s):
                        if sr[t] > 1e-4:
                            disp_range = [dispatch[i][t+1] + j*(max_out[k][i][t+1] - dispatch[i][t+1])/n for j in range(n+1)]
                            margin_cost[k]['capacity']['spin_reserve'][i][t] = [sr[t]/n for j in range(n)]
                            mc = [piecewise_tangent(gen[i],disp_range[j],scale_cost[i][t]) for j in range(n+1)]
                            margin_cost[k]['cost']['spin_reserve'][i][t] = [(mc[j+1] + mc[j])/2 for j in range(n)]
                            margin_cost[k]['cost']['non_spin'][i][t]= [float('inf') for j in range(n)]
                        else:
                            states = gen[i]['states'][-1]
                            disp_range = [gen[i]['lb'] + j*(gen[i]['ub'] - gen[i]['lb'])/n for j in range(n+1)]
                            if disp_range[0]>0:
                                disp_range.insert(0,0)
                            lb = disp_range[1]
                            cost  = [gen[i][states[0]]['f'][-1]*scale_cost[i][t]]
                            if 'start_cost' in gen[i] and gen[i]['start_cost']>0:
                                cost[0] += gen[i]['start_cost']/lb
                            if 'const_cost' in gen[i] and  gen[i]['const_cost']>0:
                                cost[0] += gen[i]['const_cost']*scale_cost[i][t]/lb
                            if gen[i]['type'] == 'Chiller' and  'electrical' in gen[i]['const_demand']:
                                cost[0] += gen[i]['const_demand']['electrical']*min([margin_cost['e']['cost']['spin_reserve'][j][t][0] for j in range(n_g)])/lb
                            mc = [piecewise_tangent(gen[i],disp_range[j+1],scale_cost[i][t]) for j in range(len(disp_range)-1)]
                            cost.extend([(mc[j+1] + mc[j])/2 for j in range(len(disp_range)-2)])
                            margin_cost[k]['capacity']['non_spin'][i][t] = [disp_range[x+1] - disp_range[x] for x in range(len(disp_range)-1)]
                            margin_cost[k]['cost']['non_spin'][i][t] = cost
                            margin_cost[k]['cost']['spin_reserve'][i][t] = [float('inf') for j in range(len(disp_range)-1)]
    return margin_cost


def sort_mc(margin_cost, out, t_max, off_gen, dt):
    '''
    Five attributes tracked as sorting marginal cost
    %1 = cumulative marginal energy, 
    %2 = cumulative marginal cost, used for interpolating to see which blocks are used
    %3 = Generator that increases output, 
    %4 = time point at which generator increases output, 
    %5 = amount that generator increases output (kW)
    '''
    mc = {'capacity':[],'marginal_cost':[],'generator':[],'timestep':[],'duration':[]}
    if not out in margin_cost and out=='dc' and 'e' in margin_cost:
        out = 'e'
    elif not  out in margin_cost and out=='e' and 'dc' in margin_cost:
        out = 'dc'
    n = 4 # must match n in marginal_cost
    n_g = len(margin_cost[out]['capacity']['spin_reserve'])

    for i in range(n_g):
        if off_gen == None or not i == off_gen:
            for t in range(t_max): #+1 because t_max is an index
                if margin_cost[out]['capacity']['spin_reserve'][i][t][0]>0:
                    for j in range(n):
                        mc['capacity'].append(margin_cost[out]['capacity']['spin_reserve'][i][t][j])
                        mc['marginal_cost'].append(margin_cost[out]['cost']['spin_reserve'][i][t][j])
                        mc['generator'].append(i)
                        mc['timestep'].append(t)
                        mc['duration'].append(dt[t])
    if len(mc['capacity'])>0:
        ind = sorted(range(len(mc['marginal_cost'])), key=mc['marginal_cost'].__getitem__)
        cum_cost = [mc['marginal_cost'][ind[0]]*mc['capacity'][ind[0]]*mc['duration'][ind[0]]]
        cum_energy = [mc['capacity'][ind[0]]*mc['duration'][ind[0]]]
        for i in range(len(ind)-1):
            j = ind[i+1]
            c = cum_cost[-1] + mc['marginal_cost'][j]*mc['capacity'][j]*mc['duration'][j]
            e = cum_energy[-1] + mc['capacity'][j]*mc['duration'][j]
            cum_cost.extend([c])
            cum_energy.extend([e])
        mc_sorted = {'cumulative_energy':cum_energy,'cumulative_cost':cum_cost,'generator':[mc['generator'][i] for i in ind],'timestep':[mc['timestep'][i] for i in ind],'capacity':[mc['capacity'][i] for i in ind],'marginal_cost':[mc['marginal_cost'][i] for i in ind]}
    else:
        mc_sorted = None
    return mc_sorted


def piecewise_tangent(gen,dispatch,scale_cost):
    states = gen['states'][-1]
    p = 0
    j = 0
    while p<dispatch and j < len(states):
        x = min([gen[states[j]]['ub'][-1],dispatch-p])
        p +=x
        j +=1
    mc = (gen[states[j-1]]['f'][-1] + x*gen[states[j-1]]['h'][-1])*scale_cost
    return mc

def locate_node_gen(gen,subnet):
    gen_names = [gen[i]['name'] for i in range(len(gen))]
    gen_loc = {}
    for net in subnet['network_names']: #make sure 'e' and 'dc', and 'h' before 'c'
        net_abbrev = subnet[net]['abbreviation']
        gen_loc[net_abbrev] = [None for i in range(len(gen))]
        for n in range(len(subnet[net]['nodes'])):
            agregate_node = subnet[net]['nodes'][n][0]
            gen_num = [gen_names.index(e_name) for e_name in subnet[net]['equipment'][n]]
            for gn in gen_num:
                gen_loc[net_abbrev][gn] = agregate_node
    return gen_loc

def marginal_node(net_abbrev,gen_num,gen_loc,marginal):
    m_node = {}
    for f in list(marginal.keys()):
        if not f == net_abbrev:
            connect_node = []
            for j in gen_num:
                if not gen_loc[f][j] is None and not gen_loc[f][j] in connect_node:
                    connect_node.append(gen_loc[f][j])
            if len(connect_node)>0:
                m_node[f] = min([marginal[f][j] for j in connect_node])
    return m_node

def node_marginal(gen,subnet,dispatch,scale_cost,v_h):
    net_abbrev = [subnet[net]['abbreviation'] for net in subnet['network_names']]
    marginal = {}
    gen_loc = locate_node_gen(gen,subnet)
    for net in subnet['network_names']: #make sure 'e' and 'dc', and 'h' before 'c'
        net_abbrev = subnet[net]['abbreviation']
        marginal[net_abbrev] = {}
        for n in range(len(subnet[net]['nodes'])):
            agregate_node = subnet[net]['nodes'][n][0]
            marginal[net_abbrev][agregate_node] = None
            gen_num = [i for i in range(len(gen)) if gen_loc[net_abbrev][i] == agregate_node]
            gen_node = [gen[i] for i in gen_num]
            gen_scale = [scale_cost[i] for i in gen_num]
            gen_disp = None
            if not dispatch is None:
                gen_disp = [dispatch[i] for i in gen_num]
            m_node = marginal_node(net_abbrev,gen_num,gen_loc,marginal)
            marginal[net_abbrev][agregate_node] = equip_marginal(gen_node,net_abbrev,gen_disp,gen_scale,m_node,v_h)
    for net in subnet['network_names']:
        net_abbrev = subnet[net]['abbreviation']
        mar_net = [marginal[net_abbrev][an] for an in list(marginal[net_abbrev].keys()) if not marginal[net_abbrev][an] is None]
        max_marginal = [max([mar_net[i][t] for i in range(len(mar_net))]) for t in range(len(mar_net[0]))] #vector of maximum marginal cost anywhere on network at each time step 

        for an in marginal[net_abbrev]:
            if marginal[net_abbrev][an] is None:
                marginal[net_abbrev][an] = [2*j for j in max_marginal]
    return marginal

def equip_marginal(gen,net_abbrev,dispatch,scale_cost,source_marginal,v_h):
    #equipment marginal output cost at a particular node 
    n_g = len(gen)
    if n_g>0:
        n_s = max([len(scale_cost[i]) for i in range(len(scale_cost))])
    chp = [i for i in range(n_g) if gen[i]['type'] == 'CombinedHeatPower']
    e_marginal = [None for i in range(n_g)]
    e_min = [None for i in range(n_g)]
    e_max = [None for i in range(n_g)]
    _, ac_dc_eff,conv = check_acdc(gen,net_abbrev)
    for i in range(n_g):
        include = False
        sc = [k for k in scale_cost[i]]
        if net_abbrev in ('e','dc') and net_abbrev in gen[i]['output'] and gen[i]['enabled'] and gen[i]['type'] in ('CombinedHeatPower', 'ElectricGenerator', 'HydrogenGenerator'):
           include = True 
           if v_h and i in chp:
                sc = [k*(1-CHP_HEAT_VALUE) for k in sc]
        elif net_abbrev in ('h') and gen[i]['enabled'] and gen[i]['type'] in ('CombinedHeatPower', 'Heater'):
            include = True 
            if i in chp:
                sc = [k*CHP_HEAT_VALUE for k in sc]
                if not v_h:
                    sc = [k/4 for k in sc]
        elif net_abbrev in ('c') and gen[i]['enabled'] and gen[i]['type'] == 'Chiller': # Cooling marginal cost. # Chillers are unique because the cost in QP.f is zero, so must have heating or electricity done first.
            include = True 
            sc = None
        elif net_abbrev in ('cw') and gen[i]['enabled'] and gen[i]['type'] == 'CoolingTower': # Cooling marginal cost. # Chillers are unique because the cost in QP.f is zero, so must have heating or electricity done first.
            include = True 
            sc = None
        ##TODO complete water and hydrogen
        elif net_abbrev in ('w') and gen[i]['enabled'] and gen[i]['type'] == 'HydroStorage':
            pass
        elif net_abbrev in ('hy') and gen[i]['enabled'] and gen[i]['type'] == 'Electrolyzer':
            pass
        if include and sc is None: #CHILLER or Cooling Tower
            f = list(gen[i]['output'].keys())
            for s in f:
                if s in source_marginal and all([i<=0 for i in gen[i]['output'][s][-1]]):
                    if not dispatch is None:
                        seg = active_seg(gen[i],dispatch[i])
                    else:
                        seg = [0 for t in range(n_s)]
                    e_marginal[i] = [source_marginal[s][t]*(-gen[i]['output'][s][-1][seg[t]]) for t in range(n_s)]
                    e_min[i] = [-gen[i]['output'][s][-1][0]*j for j in source_marginal[s]]
                    e_max[i] = [-gen[i]['output'][s][-1][-1]*j for j in source_marginal[s]]
        elif gen[i]['type'] == 'Utility' and net_abbrev in gen[i]['output']:
            e_marginal[i] = [gen[i]['x']['f']*j for j in sc]
            e_min[i] = [0.5*j for j in e_marginal[i]]
            e_max[i] = [1.5*j for j in e_marginal[i]]
        elif include or i in conv:
            states = gen[i]['states'][-1]
            if not dispatch is None:
                e_marginal[i] = [m_cost(gen[i], dispatch[i][j], sc[j], source_marginal) for j in range(len(sc))]
            else:
                e_marginal[i] = [m_cost(gen[i], None, sc[j], source_marginal) for j in range(len(sc))]
            e_min[i] = [gen[i][states[0]]['f'][-1]*j for j in sc]
            l_state = gen[i][states[-1]]
            e_max[i] = [(l_state['f'][-1]+l_state['ub'][-1]*l_state['h'][-1])*j for j in sc]
            if i in conv:
                e_marginal[i] = [j/ac_dc_eff[i] for j in e_marginal[i]]
                e_min[i] = [j/ac_dc_eff[i] for j in e_min[i]]
                e_max[i] = [j/ac_dc_eff[i] for j in e_max[i]]
    # return e_marginal, e_min, e_max
    min_marginal = None
    if any([True for j in e_marginal if not j is None ]):
        min_marginal = [min([j[t] for j in e_marginal if not j is None]) for t in range(n_s)]
    return min_marginal

def check_acdc(gen,net_abbrev):
    need_ac_dc = False
    ac_dc_eff = [1 for i in range(len(gen))]
    ac_dc = None
    conv = []
    if net_abbrev == 'e' or net_abbrev == 'dc':
        for gen_i in gen:
            if ('e' in gen_i['output'] and net_abbrev == 'dc') or ('dc' in gen_i['output'] and net_abbrev == 'e'):
                need_ac_dc = True
                break
        if need_ac_dc:
            for gen_i in gen:
                if gen_i['type'] == 'ACDCConverter':
                    ac_dc = {}
                    ac_dc['dc_to_ac_eff'] = abs(gen_i['output']['e'][0][-1])
                    ac_dc['ac_to_dc_eff'] = gen_i['output']['dc'][0][0]
            if not ac_dc is None:
                for i in range(len(gen)):
                    if gen[i]['enabled'] and gen[i]['type'] in ('CombinedHeatPower', 'ElectricGenerator', 'HydrogenGenerator'):
                        if net_abbrev == 'e' and 'dc' in gen[i]['output']:
                            ac_dc_eff[i] = 1/ac_dc['dc_to_ac_eff']
                            conv.append(i)
                        if net_abbrev == 'dc' and 'e' in gen[i]['output'] and ac_dc:
                            ac_dc_eff[i] = 1/ac_dc['ac_to_dc_eff']
                            conv.append(i)
    return ac_dc, ac_dc_eff, conv

def net_marginal_cost(gen,net_abbrev,market,dispatch, scale_cost, dt, v_h):
    """Calculate the marginal cost of energy for each energy network"""
    n_g = len(gen)
    s = []
    ac_dc = None
    
    for gen_i in gen:
        if isinstance(gen_i['output'],dict):
            f = list(gen_i['output'].keys())
            for k in f:
                if k not in s and k in net_abbrev:
                    s.append(k)
        if gen_i['type'] == 'ACDCConverter':
            ac_dc = {}
            ac_dc['dc_to_ac_eff'] = abs(gen_i['output']['e'][0][-1])
            ac_dc['ac_to_dc_eff'] = gen_i['output']['dc'][0][0]

    marginal = {}
    chp = [i for i in range(n_g) if gen[i]['type'] == 'CombinedHeatPower']
    
    if len(chp)>0 and v_h==None:
        v_h = True
    stor_include = {}
    for out in s:
        stor_include[out] = []
    for i in range(n_g):
        if 'stor' in gen[i]:
            f = list(gen[i]['output'].keys())
            stor_include[f[0]].append(i)
    scale = [[i for i in j] for j in scale_cost]
    if 'e' in s or 'dc' in s:
        # Electricity or direct current marginal cost.
        include = []
        dc_to_ac = [1] * n_g
        ac_to_dc = [1] * n_g
        for i in range(n_g):
            if gen[i]['enabled'] and gen[i]['type'] in ('CombinedHeatPower', 'ElectricGenerator', 'HydrogenGenerator'):
                include.append(i)
                if 'dc' in gen_i['output'] and ac_dc:
                    dc_to_ac[i] = 1/ac_dc['dc_to_ac_eff']
                if 'e' in gen_i['output'] and ac_dc:
                    ac_to_dc[i] = 1/ac_dc['ac_to_dc_eff']
        if ac_dc and 'e' in s and 'dc' in s:
            for i in stor_include['dc']:
                dc_to_ac[i] = 1/ac_dc['dc_to_ac_eff']
            for i in stor_include['e']:
                ac_to_dc[i] = 1/ac_dc['ac_to_dc_eff']
            sie_temp = [i for i in stor_include['e']]
            sie_temp.extend(stor_include['dc'])
            stor_include['dc'].extend(stor_include['e'])
            stor_include['e'] = [i for i in sie_temp]
        if v_h:
            for j in chp:
                scale[j] = [k*(1-CHP_HEAT_VALUE) for k in scale[j]]
           
        def adjust_scale(scale,eff):
            sc = []
            for i in range(len(scale)):
                if len(scale[i])==1:
                    sc.append(scale[i][0]*eff[i])
                elif len(scale[i])>1:
                    sc.append([k*eff[i] for k in scale[i]])
                else:
                    sc.append([])
            return sc
        def one_d_list(scale):
            sc = []
            for k in scale:
                if len(k)>0:
                    sc.append(k[0])
                else:
                    sc.append([])
            return sc
        if 'e' in s:
            sc = adjust_scale(scale,dc_to_ac)
            if not dt is None and (dispatch is None or isinstance(dispatch[0],(list))):
                marginal['e'] =  min_max_cost(gen,include,stor_include['e'],sc,dispatch,'e',[],dt)
            else:
                marginal['e'] = m_loop(gen,include,sc,dispatch,'e',None)
        if 'dc' in s:
            sc = adjust_scale(scale,ac_to_dc)
            if not dt is None and (dispatch is None or isinstance(dispatch[0],(list))):
                marginal['dc'] =  min_max_cost(gen,include,stor_include['dc'],sc,dispatch,'dc',[],dt)
            else:
                marginal['dc'] = m_loop(gen,include,sc,dispatch,'dc',None)

    if 'h' in s:
        # Heating marginal cost.
        include = []
        for i in range(n_g):
            if gen[i]['enabled'] and gen[i]['type'] in ['CombinedHeatPower', 'Heater']:
                include.append(i)
        scale = [[i for i in j] for j in scale_cost]
        for j in chp:
            scale[j] = [k*CHP_HEAT_VALUE for k in scale[j]]
            if not v_h:
                scale[j] = [k/4 for k in scale[j]]
        if not dt is None and (dispatch is None or isinstance(dispatch[0],(list))):
            marginal['h'] = min_max_cost(gen,include,stor_include['h'],scale,dispatch,'h',[],dt)
        else:
            marginal['h'] = m_loop(gen,include,one_d_list(scale),dispatch,'h',None)

    if 'c' in s:
        # Cooling marginal cost.
        # Chillers are unique because the cost in QP.f is zero.
        include = []
        for i in range(n_g):
            if gen[i]['enabled'] and gen[i]['type'] == 'Chiller':
                include.append(i)
        if not dt is None and (dispatch is None or isinstance(dispatch[0],(list))):
            marginal['c'] = min_max_cost(gen,include,stor_include['c'],scale_cost,dispatch,'c',marginal,dt)
        else:
            marginal['c'] = m_loop(gen,include,one_d_list(scale_cost),dispatch,'c',marginal)

    if 'w' in s:
        if not dt is None and (dispatch is None or isinstance(dispatch[0],(list))):
            marginal['w'].min = 0
            marginal['w'].max = 1
        else:
            marginal['w'] = 1

    if 'hy' in s:
        marginal['hy'] = marginal['e']

    return marginal


def m_loop(gen, include, scale, step_profile, s, marginal):
    if not include:
        # No generators to be considered in marginal cost.  Return zero.
        return 0
    margin_cost = []
    n_g = len(gen)
    for i in include:
        if step_profile==None:
            sp = None
        else:
            sp = step_profile[i]
        margin_cost.append(m_cost(gen[i],sp,scale[i],marginal))
    m_c = float('nan')
    if not step_profile is None:
        for j in range(len(include)):
            i = include[j]
            if gen[i]['type'] in ['ElectricGenerator', 'CombinedHeatPower', 'Chiller', 'Heater', 'CoolingTower', 'Electrolyzer', 'HydrogenGenerator']:
                lb = gen[i][gen[i]['states'][1][0]]['lb'][-1]
            else:
                lb = gen[i][gen[i]['states'][0]]['lb'] #on or above lower bound
            if step_profile[i]>lb: #on or above lower bound
                if m_c != m_c:
                    m_c = margin_cost[j]
                else:
                    m_c = max([margin_cost[j],m_c])
    if step_profile==None or m_c != m_c: # or m_c==0
        m_c = min(margin_cost)
    for i in range(n_g):
        if gen[i]['type'] == 'Utility' and s in gen[i]['output']:
            if  gen[i]['x']['f']*scale[i]<m_c:
                m_c = gen[i]['x']['f']*scale[i]
    return m_c

def m_cost(gen, set_point, scale, marginal):
    #find the slope of the currently active segment (first segment if no dispatch yet)
    #if it's cost is the output of another kind, e.g. electric chiller, use the electric marginal cost
    states = gen['states'][1]
    seg = active_seg(gen,[set_point])
    m_c = gen[states[seg[0]]]['f'][-1]*scale
    if not set_point is None:
        m_c += (set_point*gen[states[seg[0]]]['h'][-1])*scale
    if m_c == 0:
        for s in list(gen['output'].keys()):
            if all([i<=0 for i in gen['output'][s][-1]]):
                m_c = marginal[s]*(-gen['output'][s][-1][seg[0]])
    m_c = nonneg_marginal(m_c,gen,scale)
    return m_c 

def active_seg(gen,dispatch):
    #find the currently active segment (first segment if no dispatch yet)
    if not dispatch[0] is None:
        states = gen['states'][1]
        seg = [0 for t in range(len(dispatch))]
        for t in range(len(dispatch)):
            set_point = dispatch[t]*1.0
            while seg[t]<len(states)-1 and gen[states[seg[t]]]['ub'][-1]<=set_point:
                set_point -= gen[states[seg[t]]]['ub'][-1]
                seg[t] += 1
    else:
        seg = [0]
    return seg

def nonneg_marginal(m_c,gen,scale):
    if m_c<0: 
        states = gen['states'][1]
        j = 0
        while j<len(states) and m_c<0:
            j = j+1
            m_c = gen[states[j]]['f'][-1]*scale
        if m_c<0:
            m_c = 1e-3
    return m_c

def min_max_cost(gen, include, stor_include, scale, dispatch,s,marginal,dt):
    n_g = len(gen)
    n_s = len(dt)
    min_c = [[0 for t in range(n_s)] for i in range(max([1,len(include)]))]
    max_c = [[0 for t in range(n_s)] for i in range(max([1,len(include)]))]
    charge_index = [False for t in range(n_s)]
    for k in range(len(include)):    
        i = include[k]
        states = gen[i]['states'][-1]
        if gen[i]['type'] == 'Utility':
            min_c[k] = [0.5*gen[i]['x']['f']*j for j in scale[i]]
            max_c[k] = [1.5*gen[i]['x']['f']*j for j in scale[i]]
        else:
            min_c[k] = [gen[i][states[0]]['f'][-1]*j for j in scale[i]]
            l_state = gen[i][states[-1]]
            max_c[k] = [(l_state['f'][-1]+l_state['ub'][-1]*l_state['h'][-1])*j for j in scale[i]]
        if all([j==0 for j in max_c[k]]):
            f = list(gen[i]['output'].keys())
            for out in f:
                conv = [-j for j in gen[i]['output'][out][-1]]
                if all([j>=0 for j in conv]):
                    min_c[k] = [marginal[out]['min']*min(conv) for t in range(n_s)]
                    max_c[k] = [marginal[out]['max']*max(conv) for t in range(n_s)]
        if any([t<0 for t in min_c[k]]):
            j = 0
            while j<len(states) and any([t<0 for t in min_c[k]]):
                j = j+1
                min_c[k] = [gen[i][states[j]]['f'][-1]*st for st in scale[i]]
            for t in range(len(min_c[k])):
                if min_c[k][t]<0:
                    min_c[k][t] = 1e-3
    if not dispatch is None:
        for i in stor_include:
            for t in range(n_s):
                if (dispatch[i][t+1]-dispatch[i][t])>0:
                    charge_index[t] = True
        
        for k in range(len(include)):
            i = include[k]
            for t in range(n_s):
                if charge_index[t] and dispatch[i][t+1]>0:
                    max_c[k][t] = 1.25*max_c[k][t]

    if not dispatch is None and any([any([dispatch[k][j+1]>0 for j in range(n_s)]) for k in include]):
        unnec = True
    else:
        unnec = False
        
    min_on_t = []
    dt_on = []
    max_on_t = []
    for t in range(n_s):
        if unnec and any([dispatch[k][t+1]>0 for k in include]):
            min_on_t.append(min([min_c[k][t] for k in range(len(include)) if dispatch[include[k]][t+1]>0]))
            max_on_t.append(max([max_c[k][t] for k in range(len(include)) if dispatch[include[k]][t+1]>0]))
            dt_on.append(dt[t])
        elif not unnec:
            if len(include)==0:
                min_on_t.append(0)
                max_on_t.append(0)
            else:
                min_on_t.append(min([min_c[k][t] for k in range(len(include))]))
                max_on_t.append(max([max_c[k][t] for k in range(len(include))]))
            dt_on.append(dt[t])
    m_c = {}
    m_c['min'] = sum([min_on_t[i]*dt_on[i] for i in range(len(dt_on))])/sum(dt_on)
    m_c['max'] = sum([max_on_t[i]*dt_on[i] for i in range(len(dt_on))])/sum(dt_on)

    ac_dc = None
    for i in range(n_g):
        if gen[i]['type']== 'ACDCConverter':
            ac_dc = gen[i]
            break
    for i in range(n_g):
        if gen[i]['type']== 'Utility':
            sc = None
            if s in gen[i]['output']:
                sc = scale[i]
            elif not ac_dc is None and s == 'e' and 'dc' in gen[i]['output']:
                sc = [j*abs(ac_dc['output']['e'][0][-1]) for j in scale[i]]
            elif not ac_dc is None and s == 'dc' and 'e' in gen[i]['output']:
                sc = [j*ac_dc['output']['dc'][0][0] for j in scale[i]]
            if not sc is None:
                if len(include)==0:
                    m_c = bound_by_utility(None,gen[i],sc)
                else:
                    m_c = bound_by_utility(m_c,gen[i],sc)
    return m_c

def bound_by_utility(m_c,gen,scale):
    if m_c is None:
        m_c = {}
        m_c['max'] = 1.5*gen['x']['f']*max(scale)
        if 'y' in gen:
            m_c['min'] = -gen['y']['f']*min(scale)
        else:
            m_c['min'] = 0.5*gen['x']['f']*min(scale)
    else:
        m_c['max'] = min([m_c['max'], gen['x']['f']*max(scale)])
        if 'y' in gen:
            m_c['min'] = max([m_c['min'],-gen['y']['f']*min(scale)])
        else:
            m_c['min'] = min([m_c['min'], gen['x']['f']*min(scale)])
    return m_c