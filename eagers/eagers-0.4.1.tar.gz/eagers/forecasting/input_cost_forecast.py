import datetime as dt
from eagers.config.units import kWh_per_MMBtu_natgas

def input_cost_forecast(gen,date,other_data):
    """Update energy purchase costs for the current time.

    Positional arguments:
    date - (list of datetime) Dates for horizon (current time not
        included).
    gen - (list of dict) Generator information.
    utility - Timeseries utility, market, and tradepoint information.
    """
    n_s = len(date)
    n_g = len(gen)
    source = [None] * n_g
    input_cost = [[] for i in range(n_g)]
    # Get the rate for each utility.
    # Assumes there is only one utility for each network type.
    for i, g in enumerate(gen):
        if g['type'] == 'Utility':
            source[i] = g['source']
            if 'sum_start_month' in g:
                # Ensure summer and winter seasons don't start on the same day.
                yr = date[0].year
                sum_start = dt.datetime(yr, g['sum_start_month'], g['sum_start_day'])
                if g['win_start_month'] > g['sum_start_month'] or \
                    (g['win_start_month'] == g['sum_start_month'] \
                        and g['win_start_day'] > g['sum_start_day']):
                    yr +=1
                win_start = dt.datetime(yr, g['win_start_month'], g['win_start_day'])
                # Whether the winter pricing season starts this year, as
                rate = []
                for d in date:
                    h = d.hour
                    day = d.weekday()
                    if d > sum_start and d <= win_start:
                        try:
                            j = g['sum_rate_table'][day][h] - 1
                            rate.append(g['sum_rates'][j][0])
                        except:
                            rate.append(g['sum_rates'][0])
                    else:
                        try:
                            j = g['win_rate_table'][day][h] - 1
                            rate.append(g['win_rates'][j][0])
                        except:
                            rate.append(g['win_rates'][0])
                input_cost[i] = rate  # Utility rate in $/kWh.
            else:
                input_cost[i] = update_TSutility(g,other_data)
        elif g['type']=='Tradepoint': 
            input_cost[i] = update_tradepoint(g,other_data,n_s)
        ##TODO add market correctly with Haley's matlab update
        # elif g['type']=='Market': #Market varaible/bids is empty during initialization
        #     if market_rate == None:
        #         market_rate = [[]]
        #         m_num = 0
        #     else:
        #         market_rate.append([])
        #         m_num += 1
        #     na = len(market['award']['time'])
        #     awarded = 0
        #     for j in range(na):
        #         if market['award']['time'] > date[0]:
        #             # Identify how many awards have already passed.
        #             awarded += 1
        #     n = na - awarded
        #     for d in date:
        #         while n < na and d < market['award']['time'][n]:
        #             n += 1
        #         market_rate[m_num].append(market['award']['price'][m_num][n])
        #     input_cost[i] = market_rate[m_num]

    # Match each utility-fueled generator with its corresponding utility
    # cost, if a corresponding utility exists.
    for i, g in enumerate(gen):
        util_fueled = ('ElectricGenerator', 'CombinedHeatPower', 'Chiller',
            'Heater', 'CoolingTower', 'Electrolyzer', 'HydrogenGenerator')
        if g['type'] in util_fueled:
            try:
                util_index = source.index(g['source'])
            except ValueError:
                # No utility (don't scale costs).
                util_index = None
                input_cost[i] = [1] * n_s
            if util_index is not None:
                input_cost[i] = input_cost[util_index]
    return input_cost

def update_TSutility(gen,other_data):
    conversion = 1
    if gen['source'] in ('ng', 'diesel'):
        # Convert gas rate from $/MMBTU to $/kWh.
        conversion = 1 / kWh_per_MMBtu_natgas
    rate = [r*conversion for r in other_data[gen['rate']]]
    return rate

def update_tradepoint(gen,other_data,n_s):
    conversion = 1
    if gen['source'] in ('ng', 'diesel'):
        # Convert gas rate from $/MMBTU to $/kWh.
        conversion = 1 / kWh_per_MMBtu_natgas
    rate = [[other_data[f][t]*conversion for f in gen['six_param']] for t in range(n_s)]
    return rate