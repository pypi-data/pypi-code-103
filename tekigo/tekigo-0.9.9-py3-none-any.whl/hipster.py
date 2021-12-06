"""Toward an API for h!p"""
import os
import subprocess
import platform
import pkg_resources
import h5py


HIP_CMD = pkg_resources.resource_filename("tekigo", "hip_%s" % platform.system())
# Global tools
def hip_refine(
        mesh_file,
        max_spacing_gradient,
        hausdorff_distance,
        frozen_patch_list,
        sol_file=None,
        dry_run=False,
        metric_field="metric",
        periodic_adaptation = True,
    ):#pylint: disable = too-many-arguments
    """ Generates hip.in file from template

        :param mesh_file: full path to hip input file
        :type mesh_file: string
        :param max_spacing_gradient: maximum spacing gradient
        :type max_spacing_gradient: number, *optional*
        :param hausdorff_distance: target hausdorff distance
        :type hausdorff_distance: number, *optional*
        :param frozen_patch_list: list of patches to freeze during refinement
        :type frozen_patch_list: list of integers, *optional*
        :param *optional* sol_file: solution file, if None a solution
                               file is created
        :param dry_run: if True no refinement is done
        :type dry_run: boolean, *optional*
        :param metric_field: metric index parameter
        :type metric_field: string, *optional*
        :param periodic_adaptation: if True periodic adaptation is activated in hip
        :type periodic_adaptation: boolean, *optional*

        :returns: output of hip
    """
    mesh_f = os.path.basename(mesh_file)
    sol_f = None
    if sol_file is not None:
        sol_f = os.path.basename(sol_file)

    step = int(mesh_f[-12:-8])
    cmd_lines = []

    cmd_lines.append("set check level 0")
    cmd_lines.append(f"re hd -a {mesh_f}")
    if sol_f is not None:
        cmd_lines[-1] = cmd_lines[-1] + f" -s {sol_f}"
    if not periodic_adaptation:
        print("Note:Periodic adaptation is deactivated")
        print()
        cmd_lines.append("se ad-per 0")

    if sol_file is not None and not dry_run:
        cmd_lines.append("var")
        if  frozen_patch_list is not None:
            bc_string = [str(frozen_patch_list) for frozen_patch_list in frozen_patch_list]
            bc_list = ','.join(bc_string)
            print("Freezing patch nb(s)", bc_list)
            cmd_lines.append("se bc-mark "+ bc_list)

        metric_index = _get_metric_kw_index(sol_file, metric_field)
        if hausdorff_distance is not None:
            cmd_lines.append(
                f"mm isoVar -v {metric_index} -g {max_spacing_gradient} -h {hausdorff_distance}"
            )
        else:
            cmd_lines.append(f"mm isoVar -v {metric_index} -g {max_spacing_gradient}")
        step += 1

    cmd_lines.append("wr hd %s%04d" % (mesh_f[:-12], step))
    cmd_lines.append("ex")

    return cmd_lines


def hip_interpolate(old_mesh, old_sol, new_mesh, new_sol):
    """  Generates hip.in file from template

        :param old_mesh: meshfile to be loaded
        :type old_mesh: os.PATH
        :param old_sol: solfile to be loaded
        :type old_sol: os.PATH
        :param new_mesh: meshfile to be updated
        :type new_mesh: os.PATH
        :param new_sol: solfile to be updated
        :type new_sol: os.PATH

        :returns: output of hip
    """
    cmd_lines = []
    cmd_lines.append("set check level 0")
    cmd_lines.append(
        "re hd -a %s -s %s" % (os.path.basename(old_mesh), os.path.basename(old_sol))
    )
    cmd_lines.append("re hd -a %s" % os.path.basename(new_mesh))
    cmd_lines.append("in grid 1")
    cmd_lines.append("wr hd -a %s" % os.path.basename(new_sol).split(".sol.h5")[0])
    cmd_lines.append("ex")

    return cmd_lines


def hip_process(hip_cmd_lines, mesh_file):
    """runner for hipster, uses hip in subprocess, takes command lines, runs it and returns output

    :param hip_cmd_lines: hip script (with newlines) to be runned
    :param mesh_file: mesh (and its directory !) to be read by hip.
    """
    mesh_dir = os.path.abspath(os.path.dirname(mesh_file))
    hip_file = "%s/%d_hip.in" % (mesh_dir, os.getpid())

    with open(hip_file, "w") as fout:
        fout.write("\n".join(hip_cmd_lines))

    process = subprocess.run(
        [HIP_CMD, "%s" % hip_file], stdout=subprocess.PIPE, cwd=mesh_dir, check=True
    )
    os.remove(hip_file)
    hip_out = process.stdout.splitlines()
    hip_out = [line.decode("utf-8") + "\n" for line in hip_out]

    return hip_out


# Internal tools
def _get_metric_kw_index(sol_file, metric_field_kw):
    """ @ TODO
    """
    with h5py.File(sol_file, "r") as h5f:
        groups = []
        fields = []
        for group in h5f:
            for var in h5f[group]:
                fields.append(var)
                groups.append(group)
    groups, fields = zip(*sorted(zip(groups, fields)))
    metric_index = list(fields).index(metric_field_kw) + 1
    return metric_index
