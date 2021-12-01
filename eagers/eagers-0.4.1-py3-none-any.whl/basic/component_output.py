def component_output(gen,subnet,gen_state,t):
    dispatch = {}
    for k in gen_state:
        dispatch[k] = gen_state[k][t]
    gen_names = [g['name'] for g in gen]
    source_input = [0 for k in range(len(gen))]
    for i in range(len(gen)):
        if 'eff' in gen[i] and 'cap' in gen[i]:
            k = gen[i]['name']
            source_input[i] = dispatch[k]/eff_interp(gen[i]['cap'],gen[i]['eff'],dispatch[k])
    out = subnet['abbreviation']
    nn = len(subnet['nodes'])
    node_prod = [[] for n in range(nn)]
    for n in range(nn):
        n_equip = subnet['equipment'][n]
        for equip in n_equip:
            k = gen_names.index(equip)
            if out in gen[k]['output']:
                #exceptions for cold-water and combined heat and power. Everything else has 1 input and 1 output
                ##TODO change sign on cw output in chiller and coolingtower
                if out == 'cw' and gen[k]['type'] == 'Chiller':
                    ##TODO add pumping work?
                    node_prod[n].append(-dispatch[equip] - source_input[k])
                elif out == 'cw' and gen[k]['type'] == ['CoolingTower']:
                    node_prod[n].append(dispatch[equip])
                elif out == 'h' and gen[k]['type'] == 'CombinedHeatPower':
                    node_prod[n].append(source_input[k]*eff_interp(gen[k]['cap'],gen[k]['chp_eff'],dispatch[equip]))
                elif out == 'e' and gen[k]['type'] == 'ACDCConverter':
                    if dispatch[equip]>0:
                        node_prod[n].append(-dispatch[equip])
                    else:
                        node_prod[n].append(abs(gen[k]['output']['e'][0][-1]*dispatch[equip]))
                elif out == 'dc' and gen[k]['type'] == 'ACDCConverter':
                    if dispatch[equip]<0:
                        node_prod[n].append(dispatch[equip])
                    else:
                        node_prod[n].append(gen[k]['output']['dc'][0][0]*dispatch[equip])
                elif gen[k]['type'] == 'Utility':
                    node_prod[n].append(dispatch[equip])
                elif all([j>0 for j in gen[k]['output'][out][-1]]):
                    node_prod[n].append(dispatch[equip])
                elif all([j<0 for j in gen[k]['output'][out][-1]]):
                    node_prod[n].append(-source_input[k])
    net_production = [sum(node_prod[n]) for n in range(nn)]
    mag_production = [sum([abs(prod) for prod in node_prod[n]]) for n in range(nn)]
    return net_production, mag_production

def eff_interp(cap,eff,x):
    if x == 0:
        eff_t = 1 #avoid divide by zero
    elif x<cap[0]:
        eff_t = eff[0]
    else:
        i = 1
        while i<len(cap)-1 and x>cap[i]:
            i+=1
        r = (x-cap[i-1])/(cap[i]-cap[i-1])
        eff_t = (1-r)*eff[i-1] + r*eff[i]
    return eff_t 