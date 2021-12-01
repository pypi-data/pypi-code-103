"""Logic for calculating net cost.
"""

def net_cost(gen, dispatch, date, input_cost):
    """Net cost.

    Positional arguments:
    gen - (list of dict) QP form of each component.
    dispatch - (list of list) Dispatch solution for each component.
    date - (list of datetime) Timestamps to calculate cost for.
    input_cost --  cost for fuel etc of each component
    """
    n_g = len(gen)
    gen_cost = [[0] for i in range(n_g)]
    n_s = len(date) - 1
    dt = [(date[t+1] - date[t]).seconds/3600 for t in range(n_s)]
    for i, g in enumerate(gen):
        if g['type'] in ['ElectricGenerator','CombinedHeatPower','Heater', 'CoolingTower', 'Electrolyzer', 'HydrogenGenerator']:                
            states = g['states'][-1]
            for t in range(n_s):
                p = 0
                j = 0
                c = 0
                while p < dispatch[i][t+1] and j < len(states):
                    x = min([g[states[j]]['ub'][-1],dispatch[i][t+1]-p])
                    p +=x
                    c += (x*g[states[j]]['f'][-1] + x*x*g[states[j]]['h'][-1])*input_cost[i][t]*dt[t]
                    j +=1
                if 'start_cost' in g and dispatch[i][t+1]>0 and dispatch[i][t]==0:
                    c += g['start_cost']
                gen_cost[i].append(c)
        elif g['type'] == 'Utility':
            for t in range(n_s):
                if dispatch[i][t] >= 0:
                    c = dispatch[i][t] * input_cost[i][t] * dt[t]
                elif 'sellback_rate' in g:
                    if g['sellback_rate'] > 0:
                        # Constant sellback rate.
                        c = dispatch[i][t] * g['sellback_rate'] * dt[t]
                    else:
                        c = dispatch[i][t] * g['sellback_perc'] / 100 * input_cost[i][t] * dt[t]
                else:
                    c = 0
                gen_cost[i].append(c)
        elif g['type'] == 'Tradepoint':
            for t in range(n_s):
                six_param = input_cost[i][t]
                x = dispatch[i][t]
                if x>0:
                    c = (x*six_param[0] + x*x*six_param[1])*dt[t]
                elif x<0:
                    c = (x*six_param[3] + x*x*six_param[4])*dt[t]
                gen_cost[i].append(c)
    cost = sum([sum(gen_cost[i]) for i in range(n_g)])
    return cost
