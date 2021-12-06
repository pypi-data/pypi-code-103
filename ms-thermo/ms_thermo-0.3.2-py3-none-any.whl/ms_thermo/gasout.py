"""Module with functions helpers to  create gasout for CFD solvers"""

import numpy as np


HEADLOG = """
   ### Gasout tool from ms_thermo package ###

    This is a demonstrator! 
    It has not been thoroughy tested yet!

"""

__all__ = [
    "gasout_with_input",
    "gasout_dump_default_input",
    "alter_state",
    "spherical_tanh_mask",
    "directional_linear_mask",
    "fraction_z_mask",
]


def alter_state(state, alpha, temp_new=None, press_new=None, y_new=None, verbose=False):
    """ Alter the state field rho;rhoE, rhoY

    :param state: a ms_thermo State object od size n points.
    :param alpha: a mask of alteration shape(n)
        btw 0 (no alteration) to 1 (full alteration)
    
    :param press_new: (optionnal) the new mass pressure to apply
         either float or numpy array of shape (n)
    :param temp_new: (optionnal) the new temperature to apply
        either float or numpy array of shape (n)
    :param y_new: (optionnal) the new mass fractions to apply
        dict of species {"O2": 0.1, "N2", 0.9}
        values either floats or numpy arrays of shape (n)
    """
    log = str()
    if temp_new is not None:
        temp = np.array(state.temperature)
        state.temperature = temp + alpha * (temp_new - temp)

    if y_new is not None:
        y_mix = dict()
        state_species = list(state.mass_fracs.keys())

        for spec in y_new:
            if spec not in state_species:
                msgerr = "\n\n Species mismatch:"
                msgerr += "\n" + str(spec) + " is not part of the mixture:\n"
                msgerr += "/".join(state_species)
                msgerr += "\nCheck your input file pretty please..."
                raise RuntimeWarning(msgerr)

        for spec in state.mass_fracs:
            value = 0
            if spec in y_new:
                value = y_new[spec]

            y_mix[spec] = state.mass_fracs[spec] + alpha * (
                value - state.mass_fracs[spec]
            )
        state.mass_fracs = y_mix

    if press_new is not None:
        state.pressure = state.pressure + alpha * (press_new - state.pressure)

    if verbose:
        footprint = 100.0 * np.sum(alpha) / alpha.shape[0]
        log += f"Footprint : {footprint: .3f} %"
    return log


def spherical_tanh_mask(coor, center=None, radius=None, delta=None, verbose=False):
    """Compute a spherical mask.

    :param coor: the n points coordinates
        a numpy array of shape (n, ndim)

    :param center: center coordinates of gasout [m]
            a list/tuple/nparray of size ndim
    :param radius: the radius of gasout [m]
    :param delta: the transition of gasout [m]

    :return:
        alpha, a  mask of floats shape (n)
        0 if no mask
        1 if masked

    """
    if center is None:
        center = np.average(coor, axis=0)
    if radius is None:
        size = min(np.max(coor, axis=0) - np.min(coor, axis=0))
        radius = 0.2 * size
    if delta is None:
        delta = 0.5 * rad_0

    center = np.array(center)
    center_ndim = center.shape[0]
    coor_ndim = coor.shape[-1]
    if center_ndim != coor_ndim:
        msg_err = "\n\nDimension mismatch in the spherical center"
        msg_err += "\nCenter is " + str(center_ndim) + "D"
        msg_err += "\nCoords are " + str(coor_ndim) + "D"
        msg_err += "\nCheck your input file pretty please..."
        raise RuntimeWarning(msg_err)

    r_coor = np.linalg.norm(coor - center, axis=1)
    alpha = 0.5 * (1.0 - np.tanh((r_coor - radius) / (delta / 2)))
    return alpha


def directional_linear_mask(
    coor, axis=0, startstop=None,
):
    """Compute a linear transition mask

    :param coor: the n points coordinates
        a numpy array of shape (n, ndim)
    :param axis: 0 x, 1 y , 2 z
    :param startstop: start and stop on the direction [m]

    :return:
        alpha, a  mask of floats shape (n)
        0 if no mask
        1 if masked

    """
    direction = coor[:, axis]
    center = np.average(direction)
    size = np.max(direction) - np.min(direction)
    if startstop is None:
        startstop = (center - 0.2 * size, center + 0.2 * size)

    alpha = (direction - startstop[0]) / (startstop[1] - startstop[0])
    alpha = np.clip(alpha, 0.0, 1.0)

    return alpha


def fraction_z_mask(
    state,
    specfuel,
    zmin=0.3,
    zmax=0.7,
    fuel_mass_fracs=None,
    oxyd_mass_fracs=None,
    atom_ref=None,
    verbose=False,
):
    """Compute a mask found by a transition in Z farction

    :param state: a ms_thermo state object
    :specfuel: string the fuel species name
    :param z_min: mask disabled (0) below this value
    :param z_max: mask disabled (0) over this value

    :return:
        alpha, a  mask of floats shape (n)
        0 if no mask
        1 if masked

    """
    z_frac = state.compute_z_frac(
        specfuel,
        fuel_mass_fracs=None,
        oxyd_mass_fracs=None,
        atom_ref="C",
        verbose=False,
    )

    z_mid = 0.5 * (zmax + zmin)
    z_gap = 0.5 * (zmax - zmin)
    alpha = np.where(abs(z_frac - z_mid) < z_gap, 1.0, 0)
    return alpha


def gasout_with_input(coor, state, in_nob):
    """Gasout function based upon a nest obeject input

    :param coor: the n points coordinates
        a numpy array of shape (n, ndim)

    :param state: a ms_thermo State object od size n points.
    :param in_nob: a nested object for input,
        see gasout_dump_default_input fro reference

    """

    log = str(HEADLOG)
    log += "\nInitial state"
    log += "\n ==========="
    log += "\n" + state.__repr__()

    for i, action in enumerate(in_nob["actions"]):

        log += "\n\nAction " + str(i) + ":" + action["type"]

        if action["type"] == "directional_linear_mask":
            reqd_keys = [
                "direction",
                "max_abcissa",
                "min_abcissa",
                "new_pressure",
                "new_temperature",
                "new_yk",
            ]
            check = _check_action_params(reqd_keys, list(action.keys()))
            if check != "":
                raise RuntimeWarning(log + check)

            if action["direction"] == "x":
                axis = 0
            elif action["direction"] == "y":
                axis = 1
            elif action["direction"] == "z":
                axis = 2
            else:
                msgerr = "\n INPUT ERROR : " + "Direction must be one of x, y or z"
                raise RuntimeWarning(log + msgerr)

            alpha = directional_linear_mask(
                coor,
                axis=axis,
                startstop=[action["min_abcissa"], action["max_abcissa"]],
            )

        elif action["type"] == "spherical_tanh_mask":
            reqd_keys = [
                "center",
                "radius",
                "delta",
                "new_pressure",
                "new_temperature",
                "new_yk",
            ]
            check = _check_action_params(reqd_keys, list(action.keys()))
            if check != "":
                raise RuntimeWarning(log + check)

            alpha = spherical_tanh_mask(
                coor,
                center=action["center"],
                radius=action["radius"],
                delta=action["delta"],
            )

        elif action["type"] == "fraction_z_mask":
            reqd_keys = [
                "specfuel",
                "atom_ref",
                "oxyd_mass_fracs",
                "fuel_mass_fracs",
                "zmax",
                "zmin",
                "new_pressure",
                "new_temperature",
                "new_yk",
            ]

            check = _check_action_params(reqd_keys, list(action.keys()))
            if check != "":
                raise RuntimeWarning(log + check)

            alpha = fraction_z_mask(
                state,
                action["specfuel"],
                zmin=action["zmin"],
                zmax=action["zmax"],
                fuel_mass_fracs=action["fuel_mass_fracs"],
                oxyd_mass_fracs=action["oxyd_mass_fracs"],
                atom_ref=action["specfuel"],
                verbose=True,
            )

        out = alter_state(
            state,
            alpha,
            temp_new=action["new_temperature"],
            press_new=action["new_pressure"],
            y_new=action["new_yk"],
            verbose=True,
        )
        log += "\n" + out

    log += "\n\n Final state"
    log += "\n ==========="

    log += "\n" + state.__repr__()

    return state, log


def gasout_dump_default_input(fname="gasout_in.yml"):
    """Dump a Yamlf file adapted to control gasout_with_input

    Note: i Stored this with a string to include
    the comments in the YAML. Not my best code...
    """

    default_input = """
#This is the tentative input file of a pytohon Gasout.
# Enable YAML syntax highlighting in you IDE for the best experience.

# input files
inst_solut: ./solut_0003.sol.h5
mesh: ./solut_0003.mesh.h5
inst_solut_output: ./gasouted.sol.h5

# list (each - block) of actions to take
actions:
- type: directional_linear_mask
  direction: "x"             #direction x, y, or z
  max_abcissa: 0.11        #If None, takes  70% of CAO size
  min_abcissa: 0.1         #If None, takes  30% of CAO size
  new_pressure: null       #use null if you dont want to edit this field
  new_temperature: 2000.0  # Temp in K.
  new_yk: null

- type: spherical_tanh_mask
  center: [0.1, 0.1, 0]    # center sphere. If None, takes CAO center.
  radius: 0.01              # radius sphere [m]. If None, takes from CAO size
  delta: 0.05              # transition thickness [m], If None, takes half rad
  new_pressure: null
  new_temperature: 1600.
  new_yk:                  # dictionnary of species Yk
    N2: 0.8                # order and competion does not matter
    O2: 0.2                # Sum MUST be 1!

- type: fraction_z_mask
  specfuel: KERO_LUCHE     # Fuel spec name
  atom_ref: C              # reference atom for Z computation
  oxyd_mass_fracs:                 # Mixture oxidizer, for Z computation.
    O2: 0.233              #   If None, takes AIR
    N2: 0.767
  fuel_mass_fracs:  None          # Mixture fuel. dict of Yk.
  zmax: 0.02              #   If None, takes the mix at the Higesh Yk fuel
  zmin: 0.01
  new_pressure: 103000.0  # Pressure in Pa
  new_temperature: null
  new_yk: null

- type: fraction_z_mask    # You can repeat several treatments
  specfuel: KERO_LUCHE
  atom_ref: C
  oxyd_mass_fracs:
    O2: 0.233
    N2: 0.767
  fuel_mass_fracs:  None
  zmax: 0.05
  zmin: 0.04
  new_pressure: 103000.0
  new_temperature: null
  new_yk: null
"""
    print("A default input has been created: " + fname)
    with open(fname, "w") as fin:
        fin.write(default_input)


def _check_action_params(reqd_keys, provided_keys):
    """Feedback on the keys provided"""
    log = str()
    for key in provided_keys:
        if key not in reqd_keys + ["type"]:
            log += "\n.   - key " + key + " not accepted"
    if log != "":
        log += "\n.  - Accepted keys"
        log += "\n.      >".join(reqd_keys)

    for key in reqd_keys:
        if key not in provided_keys:
            log += "\n key " + key + " is missing."
    return log
