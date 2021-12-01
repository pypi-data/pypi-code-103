"""After-the-fact dispatch result plotting logic from Excel project
file.

Functions:
plot_dispatch_result - Plot a dispatch result.
extract_dispatch_data - Extract dispatch data from HDF5 result file.
"""

from eagers.config.path_spec import HDF5_SUFFIX, USER_DIR_SIMRESULTS
from eagers.basic.file_handling import find_file_in_userdir
from eagers.basic.hdf5 import h5file_context, DatetimeFloatConverter as DFC
from eagers.write.result_file import name_dictionary, additional_fields
from eagers.basic.all_demands import count_nodes
from eagers.basic.result_template import result_template
from eagers.setup.initialize_observer import  initialize_building_observer


def load_dispatch_result(proj):
    """Plot the dispatch result for a saved simulation file.
    """
    # Extract dispatch data from HDF5 file
    names = name_dictionary(proj['preload'],proj['plant'])
    
    date = [proj['options']['start_date']]
    _,zones,pl = initialize_building_observer(proj['plant']['building'], proj['test_data']['weather'], date)
    all_data_nodes = count_nodes(proj['preload']['subnet'],proj['test_data'])
    history = result_template(all_data_nodes,names, zones, pl)
    history,disp_data = extract_dispatch_data(proj,names)
    gen = proj['preload']['gen_qp_form']
    subnet = proj['preload']['subnet']
    return history, disp_data, gen, subnet

def extract_dispatch_data(project,names):
    """Extract dispatch data for the given Eagers object.

    Returns a dictionary of the structure:
        data['power'][network][Component name] (kW)
    OR:
        data['soc'][network]['x' (timestamp) or 'y' (value)] (frac)
    """
    # Get data from HDF5 file.
    filepath = find_file_in_userdir(
        USER_DIR_SIMRESULTS, project['name'], HDF5_SUFFIX)
    minimization_directives = additional_fields(names)
    history = {}
    dispatch = {}
    history['generator_state'] = {}
    for n in names['components']:
        history['generator_state'][n] = []
    history['storage_state'] = {}
    for n in names['storage']:
        history['storage_state'][n] = []
    dispatch['node_data'] = {}
    for n in names['nodes']:
        dispatch['node_data'][n] = {}
        dispatch['node_data'][n]['demand'] = []
        if minimization_directives['hydro_exists']:
            dispatch['node_data'][n]['inflow'] = []
            dispatch['node_data'][n]['outflow'] = []
    dispatch['weather'] = {}
    dispatch['weather']['dir_norm_irr'] = []
    wf = ['glo_horz_irr','dif_horz_irr','t_dryb','t_dewp','rh','pres_pa','wdir','wspd','tot_cld','opq_cld']
    if minimization_directives['building_exists']:
        for f in wf:
            dispatch['weather'][f] = []
    # Open file in read mode.
    with h5file_context(filepath, mode='r') as h5f:
        table = h5f.root.dispatch
        timestamp = table.col('timestamp')
        history['timestamp'] = [DFC.f2d_sgl2sgl(t) for t in timestamp]# Convert array of timestamp floats to list of datetimes.
        dispatch['timestamp'] = history['timestamp']
        generator_state = table.col('generator_state')
        for r in generator_state:
            for i,name in enumerate(names['components']):
                history['generator_state'][name].append(r[i])
        storage_state = table.col('storage_state')
        for r in storage_state:
            for i,name in enumerate(names['storage']):
                history['storage_state'][name].append(r[i])
        node_data = table.col('nodedata')
        for r in node_data:
            for i,name in enumerate(names['nodes']):
                dispatch['node_data'][name]['demand'].append(r[i][0])
                if minimization_directives['hydro_exists']:
                    dispatch['node_data'][name]['inflow'].append(r[i][2])
                    dispatch['node_data'][name]['outflow'].append(r[i][3])
        weather = table.col('weather')
        for r in weather:
            dispatch['weather']['dir_norm_irr'].append(r[0])
            if minimization_directives['building_exists']:
                for i,f in enumerate(wf):
                    dispatch['weather'][f].append(r[i+1])
        ##TODO finish importing data
        # if minimization_directives['multinode']:
        #     lineflow = table.col('line_flow')
        #     dispatch['line_flow'] = gen_descr(names['lines'], shape=None, pos=3)
        # if minimization_directives['fluidloop_exists']:
        #     dispatch['fluid_loop'] = gen_descr(names['fluid_loop'], shape=None, pos=4)
        # if minimization_directives['building_exists']:
        #     dispatch['building'] = building_descr(names['buildings'], z_dif, pl_dif, shape=None, pos=5)
    return history, dispatch
