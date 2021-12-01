'''Defines logic pertaining to the handling of HDF5 simulation results
files.

Classes:
Preamble

Functions:
new_result_file
result_file_setup
new_h5_result_filepath
existing_h5_result_filepath
append_dispatch_ic
append_step_result
groom_for_record
write_dispatch_step
write_predicted_step
write_solution
write_data
read_dispatch
extract_dispatch_data
'''

from typing import Optional

import numpy as np

from eagers.basic.file_handling import (
    ensure_dirpath,
    ensure_suffix,
    find_file_in_userdir,
)
from eagers.basic.hdf5 import h5file_context, DatetimeFloatConverter as DFC
from eagers.config.path_spec import HDF5_SUFFIX, USER_DIR_SIMRESULTS
from eagers.config.user import DEBUG_MODE
from eagers.write.result_description import result_description
from eagers.basic.gen_limit import chp_heat

class Preamble:
    '''Holds a '/'-separated string for defining a path to a certain
    node in an HDF5 file.
    '''

    sep = '/'

    def __init__(self, s: Optional[str] = None):
        self.s = s.strip(self.sep) if s else ''

    def __repr__(self):
        return f'{type(self).__name__}({self.s!r})'

    def __str__(self):
        return self.s

    def __truediv__(self, other):
        new_instance = self.__class__(self.s)
        new_instance.append(other)
        return new_instance

    def append(self, x):
        addition = x.strip(self.sep)
        if self.s:
            addition = f'{self.sep}{addition}'
        self.s += addition

    @property
    def levels(self):
        return self.s.split(self.sep)


def new_result_file(proj_name, names, dimensions, zones, pl):
    '''Create a new HDF5 results file.

    Positional arguments:
    proj_name - (str) Name of the project. This becomes the name of the
        file.
    names - (dict of list of str) All generator, storage, node, line,
        building and fluid_loop names in the project.
    dimensions - (dict) Dimension counts for space to be allocated in
        result file structures.
    '''
    # Check that the given file name does not already exist.
    filepath = new_h5_result_filepath(proj_name)
    if not DEBUG_MODE and filepath.exists():
        raise ValueError(f'File with name {proj_name!r} already exists.')
    minimization_directives = additional_fields(names)
    # Open file in 'w'rite mode.
    with h5file_context(filepath, mode='w', title=f'{proj_name} results') as h5file:
        # Create tables based on specified dimensions.
        disp, pred, solu = result_description(
            names, dimensions, minimization_directives, zones, pl
        )
        h5file.create_table('/', 'dispatch', disp)
        h5file.create_table('/', 'predicted', pred)
        h5file.create_table('/', 'solution', solu)


def result_file_setup(preload, plant, date, zones, pl):
    '''Returns a dictionary of result file dimensions.'''
    # Create dictionary of element names for results to be saved in.
    names = name_dictionary(preload,plant)
    dimensions = dict(
        horizon=len(date) - 1,
        zone=max(zones),
        plantloop=max(pl),
        timer=3,
    )
    
    return names, dimensions

def additional_fields(names):
    '''minimization_directives - (dict) Directives for minimizing file
        size.'''
    minimization_directives = dict(
        heating_exists=bool(names['heating_nodes']),
        cooling_exists=bool(names['cooling_nodes']),
        hydro_exists=bool(names['hydro']),
        multinode=len(names['nodes']) > 1,
        fluidloop_exists=bool(names['fluid_loop']),
        building_exists=bool(names['buildings']),
    )
    return minimization_directives

def name_dictionary(preload,plant):
    names = {}
    names['components'] = [g['name'] for g in preload['gen_qp_form']]
    names['storage'] = [g['name'] for g in preload['gen_qp_form'] if 'stor' in g]
    names['nodes'] = [n['name'] for n in plant['network']]
    names['lines'] = []
    for net in preload['subnet']['network_names']:
        snl = preload['subnet'][net]['line']
        names['lines'].extend([snl['node1'][i] + '_to_' + snl['node2'][i]for i in range(len(snl['node1']))])
    names['buildings'] = [b['name'] for b in plant['building']]
    names['fluid_loop'] = [fl['name'] for fl in plant['fluid_loop']]
    if 'district_heat' in preload['subnet']:
        names['heating_nodes'] = [n[0] for n in preload['subnet']['district_heat']['nodes']]
    else:
        names['heating_nodes'] = []
    if 'district_cool' in preload['subnet']:
        names['cooling_nodes'] = [n[0] for n in preload['subnet']['district_cool']['nodes']]
    else:
        names['cooling_nodes'] = []
    names['hydro'] = [g['name'] for g in preload['gen_qp_form'] if g['type'] == 'HydroStorage']
    return names

def new_h5_result_filepath(filename):
    '''Generate the path to a new HDF5 results file with the given name.'''
    return ensure_dirpath(USER_DIR_SIMRESULTS / ensure_suffix(filename, HDF5_SUFFIX))


def existing_h5_result_filepath(filename):
    '''Generate the path to the existing HDF5 results file with the
    given name.
    '''
    return find_file_in_userdir(USER_DIR_SIMRESULTS, filename, HDF5_SUFFIX)


def append_dispatch_ic(proj_name, disp_ic):
    '''Append an initial condition result to the file corresponding to
    the given project name.

    Positional arguments:
    proj_name - (str) Name of the project.
    disp_ic - (dict) Data for the initial condition dispatch result.
    '''
    # Convert vanilla Python lists to NumPy arrays, and remove empty
    # lists.
    groomed_disp = groom_for_record(disp_ic)
    # Open file in append mode, requiring its existence already.
    filepath = existing_h5_result_filepath(proj_name)
    with h5file_context(filepath, mode='r+') as h5file:
        # Write to the table's Row object, then append it to the table.
        table = h5file.root.dispatch
        write_dispatch_step(table, groomed_disp)
        table.row.append()


def append_step_predicted(proj_name, pred_step):
    '''Append a single step prediction to the file corresponding to the
    given project name.

    Positional arguments:
    proj_name - (str) Name of the project.
    pred_step - (dict) Data for this step's predicted result.
    '''
    # Convert vanilla Python lists to NumPy arrays, and remove empty
    # lists.
    groomed_pred = groom_for_record(pred_step)
    # Open file in append mode, requiring its existence already.
    filepath = existing_h5_result_filepath(proj_name)
    with h5file_context(filepath, mode='r+') as h5file:
        # Write to the table's Row object, then append it to the table.
        table = h5file.root.predicted
        write_predicted_step(table, groomed_pred)
        table.row.append()


def append_step_solution(proj_name, solution):
    '''Append a single step solution to the file corresponding to the
    given project name.

    Positional arguments:
    proj_name - (str) Name of the project.
    solution - (dict) Data for this step's solution result.
    '''
    # Convert vanilla Python lists to NumPy arrays, and remove empty
    # lists.
    groomed_solu = groom_for_record(solution)
    # Open file in append mode, requiring its existence already.
    filepath = existing_h5_result_filepath(proj_name)
    with h5file_context(filepath, mode='r+') as h5file:
        # Write to the table's Row object, then append it to the table.
        table = h5file.root.solution
        write_solution(table, groomed_solu)
        table.row.append()


def append_step_dispatch(proj_name, disp_step):
    '''Append a single step result to the file corresponding to the
    given project name.

    Positional arguments:
    proj_name - (str) Name of the project.
    disp_step - (dict) Data for this step's dispatch result.
    '''
    # Convert vanilla Python lists to NumPy arrays, and remove empty
    # lists.
    groomed_disp = groom_for_record(disp_step)
    # Open file in append mode, requiring its existence already.
    filepath = existing_h5_result_filepath(proj_name)
    with h5file_context(filepath, mode='r+') as h5file:
        # Write to the table's Row object, then append it to the table.
        table = h5file.root.dispatch
        write_dispatch_step(table, groomed_disp)
        table.row.append()


def groom_for_record(data):
    '''Convert the given data structure's vanilla Python lists to NumPy
    arrays.

    Positional arguments:
    data - (dict) Data structure.
    '''
    # Define function to handle NumPy arrays.
    def groom_ndarray(a):
        if 0 not in a.shape:
            # The array is not empty.
            # If the array can be flattened, flatten it to match the
            # shape of its column description.
            if a.ndim > 1:
                # Number of dimensions > 1.
                n_largedim = np.count_nonzero(np.array(a.shape) > 1)
                if n_largedim <= 1:
                    a = a.flatten()
            return a

    result = {}
    for k, v in data.items():
        if isinstance(v, dict):
            result[k] = groom_for_record(v)
        elif isinstance(v, list):
            if v != []:
                result[k] = groom_ndarray(np.array(v))
        elif isinstance(v, np.ndarray):
            result[k] = groom_ndarray(v)
        elif v != None:
            result[k] = v
    return result


def write_dispatch_step(table, disp_step):
    '''Write one step of dispatch results to HDF5 file.'''
    # Write timestamp.
    table.row['timestamp'] = DFC.d2f_sgl2sgl(disp_step.get('timestamp'))
    # Write dispatch data.
    write_data_structure(table, disp_step, Preamble(), {'timestamp'})


def write_predicted_step(table, pred_step):
    '''Write one step of predicted results to HDF5 file.'''
    # Write timestamp.
    table.row['timestamp'] = DFC.d2f_sgl2sgl(pred_step.get('timestamp'))
    table.row['cost'] = pred_step.get('cost')
    # Write predicted data.
    write_data_structure(table, pred_step, Preamble(), {'timestamp', 'cost'})


def write_solution(table, solu):
    '''Write solution results to HDF5 file.'''
    table.row['timestamp'] = DFC.d2f_sgl2sgl(solu.get('timestamp'))
    table.row['timer'] = solu.get('timer')
    # Write solution data.
    write_data_structure(table, solu, Preamble(), {'timestamp', 'timer'})


def write_data_structure(table, source, preamble, excluded_fields):
    keys = set(source.keys()) - excluded_fields
    for k in keys:
        v = source.get(k)
        subitems = None
        try:
            subitems = v.items()
        except (AttributeError, TypeError):
            # v has no 'items' attribute or v.items isn't callable.
            write_data(table, source, preamble, excluded_fields)
            continue
        if any(isinstance(v1, dict) for k1, v1 in subitems):
            write_data_structure(table, v, preamble / k, excluded_fields)
        else:
            write_data(table, source, preamble / k, excluded_fields)


def write_data(table, source, preamble, excluded_fields):
    '''Generalization for writing data from a given set of fields to the
    corresponding HDF5 table location.

    Positional arguments:
    table - (tables.Table) Table to write to.
    source - (dict) Dictionary to be read from.
    preamble - (str) String specifying the path within the HDF5 table to
        the write location.
    excluded_fields - (set of str) Fields of source to be excluded.
    '''
    colobjects = table.description
    for lvl in preamble.levels:
        try:
            source = source[lvl]
        except KeyError:
            pass
        colobjects = colobjects._v_colobjects.get(lvl)

    # Write data.
    # Any fields in the intersection between the description and the
    # given source will be written to the file.
    desc_fields = set(colobjects._v_names) if colobjects else set()
    source_fields = set(source.keys())
    fields = (desc_fields - excluded_fields) & source_fields
    for f in fields:
        to_insert = source.get(f)
        # Use type check instead of equality check to accommodate NumPy
        # arrays, which return a boolean array when compared to another
        # value.
        # Looking for one of these:
        #   - Raw values (e.g. 3, -2.9, 'electric').
        #   - Non-empty NumPy arrays.
        # Shouldn't encounter a non-empty dict or list here.
        if not isinstance(to_insert, type(None)) and (
            not isinstance(to_insert, (dict, list, np.ndarray)) or len(to_insert)
        ):
            table.row[f'{preamble}/{f}'] = to_insert


def read_dispatch(project_name, *args):
    '''Return dispatch data for the given project.'''
    from eagers.read.excel_interface import ProjectTemplateReader
    from eagers.setup.preload import preload
    proj = ProjectTemplateReader.read_userfile(project_name)
    # ProjectPreload(proj['plant'], proj['test_data'] ,proj['options'])
    proj['preload'] = preload(proj['plant'], proj['test_data'] ,proj['options'])
    components = proj['preload']['gen_qp_form']
    subnet = proj['preload']['subnet']
    filepath = existing_h5_result_filepath(project_name)
    with h5file_context(filepath, 'r') as h5f:
        table = getattr(h5f.root, 'dispatch')
        descr = table.description._v_colobjects
        r_str = dict(components='generator_state', storage = 'storage_state', nodes = 'nodedata', lines = 'line_flow', buildings = 'building', fluid_loop = 'fluid_loop')
        names = {}
        for v in r_str:
            k = r_str[v]
            if k in descr:
                names[v] = descr[k]._v_names
        gen_state = {}
        stor_state = {}
        for net in subnet['network_names']:
            gen_state[net] = {}
            stor_state[net] = {}
            for comp in components:
                k = comp['name']
                if any(k in ne for ne in subnet[net]['equipment']):
                    gen_state[net][k] = table.read(field='generator_state/'+k)
                    if comp['type'] == 'ACDCConverter':
                        if net == 'direct_current':
                            gen_state[net][k] = [j*abs(comp['output']['e'][0][-1]) if j>0 else j for j in gen_state[net][k]]
                        elif net == 'electrical':
                            gen_state[net][k] = [-j*comp['output']['dc'][0][0] if j<0 else -j for j in gen_state[net][k]]
                    if comp['type'] == 'CombinedHeatPower' and net == 'district_heat':
                        gen_state[net][k] = chp_heat(comp,gen_state[net][k])
                    if k in names['storage']:
                        unusable = comp['stor']['size'] - comp['stor']['usable_size']
                        st_soc = table.read(field='storage_state/'+k)
                        stor_state[net][k] = [j + unusable for j in st_soc]
    return gen_state, stor_state
