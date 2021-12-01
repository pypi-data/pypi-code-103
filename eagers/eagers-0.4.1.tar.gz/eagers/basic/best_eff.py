def best_eff(gen, scale_cost, marginal):
    '''
    identifies the operating point of maximum efficiency (lowest cost per kW)
    used to estimate the lowest possible cost if a generator is added 
    in order to eliminate expensive cases without testing them
    '''
    n_g = len(gen)
    c_red = {}
    c_red['eff'] = [0 for i in range(n_g)]
    c_red['p'] = [0 for i in range(n_g)]
    c_red['c'] = [0 for i in range(n_g)]
    c_red['ab'] = [None for i in range(n_g)]
    for i in range(n_g):
        if gen[i]['type'] in ['CombinedHeatPower', 'ElectricGenerator', 'HydrogenGenerator','Heater','Chiller']:
            c_red['eff'][i] = gen[i]['max_eff']
            c_red['p'][i] = gen[i]['max_eff_point']
            c_red['c'][i] = scale_cost[i][0]
        if gen[i]['type'] in ['CombinedHeatPower', 'ElectricGenerator']:
            if 'e' in gen[i]['output']:
                c_red['ab'][i] = 'e'
            elif 'dc' in gen[i]['output']: 
                c_red['ab'][i] = 'dc'
        if gen[i]['type'] == 'Chiller':
            c_red['ab'][i] = 'c'
            if gen[i]['source'] == 'heat':
                c_red['c'][i] = marginal['h']
            else:
                c_red['c'][i] = marginal['e']
        if gen[i]['type'] == 'Heater':
            c_red['ab'][i] = 'h'
        if gen[i]['type'] in  ['HydrogenGenerator','CoolingTower','Electrolyzer']:
            c_red['c'][i] = marginal['e']
            c_red['ab'][i] = 'hy'
            if gen[i]['type'] == 'CoolingTower':
                c_red['ab'][i] = 'cw'
    return c_red