'''Contains structure descriptions for results to be saved in HDF5
format.

In the following functions, if a column is specified as a dictionary,
shape can be specified as a tuple of strings.  The SHAPECODE_MAP
variable in config/dataset.py defines the mapping between field names
specified in the given dimension information dictionary and letters used
in column shape specifications.

Functions:
nodedata_descr
weather_descr
dispatch_descr
predicted_descr
solution_descr
result_description
'''

import tables as tb

from eagers.basic.hdf5 import realize_all_columns


def nodedata_descr(node_names, hydro_exists, shape=None, pos=None):
    common = dict(col='Float32Col')
    if shape is not None:
        common['shape'] = shape

    def make_nd_dict(pos):
        d = dict(
            _v_pos=pos,
            demand=dict(**common, pos=0),
            demand_history=dict(**common, pos=1),
        )
        if hydro_exists:
            d.update(
                dict(
                    inflow=dict(**common, pos=2),
                    outflow=dict(**common, pos=3),
                    inflow_history=dict(**common, pos=4),
                    outflow_history=dict(**common, pos=5),
                )
            )
        return d

    nddesc = {}
    for i, n in enumerate(node_names):
        nddesc[n] = make_nd_dict(i)
    if pos is not None:
        nddesc['_v_pos'] = pos
    return nddesc


def weather_descr(building_exists, shape=None, pos=None):
    common = dict(col='Float32Col')
    if shape is not None:
        common['shape'] = shape
    wedesc = dict(dir_norm_irr=dict(**common, pos=0))
    if building_exists:
        wedesc.update(
            dict(
                glo_horz_irr=dict(**common, pos=1),
                dif_horz_irr=dict(**common, pos=2),
                t_dryb=dict(**common, pos=3),
                t_dewp=dict(**common, pos=4),
                rh=dict(**common, pos=5),
                pres_pa=dict(**common, pos=6),
                wdir=dict(**common, pos=7),
                wspd=dict(**common, pos=8),
                tot_cld=dict(**common, pos=9),
                opq_cld=dict(**common, pos=10),
            )
        )
    if pos is not None:
        wedesc['_v_pos'] = pos
    return wedesc


def gen_descr(names, shape=None, pos=None):
    gendesc = {}
    for i, name in enumerate(names):
        gendesc[name] = dict(col='Float32Col', pos=i)
        if shape is not None:
            gendesc[name]['shape'] = shape
    if pos is not None:
        gendesc['_v_pos'] = pos
    return gendesc


def building_descr(build_names, z_dif, pl_dif, shape=None, pos=None):
    def make_build_dict(pos, shape, z_dif, pl_dif):
        if shape is None:
            f_list = [
                'avg_T',
                'Tzone',
                'electric',
                'cooling',
                'heating',
                'return_',
                'supply',
            ]
            s_list = [None, 'z', None, None, None, 'p', 'p']
        else:
            if z_dif is None:
                f_list = ['heating', 'cooling', 'temperature']
                s_list = [None, None, None]
            else:
                f_list = ['avg_T', 'Tzone', 'electric', 'cooling', 'heating']
                s_list = [None, 'z', None, None, None]

        desc = dict(_v_pos=pos)
        for j, f in enumerate(f_list):
            if s_list[j] is None:
                desc[f] = dict(col='Float32Col', pos=j)
                if not shape is None:
                    desc[f]['shape'] = shape
            else:
                sh = s_list[j]
                if sh == 'z' and z_dif > 0:
                    sh = sh + '-' + str(int(z_dif))
                elif sh == 'p' and pl_dif > 0:
                    sh = sh + '-' + str(int(pl_dif))
                if shape is None:
                    desc[f] = dict(col='Float32Col', pos=j, shape=sh)
                else:
                    desc[f] = dict(col='Float32Col', pos=j, shape=[shape, sh])
        return desc

    build = {}
    for i, n in enumerate(build_names):
        if z_dif is None:
            build[n] = make_build_dict(i, shape, None, None)
        else:
            build[n] = make_build_dict(i, shape, z_dif[i], pl_dif[i])
    build['_v_pos'] = pos
    return build


def dispatch_descr(names, min_dir, z_dif, pl_dif):
    dispatch = dict(
        timestamp=dict(col='Time64Col', pos=0),
        generator_state=gen_descr(names['components'], shape=None, pos=1),
        storage_state=gen_descr(names['storage'], shape=None, pos=2),
        nodedata=nodedata_descr(names['nodes'], min_dir['hydro_exists'], shape=None, pos=6),
        weather=weather_descr(min_dir['building_exists'], shape=None, pos=7),
    )
    if min_dir['multinode']:
        dispatch['line_flow'] = gen_descr(names['lines'], shape=None, pos=3)
    if min_dir['fluidloop_exists']:
        dispatch['fluid_loop'] = gen_descr(names['fluid_loop'], shape=None, pos=4)
    if min_dir['building_exists']:
        dispatch['building'] = building_descr(names['buildings'], z_dif, pl_dif, shape=None, pos=5)
    return dispatch


def predicted_descr(names, min_dir, z_dif, pl_dif):
    predicted = dict(
        timestamp=dict(col='Time64Col', shape='h', pos=0),
        generator_state=gen_descr(names['components'], 'h', pos=1),
        storage_state=gen_descr(names['storage'], 'h', pos=2),
        cost=dict(col='Time64Col', pos=3),
        lb_relax=dict(col='Time64Col', pos=4),
        nodedata=nodedata_descr(names['nodes'], min_dir['hydro_exists'], shape='h', pos=8),
        weather=weather_descr(min_dir['building_exists'], shape='h', pos=9),
    )
    if min_dir['multinode']:
        predicted['line_flow'] = gen_descr(names['lines'], 'h', pos=5)
    if min_dir['fluidloop_exists']:
        predicted['fluid_loop'] = gen_descr(names['fluid_loop'], 'h', pos=6)
    if min_dir['building_exists']:
        predicted['building'] = building_descr(names['buildings'], z_dif, pl_dif, 'h', pos=7)
    return predicted


def solution_descr(names, min_dir):
    solution = dict(
        timestamp=dict(col='Time64Col', shape=('h+1',), pos=0),
        timer=tb.Float32Col(shape=3, pos=1),
        generator_state=gen_descr(names['components'], 'h', pos=2),
        storage_state=gen_descr(names['storage'], 'h', pos=3),
    )
    if min_dir['heating_exists']:
        solution['excess_heat'] = gen_descr(names['heating_nodes'], 'h', pos=4)
    if min_dir['cooling_exists']:
        solution['excess_cool'] = gen_descr(names['cooling_nodes'], 'h', pos=5)
    if min_dir['multinode']:
        solution['line_flow'] = gen_descr(names['lines'], 'h', pos=6)
        solution['line_loss'] = gen_descr(names['lines'], 'h', pos=7)
    if min_dir['fluidloop_exists']:
        solution['fluid_loop'] = gen_descr(names['fluid_loop'], 'h', pos=8)
    if min_dir['building_exists']:
        solution['building'] = building_descr(names['buildings'], None, None, 'h', pos=9)
    return solution


def result_description(names, dimensions, minimization_directives, zones, pl):
    '''Return the result description, accounting for the different
    project-related dimensions specified.

    Positional arguments:
    node_names - (list of str) Node names.
    dimensions - (dict) Dictionary specifying dimension counts for
        different project elements.
    minimization_directives - (dict) Dictionary indicating whether to
        include different aspects of a result file.
    '''
    z_dif = [dimensions['zone'] - z for z in zones]
    pl_dif = [dimensions['plantloop'] - n for n in pl]
    # Update dispatch description.
    disp = realize_all_columns(dispatch_descr(names, minimization_directives, z_dif, pl_dif), dimensions)
    # Update predicted description.
    pred = realize_all_columns(predicted_descr(names, minimization_directives, z_dif, pl_dif), dimensions)
    # Update solution description.
    solu = realize_all_columns(solution_descr(names, minimization_directives), dimensions)
    # Create and return result description.
    return disp, pred, solu
