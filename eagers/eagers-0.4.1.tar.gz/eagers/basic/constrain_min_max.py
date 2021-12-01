def constrain_min_max(gen, limit, ic, dt, dt_sum):
    n_g = len(gen)
    
    min_power = []
    max_power = []
    for i in range(n_g):
        upper_bound = 0
        lower_bound = 0
        ramp_down = None
        ramp_up = None
        if 'ramp' in list(gen[i].keys()):
            ramp_down = gen[i]['ramp']['b'][0]
            ramp_up = gen[i]['ramp']['b'][1]
        if gen[i]['type'] in ['ElectricGenerator','CombinedHeatPower','Chiller','Heater','CoolingTower','Electrolyzer','HydrogenGenerator'] and len(gen[i]['states'][-1])>0 :
            for j in gen[i]['states'][-1]:
                upper_bound += gen[i][j]['ub'][-1]
        elif gen[i]['type'] == 'HydroStorage':
            pass # Do something to set UB.
        elif gen[i]['type'] == 'Market':
            pass # Do something to set UB.
        elif gen[i]['type'] == 'Utility' and len(gen[i]['states'][-1])>0:
            upper_bound = gen[i][gen[i]['states'][0][0]]['ub']
            if len(gen[i]['states'][-1])>1:
                lower_bound = -gen[i][gen[i]['states'][0][1]]['ub']
        if limit == 'unconstrained' or ic is None or ramp_down is None:
            min_power.append(lower_bound)
            max_power.append(upper_bound)
        else:
            if limit == 'constrained':
                dtr = dt
            else:
                dtr = dt_sum
            min_power.append(max([lower_bound,ic[i]-ramp_down*dtr]))
            max_power.append(min([upper_bound,ic[i]+ramp_up*dtr]))
    return min_power, max_power