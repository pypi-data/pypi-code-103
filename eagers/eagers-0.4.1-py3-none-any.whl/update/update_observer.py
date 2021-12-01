import datetime
from eagers.solver.sort_solution import soc_2_power

def update_observer(gen,subnet,observer,date,options,solution,actual_data,forecast):   
    trim_history(gen,observer['history'],date[0],24)
    observer_short_history(gen,date,actual_data,subnet,solution,observer['history'])
    if options['method'] == 'planning': #assumes forecast is perfect
        n_s = len(date)-1
        date = [date[t] + datetime.timedelta(hours=options['horizon']) for t in range(len(date))] #count forward by len of the horizon, rounded to nearest second
    elif options['method'] in ['dispatch', 'control']:
        observer_future(gen,date,subnet,solution,forecast,observer['future'])
        n_s = 1 
        date =  [date[t] + datetime.timedelta(hours=options['resolution']) for t in range(len(date))] #count forward 1 step, rounded to nearest second
    observer['timestamp'] = date[0]
    n_g = len(gen)
    for i in range(n_g):
        if gen[i]['type'] in ['ElectricGenerator','CombinedHeatPower','Chiller','Heater','Electolyzer','HydrogenGenerator','CoolingTower']:
            observer['gen_state'][i] = solution['dispatch'][i][n_s]
            observer['gen_status'][i] = solution['dispatch'][i][n_s]>0
        elif gen[i]['type'] in ['ElectricStorage','ThermalStorage','HydrogenStorage']:
            observer['stor_state'][i] = solution['dispatch'][i][n_s]
        elif gen[i]['type'] in ['HydroStorage']:
            n = gen[i]['subnet_node']['hydro'] #dam #
            observer['stor_state'][i] = solution['hydro_soc'][n][n_s-1]  
    for i,k in enumerate(solution['line_flow']):
        observer['line_flow'][i] = solution['line_flow'][k][n_s-1]
    for i,k in enumerate(solution['fluid_loop']):
        observer['fluid_loop_temperature'][i] = solution['fluid_loop'][k][n_s-1]
    return date

def observer_short_history(gen,date,actual_data,subnet,solution,history):
    dt = [(date[t+1] - date[t]).total_seconds()/3600 for t in range(len(date)-1)]
    n_s = len(actual_data['timestamp'])
    history['timestamp'].extend(date[1:n_s+1])
    for i,k in enumerate(history['generator_state']):
        if 'stor' in gen[i]:
            sd = soc_2_power(gen[i]['stor'],solution['dispatch'][i],dt)
            history['generator_state'][k].extend(sd[:n_s])
            history['storage_state'][k].extend(solution['dispatch'][i][1:n_s+1])
        else:
            history['generator_state'][k].extend(solution['dispatch'][i][1:n_s+1])
    for k in history['line_flow']:
            history['line_flow'][k].extend(solution['line_flow'][k][:n_s])
    for k in history['fluid_loop']:
            history['fluid_loop'][k].extend(solution['fluid_loop'][k][:n_s])
    for net in subnet['network_names']:
        for an in subnet[net]['nodes']:
            for n in an:
                if n in actual_data:
                    headers = list(actual_data[n].keys())
                    headers.remove('network')
                    for h in headers:
                        if not h in history['nodedata'][n]:
                            history['nodedata'][n][h] = []
                        history['nodedata'][n][h].extend(actual_data[n][h][:n_s])
    for k in list(actual_data['weather'].keys()):
        history['weather'][k].extend(actual_data['weather'][k][:n_s])
    if 'lb_relax' in solution:
        if 'lb_relax' not in history:
            history['lb_relax'] = []
        history['lb_relax'].extend(solution['lb_relax'][:n_s])

def observer_future(gen,date,subnet,solution,forecast,future):
    dt = [(date[t+1] - date[t]).total_seconds()/3600 for t in range(len(date)-1)]
    future['timestamp'] = forecast['timestamp'][1:]
    for i,k in enumerate(future['generator_state']):
        if k in future['storage_state']:
            sd = soc_2_power(gen[i]['stor'],solution['dispatch'][i],dt)
            future['generator_state'][k] = sd[1:]
            future['storage_state'][k] = solution['dispatch'][i][2:]
        else:
            future['generator_state'][k] = solution['dispatch'][i][2:]
    for k in future['line_flow']:
        future['line_flow'][k] = solution['line_flow'][k][1:]
    for k in future['fluid_loop']:
        future['fluid_loop'][k] = solution['fluid_loop'][k][1:]
    for net in subnet['network_names']:
        for an in subnet[net]['nodes']:
            for n in an:
                if n in forecast:
                    headers = list(forecast[n].keys())
                    headers.remove('network')
                    for h in headers:
                        if not h in future['nodedata'][n]:
                            future['nodedata'][n][h] = []
                        future['nodedata'][n][h].append(forecast[n][h][1:])
    for k in list(forecast['weather'].keys()):
        future['weather'][k] = forecast['weather'][k][1:]
    if 'lb_relax' in solution:
        future['lb_relax'] = solution['lb_relax'][1:]


def trim_history(gen,history,date,length):
    h_time = history['timestamp']
    td = 0
    while h_time[td]<(date-datetime.timedelta(hours=length)):
        td +=1
    if td>0:
        headers = list(history.keys())
        for h in headers:
            if isinstance(history[h],list) and len(history[h])>0:
                if isinstance(history[h][0],(float,int)) or h == 'timestamp':
                    del history[h][0:td]
                else:
                    for x in range(len(history[h])):
                        del history[h][x][0:td]
            elif isinstance(history[h],dict):
                sub_headers = list(history[h].keys())
                for sh in sub_headers:
                    if isinstance(history[h][sh],list) and len(history[h][sh])>0:
                        if isinstance(history[h][sh][0],(float,int)):
                            del history[h][sh][0:td]
                        else:
                            for x in range(len(history[h][sh])):
                                del history[h][sh][x][0:td]