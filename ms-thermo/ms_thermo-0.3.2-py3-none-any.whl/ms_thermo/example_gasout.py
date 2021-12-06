"""Module to show how a tool can vbe created from ms thermo.

Here we create a simple CLI for the Gasout tool"""

import os


"""Example of gasout use.

Here this is a tool for the CFL LES solver AVBP
"""
import yaml
import copy
import h5py
import numpy as np
from h5cross import hdfdict
from ms_thermo.gasout import gasout_with_input, gasout_dump_default_input
from ms_thermo.state import State


def load_mesh_and_solution(fname, mname):
    """Read HDF5 mesh and solution files"""
    print("Reading solution in ", fname)
    with h5py.File(fname, "r") as fin:
        sol = hdfdict.load(fin, lazy=False)
    print("Reading mesh in ", mname)
    with h5py.File(mname, "r") as fin:
        mesh = hdfdict.load(fin, lazy=False)
    return mesh, sol


def build_data_from_avbp(mesh, sol):
    """Buid the data set from"""
    state = State.from_cons(
        sol["GaseousPhase"]["rho"], sol["GaseousPhase"]["rhoE"], sol["RhoSpecies"]
    )

    x_coor = mesh["Coordinates"]["x"]
    y_coor = mesh["Coordinates"]["y"]
    try:
        z_coor = mesh["Coordinates"]["z"]
        coor = np.stack((x_coor, y_coor, z_coor), axis=-1)
    except KeyError:
        coor = np.stack((x_coor, y_coor), axis=-1)

    return coor, state


def save_data_for_avbp(state, sol, fname):
    """Update the full solution with the state parameters"""
    sol_new = copy.deepcopy(sol)
    sol_new["GaseousPhase"]["rho"] = state.rho
    sol_new["GaseousPhase"]["rhoE"] = state.rho * state.energy
    for spec in sol_new["RhoSpecies"]:
        sol_new["RhoSpecies"][spec] = state.rho * state.mass_fracs[spec]

    try:
        sol_new["Additionals"]["temperature"] = state.temperature
        sol_new["Additionals"]["pressure"] = state.pressure
    except KeyError:
        print("-Additionals- group is not part of the solution.")

    print("Saving solution in ", fname)
    with h5py.File(fname, "w") as fout:
        hdfdict.dump(sol_new, fout)


def gasout_tool(inputfile):
    """Main call"""

    with open(inputfile, "r") as fin:
        in_nob = yaml.load(fin, Loader=yaml.Loader)

    mesh, sol = load_mesh_and_solution(in_nob["inst_solut"], in_nob["mesh"])

    coor, state = build_data_from_avbp(mesh, sol)

    state_new, log = gasout_with_input(coor, state, in_nob)

    print(log)

    save_data_for_avbp(state_new, sol, in_nob["inst_solut_output"])
