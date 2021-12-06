from ms_thermo.state import State
from ms_thermo.yk_from_phi import yk_from_phi

__all__ = ["fresh_gas"]


def fresh_gas(temperature, pressure, phi, fuel="KERO"):
    """ Return the the conservative values of the fresh gas from the primitive 
    values.

    :param temperature: the fresh gas temperature
    :type temperature: float
    :param pressure: pressure of the fresh gas
    :type pressure: float
    :param phi: equivalence ratio of the air-fuel mixture
    :type phi: float
    :param fuel: fuel
    :type fuel: string

    :returns:
    	- **rho** - Density
    	- **rhoE** - Conservative energy
    	- **rhoyk** - Dict of conservative mass fractions

    """
    if fuel == "KERO":
        yk = yk_from_phi(phi, 10, 22)
        yk["KERO"] = yk.pop("fuel")

    fresh_gas = State(None, temperature, pressure, yk)
    # print(fresh_gas.keys())
    rho = fresh_gas.rho
    rhoE = fresh_gas.rho * fresh_gas.energy
    rhoyk = dict()
    for specie in fresh_gas._y_k.keys():
        rhoyk[specie] = fresh_gas.rho * fresh_gas._y_k[specie]
    return rho, rhoE, rhoyk
