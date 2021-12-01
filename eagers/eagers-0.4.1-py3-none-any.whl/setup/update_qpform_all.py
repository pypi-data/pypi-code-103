"""Logic for updating QPForm.

Functions:
update_qpform_all
find_subnet_node
find_buffer
locate_rivers
load_utility
load_market
load_tradepoint
load_piecewise
remove_segments
state_limits
load_storage
load_hydro_storage
load_ac_dc
fit_fcn
fit_with_intercept
fit_residual
fit_coproduction
fit_fcn_2
fit_with_intercept2
max_ac_dc_gen
update_utility_sellback_limit
load_solar
"""

import numpy as np

from eagers.config.network import NETWORK_NAME_ABBR_MAP, OUTPUT_NETWORK_ABBR_MAP, OUTPUT_NETWORK_NAME_MAP, NETWORK_NAMES, OUTPUT_NAMES
from eagers.basic.ss_response import ss_response
from eagers.solver.ecos_ls import ecos_ls


def update_qpform_all(generator, subnet, test_data, scale_time):
    """Loads generators for economic dispatch.
    This function identifies the values that will be used to represent each
    generator in the quadratic optimizations.
    """
    n_g = len(generator)
    n = 5  # Number of segments in piecewise quadratic fits.
    qpform = [{}] * n_g
    for i, gen in enumerate(generator):
        if 'RTUtility' in gen['_type'] or 'TSUtility' in gen['_type']:
            qpform[i] = load_utility(gen,subnet['network_names'])
        elif gen['_type'] == 'Tradepoint':
            qpform[i] = load_tradepoint(gen)
        elif gen['_type'] == 'Market':
            qpform[i] = load_market(gen)
        elif gen['_type'] in ['ElecGeneratorAC', 'ElecGeneratorDC','CombHeatPowerAC', 'CombHeatPowerDC', 'Chiller',
                'Heater', 'CoolingTower', 'Electrolyzer', 'HydrogenGenerator']:
            max_seg = max([1,min([n,len(gen['output']['capacity'])-3])])
            qpform[i] = load_piecewise(gen, max_seg)
            gen['lower_bound'] = gen_lb(gen['_type'],gen['startup'])
            ramp_rate = ss_response(gen)
            ramp_rate = ramp_rate/scale_time
            qpform[i]['ramp'] = {}
            qpform[i]['ramp']['b'] = [ramp_rate for j in range(2)] # [ramp up, ramp down]
        elif gen['_type'] == 'Solar':
            qpform[i] = load_solar(gen,subnet)
        elif gen['_type'] == 'HydroStorage':
            qpform[i] = load_hydro_storage(gen, scale_time)
            qpform[i]['ramp'] = [gen['ramp_up'] / scale_time,gen['ramp_up'] / scale_time]
        elif gen['_type'] in ['ElectricStorage','ThermalStorage','HydrogenStorage']:
            qpform[i] = load_storage(gen, scale_time)
            if gen['_type'] == 'ElectricStorage' and not 'direct_current' in subnet:
                qpform[i]['output'] = {}
                qpform[i]['output']['e'] = [[1]]
        elif gen['_type'] == 'ACDCConverter':
            qpform[i] = load_ac_dc(gen)        
        qpform[i]['type'] = assign_type(gen)
        qpform[i]['name'] = gen['name']
        if 'source' in gen:
            qpform[i]['source'] = gen['source']
        qpform[i]['enabled'] = True
        
    max_ac_gen, max_dc_gen = max_ac_dc_gen(subnet,qpform)
    qpform = update_utility_sellback_limit(qpform,test_data,max_ac_gen, max_dc_gen)
    qpform = locate_rivers(subnet,qpform)
    qpform = find_buffer(subnet,qpform)
    qpform = find_subnet_node(qpform,subnet)
    return qpform

def assign_type(gen):
    # Assign generator type.
    gen_type = None
    if gen['_type'] in ['CombHeatPowerAC', 'CombHeatPowerDC']:
        gen_type = 'CombinedHeatPower'
    elif gen['_type'] in ['ElecGeneratorAC', 'ElecGeneratorDC']:
        gen_type = 'ElectricGenerator'
    elif 'RTUtility' in gen['_type'] or 'TSUtility' in gen['_type']:
        gen_type = 'Utility'
    else:
        gen_type = gen['_type']
    return gen_type

def find_subnet_node(qpform,subnet):
    gen_names = [qpform[i]['name'] for i in range(len(qpform))]
    for i in range(len(qpform)):
        qpform[i]['subnet_node'] = {}
    for net in subnet['network_names']:
        for n in range(len(subnet[net]['nodes'])):
            equip= subnet[net]['equipment'][n]
            for j in equip:
                gen_i = gen_names.index(j)
                qpform[gen_i]['subnet_node'][net] = n
    return qpform

def find_buffer(subnet,qpform):
    """calculate the upper and lower buffer thresholds for each storage system
    """
    gen_names = [qpform[i]['name'] for i in range(len(qpform))]
    for net in subnet['network_names']:
        for m in range(len(subnet[net]['nodes'])):
            equip = subnet[net]['equipment'][m]
            for j in equip:
                k = gen_names.index(j)
                if 'stor' in qpform[k] and 'u' in qpform[k]['states'][0]:
                    if 'buffer' in qpform[k]:
                        buff_perc = qpform[k]['buffer']
                    else:
                        buff_perc = 0
                    if net =='hydro':
                        dischargeCapacity = (qpform[k]['max_gen_flow'] + qpform[k]['s']['ub'])*24/12.1 #amount the resevoir can discharge in a day #flow rate in 1000 ft^3 converted to 1000 acre ft (1000 acre-ft = 12.1 x 1000 ft^3/s * 1 hr)
                        buffer = min([(buff_perc/100)*qpform[k]['stor']['usable_size'],dischargeCapacity])
                    else:
                        buffer = (buff_perc/100)*qpform[k]['stor']['usable_size']
                    qpform[k]['link']['bineq'][-2] = -buffer
                    qpform[k]['link']['bineq'][-1] = qpform[k]['stor']['usable_size'] - buffer
                    qpform[k]['u']['ub'] = buffer
                    qpform[k]['l']['ub'] = buffer           
    return qpform

def locate_rivers(subnet,qpform):
    gen_names = [qpform[i]['name'] for i in range(len(qpform))]
    if 'hydro' in subnet:
        nhn = len(subnet['hydro']['nodes'])    
        for n in range(nhn):
            equip = subnet['hydro']['equipment'][n]
            for j in equip:
                gen_i = gen_names.index(j)
                if 'w' in qpform[gen_i]['output']:
                    qpform[gen_i]['subnet_node']['hydro'] = n
                    if qpform[gen_i]['type'] == 'HydroStorage':
                        qpform[gen_i]['hydro']['downriver'] = subnet['hydro']['line_number'][n][0]
    return qpform

def load_utility(gen,nn):
    
    qpform = {}
    if not 'source' in gen:
        gen['source'] = legacy_utility_source(gen['_type'])

    qpform['source'] = gen['source']
    if gen['source'] in OUTPUT_NAMES and NETWORK_NAMES[OUTPUT_NAMES.index(gen['source'])] in nn: # gen is not a fuel utility.
        # No sellback allowed (only 1 state).
        qpform['output'] = {}
        qpform['states'] = [['x']]
        qpform['x'] = {}
        qpform['x']['h'] = 0
        qpform['x']['f'] = 1
        
        qpform['x']['ub'] = float('inf')
        qpform['ub'] = float('inf')
        s = OUTPUT_NETWORK_ABBR_MAP[gen['source']]
        qpform['output'][s] = [[1]]
        if 'min_import_thresh' in gen:
            qpform['x']['lb'] = gen['min_import_thresh']
            qpform['sellback_rate'] = gen['sellback_rate']
            qpform['sellback_perc'] = gen['sellback_perc']
            if gen['min_import_thresh'] <= 0 and (gen['sellback_rate'] > 0  or (gen['sellback_rate'] == -1 and gen['sellback_perc'] != 1)):
                # Add sellback state.
                qpform['states'] = [['x','y']]
                qpform['y'] = {}
                if gen['sellback_rate'] > 0:
                    qpform['y']['f'] = -gen['sellback_rate']  # Constant sellback rate
                else:
                    # Ensure less than 1, so no issues with pass-through power.
                    qpform['y']['f'] =-min(gen['sellback_perc']/100, 1 - 1e-6)
                qpform['y']['h'] = 0
                qpform['y']['lb'] = 0
                qpform['y']['ub'] = float('inf')
                qpform['x']['lb'] = 0
                qpform['output'][s][0].append(-1)
        else:
            qpform['x']['lb'] = 0
    else:
        qpform['states'] = [[]]
        qpform['output'] = []
        qpform['ub'] = float('inf')
        #TODO timestamp and rate?
    if 'RTUtility' in gen['_type']:
        kys = ['sum_start_month','sum_start_day','win_start_month','win_start_day','sum_rate_table','win_rate_table','sum_rates','win_rates']
    elif 'TSUtility' in gen['_type']:
        kys = ['timestamp','rate']
    for k in kys:
        qpform[k] = gen[k]
    return qpform

def legacy_utility_source(u_type):
    if 'Electric' in u_type:
        source = 'electricity'
    elif 'Heat' in u_type:
        source = 'heat'
    elif 'Cool' in u_type:
        source ='cooling'
    elif 'Coal' in u_type:
        source = 'coal'
    elif 'Natgas' in u_type:
        source ='ng'
    elif 'Diesel' in u_type:
        source = 'diesel'
    else:
        source ='nuclear'
    return source

def load_market(market):
    qpform = {}
    qpform['states'] = [['x']]
    qpform['x']['h'] = 0
    qpform['x']['f'] = 1
    qpform['x']['lb'] = 0 #initial market assumes 0 bids
    qpform['x']['ub'] = 0 # upper and lower bound set to the awarded bid
    qpform['output']['e'] = [[1]]
    if market.MinImportThresh<=0: #add sell back state
        qpform['states'] = [['x','y']]
        #Value for selling to market will be updated as market closes
        if 'sellback_rate' in market:
            qpform['y']['f'] = -market.sellback_rate #default selling rate set to -1 
        else:
            qpform['y']['f'] = -1 #set to sellback indicated by market
        qpform['y']['h'] = 0
        qpform['y']['lb'] = 0 #initial market assumes 0 bids
        qpform['y']['ub'] = 0 #upper and lower bound set to the awarded bid
        qpform['output']['e'][0].append(-1)
    return qpform

def load_tradepoint(t_point):
    ##TODO b0, b1, etc are time series and need to be updated in matrices
    qpform = {}
    qpform['six_param'] = [t_point.b0,t_point.b1,t_point.max_buy,t_point.s0,t_point.s1,t_point.max_sell]
    qpform['states'] = [['x','y']]
    qpform['x']['f'] = t_point.b0
    qpform['x']['h'] = t_point.b1
    qpform['x']['lb'] = 0
    qpform['x']['ub'] = t_point.max_buy

    qpform['y']['f'] = t_point.s0 #selling rate
    qpform['y']['h']= t_point.s1
    qpform['y']['lb'] = 0
    qpform['y']['ub'] = t_point.max_sell
    qpform['output']['e'] = [[1,-1]]
    qpform['lb'] = qpform['y']['ub']
    qpform['ub'] = qpform['x']['ub']
    return qpform 

def load_piecewise(gen, n):
    """This function loads the parameters for a combined heat and power
    generator, regular electric generator, or chiller.\n
    n is number of segments.\n
    order is either 1 or 2. When order is 2 it solves for the quadratic.\n
    Coefficients of C = c_0 + a_1*x_1 + a_2*x_2 + ... + a_n*X_n + b_1*x_1^2
        + b_2*x_2^2 + ... + b_n*X_n^2 subject to b_i > 0, and a_i > a_(i-1)
        + b_(i-1)*(x_i)_max\n
    If order is 1 it solves for linear coefficients of
        C = c_0 + a_1*x_1 + a_2*x_2 + ... + a_n*X_n subject to a_i > a_(i-1)"""
    qpform = {}
    qpform['output'] ={}
    order = 2
    if gen['_type'] == 'Electrolyzer':
        lb = gen['startup']['hydrogen'][0,-1]
        qpform['output']['hy'] = [[1]]
        efficiency = gen['output']['hydrogen']
    elif gen['_type'] in ['CombHeatPowerAC', 'CombHeatPowerDC', 'ElecGeneratorAC', 'ElecGeneratorDC', 'HydrogenGenerator']:
        if 'electricity' in gen['output']:
            lb = gen['startup']['electricity'][-1]
            efficiency = gen['output']['electricity']
            qpform['output']['e'] = [[1]]
        elif 'direct_current' in gen['output']:
            lb = gen['startup']['direct_current'][-1]
            efficiency = gen['output']['direct_current']
            qpform['output']['dc'] = [[1]]
    elif gen['_type'] == 'Heater':
        lb = gen['startup']['heat'][-1]
        qpform['output']['h'] = [[1]]
        efficiency = gen['output']['heat']
    elif gen['_type'] == 'Chiller':
        order = 1
        lb = gen['startup']['cooling'][-1]
        qpform['output']['c'] = [[1]]
        efficiency = gen['output']['cooling']
    elif gen['_type'] == 'CoolingTower':
        order = 1
        lb = gen['startup']['heat_reject'][-1]
        qpform['output']['cw'] = [[-1]]
        efficiency = gen['output']['heat_reject']
    
    qpform['max_eff'] = max(efficiency)
    p_i = max(range(len(efficiency)), key=efficiency.__getitem__)
    qpform['max_eff_point'] = gen['output']['capacity'][p_i]*gen['size_kw']

    ub = gen['size_kw']
    qpform['lb'] = lb
    qpform['ub'] = ub
    operation_range = [i for i, x in enumerate(gen['output']['capacity'])
        if float('%.6f' % x) >= float('%.6f' % (lb/ub))]
    # Sort list of (index, value) pairs based on values, where values are the
    # elements of capacity at indices specified by operation_range.
    valid_capacity = [gen['output']['capacity'][i] for i in operation_range]
    valid_eff = [efficiency[i] for i in operation_range]
    c_sort = sorted(range(len(valid_capacity)), key=lambda k: valid_capacity[k])
    p = [valid_capacity[i] for i in c_sort]
    eff = [valid_eff[i] for i in c_sort]
    
    qpform['eff'] = eff
    qpform['cap'] = [p[i]*ub for i in range(len(p))]
    if gen['_type'] in ['CombHeatPowerAC', 'CombHeatPowerDC']:
        chp_heat_eff = gen['output']['heat']
        valid_chp_eff = [chp_heat_eff[i] for i in operation_range]
        qpform['chp_eff'] = [valid_chp_eff[i] for i in c_sort]
    # Cost of generator in terms of input at outputs p.
    y = []
    for i in range(len(eff)):
        if eff[i]>0:
            y.append(p[i]/eff[i])
        else:
            y.append(0)

    seg_end = [lb/ub + (1-lb/ub)*(i+1)/n for i in range(n)]
    _, a, _ = fit_fcn(p, y, seg_end, n, order, 0)  # In fit A: c_0 = 0
    _, b, c_0 = fit_fcn(p, y, seg_end, n, order, 1)

    
    qpform['const_cost'] = c_0 * ub
    if 'start_cost' in gen:
        qpform['start_cost'] = gen['start_cost']
    else: 
        qpform['start_cost'] = 0
    qpform['const_demand'] = {}
    x_max = [seg_end[0]]
    x_max.extend([seg_end[i+1] - seg_end[i] for i in range(n-1)])

    if gen['_type'] in ['CombHeatPowerAC', 'CombHeatPowerDC']:
        h_0, heat_out, qpform['max_heat'] = fit_coproduction(gen, a, b, n)
        qpform['const_demand']['district_heat'] = -h_0 * ub
    else:
        heat_out = [None,None]

    a, keep_a = remove_segments(a, n, x_max, order, heat_out[0])
    b, keep_b = remove_segments(b, n, x_max, order, heat_out[1])
    # n_a, n_b must be integers for later use in setting list length
    n_a = 0
    for i in range(n):
        if keep_a[i]:
            n_a += 1
    n_b = 0
    for i in range(n):
        if keep_b[i]:
            n_b += 1
    qpform['states'] = [[],[]]
    if gen['_type'] == 'Chiller':
        net = OUTPUT_NETWORK_NAME_MAP[gen['source']]
        source = NETWORK_NAME_ABBR_MAP[net]
        if source == 'h':
            # Absorption chiller has no direct electrical load, but later pump for cooling tower can be added.
            qpform['output']['e'] = [[0]]
        qpform['output'][source] = [[] for j in range(2)]
        qpform['output'][source][0] = [-a[j] for j in range(len(a)) if keep_a[j]]
        qpform['output'][source][1] = [-b[j] for j in range(len(b)) if keep_b[j]]
        qpform['output']['cw'] = [[] for j in range(2)]
        qpform['output']['cw'][0] = [1-qpform['output'][source][0][i] for i in range(n_a)]
        qpform['output']['cw'][1] = [1-qpform['output'][source][1][i] for i in range(n_b)]
        qpform['const_demand'][net] = c_0 * ub
        qpform['const_demand']['cooling_water'] = -c_0 * ub# Heat added to water loop appears as a negative demand for energy in the water loop.
        qpform = state_limits(qpform,[0 for i in range(len(a))],0,ub,x_max,keep_a,order,0)
        qpform = state_limits(qpform,[0 for i in range(len(b))],lb,ub,x_max,keep_b,order,1)
        qpform['const_cost'] = 0
    elif gen['_type'] == 'CoolingTower':
        qpform['output']['e'] = [[] for j in range(2)]
        qpform['output']['e'][0] = [-a[j] for j in range(len(a)) if keep_a[j]]
        qpform['output']['e'][1] = [-b[j] for j in range(len(b)) if keep_b[j]]
        qpform['const_demand']['electrical'] = c_0 * ub
        qpform['const_demand']['cooling_water'] = -c_0 * ub# Heat added to water loop appears as a negative demand for energy in the water loop.
        qpform = state_limits(qpform,[0 for i in range(len(a))],0,ub,x_max,keep_a,order,0)
        qpform = state_limits(qpform,[0 for i in range(len(b))],lb,ub,x_max,keep_b,order,1)
        qpform['const_cost'] = 0
    elif gen['_type'] in ['CombHeatPowerAC', 'CombHeatPowerDC']:
        qpform = state_limits(qpform,a,0,ub,x_max,keep_a,order,0)
        qpform = state_limits(qpform,b,lb,ub,x_max,keep_b,order,1)
        qpform['output']['h'] = [[0 for i in range(n)] for j in range(2)]
        qpform['output']['h'][0][:n_a] = [heat_out[0][i] for i in range(n) if keep_a[i]]
        qpform['output']['h'][1][:n_b] = [heat_out[1][i] for i in range(n) if keep_b[i]]
    else:
        qpform = state_limits(qpform,a,0,ub,x_max,keep_a,order,0)
        qpform = state_limits(qpform,b,lb,ub,x_max,keep_b,order,1)
    return qpform
    
def remove_segments(a, n, x_max, order, co_prod):
    """Remove segments that that have less than 1% deviation in slope 
    (and co-production if applicable) to previous segment"""
    tol = 1e-2
    keep = [True for i in range(order*n)]
    for i in range(1, n):
        if (((a[i]==0 and a[i-1]==0) or (a[i-1]!=0 and abs((a[i] - a[i-1])/a[i-1]) < tol))
                and (order == 1 or a[n+i]*x_max[i] < tol*a[i-1])
                and (co_prod is None or abs((co_prod[i] - co_prod[i-1])/co_prod[i-1]) < tol)):
            keep[i] = False
            if order == 2:
                keep[n+i] = False
    for i in range(n):
        if order == 2 and a[n+i]*x_max[i] < 0.1*tol*a[i]:
            a[n+i] = 0
    return a, keep

def state_limits(qpform,fit_terms,lower_bound,upper_bound,x_max,keep,order,fit):
    ## put properteries of cost and limits into states A, B, ...
    letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n']
    n_states = 0
    for i in range(len(keep)):
        if keep[i]:
            n_states +=1/order
    qpform['states'][fit] = letters[:int(n_states)]
    j = -1
    for i in range(len(x_max)):
        if keep[i]:    
            j +=1
            if not letters[j] in qpform:
                qpform[letters[j]] = {}
                qpform[letters[j]]['h'] = [[],[]]
                qpform[letters[j]]['f'] = [[],[]]
                qpform[letters[j]]['lb'] = [[],[]]
                qpform[letters[j]]['ub'] = [[],[]]
            if order == 2:
                qpform[letters[j]]['h'][fit] = fit_terms[len(x_max)+i]/upper_bound ## scale by size of gen (later can normalize by changing QPform.Output so that all states are 0-1)
            else:
                qpform[letters[j]]['h'][fit] = 0
            qpform[letters[j]]['f'][fit] = fit_terms[i]
            if i ==0:
                qpform[letters[j]]['lb'][fit] = lower_bound
                qpform[letters[j]]['ub'][fit] = max([lower_bound,x_max[i]*upper_bound])
            else:
                qpform[letters[j]]['lb'][fit] = 0
                qpform[letters[j]]['ub'][fit] = x_max[i]*upper_bound
        else:
            qpform[letters[j]]['ub'][fit] += x_max[i]*upper_bound
    return qpform

def load_storage(gen, scale_time):
    """This function just directs to either hot or cold thermal storage.\n
    If we can get rid of the CS, HS structures then this function can be
    eliminated, because all storage can be handled the same way."""

    qpform = {}
    stor = {}
    qpform['output'] = {}

    stor['size'] = gen['size_kwh'] * scale_time
    # Usable size (state x is 0 -> usable size, must calculate this
    # initial condition each time from capacity & SOC).
    stor['usable_size'] = gen['size_kwh'] * scale_time
    if 'max_dod' in gen:
        stor['usable_size'] = stor['usable_size'] * gen['max_dod'] / 100 
    # Self-discharge per hour (fraction of total charge).
    stor['self_discharge'] = gen['self_discharge']
    if 'fill_rate' in gen:
        # Thermal or hydrogen storage.
        stor['peak_disch'] = gen['disch_rate_perc'] / 100 * gen['size_kwh']  # [Thermal kW out]
        stor['peak_charge'] = gen['fill_rate_perc'] / 100 * gen['size_kwh']  # [Thermal kW in]
        stor['charge_eff'] = gen['charge_eff']
        stor['disch_eff'] = gen['disch_eff']
        if gen['source'] == 'cooling':
            qpform['output']['c'] = [[1]]
        elif gen['source'] == 'heat':
            qpform['output']['h'] = [[1]]
        elif gen['source'] == 'hydrogen':
            qpform['output']['hy'] = [[1]]
    else:
        # Electric battery.
        qpform['output']['dc'] = [[1]]
        # Can be specified by voltage and charge/discharge resistances or by
        # charge/discharge efficiencies and peak charge/discharge power.
        stor_fields = ('charge_eff', 'disch_eff', 'peak_charge', 'peak_disch')
        if any(x not in gen for x in stor_fields):
            voltage = gen['voltage']
            disch_current = gen['peak_disch'] * gen['size_kwh'] / voltage * 1000
            # Scale so the loss of power is equivelant to that specified at 100 Amps.
            disch_resist_scaled = (100 / disch_current) * gen['disch_resist'] / 1000
            # Keep in mind when calculating loss as function of discharge current.
            disch_volt_loss = disch_current * disch_resist_scaled
            charge_current = gen['peak_charge'] * gen['size_kwh'] / voltage * 1000
            # Scale so the loss of power is equivelant to that specified at 10 Amps.
            charge_resist_scaled = (100/charge_current) * gen['charge_resist'] / 1000
            charge_volt_loss = charge_current * charge_resist_scaled
            stor['charge_eff'] = voltage / (voltage + charge_volt_loss)
            stor['disch_eff'] = (voltage - disch_volt_loss) / voltage
            stor['peak_disch'] = disch_current * voltage * stor['disch_eff'] / 1000 # Peak discharge power [kW out].
            stor['peak_charge'] = charge_current * voltage / stor['charge_eff'] / 1000  # Peak charge power [kW in].
        else:
            stor.update({x: gen[x] for x in stor_fields})
    qpform['stor'] = stor
    # qpform['ramp_rate'] = [stor['peak_disch'],stor['peak_charge']]  # Storage discharge constraint [kW].
    qpform['states'] = [['x']] # State of charge, charging power, no buffers.
    qpform['x'] = {}
    qpform['x']['lb'] = 0
    qpform['x']['ub'] = stor['usable_size']
    qpform['x']['h'] = 0
    qpform['x']['f'] = 0
    a = 1 / stor['charge_eff'] - stor['disch_eff']
    qpform['ramp'] = {}
    qpform['ramp']['b'] = [stor['peak_charge'],stor['peak_disch']]
    qpform['link'] = {}
        # SOC2-SOC1 < peak_charge; SOC1-SOC2 < peak_disch
    if a != 0:# Not ideal storage, add charging state.
        qpform['states'] = [['x','y']] # State of charge, charging power, no buffers.
        qpform['link']['ineq'] = [[a, -1]] # (1/nc - nd) * (SOC(t) - SOC(t-1)) - charging <------ charging is 1/inefficiency + 1
        qpform['link']['bineq'] = [0]
        qpform['y'] = {}
        qpform['y']['lb'] = 0
        qpform['y']['ub'] = stor['peak_charge']  # The limit on how much charging power can be delivered is handled by the generators' limits, so put inf here to prevent redundancy.
        qpform['y']['h'] = 0  # Cost of charging power is handled by the generators.
        qpform['y']['f'] = 0
    if 'buffer' in gen and gen['buffer'] != 0:  # Buffer states.
        if a == 0: # Ideal storage, ignore charging state.
            qpform['states'] = [['x','u','l']]  # SOC(t+1), charging power, upper buffer, lower buffer
            qpform['link']['ineq'] = [[-1, 0, -1], [1, -1, 0]] # -SOC(t) - lowerbuffer < -0.2 and SOC(t) - upperbuffer < 0.8
            qpform['link']['bineq'] = [0, 0]  # Note: the magnitude of the buffer is set later in find_buffer.
        else:
            qpform['states'] = [['x','y','u','l']]  # SOC(t+1), charging power, upper buffer, lower buffer.
            qpform['link']['ineq'] = [[a, -1, 0, 0], [-1, 0, 0, -1], [1, 0, -1, 0]] # -SOC(t) - lowerbuffer < -0.2 qpform.link.ineq = [qp_form.link.ineq, [1, 0, -1, 0]] SOC(t) - upperbuffer < 0.8
            qpform['link']['bineq'] = [0, 0, 0]
        qpform['buffer'] = gen['buffer']
        qpform['u'] = {}
        qpform['l'] = {}
        qpform['u']['lb'] = 0
        qpform['u']['ub'] = 0  # Note: the magnitude of the buffer is set later in find_buffer.
        qpform['u']['h'] = 0
        qpform['u']['f'] = 0
        qpform['l']['lb'] = 0
        qpform['l']['ub'] = 0  # Note: the magnitude of the buffer is set later in find_buffer.
        qpform['l']['h'] = 0
        qpform['l']['f'] = 0
    return qpform


def load_hydro_storage(gen, scale_time):
    """This function loads the parameters for a hydroelectric plant."""
    qpform = {}
    qpform['stor'] = {}
    qpform['output'] = {}
    qpform['x'] = {}
    qpform['y'] = {}
    qpform['link'] = {}
    
    eff = gen['max_gen_capacity'] / (gen['max_gen_flow'] * gen['max_head'] * 84.674) # Power (kW)/ideal power in kW
    qpform['max_gen_flow'] = gen['max_gen_flow']
    qpform['start_wy'] = gen['start_wy_state']
    qpform['stor']['size'] = gen['size_kwh'] * scale_time
    qpform['stor']['self_discharge'] = 0  # Needs to be evaporative losses.
    qpform['stor']['disch_eff'] = 1  # 100% efficient.
    qpform['stor']['usable_size'] = qpform['stor']['size'] * gen['min_head'] / gen['max_head']
    qpform['stor']['power_to_flow'] = 1 / (eff * gen['max_head'] * 84.674)# Power [kW] = efficiency [%] * Flow [1000 ft^3/s] * Head [ft] * 84.674 [kJ/(1000ft^3*ft)]
    qpform['output']['w'] = [[0]]
    qpform['output']['e'] = [[1, 0]]
    qpform['states'] = ['x','y']  # Power and state of charge.
    qpform['x']['lb'] = 0
    qpform['x']['ub'] = gen['max_gen_capacity']
    qpform['x']['h'] = 0
    qpform['x']['f'] = 0

    qpform['y']['lb'] = 0
    qpform['y']['ub'] = qpform['stor']['usable_size']
    qpform['y']['h'] = 0
    qpform['y']['f'] = 0
    qpform['ramp']['b'] = [gen['ramp_down'], gen['ramp_up']]  # Change in power generation.
    qpform['link']['eq'] = [qpform['stor']['power_to_flow'], 0]  # Convert power to flow rate (1000 cfs).
    qpform['link']['b_eq'] = [0]       
    if gen['max_spill_flow'] > 0:
        qpform['states'] = ['x','y','s']  # Add spill flow state.
        qpform['s'] = {}
        qpform['s']['lb'] = 0
        qpform['s']['ub'] = gen['max_spill_flow']
        qpform['s']['h'] = 0
        qpform['s']['f'] = 0
        qpform['link']['eq'] = [[qpform['stor']['power_to_flow'], 0, 1]]
        qpform['link']['b_eq'] = [0]
        qpform['output']['e'] = [[1, 0, 0]]
    if 'buffer' in gen and gen['buffer'] != 0:  # Buffer states.
        if gen['max_spill_flow'] > 0:
            qpform['states'] = ['x','y','s','u','l']
            qpform['link']['eq'] =[[qpform['stor']['power_to_flow'], 0, 1, 0, 0]]
            qpform['link']['ineq'] =[[0, -1, 0, 0, -1], [0, 1, 0, -1, 0]] # -SOC(t)-lowerbuffer < -0.2, SOC(t)-upperbuffer < 0.8
            qpform['output']['e'] = [[1, 0, 0, 0, 0]]
        else:
            qpform['states'] = ['x','y','u','l']
            qpform['link']['eq'] = [[qpform['stor']['power_to_flow'], 0, 0, 0]]
            qpform['link']['ineq'] = [[0, -1, 0, -1], [0, 1, -1, 0]] # -SOC(t)-lowerbuffer < -0.2, SOC(t)-upperbuffer < 0.8
            qpform['output']['e'] = [[1, 0, 0, 0]]
        qpform['link']['bineq'] = [0, 0]

        qpform['u'] = {}
        qpform['u']['lb'] = 0
        qpform['u']['ub'] = 0
        qpform['u']['h'] = 0
        qpform['u']['f'] = 0

        qpform['l'] = {}
        qpform['l']['lb'] = 0
        qpform['l']['ub'] = 0
        qpform['l']['h'] = 0
        qpform['l']['f'] = 0
    return qpform


def load_ac_dc(gen):
    """Load AC/DC generator."""
    # First state is AC power transferred to DC power.
    # Second state is DC power transferred to AC power.
    # Unless perfect, then just 1 state
    qpform = {}
    qpform['output'] = {}
    qpform['a'] = {}
    qpform['a']['ub'] = gen['capacity']
    qpform['a']['f'] = 0
    qpform['a']['h'] = 0
    if gen['dc_to_ac_eff']==1 and gen['ac_to_dc_eff']==1:
        qpform['a']['lb'] = -gen['capacity']
        qpform['output']['e'] = [[-1]]
        qpform['output']['dc'] = [[1]]
        qpform['states'] = [['a']]
    else:
        qpform['a']['lb'] = 0
        qpform['output']['e'] = [[-1, gen['dc_to_ac_eff']]]
        qpform['output']['dc'] = [[gen['ac_to_dc_eff'], -1]]
        qpform['states'] = [['a','b']]
        qpform['b'] = {}
        qpform['b']['ub'] = gen['capacity']
        qpform['b']['lb'] = 0
        qpform['b']['f'] = 0
        qpform['b']['h'] = 0
    return qpform


def fit_fcn(outpt, inpt, seg_end, n, order, intercept):
    x_max = [seg_end[0]]
    x_max.extend([seg_end[i+1] - seg_end[i] for i in range(n-1)])
    x = [[0 for j in range(len(outpt))] for i in range(n)]
    for i in range(len(outpt)):
        x[0][i] = min([outpt[i], seg_end[0]])
        for j in range(1,n):
            x[j][i] = max([0, min([x_max[j], outpt[i] - sum([x[k][i] for k in range(j)])])])
    qp = {}
    qp['h'] = [[1 for i in range(order*n)] for j in range(order*n)]
    qp['f'] = [1 for i in range(order*n)]
    for i in range(order*n):
        if i < n:
            a = x[i]
        else:
            a = [x[i-n][j]**2 for j in range(len(x[i-n]))]
        for j in range(i+1):
            if j < n:
                b = x[j]
            else:
                b = [x[j-n][k]**2 for k in range(len(x[j-n]))]
            ab = sum([a[k]*b[k] for k in range(len(a))])
            qp['h'][i][j] = 2*ab
            qp['h'][j][i] = 2*ab
        qp['f'][i] = -2 * sum([a[k]*inpt[k] for k in range(len(a))])

    qp['a'] = [[0 for i in range(order*n)] for j in range(order*n-1)]
    qp['b'] = [0 for j in range(order*n-1)]
    for i in range(n-1):
        qp['a'][i][i] = 1
        qp['a'][i][i+1] = -1
        if order == 2:
            qp['a'][i][n+i] = 2 * x_max[i]
    qp['a_eq'] = [[x_max[i]*1 for i in range(len(x_max))]]
    if order == 2:
        for i in range(n-1, 2*n-1):
            qp['a'][i][i+1] = -1
        qp['a_eq'][0].extend([x_max[i]**2 for i in range(len(x_max))])
        
    qp['b_eq'] = [inpt[-1]]
    qp['lb'] = []
    qp['ub'] = []
    if intercept:
        a = fit_with_intercept(qp,inpt,order,x,n)
    else:
        a,_ = ecos_ls(qp['h'], qp['f'], qp['a'], qp['b'], qp['a_eq'], qp['b_eq'])

    if order == 2:
        for i in range(n, 2*n):
            if a[i] < 1e-6:
                a[i] = 0
    if intercept:
        c_0 = a[0]
        a = a[1:]
    else:
        c_0 = 0

    # plot_fitting(x_max,outpt,inpt,order,A,c_0,n,ones(length(A),1))
    r_square = fit_residual(inpt,outpt,c_0,x,a,order)
    return r_square, a, c_0

def fit_with_intercept(qp,inpt,order,x,n):
    a = [0 for i in range(order*n)]
    for i in range(order*n):
        if i<n:
            a[i] = 2*sum([j for j in x[i]])
        else:
            a[i] = 2*sum([j**2 for j in x[i-n]])
        qp['h'][i].insert(0,a[i])
    a.insert(0,2*len(inpt))
    qp['h'].insert(0,a)
    qp['f'].insert(0,-2*sum(inpt))
    for i in range(order*n-1):
        qp['a'][i].insert(0,0)
    qp['a_eq'][0].insert(0,1)
    a,_ = ecos_ls(qp['h'], qp['f'], qp['a'], qp['b'], qp['a_eq'], qp['b_eq'])
    return a

def fit_residual(inpt,outpt,c_0,x,a,order):
    #find residual of result
    ss_res = 0
    ss_mean = 0
    mean_inpt = sum(inpt)/len(inpt)
    for i in range(len(outpt)):
        if order == 2:
            x2 = [x[j][i] for j in range(len(x))]
            x2.extend([x[j][i]**2 for j in range(len(x))])
            fit_i = c_0 + sum([a[j] for j in range(len(a))])
        else:
            fit_i = c_0 + sum([a[j]*x[j][i] for j in range(len(x))])
        ss_res += (inpt[i] - fit_i)**2
        ss_mean += (inpt[i] - mean_inpt)**2
    r_square = 1 - ss_res / ss_mean
    return r_square

def fit_coproduction(gen, a, b, n):
    """Sets up two least squares problems to find the coefficients of the heat
    co-production."""
    ub = gen['size_kw']
    if 'electricity' in gen['output']:
        lb = gen['startup']['electricity'][-1]
    elif 'direct_current' in gen['output']:
        lb = gen['startup']['direct_current'][-1]
    seg_end = [lb + (ub-lb)*(i+1)/n for i in range(n)]
    c_sort = sorted(range(len(gen['output']['capacity'])), key=lambda k: gen['output']['capacity'][k])
    cap = [gen['output']['capacity'][i] for i in c_sort]
    heat = [gen['output']['heat'][i] for i in c_sort]   
    if 'electricity' in gen['output']:
        elec = [gen['output']['electricity'][i] for i in c_sort]
    elif 'direct_current' in gen['output']:
        elec = [gen['output']['direct_current'][i] for i in c_sort]
    #interpolate input and heat output
    i = 0
    fuel_input = []
    seg_heat = []
    for j in range(len(seg_end)):
        while seg_end[j]/ub - cap[i+1]>1e-6:
            i+=1
        r = (cap[i+1]-seg_end[j]/ub)/(cap[i+1]-cap[i])
        fuel_input.append(r*seg_end[j]/elec[i] + (1-r)*seg_end[j]/elec[i+1])
        seg_heat.append((r*fuel_input[j]*heat[i] + (1-r)*fuel_input[j]*heat[i+1])*0.95) # Reduce heat co-production by 5% for fitting, because it is better to slightly underestimate.

    cumulative_slope = [seg_heat[i]/seg_end[i] for i in range(len(seg_end))]
    mean_slope = sum(cumulative_slope[:(len(seg_heat)-1)])/(len(seg_heat)-1)
    seg_heat = [min([seg_heat[i],1.3*mean_slope*seg_end[i]]) for i in range(len(seg_end))]
    local_slope = [seg_heat[0]/seg_end[0]]
    for i in range(len(seg_end)-1):
        local_slope.append((seg_heat[i+1]-seg_heat[i])/(seg_end[i+1]-seg_end[i]))

    # Maximum that beta (slope of heat ratio) can increase and remain convex
    # due to convex cost function.
    max_slope_inc = [(a[i+1] - a[i]) / a[i] * local_slope[i] for i in range(len(seg_end)-1)]

    seg_5n = [lb/ub for i in range(n)]
    seg_5n.extend(np.linspace(lb/ub, 1, 5*n+1).tolist())
    seg_fuel_5n = []
    seg_heat_5n = []
    i = 0
    for j in range(6*n+1):
        while cap[i+1]<seg_5n[j]:
            i+=1
        r = (cap[i+1]-seg_5n[j])/(cap[i+1]-cap[i])
        seg_fuel_5n.append(r*seg_5n[j]/elec[i] + (1-r)*seg_5n[j]/elec[i+1])
        seg_heat_5n.append((r*seg_fuel_5n[j]*heat[i] + (1-r)*seg_fuel_5n[j]*heat[i+1])*0.95) 

    heat_out = [[],[]]
    heat_out[0], _ = fit_fcn_2(seg_5n, seg_heat_5n, [seg_end[i]/ub for i in range(len(seg_end))], n, max_slope_inc,None)

    # Repeat for non-zero y-intercept.
    # Slope of 1st segment wih non-zero y-intercept.
    i = 0
    while cap[i+1]<lb/ub:
        i+=1
    r = (cap[i+1]-lb/ub)/(cap[i+1]-cap[i])
    min_fuel = r*lb/elec[i] + (1-r)*lb/elec[i+1]
    min_heat = min_fuel*(r*heat[i] + (1-r)*heat[i+1])

    local_slope[0] = (seg_heat[0]-min_heat)/(seg_end[0]-lb)
    # y_intercept = seg_heat[0] - seg_end[0] * local_slope[0]

    # Maximum that beta (slope of heat ratio) can increase and remain convex
    # due to convex cost function.
    max_slope_inc = [2*(b[i+1] - b[i]) / b[i] * local_slope[i] for i in range(len(seg_end)-1)]
    heat_out[1], h_0 = fit_fcn_2(seg_5n, seg_heat_5n,  [x/ub for x in seg_end], n, max_slope_inc, 1.1*local_slope[0])

    max_heat = max([ub*cap[i]/elec[i]*heat[i] for i in range(len(cap)) if elec[i]>0 and heat[i]>0])
    # max_heat = h_0*ub + seg_end[0]*heat_out[1][0]
    # for i in range(len(heat_out[1])-1):
    #     max_heat += heat_out[1][i+1]*(seg_end[i+1] - seg_end[i])
    return h_0, heat_out, max_heat


def fit_fcn_2(outpt, inpt, seg_end, n, max_slope_inc, local_slope_1):
    """Sets up a least squares problem to find the linear piecewise
    coefficients of the heat co-production."""
    qp = {}
    x_max = [seg_end[0]]
    x_max.extend([seg_end[i+1] - seg_end[i] for i in range(n-1)])
    x = [[0 for j in range(len(outpt))] for i in range(n)]
    for i in range(len(outpt)):
        x[0][i] = min([outpt[i], seg_end[0]])
        for j in range(1,n):
            x[j][i] = max([0, min([x_max[j], outpt[i] - sum([x[k][i] for k in range(j)])])])

    qp['h'] = [[1 for i in range(n)] for j in range(n)]
    qp['f'] = [1 for i in range(n)]
    for i in range(n):
        a = x[i]
        for j in range(i+1):
            b = x[j]
            ab = sum([a[k]*b[k] for k in range(len(a))])
            qp['h'][i][j] = 2*ab
            qp['h'][j][i] = 2*ab
        qp['f'][i] = -2 * sum([a[k]*inpt[k] for k in range(len(a))])

    qp['a'] = [[0 for i in range(n)] for j in range(n-1)]
    qp['b'] = [x*1 for x in max_slope_inc]

    # The sign of this constraint is switched from fit_fcn because we want the
    # coefficients of heat recovery to get smaller.
    for i in range(n-1):
        qp['a'][i][i] = -1
        qp['a'][i][i+1] = 1
    qp['a_eq'] = []
    qp['b_eq'] = []
    if not local_slope_1 is None:
        a = fit_with_intercept2(qp,inpt,local_slope_1,x,n)
        h_0 = a[0]
        fit = a[1:]
    else:
        fit,_ = ecos_ls(qp['h'], qp['f'], qp['a'], qp['b'], qp['a_eq'], qp['b_eq'])
        h_0 = 0
    return fit, h_0

def fit_with_intercept2(qp,inpt,local_slope,x,n):
    a = [0] * n
    for i in range(n):
        a[i] = 2*sum([j for j in x[i]])
        qp['h'][i].insert(0,a[i])
        
    lsc = [0,1]
    for i in range(n-1):
        qp['a'][i].insert(0,0)
        lsc.append(0)
    a.insert(0,2*len(inpt))
    qp['h'].insert(0,a)
    qp['f'].insert(0,-2*sum(inpt))
    qp['a'].append(lsc)
    qp['b'].append(local_slope)
    a,_ = ecos_ls(qp['h'], qp['f'], qp['a'], qp['b'], qp['a_eq'], qp['b_eq'])
    return a

def max_ac_dc_gen(subnet,qpform):
    #identify upper bound for utility states (helps with scaling)
    max_dc_gen = 0
    gen_names = [qpform[i]['name'] for i in range(len(qpform))]
    if 'direct_current' in subnet:
        nn = len(subnet['direct_current']['nodes'])
        for n in range(nn):
            equip = subnet['direct_current']['equipment'][n]
            ne = len(equip)
            for j in range(ne):
                k = gen_names.index(equip[j])
                if qpform[k]['type'] == 'HydroStorage':
                    max_dc_gen += qpform[k]['x']['ub']
                elif qpform[k]['type'] == 'ElectricStorage':
                    max_dc_gen += qpform[k]['stor']['peak_disch']
                elif not qpform[k]['type'] == 'ACDCConverter':
                    if qpform[k]['type'] == 'Solar': #Solar
                        max_dc_gen += qpform[k]['size_kw']*qpform[k]['output']['dc'][0][0]
                    else:
                        if len(qpform[k]['output']['dc'][-1]) == 1:
                            dc_output = [qpform[k]['output']['dc'][-1][0] for s in range(len(qpform[k]['states'][-1]))]
                        else:
                            dc_output = qpform[k]['output']['dc'][-1]
                        s_ub = [qpform[k][s]['ub'][-1] for s in qpform[k]['states'][-1]]
                        max_dc_gen += max([0,sum([s_ub[i]*dc_output[i] for i in range(len(s_ub))])])
    max_ac_gen = 0
    if 'electrical' in subnet:
        nn = len(subnet['electrical']['nodes'])
        for n in range(nn):
            equip = subnet['electrical']['equipment'][n]
            ne = len(equip)
            for j in range(ne):
                k = gen_names.index(equip[j])
                if qpform[k]['type'] == 'HydroStorage':
                    max_ac_gen += qpform[k]['x']['ub']
                elif qpform[k]['type'] == 'ElectricStorage':
                    max_ac_gen += qpform[k]['stor']['peak_disch']
                elif not qpform[k]['type'] == 'ACDCConverter':
                    if len(qpform[k]['states']) == 0: #Solar
                        max_ac_gen += qpform[k]['size_kw']*qpform[k]['output']['e'][0][0]
                    else:
                        if len(qpform[k]['output']['e'][-1]) == 1:
                            ac_output = [qpform[k]['output']['e'][-1][0] for s in range(len(qpform[k]['states'][-1]))]
                        else:
                            ac_output = qpform[k]['output']['e'][-1]
                        s_ub = []
                        for s in qpform[k]['states'][-1]:
                            if isinstance(qpform[k][s]['ub'],list):
                                s_ub.append(qpform[k][s]['ub'][-1])
                            else:
                                s_ub.append(qpform[k][s]['ub'])
                        max_ac_gen += max([0,sum([s_ub[i]*ac_output[i] for i in range(len(s_ub))])])
    return max_ac_gen, max_dc_gen

def update_utility_sellback_limit(qpform,test_data,max_ac_gen, max_dc_gen):
    n_g = len(qpform)
    for i in range(n_g):
        if qpform[i]['type'] == 'Utility'and len(qpform[i]['states'][0])>0: #avoid things like gas utility with no states
            #identify the network
            out = [*qpform[i]['output']] 
            if 'e' in out:
                net = 'electrical'
            elif 'h' in out:
                net = 'district_heat'
            elif 'c' in out:
                net = 'district_cool'
            elif 'w' in out:
                net = 'hydro'
            d = []
            if net in test_data['nodedata_network_info']:
                for n in test_data['nodedata_network_info'][net]:
                    if 'demand_history' in n:
                        #To accomodate different time stamps on history it will just add the maximum of each node, even if maximums are not coeincident.
                        d.append(float(max(test_data['nodedata'].read(n['demand_history'][0],0,-1, field = n['demand_history'][1]))))
            if len(d)>0:
                qpform[i]['x']['ub'] = 10*sum(d) #max Purchase
            else:
                qpform[i]['x']['ub'] = 1e6 #arbitrary upper bound that is not inf
            qpform[i]['ub'] = qpform[i]['x']['ub']
            if net == 'electrical' and 'y' in qpform[i]:
                qpform[i]['y']['ub'] = max_ac_gen + max_dc_gen
        if qpform[i]['type']=='ACDCConverter':
            qpform[i]['a']['ub'] = max_ac_gen
            if 'b' in qpform[i]:
                qpform[i]['b']['ub'] = max_dc_gen
            else:
                qpform[i]['a']['lb'] = -max_dc_gen
    return qpform

def load_solar(gen,subnet):
    # There are no states or outputs for solar because renewable
    # outputs are handled on the demand side.
    qpform = {}
    qpform['azimuth'] = gen['azimuth']
    qpform['eff'] = gen['eff']
    qpform['pv_type'] = gen['pv_type']
    qpform['size_m2'] = gen['size_m2']
    qpform['size_kw'] = gen['size_kw']
    qpform['tilt'] = gen['tilt']
    qpform['tracking'] = gen['tracking']
    qpform['states'] = [[]]
    qpform['output'] = {}
    if 'direct_current' in subnet and any(gen['name'] in agg
            for agg in subnet['direct_current']['equipment']):
        qpform['output']['dc'] = [[1]]
    else:
        qpform['output']['e'] = [[1]]
    qpform['location'] = {}
    
    if 'direct_current' in subnet:
        for n in range(len(subnet['direct_current']['nodes'])):
            if gen['name'] in subnet['direct_current']['equipment'][n]:
                qpform['location'] = subnet['direct_current']['location'][n]
                break
    if not 'latitude' in qpform['location']:
        for n in range(len(subnet['electrical']['nodes'])):
            if gen['name'] in subnet['electrical']['equipment'][n]:
                qpform['location'] = subnet['electrical']['location'][n]
                break
    return qpform

def gen_lb(gtype,gstart):
    if gtype in ['ElecGeneratorAC', 'CombHeatPowerAC']:
        lb = gstart['electricity'][-1]
    elif gtype in ['ElecGeneratorDC', 'CombHeatPowerDC']:
        lb = gstart['direct_current'][-1]
    elif gtype in ['Chiller']:
        lb = gstart['cooling'][-1]
    elif gtype in ['Heater']:
        lb = gstart['heat'][-1]
    elif gtype in ['CoolingTower']:
        lb = gstart['heat_reject'][-1]
    elif gtype in ['Electrolyzer', 'HydrogenGenerator']:
        lb = gstart['hydrogen'][-1]
    return lb