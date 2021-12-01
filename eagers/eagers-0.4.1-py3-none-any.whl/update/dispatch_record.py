"""Logic for recording the result of one step of the dispatch loop.

Functions:
dispatch_record
record_initial_conditions
"""
from eagers.basic.net_cost import net_cost
from eagers.basic.result_template import result_template
from eagers.write.result_file import \
    append_step_dispatch, append_dispatch_ic, append_step_predicted


def dispatch_record(gen, dispatch, observer, subnet, actual_data, solution, project_name):
    """Records the last dispatch 
    """
    dispatch['timestamp'] = solution['timestamp'][0]
    for i,k in enumerate(observer['gen_names']):
        dispatch['generator_state'][k] = solution['generator_state'][k][0]
        if k in solution['storage_state']:
            dispatch['storage_state'][k] = solution['storage_state'][k][0]
    for i,k in enumerate(observer['line_names']):
        dispatch['line_flow'][k] = solution['line_flow'][k][0]
    for i in range(len(observer['building_avg_temp'])):
        k = observer['building_name'][i]
        dispatch['building'][k]['cooling'] = solution['building'][k]['cooling'][0]
        dispatch['building'][k]['heating'] = solution['building'][k]['heating'][0]
        dispatch['building'][k]['Tzone'] = observer['building_zone_temp'][i]
        dispatch['building'][k]['supply'] = observer['building_supply'][i]
        dispatch['building'][k]['return_'] = observer['building_return'][i]
        dispatch['building'][k]['avg_T'] = observer['building_avg_temp'][i]
        dispatch['building'][k]['electric'] = actual_data['building']['E0'][0][i]
        
    for i in range(len(observer['fluid_loop_name'])):
        dispatch['fluid_loop'][observer['fluid_loop_name'][i]] = observer['fluid_loop_temperature'][i]
    
    for net in subnet['network_names']:
        for an in subnet[net]['nodes']:
            for n in an:
                if n in actual_data and 'demand' in actual_data[n]:
                    dispatch['nodedata'][n]['demand'] = actual_data[n]['demand'][0]
    for k in list(actual_data['weather'].keys()):
        dispatch['weather'][k] = actual_data['weather'][k][0]
    if 'hydro_soc' in solution and len(solution['hydro_soc']) > 0:
        dispatch['out_flow'] = [solution['line_flow'][subnet['hydro']['line_number'][n]][0] for n in range(len(subnet['hydro']['nodes']))]
    # Write result of simulation step to HDF5 file.
    append_step_dispatch(project_name, dispatch)

def predict_record(gen, predicted, observer, subnet, date, forecast, solution, project_name):
    n_s = len(date) - 1  # Numer of steps.
    predicted['timestamp'] = forecast['timestamp']
    predicted['cost'] = net_cost(gen, solution['dispatch'], date, forecast['input_cost'])
    for i,k in enumerate(observer['gen_names']):
        predicted['generator_state'][k] = solution['generator_state'][k]
        if k in solution['storage_state']:
            predicted['storage_state'][k] = solution['storage_state'][k]
    for i in range(len(observer['building_avg_temp'])):
        k = observer['building_name'][i]
        predicted['building'][k]['Tzone'] = [forecast['building']['Tzone'][t][i] for t in range(n_s)]
        predicted['building'][k]['electric'] = [forecast['building']['E0'][t][i] for t in range(n_s)]
        predicted['building'][k]['cooling'] = [forecast['building']['C0'][t][i] for t in range(n_s)]
        predicted['building'][k]['heating'] = [forecast['building']['H0'][t][i] for t in range(n_s)]
        predicted['building'][k]['avg_T'] = [forecast['building']['T_avg'][t][i] for t in range(n_s)]
    for i,k in enumerate(observer['line_names']):
        predicted['line_flow'][k] = solution['line_flow'][k]
    for i,k in enumerate(observer['fluid_loop_name']):
        predicted['fluid_loop'][k] = solution['fluid_loop'][k]
    for net in subnet['network_names']:
            for an in subnet[net]['nodes']:
                for n in an:
                    if n in forecast and 'demand' in forecast[n]:
                        predicted['nodedata'][n]['demand'] = forecast[n]['demand']
    for k in list(forecast['weather'].keys()):
        predicted['weather'][k] = forecast['weather'][k]
    if 'lb_relax' in solution:
        predicted['lb_relax'] = solution['lb_relax']

    # Write result of simulation step to HDF5 file.
    append_step_predicted(project_name, predicted)


def record_initial_conditions(data_t0, all_data_nodes, names, zones, pl, subnet, observer, project_name):
    dispatch = result_template(all_data_nodes,names, zones, pl)
    dispatch['timestamp'] = data_t0['timestamp'][0]
    observer['history']['timestamp'] = [data_t0['timestamp'][0]]
    for i,k in enumerate(observer['history']['generator_state']):
        dispatch['generator_state'][k] = observer['gen_state'][i]
        observer['history']['generator_state'][k] = [observer['gen_state'][i]]
        if k in observer['history']['storage_state']:
            dispatch['storage_state'][k] = observer['stor_state'][i]
            observer['history']['storage_state'][k] = [observer['stor_state'][i]]
    if len(observer['building_name'])>0:
        for i in range(len(observer['building_name'])):
            k = observer['building_name'][i]
            A = observer['building_conditioned_floor_area'][i]
            # Area-weighted temperature: Current average building zone
            # temperature (used as IC in optimization).
            t = sum([observer['building_zone_temp'][i][z]*A[z] for z in range(len(A))]) / sum(A)
            dispatch['building'][k]['avg_T'] = [t]
            observer['history']['building'][k]['avg_T'] = [t]
            dispatch['building'][k]['electric'] = [data_t0['building']['E0'][0][i]]
            dispatch['building'][k]['cooling'] = [data_t0['building']['C0'][0][i]]
            dispatch['building'][k]['heating'] = [data_t0['building']['H0'][0][i]]
            dispatch['building'][k]['Tzone'] = [observer['building_zone_temp'][i]]
            dispatch['building'][k]['return_'] = [observer['building_return'][i]]
            dispatch['building'][k]['supply'] = [observer['building_supply'][i]]
    for net in subnet['network_names']:
        for an in subnet[net]['nodes']:
            for n in an:
                if n in data_t0:
                    headers = list(data_t0[n].keys())
                    headers.remove('network')
                    for h in headers:
                        dispatch['nodedata'][n][h] = data_t0[n][h][0]
                        observer['history']['nodedata'][n][h] = [data_t0[n][h][0]]
    for k in data_t0['weather'].keys():
        dispatch['weather'][k] = data_t0['weather'][k][0]
        observer['history']['weather'][k] = [data_t0['weather'][k][0]]
    

    if not project_name is None:
        # Write to file.
        append_dispatch_ic(project_name, dispatch)