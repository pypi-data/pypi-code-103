"""

************
Examples for State.
************

State is an object handling the Internal state of a CFD fluid, namely:
- density
- Chemical Energy
- Mass Fractions

Limits of State object
======================
Velocity is NOT partof the state object and must be treated separately.
State refer to a point (shape 1) or a set of points (shape n).
The spatial aspects, i.e. the position of the points,
or the mesh, must be handled separately.
"""
import numpy as np
from ms_thermo.state import State#, build_thermo_from_cantera, build_thermo_from_avbp

def how_to_state_single():
    """

    live Example
    ============
    In the following a state for a single point is created
    using the primitive variables T, P, Y_k.
    """
    #Prerequisites : - a thermodynamic database (a default AVBP one is used)
    # species = build_thermo_from_cantera("./chem.cti")           #for cantera species database
    # species = build_thermo_from_chemkin("./thermo.dat")         #for chemkin species database
    # species = build_thermo_from_avbp("./species_database.dat")  #for avbp species database


    # State object initialization
    # basic : mass fractions, temperature, pressure setup
    # the variables can be in arrays of the same size
    state = State(temperature=600.,               # Kelvin, optional, deaults to 300.
                  pressure=100000.,               # Pa, optional, defaults to 101325.
                  mass_fractions_dict={'N2': 1.})#,#optional, defaults to {'O2':0.2325,'N2':0.7675}
                  # species_db=species)     # defaults to the avbp species_database.dat from pyavbp

    # this shows the most common value, the minima and maxima of the current state variables
    print(state)

    # reachable variables
    print(state.energy)         # in J
    print(state.rho)            # in Kg.m^-3
    print(state.mass_fracs)     # no unit
    print(state.temperature)    # in K
    print(state.pressure)       # in Pa

    # those can be updated directly from energy or rho:
    state.energy = 216038.00954532798
    state.rho = 1.171918080399414

    # or from primitives : temperature, pressure, mass_fractions:
    state.mass_fracs = {'O2': 0.2325, 'N2': 0.7675} #recomputes rho and mass fracs, keeps energy
    state.pressure = 101325.        #recomputes density, keeps mass fractions and energy
    state.temperature = 300.        #recomputes energy and density, keeps mass fractions

    #this can be useful to update the primitives all at once, or to ensure a meaningful state:
    state.update_state()

    #useful methods that does not update the state variables
    print(state.list_species())             # list of the species present in the mixture
    print(state.mix_energy(600.))           # gets the energy (J) value at given temperature (K)
    print(state.mix_enthalpy(600.))         # gets the enthalpy (J) value at given temperature (K)
    print(state.mix_molecular_weight())     # computes the total molecular weight of the mixture
    return state

def how_to_state_hundred():
    """

    live Example
    ============
    In the following a state for a hundred point is created
    using the primitive variables T, P, Y_k.
    """
    state = State(temperature=600. * np.ones(100),                  #optional
                  pressure=100000.* np.ones(100),                   #optional
                  mass_fractions_dict={'N2': 1. * np.ones(100)})    #optional
    #WARNING be careful with the variables shapes, the main ones are energy, rho and mass_fracs
    state.update_state(temperature=300. * np.ones(100),         #optional
                       pressure=101325.* np.ones(100),          #optional
                       mass_fracs={'O2': 1. * np.ones(100)})    #optional

    # this recomputes mass fractions (thus stores density and mass fractions)
    # then temperature (thus stores energy and density)
    # then pressure (thus stores density)
    return state

def how_to_state_conservatives():
    """

    live Example
    ============
    In the following a state for a single point is created
    using the conservative variables rho, rho_e, rho_y
    """
    # state can also be initalized from conservatives : rho, rho_e, rho_y in that order
    rho = 1.171918080399414
    rho_e = rho * 216038.00954532798
    rho_y = {'O2': 0.2325 * rho, 'N2': 0.7675 * rho}
    state_cons = State.from_cons(rho, rho_e, rho_y)
    print(state_cons.temperature)
    print(state_cons.energy)
    print(state_cons.mix_energy(300.))
    return state_cons

if __name__ == '__main__':
    _ = how_to_state_single()
    _ = how_to_state_hundred()
    _ = how_to_state_conservatives()
