'''Defines functionality for calculating generator limits.

Functions:
gen_limit
chp_heat
'''


def gen_limit(gen, gen_output, binary, dt, s):
    '''Return the generator limit.'''
    n_g = len(gen)
    n_s = len(dt)
    ramp_up = [[] for i in range(n_g)]
    ramp_down = [[] for i in range(n_g)]
    upper_bound = [0 for i in range(n_g)]
    lower_bound = [0 for i in range(n_g)]
    constraint = [[None for t in range(n_s)] for i in range(n_g)]

    acdc = False
    for i in range(n_g):
        if 'ramp' in gen[i] and not 'stor' in gen[i]:
            ramp_up[i] = [gen[i]['ramp']['b'][0] * dt[t] for t in range(n_s)]
            ramp_down[i] = [gen[i]['ramp']['b'][1] * dt[t] for t in range(n_s)]
            starts = [t for t in range(n_s) if binary[i][t + 1] and not binary[i][t]]
            stops = [t for t in range(n_s) if not binary[i][t + 1] and binary[i][t]]
            lower_bound[i] = gen[i][gen[i]['states'][0][0]]['lb'][-1]
            for st in starts:
                # If the ramp rate is less than the lb, increase ramp
                # rate at moment of startup.
                ramp_up[i][st] = max(ramp_up[i][st], lower_bound[i])
            for st in stops:
                # If the ramp rate is less than the lb, increase ramp
                # rate at moment of shutdown.
                ramp_down[i][st] = max(ramp_down[i][st], lower_bound[i])
            upper_bound[i] = gen[i]['ub']
        if gen[i]['type'] == 'ACDCConverter':
            acdc = True
            dc_ac = abs(gen[i]['output']['e'][0][-1])
            ac_dc = gen[i]['output']['dc'][0][0]
    if len(s) == 1 and (s[0] == 'e' or s[0] == 'dc') and any([g['type']== 'CombinedHeatPower' for g in gen]):
        # For combined heat and power cases.
        s.append('h')
    if acdc and not 'dc' in s:
        s.append('dc')
    if acdc and not 'e' in s:
        s.append('e')
    if 'h' in s:
        elec = False
        direct = False
        for i in range(n_g):
            if gen[i]['type'] == 'CombinedHeatPower':
                if 'e' in gen[i]['output']:
                    elec = True
                if 'dc' in gen[i]['output']:
                    direct = True
        if not 'e' in s and elec:
            s.append('e')
        if not 'dc' in s and direct:
            s.append('dc')
    s2 = {
        'e': ['CombinedHeatPower', 'ElectricGenerator'],
        'dc': ['CombinedHeatPower', 'ElectricGenerator'],
        'h': ['CombinedHeatPower','Heater'],
        'c': ['Chiller'],
        'cw': ['Chiller', 'CoolingTower'],
        'hy': ['Electrolyzer', 'HydrogenGenerator'],
    }
    spare_gen = {}
    max_out = {}
    inc = {}
    heat_output = [[] for i in range(n_g)]
    for k in s:
        spare_gen[k] = [0 for i in range(n_s)]
        max_out[k] = [[0 for t in range(n_s + 1)] for i in range(n_g)]
        inc[k] = []
        for i in range(n_g):
            if not 'stor' in gen[i] and gen[i]['type'] in s2[k]:
                if k == 'e' and acdc and 'dc' in gen[i]['output']:
                    inc[k].append(i)
                elif k == 'dc' and acdc and 'e' in gen[i]['output']:
                    inc[k].append(i)
                elif k in gen[i]['output']:
                    inc[k].append(i)
        for i in range(n_g):
            if i in inc[k]:
                max_out[k][i][0] = gen_output[i][0]
                # Constrained by initial condition (can't do anything).
                start = None
                for t in range(n_s):
                    if binary[i][t + 1]:
                        if not binary[i][t]:
                            start = t  # Just turned on.
                        if upper_bound[i] <= max_out[k][i][t] + ramp_up[i][t]:
                            max_out[k][i][t + 1] = upper_bound[i]
                        else:
                            max_out[k][i][t + 1] = max_out[k][i][t] + ramp_up[i][t]
                        if not start is None:
                            # Last index (0->n_s-1) when gen was off where it could be turned on early if neccesary to satisfy ramping constraint.
                            constraint[i][t] = start - 1
                for t in range(n_s - 1, 0, -1):
                    if (max_out[k][i][t] - ramp_down[i][t]) > max_out[k][i][t+1]:
                        # Constrained by shutdown.
                        max_out[k][i][t] = min([upper_bound[i],(max_out[k][i][t + 1] + ramp_down[i][t])])
                        if constraint[i][t - 1] is None:
                            # First index (0-->n_s-1) where gen has shut down, where it could be left on to satisfy ramping constraint.
                            constraint[i][t - 1] = min([z - 1 for z in range(t + 1, n_s + 1) if max_out[k][i][z] == 0])
                if k == 'h' and gen[i]['type'] == 'CombinedHeatPower':# Convert GenOutput to heatOutput.
                    heat_output[i] = chp_heat(gen[i], gen_output[i])
                    if 'e' in gen[i]['output']:
                        max_out['h'][i] = chp_heat(gen[i], max_out[k][i])
                    else:
                        max_out['h'][i] = chp_heat(gen[i], max_out[k][i])
                if gen[i]['type'] == 'Chiller' and gen[i]['source'] == 'heat':
                    # Assume net heat production remains the same, so do
                    # not count spare absorption chiller capacity.
                    # Don't count towards spare capacity.
                    max_out[k][i] = gen_output[i]
            if gen[i]['type'] == 'Utility' and k in gen[i]['output']:
                max_out[k][i] = [gen[i]['x']['ub']]
                # max_out[k][i].extend([gen_output[i][j+1] for j in range(n_s)])
                max_out[k][i].extend([gen[i]['x']['ub'] for j in range(n_s)])
    if acdc:
        for i in inc['e']:
            if 'dc' in gen[i]['output']:
                max_out['e'][i] = [z * dc_ac for z in max_out['dc'][i]]
        for i in inc['dc']:
            if 'e' in gen[i]['output']:
                max_out['dc'][i] = [z * ac_dc for z in max_out['e'][i]]
    spare_capacity = {}
    for k in s:
        for i in inc[k]:
            if k == 'h' and gen[i]['type'] == 'CombinedHeatPower':
                spare_gen[k] = [spare_gen[k][t] + (max_out[k][i][t + 1] - heat_output[i][t + 1]) for t in range(n_s)]
            elif k == 'e' and 'dc' in gen[i]['output']:
                spare_gen[k] = [spare_gen[k][t] + (max_out[k][i][t + 1] - gen_output[i][t + 1]) * dc_ac for t in range(n_s)]
            elif k == 'dc' and 'e' in gen[i]['output']:
                spare_gen[k] = [spare_gen[k][t] + (max_out[k][i][t + 1] - gen_output[i][t + 1]) * ac_dc for t in range(n_s)]
            else:
                spare_gen[k] = [spare_gen[k][t] + (max_out[k][i][t + 1] - gen_output[i][t + 1]) for t in range(n_s)]
        for i in range(n_g):
            if gen[i]['type'] == 'Utility' and k in gen[i]['output']:
                spare_capacity[k] = [spare_gen[k][t] + (gen[i]['x']['ub'] - gen_output[i][t + 1])for t in range(n_s)]
        if not k in spare_capacity:
            spare_capacity[k] = [spare_gen[k][t] + 0 for t in range(n_s)]
    return max_out, constraint, spare_capacity, spare_gen


def chp_heat(gen, output):
    n_s = len(output)
    # Assuming all outputs are nx1.
    heat_out = [
        -gen['const_demand']['district_heat'] * int(output[t] > 0)
        for t in range(n_s)
    ]
    states = gen['states'][-1]
    for t in range(n_s):
        net_out = 0
        j = 0
        # Use < instead of <= because index is 1 less than number of
        # states.
        while (j < len(states) and net_out < output[t]):
            seg = min([output[t] - net_out, gen[states[j]]['ub'][1]])
            net_out += seg
            heat_out[t] += seg * gen['output']['h'][-1][j]
            j += 1

    return heat_out
