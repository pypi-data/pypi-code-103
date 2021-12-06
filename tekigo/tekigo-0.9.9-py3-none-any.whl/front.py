"""Simple API to Tékigô.

Tékigô's main function *tekigo.refine* takes as input the *TekigoSolution* class and
a *function* (which takes a *TekigoSolution* class as argument)
that computes the criteria of refinement into a dictionnary
holding the different criterion over the mesh.

In order to use *tekigo.refine*:

- One needs to declare a *TekigoSolution* class.
- One needs to create one or multiple *criteria of refinement* following those rules :
    - each criterion being **clipped into [-1;1]** at each node:
        - a **positive** value refines
        - a **negative** one coarses
        - *zero* equals no refinement
    - those criterions can be **monitored** i.e. One can define a window of interest
        - that window shall be within [0;1], 0 shuts the refinement down, 1 keeps it.
"""
import time
import os
import shutil
from pathlib import Path
import warnings
import pkg_resources
import h5py
import numpy as np
from h5cross import hdfdict as h5d
from nob import Nob
from tekigo.base import (
    gen_filename,
    update_h5_file,
    collect_solution,
    update_step_param,
    get_metric_stats,
)
from tekigo.tools import (
    approx_vol_node_from_edge,
    approx_edge_from_vol_node,
    approx_vol_node_from_vol_cell,
    approx_vol_cell_from_vol_node,
)

__all__ = ["TekigoSolution", "refine", "raw_adapt"]
# Subdirectories to which results are stored:
# Here : - Mesh corresponds to where xmf and h5 file are stored
#        -  Logs contains logs
SUBDIRS = ["", "Mesh", "Logs"]
warnings.simplefilter("always", DeprecationWarning)

# global tools
class TekigoSolution:
    """ Base class for tekigo

        :param mesh: Full or relative path to mesh file (.mesh.h5)
        :type mesh: string
        :param solution: Full or relative path to instantaneous solution file
        :type solution: string
        :param average_sol: Full or relative path to average solution file
        :type average_sol: string
        :param out_dir: Results output directory
        :type out_dir: string, *optional*
        :param overwrite_dir: option to overwrite old results dir.
        :type overwrite_dir: string, *optional*
        :param only_sol_vars: *optional*, list of runtime instantaneous solution variables. ie :
                the variables that will be considered in refinement
                criteria. e.g = ['rho', 'rhou', 'rhov', 'temperature']
        :param only_ave_vars: *optional*, list of runtime average solution variables. ie :
                the variables that will be considered in refinement
                criteria. e.g = [yplus, 'like']
        :param only_sol_vars: *optional*, list of runtime mesh variables. ie :
                the variables that will be considered in refinement
                criteria. e.g = ['volume']
    """

    def __init__(
            self,
            mesh,
            solution,
            average_sol=None,
            out_dir="Results",
            overwrite_dir=False,
            only_sol_vars=None,
            only_msh_vars=None,
            only_ave_vars=None,
        ):
        # pylint: disable=too-many-arguments
        """instantiation method"""
        if Path(out_dir + "/Mesh").is_dir():
            if overwrite_dir:
                warnings.warn(
                    f"Removing old results and logs directories in {out_dir}",
                    stacklevel=2,
                )
                shutil.rmtree(Path(out_dir + "/Mesh"), ignore_errors=True)
                shutil.rmtree(Path(out_dir + "/Logs"), ignore_errors=True)
            else:
                raise ValueError(
                    f"\nOutput directory {out_dir} contains Tekigo data!"
                    "\nChange the name or allow overwriting"
                )

        self._step = 0
        self.file_kw = dict()
        self.file_kw["out_dir"] = out_dir
        self.file_kw["prefix"] = "tekigo_solut"

        for sub_ in SUBDIRS:
            path = f"{self.file_kw['out_dir']}/{sub_}"
            if not os.path.exists(path):
                os.makedirs(path)

        self.params = dict()
        self.params["metric_l2_norm"] = None

        self.params["mesh_vars"] = only_msh_vars
        dest = gen_filename(
            sub_dir="Mesh", kind="mesh", current_step=self._step, **self.file_kw
        )
        shutil.copy(mesh, dest)
        self.params["initial_mesh"] = dest

        dest = f"{self.file_kw['out_dir']}/Mesh/initial.sol.h5"
        shutil.copy(solution, dest)
        self.params["initial_solution"] = dest

        extract_sol = gen_filename(
            sub_dir="Mesh", kind="sol", current_step=self._step, **self.file_kw
        )
        _extract_fields(
            dest,
            extract_sol,
            sol_fields=only_sol_vars,
            ave_fields=only_ave_vars,
            ave_sol_file=average_sol,
        )
        if average_sol is None:
            self.params["solution_vars"] = only_sol_vars
        elif only_sol_vars is None:
            self.params["solution_vars"] = only_ave_vars
        elif only_ave_vars is None:
            raise ValueError(
                "An average solution ('average_sol' parameter) is given but no "
                "field is read in it, please fill in the 'only_ave_vars' "
                "parameter or remove the average solution"
            )
        else:
            self.params["solution_vars"] = only_sol_vars + only_ave_vars

    def load_current_solution(self):
        """ Load current solution as a dictionnary

            :returns: dictionnary holding solution information
        """
        sol_file = gen_filename(
            sub_dir="Mesh", kind="sol", current_step=self._step, **self.file_kw
        )
        print(f" ---- Loading sol {sol_file} ")
        with h5py.File(sol_file, "r") as fin:
            sol_prx = Nob(h5d.load(fin, lazy=False))

        varst = ",".join([str(path) for path in sol_prx.paths])

        print(f" ---- vars available : [{varst}]")
       
        solution = dict()
        varst = ",".join(self.params["solution_vars"])
        print(f" ---- loading only vars : [{varst}] ")
       
        for variable in self.params["solution_vars"]:
            solution[variable] = sol_prx[variable][:]
        return solution

    def load_current_mesh(self):
        """ Load current mesh as a dictionnary

            :returns: mesh information as ProxyH5 type dict
        """
        mesh_file = gen_filename(
            sub_dir="Mesh", kind="mesh", current_step=self._step, **self.file_kw
        )
        with h5py.File(mesh_file, "r") as fin:
            msh_prx = Nob(h5d.load(fin, lazy=False))

        mesh = dict()
        for variable in self.params["mesh_vars"]:
            mesh[variable] = msh_prx[variable][:]
        return mesh

    @property
    def step(self):
        """ Update step parameter

            :returns: None
        """
        return self._step

    @step.setter
    def step(self, value):
        self._step = value


def refine(tekigo_sol, custom_criteria, **kwargs):
    # pylint: disable=too-many-arguments
    # pylint: disable=line-too-long
    """
    Make adaptative refinement based on refinement criteria

    :param tekigo_solution: TekigoSolution object
    :param custom_criteria: function taking as input a tekigo object and returning a dictionnary of criteria to be used. see example

    *kwargs* : additional keyword arguments for refinement, as defined below:

    :param dry_run: If True, only metrics will be computed,
                    no refinment is performed
    :type dry_run: boolean, *optional*
    :param iteration_max: Maximum refinement iterations number
    :type iteration_max: number, *optional*
    :param nnode_max: Maximum nodes allowed, **DEPRECATED**
    :type nnode_max: number, *optional*
    :param ncell_max: Maximum cells allowed
    :type ncell_max: number, *optional*
    :param min_vol: Minimal cell volume allowed, **DEPRECATED**
    :type min_vol: number, *optional*
    :param min_edge: Minimal edge size allowed
    :type min_edge: number, *optional*
    :param l2_crit: Maximum metric L2-norm allowed
    :type l2_crit: number, *optional*
    :param met_mix: criteria computing rule
    :type met_mix: string, *optional*
    :param max_refinement_ratio: maximum allowed refinement ratio
    :type max_refinement_ratio: number, *optional*
    :param max_spacing_gradient: maximum allowed spacing gradient
    :type max_spacing_gradient: number, *optional*
    :param hausdorff_distance: target hausdorff distance
    :type hausdorff_distance: number, *optional*
    :param frozen_patch_list: list of patches to freeze during refinement
    :type frozen_patch_list: list of integers, *optional*
    :param coarsen: enable or disable coarsening while refining
    :type coarsen: bool, *optional*

    :returns: None
    """
    params, logger = _refine_init(tekigo_sol, **kwargs)

    (
        tekigo_sol.step,
        params["n_node"],
        params["h_min"],
        params["ncell"],
    ) = update_step_param(
        params["dry_run"],
        -1,
        params["max_spacing_gradient"],
        params["hausdorff_distance"],
        params["frozen_patch_list"],
        params["periodic_adaptation"],
        **tekigo_sol.file_kw,
    )
    _inf_loop_warning(params["n_node"], params["nnode_max"], logger)

    while _refinement_converged(
            tekigo_sol.step,
            params["l2_crit"],
            params["metric_l2_norm"],
            params["iteration_max"],
        ):
        refine_criteria = custom_criteria(tekigo_sol)
        _criteria_range_check(refine_criteria, logger, params["coarsen"])
        update_h5_file(
            gen_filename(
                sub_dir="Mesh",
                kind="sol",
                current_step=tekigo_sol.step,
                **tekigo_sol.file_kw,
            ),
            parent_group="Adapt",
            data_dict=refine_criteria,
        )
        metric_stats, metric = get_metric_stats(
            refine_criteria, tekigo_sol.step, raw=False, **tekigo_sol.file_kw, **params
        )

        logger.loop_state(
            metric,
            criteria=refine_criteria,
            step=tekigo_sol.step,
            **metric_stats,
            **params,
        )

        (
            tekigo_sol.step,
            params["n_node"],
            params["h_min"],
            params["ncell"],
        ) = update_step_param(
            params["dry_run"],
            tekigo_sol.step,
            params["max_spacing_gradient"],
            params["hausdorff_distance"],
            params["frozen_patch_list"],
            params["periodic_adaptation"],
            **tekigo_sol.file_kw,
        )
        params["metric_l2_norm"] = metric_stats["l2_norm"]

        if params["dry_run"]:
            logger.redirect_output(
                "\n* Warning: Dry run to check the metric (no refinement)", "a"
            )
            print("\n* Warning: Dry run to check the metric (no refinement)")
            break

        logger.update(metric_stats["l2_norm"], step=tekigo_sol.step, **params)

    if not params["dry_run"]:
        logger.show_exit_criteria(
            tekigo_sol.step,
            params["l2_crit"],
            params["metric_l2_norm"],
            params["iteration_max"],
        )
        collect_solution(
            initial_mesh=params["initial_mesh"],
            initial_solution=params["initial_solution"],
            current_step=tekigo_sol.step,
            **tekigo_sol.file_kw,
        )


def raw_adapt(
        tekigo_sol,
        custom_metric,
        max_spacing_gradient = 1.4,
        hausdorff_distance= None,
        frozen_patch_list = None,
        dry_run = False,
        periodic_adaptation = False,
    ):
    """
    Make adaptative refinement directly based on raw metric

    :param tekigo_solution: TekigoSolution object
    :param custom_metric: metric field to refine the mesh over
    :param dry_run: If True, only metrics will be computed,
                    no refinment is performed
    :type dry_un: boolean, *optional*
    :param max_spacing_gradient: maximum allowed spacing gradient
    :type max_spacing_gradient: number, *optional*
    :param hausdorff_distance: target hausdorff distance
    :type hausdorff_distance: number, *optional*
    :param frozen_patch_list: list of patches to freeze during refinement
    :type frozen_patch_list: list of integers, *optional*
    :param periodic_adaptation: if True periodic adaptation is activated in hip
    :type periodic_adaptation: boolean, *optional*

    :returns: None
    """
    metric = {"metric": custom_metric}
    # initialisation
    print("\nWarning: Raw metric field computation\n")
    logger = _Logger(
        current_step=0,
        raw=True,
        max_spacing_gradient=max_spacing_gradient,
        **tekigo_sol.file_kw,
    )
    (tekigo_sol.step, nnode, h_min, ncell) = update_step_param(
        dry_run, -1, max_spacing_gradient, hausdorff_distance, frozen_patch_list, periodic_adaptation, **tekigo_sol.file_kw
    )

    # metric computation
    update_h5_file(
        gen_filename(
            sub_dir="Mesh",
            kind="sol",
            current_step=tekigo_sol.step,
            **tekigo_sol.file_kw,
        ),
        parent_group="Adapt",
        data_dict=metric,
    )

    metric_stats, metric = get_metric_stats(
        metric, tekigo_sol.step, raw=True, **{**tekigo_sol.file_kw, "dry_run": dry_run}
    )

    logger.loop_state(
        metric, **metric_stats, **{"n_node": nnode, "h_min": h_min, "ncell": ncell}
    )

    (tekigo_sol.step, nnode, h_min, ncell) = update_step_param(
        dry_run,
        tekigo_sol.step,
        max_spacing_gradient,
        hausdorff_distance,
        frozen_patch_list,
        periodic_adaptation,
        **tekigo_sol.file_kw,
    )

    # outputs
    if not dry_run:
        logger.update(
            metric_stats["l2_norm"], **{"n_node": nnode, "h_min": h_min, "ncell": ncell}
        )
        collect_solution(
            initial_mesh=tekigo_sol.params["initial_mesh"],
            initial_solution=tekigo_sol.params["initial_solution"],
            current_step=tekigo_sol.step,
            **tekigo_sol.file_kw,
        )

        logger.redirect_output("\n* Raw metric computation successful", "a")
        print("\n* Raw metric computation successful")
    else:
        logger.redirect_output(
            "\n* Warning: Dry run to check the metric (no refinement)", "a"
        )
        print("\n* Warning: Dry run to check the metric (no refinement)")


# internal tools
def _refine_init(
        tekigo_sol,
        dry_run = False,
        iteration_max = 10,
        nnode_max = None,
        ncell_max = None,
        min_vol = None,
        min_edge = None,
        l2_crit = 0.005,
        met_mix = "abs_max",
        max_refinement_ratio = 0.6,
        max_spacing_gradient = 1.4,
        hausdorff_distance = None,
        frozen_patch_list = None,
        periodic_adaptation = False,
        coarsen = False,
    ):
    # pylint: disable=too-many-arguments
    """
    Generates refinement parameters

    :param tekigo_solution: TekigoSolution object
    :param dry_run: If True, only metrics will be computed,
                    no refinment is performed
    :type dry_run: boolean, *optional*
    :param iteration_max: Maximum refinement iterations number
    :type iteration_max: number, *optional*
    :param nnode_max: Maximum nodes allowed - deprecated
    :type nnode_max: number, *optional*
    :param ncell_max: Maximum cells allowed
    :type ncell_max: number, *optional*
    :param min_vol: Minimal cell volume allowed - deprecated
    :type min_vol: number, *optional*
    param min_edge: Minimal edge size allowed
    :type min_edge: number, *optional*
    :param l2_crit: Maximum metric L2-norm allowed
    :type l2_crit: number, *optional*
    :param met_mix: criteria treatment order
    :type met_mix: string, *optional*
    :param max_refinement_ratio: maximum allowed refinement ratio
    :type max_refinement_ratio: number, *optional*
    :param max_spacing_gradient: maximum allowed spacing gradient
    :type max_spacing_gradient: number, *optional*
    :param hausdorff_distance: target hausdorff distance
    :type hausdorff_distance: number, *optional*
    :param frozen_patch_list: list of patches to freeze during refinement
    :type frozen_patch_list: list of integers, *optional*
    :param coarsen: enable or disable coarsening while refining
    :type coarsen: bool, *optional*
    :param periodic_adaptation: if True periodic adaptation is activated in hip
    :type periodic_adaptation: boolean, *optional*

    :returns: dictionnaries holding parameters, Tékigô log class
    """

    ref_params = {
        "dry_run": dry_run,
        "iteration_max": iteration_max,
        "nnode_max": _nnode_max_deprecated(ncell_max, nnode_max),
        "min_vol": _min_vol_deprecated(min_edge, min_vol),
        "l2_crit": l2_crit,
        "met_mix": met_mix,
        "max_refinement_ratio": max_refinement_ratio,
        "max_spacing_gradient": max_spacing_gradient,
        "hausdorff_distance": hausdorff_distance,
        "frozen_patch_list": frozen_patch_list,
        "periodic_adaptation": periodic_adaptation,
        "coarsen": coarsen,
    }

    return (
        {**tekigo_sol.params, **ref_params},
        _Logger(
            current_step=tekigo_sol.step,
            **tekigo_sol.file_kw,
            **{**tekigo_sol.params, **ref_params}
        )
    )

def _extract_fields(
        solution_file, out_file, sol_fields, ave_fields=None, ave_sol_file=None
    ):
    """ Extracts specific fields from existing avbp solution
        and writes into another file

        Parameters:
        ==========
        solution_file : full path to existing avbp solution
        out_file : full path to output file
        keep_fields: a list of solution fields to keep in the new file

        Returns:
        =======
        None
    """
    with h5py.File(solution_file, "r") as node:
        solution = h5d.load(node, lazy=False)

    out_sol = dict()
    for group in solution:
        if sol_fields is not None:
            group_vars = [var for var in sol_fields if var in solution[group]]
        else:
            group_vars = []
        if group == "Parameters":
            group_vars = list(solution[group].keys())

        group_name = group
        if group == "GaseousPhase":
            group_name = group + "_tekigo"

        if group not in ['Adapt']:
            out_sol[group_name] = dict()
            for var in group_vars:
                out_sol[group_name][var] = solution[group][var]

    if ave_sol_file is not None:
        with h5py.File(ave_sol_file, "r") as fin:
            average = h5d.load(fin, lazy=False)
            
        for group in average:
            if group != "Parameters":
                group_vars = [var for var in ave_fields if var in average[group]]

                out_sol[group] = dict()
                for var in group_vars:
                    out_sol[group][var] = average[group][var]

    with h5py.File(out_file, "w") as fout:
        h5d.dump(out_sol, fout)
        fout.create_group("Adapt")


def _criteria_range_check(criteria, logger, coarsen):
    """ Check if the ranges of the criteria are out of bounds

        :param criteria: dictionnary holding criteria for mesh adaptation
        :type criteria: dict( )
        :param logger: instanciated Tékigô Class for logs on screen/file

        :returns: None
    """

    over_crit_max = [np.any(criteria[variable] > 1.0) for variable in criteria]
    if coarsen:
        min_limit = " -1"
        over_crit_min = [np.any(criteria[variable] < -1.0) for variable in criteria]
    else:
        over_crit_min = [np.any(criteria[variable] < 0.0) for variable in criteria]
        min_limit = " 0"

    if any(over_crit_max + over_crit_min):
        crit_max_names = [
            crit_name for i, crit_name in enumerate(criteria) if over_crit_max[i]
        ]
        crit_min_names = [
            crit_name for i, crit_name in enumerate(criteria) if over_crit_min[i]
        ]
        line = "ERROR: Change the range of the following criteria" + "\n"
        if crit_max_names:
            line += (
                str(crit_max_names)[1:-1] + "contains a value(s) larger than 1" + "\n"
            )
        if crit_min_names:
            line += (
                str(crit_min_names)[1:-1]
                + "contains a value(s) smaller than"
                + min_limit
            )

        logger.redirect_output(line, "a")
        raise ValueError(line)


def _nnode_max_deprecated(ncell_max, nnode_max):
    """deprecation of nnode_max output and reassigning ncell_max"""
    if nnode_max is not None and ncell_max is not None:
        raise RuntimeError("Ncell Max and Nnode Max are mutually exclusive")
    if nnode_max is None and ncell_max is None:
        return np.int_(approx_vol_cell_from_vol_node(100000 * 4.5))
    if ncell_max is not None:
        return np.int_(approx_vol_cell_from_vol_node(ncell_max))
    warnings.warn(
        "The nnode_max parameter is deprecated, usage of ncell_max is preconised",
        DeprecationWarning,
        stacklevel=4,
    )
    return nnode_max


def _min_vol_deprecated(min_edge, min_vol):
    """deprecation of min_vol output and reassigning min_edge"""
    if min_vol is not None and min_edge is not None:
        raise RuntimeError("Min Vol and Min Edge are mutually exclusive")
    if min_vol is None and min_edge is None:
        return approx_vol_node_from_edge(1.0e-5)
    if min_edge is not None:
        return approx_vol_node_from_edge(min_edge)
    warnings.warn(
        "The min_vol parameter is deprecated, usage of min_edge is preconised",
        DeprecationWarning,
        stacklevel=4,
    )
    return min_vol


def _inf_loop_warning(n_node, nnode_max, logger):
    """ Warns the user in the case of a bad setting
         leading to infinite loop

        Parameters:
        ==========
        params: a dictionary holding setup parameters
    """
    if n_node > nnode_max:
        msg = ["Tekigo Warning : Infinite loop detected"]
        msg.append("Initial mesh nodes number (%d) is larger than" % n_node)
        msg.append("maximum node number (%d)." % nnode_max)
        msg = "\n".join(msg)
        print(msg)
        logger.redirect_output(str(msg) + "\n", "a")


def _convergence_conditions(current_step, l2_crit, metric_l2_norm, iteration_max):
    """ Evaluates all refinement convergence conditions

        Parameters:
        ==========
        params: a dictionary holding setup parameters

        Returns :
        =======
        conds : refinement convergence conditions evaluation
    """

    conds = []
    if l2_crit:
        l2_cond = True
        if current_step > 0:
            l2_cond = metric_l2_norm > l2_crit
        conds.append(l2_cond)

    if iteration_max:
        iter_cond = current_step < iteration_max
        conds.append(iter_cond)

    return conds


def _refinement_converged(current_step, l2_crit, metric_l2_norm, iteration_max):
    """ Evaluates whether refinement is converged

        :param params: a dictionary holding setup parameters
        :type params: dict( )

        :returns: when True convergence is obtained
    """
    conds = _convergence_conditions(
        current_step, l2_crit, metric_l2_norm, iteration_max
    )
    convergence = all(conds)
    return convergence


def _verbose_input(raw=False, **params):
    ver = pkg_resources.get_distribution("tekigo").version
    if not raw:
        head = (
            f"\n\nThis is the iterative function of the Tékigô package (version {ver}).\n\n"
            "The input values are:\n"
            f"Maximum possible iterations:       {params['iteration_max']}\n"
            "Target minimum edge:               "
            f"{approx_edge_from_vol_node(params['min_vol'])}\n"
            "Target number of cells:            "
            f"{np.int_(approx_vol_node_from_vol_cell(params['nnode_max']))}\n"
            f"Target convergence criterion:      {params['l2_crit']}\n"
            "This convergence criterion is computed as: "
            "(sum((metric_field - 1)**2 * node_vol) / sum(node_vol)\n"
            "\nOther optional parameters are:\n"
            f"Metric computing ruled by:         "
        )

        if params["met_mix"] == "average":
            head += "average\n"
        else:
            head += "absolute maximum (default)\n"
        if params["max_refinement_ratio"] != 0.6:
            head += (
                "Tékigô's Maximum refinement ratio:"
                f" {params['max_refinement_ratio']}\n"
            )
        else:
            head += (
                "Tékigô's Maximum refinement ratio:"
                f" {params['max_refinement_ratio']} (default)\n"
            )
        if params["coarsen"]:
            head += "Coarsening:                        enabled\n"
        else:
            head += "Coarsening:                        disabled (default)\n"
    else:
        head = (
            f"\n\nThis is the raw metric function of the Tékigô package (version {ver}).\n\n"
            "The input values are:\n"
        )
        if params["max_spacing_gradient"] != 1.4:
            head += (
                "HIP's Maximum spacing gradient: "
                f" {params['max_spacing_gradient']}\n"
            )
        else:
            head += (
                "HIP's Maximum spacing gradient: "
                f" {params['max_spacing_gradient']} (default)\n"
            )
    return head


class _Logger:
    """Class for logging results on screen and to file

        :param params: a dictionary holding setup parameters
        :type params: dict( )

    """

    def __init__(self, current_step=0, **kwargs):
        """initialisation method of the Logger Class"""
        file_kw = {"out_dir": kwargs["out_dir"], "prefix": kwargs["prefix"]}
        self.log_file = gen_filename(
            sub_dir="Logs", kind="log", current_step=current_step, **file_kw
        )
        self.time = time.time()
        self.elapsed = 0
        self._header = _verbose_input(**kwargs)
        self.redirect_output(self._header + "\n", "w")
        self._header = self._header.replace(",", "\t")
        print(self._header)

    def loop_state(self, metric, criteria=None, step=None, **kwargs):
        """ Get and format text before loop

            :param kwargs: a dictionary holding setup parameters
            :type kwargs: dict( )
            :param stats: a dictionary holding statistical parameters
            :type stats: dict( )

            :returns: None
        """
        if criteria is not None:
            if not kwargs["dry_run"]:
                line = f"\nIteration {step + 1}\n\nCurrent mesh info\n"
            else:
                line = "\n\nCurrent mesh info\n"
            line += (
                f"Number of nodes     {kwargs['n_node']}\n"
                f"Number of cells     {kwargs['ncell']}\n"
                f"Minimal edge size   {kwargs['h_min']:1.5e}\n"
                "\nCriterion name  , min, max\n"
            )
            tot = np.zeros(kwargs["n_node"])
            for crit in criteria:
                val = criteria[crit]
                tot += val
                line += f"{crit:16}, {np.min(val):1.4f}, {np.max(val):2.4f}\n"
            line += f"Criteria sum    , {np.min(tot):1.4f}, {np.max(tot):2.4f}\n"
        else:
            line = (
                f"Raw metric computation\n\nCurrent mesh info\n"
                f"Number of nodes     {kwargs['n_node']}\n"
                f"Number of cells     {kwargs['ncell']}\n"
                f"Minimal edge size   {kwargs['h_min']:1.5e}\n"
            )
        ncell_est = np.int_(approx_vol_node_from_vol_cell(kwargs["node_estim"]))
        line += (
            f"Metric          , {np.min(metric):1.4f}, {np.max(metric):2.4f}\n"
            "\nTekigo pre-loop estimations\n"
            f"Number of nodes    {kwargs['node_estim']}\n"
            f"Number of cells    {ncell_est}\n"
            f"Minimal edge size  {kwargs['edge_estim']:1.5e}\n"
        )

        print(line.replace(",", "\t"))
        line += "\n"
        self.redirect_output(line, "a")

    def update(self, stat, step=None, **params):
        """Get and format text after loop"""
        self.elapsed = time.time() - self.time
        self.time = time.time()
        line = "Convergence criteria\n"
        if step is not None:
            if params["l2_crit"] > stat:
                line += (
                    "Stopping on convergence criterion:    "
                    f" {params['l2_crit']:1.3e} > {stat:1.3e}\n"
                )
            else:
                line += (
                    "Not stopping on convergence criterion:"
                    f" {params['l2_crit']:1.3e} <= {stat:1.3e}\n"
                )
            if params["iteration_max"] == step:
                line += f"Stopping on iteration number:          {step}\n"
            else:
                line += (
                    f"Not stopping on iteration number:      {step}"
                    f" (thresold is {params['iteration_max']})\n"
                )
            line += "\nHip iteration statistics\n"
        else:
            line += "\nHip raw adaptation statistics\n"
        line += (
            f"Time elapsed for this iteration:,{self.elapsed:6.3f}\n"
            f"New number of nodes:            ,{params['n_node']}\n"
            f"New number of cells:            ,{params['ncell']}\n"
            f"New minimal edge size:          ,{params['h_min']:1.5e}\n"
        )

        print(line.replace(",", "\t"))
        line += "\n"
        self.redirect_output(line, "a")

    def show_exit_criteria(self, current_step, l2_crit, metric_l2_norm, iteration_max):
        """ Shows the condition that satisfies the convergence

            :param params: a dictionary holding setup parameters
            :type params: dict( )

            :returns: None
        """
        lines = []
        conds = _convergence_conditions(
            current_step, l2_crit, metric_l2_norm, iteration_max
        )
        conds = np.logical_not(conds)

        line = f"\t - Metric Norm L2 : {metric_l2_norm:3.2e} \t {l2_crit:3.2e}"
        lines.append(line)

        line = f"\t - Iterations num : {current_step:08d} \t {iteration_max:08d}"
        lines.append(line)

        for i, _ in enumerate(lines, 0):
            if conds[i]:
                lines[i] = lines[i] + "\t (Exit condition)"

        header = ["\n"]
        header.append("Solution converged for :")

        header.append("")
        header.append("\t \t \t     Value  \t Threshold")

        lines = header + lines

        exit_msg = ""
        for line in lines:
            print(line)
            exit_msg += str(line) + "\n"

        self.redirect_output(exit_msg, "a")

    def redirect_output(self, line, mode):
        """ Write and display method

            :param line: line to be wirtten
            :type line: string
            :param mode: parameter for the python open method (can be 'w', 'a', etc...)
            :type mode: string

            :returns: None
        """
        with open(self.log_file, mode) as fout:
            fout.write(line)
