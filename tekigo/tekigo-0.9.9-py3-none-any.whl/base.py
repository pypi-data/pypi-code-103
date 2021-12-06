"""Base functions library for tekigo"""
from os import rename
import numpy as np
import h5py
from h5cross import hdfdict as h5d
from nob import Nob
from tekigo.hipster import hip_refine, hip_interpolate, hip_process
from tekigo.tools import approx_edge_from_vol_node

# The id of the line containing Metric quantity according to HIP
METRIC_NAME = "metric"
# internal and global function
def gen_filename(
        sub_dir, kind, current_step, out_dir="./Results", prefix="tekigo_solut"
    ):
    """ Generates mesh/sol or prefix for file names

        :param sub_dir: the subdirectory containing the file whose name is generated
                        Should be one of Global variables "SUBDIRS"
        :param kind: the type of the file to be generated. Possible options:
                - "mesh" for prefix_xxxx.mesh.h5
                - "sol" for prefix_xxxx.sol.h5
                - "prefix" for prefix_xxxx
                - "log" for prefix_log.csv
                -"hip_log" for prefix_xxxx.log
        :param current_step: current step of the main tekigo loop
        :type current_step: integer
        :param out_dir: output main directory
        :apram prefix: common name part of current tekigo run

        :returns: full path to filename
    """

    path_upper = f"{out_dir}/{sub_dir}"
    path = path_upper + "/%s_%08d" % (prefix, current_step)
    if kind in ["mesh", "sol"]:
        path = path + f".{kind}.h5"
    elif kind == "hip_log":
        path = path + ".log"
    elif kind == "log":
        path = path_upper + f"/{prefix}.log"
    elif kind == "xmf":
        path = path + f".mesh.{kind}"
    else:
        raise NotImplementedError(
            f"This kind of file ({kind}) is not supported by Tékigô."
        )
    return path


def update_h5_file(filename, parent_group, data_dict):
    """ Update hdf5 file by adding a data dictionary to a parent group

        :param filename: the hdf5 file name
        :param parent_group: the parent group under which new datasests are appended
        :param data_dict: the data dictionary to append
    """
    with h5py.File(filename, "r+") as h5f:
        for key in data_dict:
            if key in h5f[parent_group]:
                h5f[parent_group][key][...] = data_dict[key]
            else:
                h5f[parent_group][key] = data_dict[key]


# global tools
def update_step_param(
        dry_run, current_step, max_spacing_gradient, hausdorff_distance, frozen_patch_list, periodic_adaptation, **file_kw
    ):
    """
    Generates hip file from template, execute it and increments iteration and generates log

    :param dry_run: switch between dry-run and normal modes
    :type dry_run: boolean
    :param current_step: current step of the tekigo main loop (if before loop, step is negative.)
    :type pre_step: integer
    :param max_spacing_gradient: hip parameter for the refinement
    :param frozen_patch_list: list of patches to freeze during refinement
    :type frozen_patch_list: list of integers, *optional*
    :param periodic_adaptation: if True periodic adaptation is activated in hip
    :type periodic_adaptation: boolean, *optional*

    :returns: Updated parameters dictionary (increments step)
    """
    if current_step < 0:
        current_step = 0
        log_f = gen_filename(
            sub_dir="Logs", kind="hip_log", current_step=current_step, **file_kw
        )
        mesh_f = gen_filename(
            sub_dir="Mesh", kind="mesh", current_step=current_step, **file_kw
        )
        sol_f = None
    else:
        log_f = gen_filename(
            sub_dir="Logs", kind="hip_log", current_step=current_step, **file_kw
        )
        mesh_f = gen_filename(
            sub_dir="Mesh", kind="mesh", current_step=current_step, **file_kw
        )
        sol_f = mesh_f.replace(".mesh.", ".sol.")
        if not dry_run:
            current_step += 1

    hip_cmd_lines = hip_refine(
        mesh_f,
        max_spacing_gradient,
        hausdorff_distance,
        frozen_patch_list,
        sol_file=sol_f,
        dry_run=dry_run,
        periodic_adaptation=periodic_adaptation,
    )
    hip_log = hip_process(hip_cmd_lines=hip_cmd_lines, mesh_file=mesh_f)

    with open(log_f, "w") as f_h:
        f_h.writelines(hip_log)

    # Get number of nodes
    sol_f = gen_filename(
        sub_dir="Mesh", kind="sol", current_step=current_step, **file_kw
    )
    with h5py.File(sol_f, "r") as f_h:
        nnode = f_h["Parameters"]["nnode"][...][0]
    mesh_f = gen_filename(
        sub_dir="Mesh", kind="mesh", current_step=current_step, **file_kw
    )
    # Transfer node volume to solution file
    with h5py.File(mesh_f, "r") as f_h:
        data_dict = {"vol_node": f_h["VertexData"]["volume"][()]}
        hmin = f_h["Parameters"]["h_min"][...][0]
        elem_type = list(f_h['Connectivity'].keys())[0]
        if elem_type == "tet->node":
            ncell = np.int_(f_h["Connectivity"]["tet->node"][...].shape[0] / 4)
        elif elem_type == "tri->node":
             ncell = np.int_(f_h["Connectivity"]["tri->node"][...].shape[0] / 3)
        else:
            raise ValueError('Unkown element type for computation of cell number')

    update_h5_file(sol_f, parent_group="Adapt", data_dict=data_dict)
    return current_step, nnode, hmin, ncell


def collect_solution(initial_mesh, initial_solution, current_step, **file_kw):
    """ Intepolate initial solution on refined mesh

        :param initial_mesh: initial unrefined mesh
        :type initial_mesh: string
        :param initial_solution: initial solution to be interpolated over refined mesh
        :type initial_solution: string
        :param current_step: current tekigo main loop step
        :type current_step: integer

        :returns: None
    """
    new_mesh = gen_filename(
        sub_dir="Mesh", kind="mesh", current_step=current_step, **file_kw
    )
    new_sol = gen_filename(
        sub_dir="Mesh", kind="sol", current_step=current_step, **file_kw
    )
    with h5py.File(new_sol, "r") as f_h:
        try:
            nob = Nob(h5d.load(f_h, lazy=False)).Adapt[:]
        except TypeError:
            try:
                nob = Nob(h5d.load(f_h)).Adapt[:]
            except AttributeError:
                # This is a quickfix to make sure that tekigo would
                # function with python 3.6 which can only rely on 
                # hdfdict 0.1.1. See tools.py for more info.
                from .tools import load_local
                nob = Nob(load_local(f_h)).Adapt[:]

    hip_cmd_lines = hip_interpolate(initial_mesh, initial_solution, new_mesh, new_sol)
    hip_log = hip_process(hip_cmd_lines=hip_cmd_lines, mesh_file=new_mesh)

    with h5py.File(new_sol, "a") as f_h:
        try:
            f_h.create_group("Adapt")
        except ValueError:
            pass
    update_h5_file(new_sol, parent_group="Adapt", data_dict=nob)
    # For interpolation frozen_patch_list (set to None) and periodic_adaptation do not matter
    hip_cmd_lines = hip_refine(new_mesh, 1.4, 0.01, None, sol_file=new_sol, dry_run=True, periodic_adaptation = True)
    hip_log += hip_process(hip_cmd_lines=hip_cmd_lines, mesh_file=new_mesh)

    log_filename = gen_filename(
        sub_dir="Logs", kind="hip_log", current_step=current_step, **file_kw
    )
    with open(log_filename, "w") as f_h:
        f_h.writelines(hip_log)

    xmf_filename = gen_filename(
        sub_dir="Mesh", kind="xmf", current_step=current_step, **file_kw
    )
    rename(xmf_filename, xmf_filename[:-8] + "sol-mesh.xmf")


def get_metric_stats(criteria, current_step, raw=False, **kwargs):
    """ Updates metric and compute L2 norm of new and old
        metrics

        :param criteria: a dictionary holding refinement criteria
        :type criteria: dict( )
        :param curret_step: current tekigo main loop step
        :type curret_step: integer
        :param raw: switch between normal looped refinement and raw metric method
        :type raw: boolean

        :returns: metric field statistics
    """
    file_kw = {"out_dir": kwargs["out_dir"], "prefix": kwargs["prefix"]}
    mesh_file = gen_filename(
        sub_dir="Mesh", kind="mesh", current_step=current_step, **file_kw
    )
    with h5py.File(mesh_file, "r") as h5f:
        vol_node = h5f["VertexData"]["volume"][()]

    if not raw:
        # calculate new metric
        metric_field = compute_metric(
            criteria,
            kwargs["met_mix"],
            kwargs["n_node"],
            kwargs["max_refinement_ratio"],
        )
        nnode_est, metric_field = _filter_metric(
            vol_node,
            metric_field,
            kwargs["coarsen"],
            kwargs["nnode_max"],
            kwargs["min_vol"],
        )
    else:
        metric_field = criteria["metric"]
        nnode_est = _estimate_nodes_number(metric_field)

    sol_file = gen_filename(
        sub_dir="Mesh", kind="sol", current_step=current_step, **file_kw
    )
    if current_step == 0:
        prev_metric = np.ones_like(metric_field)
        if kwargs["dry_run"]:
            update_h5_file(sol_file, "Adapt", {
                METRIC_NAME: metric_field,
                'future_edge': approx_edge_from_vol_node(vol_node) * metric_field
            })
        else:
            update_h5_file(sol_file, "Adapt", {METRIC_NAME: metric_field})

    else:
        with h5py.File(sol_file, "r+") as h5f:
            prev_metric = np.copy(h5f["Adapt"][METRIC_NAME][()])
            h5f["Adapt"][METRIC_NAME][()] = metric_field

    metric_stats = {
        "l2_norm": _get_metric_l2_norm(metric_field, vol_node),
        "l2_norm_interp": _get_metric_l2_norm(prev_metric, vol_node),
        "node_estim": nnode_est,
        "edge_estim": np.min(metric_field * approx_edge_from_vol_node(vol_node)),
    }
    return metric_stats, metric_field


# internal methods
def _estimate_nodes_number(met_field):
    """Estimates nodes number given the metric field

       Parameters :
       ==========
       met_field_array : metric field
       vol_node : the nodes volumes array

       Returns :
       =======
       node_est : an estimation of the number of nodes
    """

    node_est = int(np.sum(1.0 / (met_field ** 3)))
    return node_est


def _estimate_volume_at_node(current_volume, met_field):
    """Estimates volume_at_nodes given the metric field

       Parameters :
       ==========
       met_field_array : metric field
       vol_node : the nodes volumes array

       Returns :
       =======
       node_est : an estimation of the number of nodes
    """

    volume_est = current_volume * met_field ** 3.0

    return volume_est


def _filter_metric(vol_node, met_field, coarsen, nnode_max, min_vol, verbose=True):
    """Perform filtering on the metrics

        :param vol_node: the nodes volumes array
        :param met_field: the metric field to be filtered
        :param coarsen: boolean , allow coarsening or not
        :param nnode_max: limit the final number of nodes
        :param min_vol: limit the min volume
        

        :returns: - nnode_est : estimation of new number of nodes
                  - met_field : metric field
    """

  
    if not coarsen:
        met_field = np.clip(met_field, None, 1.)
            

    nnode_est = _estimate_nodes_number(met_field)
    msg = f"""
    |  _filter_metric
    |         coarsen  : {str(coarsen)}
    |       nnode_max  : {str(nnode_max)} 
    |          min_vol : {str(min_vol)}
    |  nnode_est start : {str(nnode_est)}

"""

    if nnode_est > nnode_max * 1.05:
        msg += "\n    | coarsen metric..."
        if coarsen :
            while nnode_est > nnode_max * 0.95:
                met_add = +0.025
                met_field += met_add
                nnode_est = _estimate_nodes_number(met_field)
                msg += f"\n    | nnodes {nnode_est} vs {nnode_max} (coarsening)"
                
        else:
            while nnode_est > nnode_max * 0.95:
                met_field = np.power(met_field, 0.8)
                nnode_est = _estimate_nodes_number(met_field)
                msg += f"\n    | nnodes {nnode_est} vs {nnode_max} (coarsening, clipped at 1)"
                
    elif nnode_est < nnode_max * 0.95:
        msg += "\n    | refine metric..."
        while nnode_est < nnode_max * 1.05:
            msg += f"\n    | nnodes {nnode_est} vs {nnode_max} (refining)"
            met_add = -0.025
            met_field += met_add
            nnode_est = _estimate_nodes_number(met_field)
        
    vol_est = _estimate_volume_at_node(vol_node, met_field)

    msg += "\n    | minimum forecasted volume"
    msg += f"\n    | before clipping :  {vol_est.min()}/{min_vol}"
    
    met_field_clean = np.where(
        vol_est > min_vol,
        met_field,
        np.power(min_vol / vol_node, 1.0 / 3.0),
    )
    vol_est = _estimate_volume_at_node(vol_node, met_field_clean)

    msg += f"\n    | after clipping : {vol_est.min()}/{min_vol}"
    
    nnode_est = _estimate_nodes_number(met_field_clean)
    if verbose:
        print(msg)
    return nnode_est, met_field_clean


def _get_metric_l2_norm(metric, vol_node):
    """Get L2 norm of metric

       :param metric: metric field
       :param vol_node: the nodes volumes array

       :returns: metric_norm : The L2 norm of the metric

    """
    vol = np.sum(vol_node)
    metric_norm = np.sum((metric - 1.0) ** 2 * vol_node) / vol
    return metric_norm


def compute_metric(criteria, met_mix, n_node, max_refinement_ratio):
    r"""
    Calculate metric and estimates new number of nodes
    given refinement criteria and criteria choice method ('met_mix' parameter)

    :param criteria: a dictionary holding refinement criteria
    :type criteria: dict( )
    :param met_mix: type of metric mixing calculation method:

if the criteria choice method is set on "average", the metric is computed as follows:

    .. math:: Metric = 1 - Rr_{max} < C >_i

    if the criteria choice method is set on "abs_max", the metric is computed as follows:

    .. math:: Metric = 1 - Rr_{max} \, C_i |_{ \tiny \displaystyle \max_{i \, \in \, C} | C_i |}

    with Metric and C (criteria) vectors of size n_nodes, Rr as Refinement ratio.

    :type met_mix: string
    :param n_node: current number of nodes
    :type n_node: integer
    :param max_refinement_ratio: refinement parameter for metric computation
    :type max_refinement_ratio: float

    :returns: metric field
    """
    met_field = np.ones(n_node) * 2.0
    if met_mix == "average":
        met_field = 0.0
        for crit in criteria:
            met_field = met_field + (1.0 - criteria[crit] * max_refinement_ratio)
        met_field = met_field / float(len(criteria))
    elif met_mix == "abs_max":
        max_crit = np.zeros(n_node)
        for crit in criteria:
            crit_value = criteria[crit] * max_refinement_ratio
            cond = np.abs(max_crit) > np.abs(crit_value)
            max_crit = np.where(cond, max_crit, crit_value)
        met_field = 1.0 - max_crit
    else:
        pass

    return met_field
