"""
State Module aiming to get additional variables from primitive variables.

State is an object handling the Internal state of a CFD fluid, namely:
    - density
    - Chemical Energy
    - Mass Fractions

Limits of State object
======================
Velocity is NOT part of the state object and must be treated separately.
State refer to a point (shape 1) or a set of points (shape n).
The spatial aspects, i.e. the position of the points,
or the mesh, must be handled separately.

**Here ENERGY accounts for the Chemical energy of the mixture.**

.. warning:: arrays sizes must be the same

*******************
Examples for State.
*******************

.. literalinclude:: ../../src/examples/example_state.py
    :language: python
    :lines: 19-22,30-73,81-94,103-110
"""
import pkg_resources
import numpy as np
from scipy.optimize import newton
from scipy.stats import mode
from ms_thermo.species import build_thermo_from_avbp
from ms_thermo.constants import GAS_CST, ATOMIC_WEIGHTS
import warnings

__all__ = ["State"]


class State:
    """Container class to handle mixtures."""

    def __init__(
        self,
        species_db=None,
        temperature=300.0,
        pressure=101325.0,
        mass_fractions_dict=None,
    ):
        r"""
        *Initialize a state object*.

        :param species_db: Species objects
        :type species_db: dict( )
        :param temperature: **temperature** holding the temperature variable
        :param pressure: **pressure** holding the pressure variable
        :param mass_fractions_dict: **Y** of the species present in the mixture (checked in DB)
        :type mass_fractions_dict: dict( )
        """
        self.species = species_db
        if self.species is None:
            self._default_thermo_database()

        self._y_k = dict()
        if mass_fractions_dict is None:
            self._y_k = {"O2": 0.2325, "N2": 0.7675}
        else:
            self._y_k = mass_fractions_dict
        self._check_y_input(self._y_k)

        self.rho = pressure * self.mix_w / (GAS_CST * temperature)

        self.energy = self.mix_energy(temperature)

    def __repr__(self):
        """Define the value returned by calling State representation (printing State)"""
        mini = dict()
        maxi = dict()
        moco = dict()
        moco["rho"] = mode(self.rho, axis=None)[0]
        mini["rho"] = np.min(self.rho)
        maxi["rho"] = np.max(self.rho)
        moco["energy"] = mode(self.energy, axis=None)[0]
        mini["energy"] = np.min(self.energy)
        maxi["energy"] = np.max(self.energy)
        moco["temperature"] = mode(self.temperature, axis=None)[0]
        mini["temperature"] = np.min(self.temperature)
        maxi["temperature"] = np.max(self.temperature)
        moco["pressure"] = mode(self.pressure, axis=None)[0]
        mini["pressure"] = np.min(self.pressure)
        maxi["pressure"] = np.max(self.pressure)
        for specy in self._y_k:
            frac_specy = "Y_" + specy
            moco[frac_specy] = mode(self._y_k[specy], axis=None)[0]
            mini[frac_specy] = np.min(self._y_k[specy])
            maxi[frac_specy] = np.max(self._y_k[specy])
        repr_str = "\nCurrent primitive state of the mixture \n"
        repr_str += "\t\t| Most Common |    Min    |    Max \n"
        repr_str += "-" * 52 + "\n"
        for var in moco:
            infos = (var, moco[var], mini[var], maxi[var])
            repr_str += "%16s| %#.05e | %#.03e | %#.03e \n" % infos

        return repr_str

    @classmethod
    def from_cons(cls, rho, rho_e, rho_y, species_db=None):
        """
        *Another way to initalize a state object from conservatives values.*

        :param species_db: Species objects
        :type species_db: dict( )
        :param rho: **rho** : holding the density variable
        :param rho_e: **energy** : holding the energy variable
        :param rho_y: species **Y** present in the mixture (checked in DB)
        :type rho_y: dict( )

        :param mixture_database: [**optionnal**]  -  species thermodynamic info
                                    If *None*, a default database is used
        :type mixture_database: dict( )

        :returns: a *State* object
        """
        y_k = dict()
        for specy in rho_y:
            y_k[specy] = np.divide(rho_y[specy], rho)
        state = cls(species_db=species_db, mass_fractions_dict=y_k)
        state.energy = np.divide(rho_e, rho)
        state.rho = rho
        return state

    @property
    def mass_fracs(self):
        """getter for mass fractions"""
        return self._y_k

    @mass_fracs.setter
    def mass_fracs(self, mass_fracs_dict):
        r"""
        *Compute density from pressure change by assuming isothermal \
        transformation i.e *T=cte* as :

        .. math:: \rho_{new}= \rho_{old} \frac{P_{new}}{P_{old}}

        :param mass_fracs_dict: A dict( ) of  mass fractions arrays to set

        :returns: **rho_1** - An array of new density values
        """
        mol_weight_old = self.mix_w
        # actual update
        self._check_y_input(mass_fracs_dict)
        self._y_k = dict()
        for k in mass_fracs_dict:
            self._y_k[k] = mass_fracs_dict[k]

        mol_weight_new = self.mix_w
        self.rho = self.rho * mol_weight_new / mol_weight_old

    @property
    def temperature(self):
        r"""
        *Compute temperature from energy by solving the equation.*.

        .. math:: \|e-\sum_{k=1}^{N_{sp}} Y_k e_k(T)\| = 0

        :returns: **temperature** - An array of temperatures
        """
        guess = np.ones_like(self.energy) * 300.0
        temperature = newton(self._temp_energy_res, guess, tol=1e-12)
        return temperature

    @temperature.setter
    def temperature(self, temp):
        """Set state according to the corresponding temperature temp. (isobaric transformation)"""
        self.rho = np.divide(np.multiply(self.rho, self.temperature), temp)
        self.energy = self.mix_energy(temp)

    @property
    def pressure(self):
        r"""
        Get pressure value by solving the isothermal equation.

        .. math:: P = \rho T \frac{R}{W_{mix}}

        :returns: **pressure** - An array of pressures
        """

        return self.rho * self.temperature * GAS_CST / self.mix_w

    @pressure.setter
    def pressure(self, press):
        """Pressure setter from isothermal transformation."""
        self.rho = np.divide(np.multiply(self.rho, press), self.pressure)

    
    @property
    def gamma(self):
        r"""
        Get species averages specific heat ratio

        
        :returns: **gamma** - An array of pressures
        """
        return  self.c_p / self.c_v
    
    @property
    def c_p(self):
        r"""
        Get species averages specific heat ratio

        
        :returns: **gamma** - An array of pressures
        """
        # YOu thought it would this, me too
        # But  no!!!
        # c_p =  sum(
        #     self._y_k[k] * self.species[k].c_p(self.temperature)
        #     for k in self.list_spec

        c_p = self.c_v + self.pressure / (self.rho*self.temperature)

        return c_p

    @property
    def c_v(self):
        r"""
        Get species averages specific heat ratio

        
        :returns: **gamma** - An array of pressures
        """
        temp = self.temperature
        return sum(
            self._y_k[k] * self.species[k].c_v(temp)
            for k in self.list_spec
        )
    
    @property
    def csound(self):
        r"""
        Get sound speed

        :returns: **csound** - An array of sound speed
        """
        csound = np.sqrt(
            self.gamma
            *GAS_CST
            /self.mix_w
            *self.temperature)
        return csound

    @property
    def list_spec(self):
        """
        *Return primitives species names*.

        :returns: **species_names** - A list( ) of primitives species names

        """
        return list(self._y_k.keys())
    
    @property
    def mix_w(self):
        r"""
        | *Compute mixture molecular weight following the formula :*

        .. math:: W_{mix} = \left[ \sum_{k=1}^{N_{sp}} \frac{Y_k}{W_k} \right]^{-1}

        :returns: **mix_mw** (float) - Mixture molecular weight
        """
        y_ov_w = [
            np.divide(self._y_k[k], self.species[k].molecular_weight)
            for k in self.list_spec
        ]
        mix_mw = 1.0 / np.sum(y_ov_w, axis=0)
        return mix_mw

    def mach(self, velocity):
        r"""
        | *Compute Mach number :*

        :param velocity: velocity (float) in m/s        

        :returns: **mach** (float) - Mach number
        """

        return velocity/self.csound

    def temperature_total(self, velocity):
        r"""
        Compute total temperature :

        This assumes an isentropic relation.
        The following equation is an approximation for constant gamma,
        for variable gamma, One should implement the integral
        
        :param velocity: velocity (float) in m/s        

        :returns: **temp_total** (float) - Total temperature in K
        """

        return (
            (1 + 0.5*(self.gamma-1)*self.mach(velocity)**2)
            *self.temperature
        )

    def pressure_total(self, velocity):
        r"""
        Compute total pressure :

        This assumes an isentropic relation.
        The following equation is an approximation for constant gamma,
        for variable gamma, One should implement the integral
        
        :param velocity: velocity (float) in m/s        

        :returns: **press_total** (float) - Total pressure in K
        """

        return (
            np.power(
                1 + 0.5*(self.gamma-1)*self.mach(velocity)**2
                , (self.gamma / (self.gamma-1))
            ) * self.pressure
        )

    def mix_energy(self, temp):
        r"""
        *Get mixture total energy as :*

        .. math:: e = \sum_{k=1}^{N_{sp}} Y_k e_k

        ! Chesterton fence
        ! func is called within setter self.temperature,
        ! do not use self.temperature here

        :param temperature: Temperature at which energy is evaluated
        :type temperature: float

        :returns: **mix_energy** - Array of mixture total energy at temperature *temp*
        """

        return sum(
            self._y_k[k] * self.species[k].chemical_energy(temp)
            for k in self.list_spec
        )

    def mix_enthalpy(self, temp):
        r"""
        *Get mixture total enthalpy as :*

        .. math:: h = \sum_{k=1}^{N_{sp}} Y_k h_k

        ! Chesterton fence
        ! func was called within setters self.temperature,
        ! so cannot use self.temperature here

        :param temperature: temperature at which enthalpy is evaluated [*K*]
        :type temperature: float

        :returns: **mix_enthalpy** - Array of mixture total enthalpy at temperature *temp*
        """
        return sum(
            self._y_k[k] * self.species[k].total_enthalpy(temp)
            for k in self.list_spec
        )

    def update_state(self, temperature=None, pressure=None, mass_fracs=None):
        r"""
        *Compute density from temperature, pressure and mass fractions \
        by assuming following transformations :*

            1) Isobaric and isothermal transform.
            i.e (*P=cte*, *T=cte* and only **composition** is varying)

            2) Isobaric and iso-composition transform.
            i.e (*P=cte*, *Y=cte* and only **temperature** is varying)

            3) Isothermal and iso-composition transform.
            i.e (*T=cte*, *Y=cte* and only **pressure** is varying)

        :param temp: Temperature array to set
        :param press: Pressure array to set
        :param mass_fracs_dict: A dict( ) of  mass fractions arrays to set

        .. note:: Energy will be computed from the new set temperature
        """
        if mass_fracs is not None:
            self.mass_fracs = mass_fracs
        if temperature is not None:
            self.temperature = temperature
        if pressure is not None:
            self.pressure = pressure

    def compute_z_frac(
        self,
        specfuel,
        fuel_mass_fracs=None,
        oxyd_mass_fracs=None,
        atom_ref="C",
        verbose=False,
    ):
        """Compute the Z mixture fraction.

        0 oxidizer, 1 fuel

        :param specfuel: name of fuel specie
        :fuel_mass_fracs: forme fuel mass fraction (dict of Yk)
        :oxyd_mass_fracs: force fuel mass fraction (dict of Yk)

        :return:
            z_frac; an array of shape (n) from 0 to 1
        """
        log = "Computing Z fraction"
        if fuel_mass_fracs is None:
            # find where the maximum fuel concentration
            fuel_mass_fracs = dict()
            idx = np.argmax(self.mass_fracs[specfuel].ravel())
            for spec in self.mass_fracs:
                fuel_mass_fracs[spec] = self.mass_fracs[spec].ravel()[idx]
            log += "   Fuel mixture taken as : "
            for spec in fuel_mass_fracs:
                log += "\n.  - " + spec + ":" + str(fuel_mass_fracs[spec])
            log += "\n"
        if oxyd_mass_fracs is None:
            oxyd_mass_fracs = {"O2": 0.233, "N2": 0.767}
            log += "\n.  Oxidizer mixture taken as AIR."

        z_frac = 0.0
        z_fuel = 0.0
        z_oxyd = 0.0

        for spec in self.mass_fracs:
            nb_atoms = self.species[spec].atoms

            rel_weight = (
                nb_atoms[atom_ref]
                * ATOMIC_WEIGHTS[atom_ref.lower()]
                / self.species[spec].molecular_weight
            )
            z_frac += self.mass_fracs[spec] * rel_weight
            if spec in fuel_mass_fracs:
                z_fuel += fuel_mass_fracs[spec] * rel_weight
            if spec in oxyd_mass_fracs:
                z_oxyd += oxyd_mass_fracs[spec] * rel_weight

        z_frac = (z_frac - z_oxyd) / (z_fuel - z_oxyd)

        if verbose:
            print(log)
        return z_frac

    def _temp_energy_res(self, temp):
        """Compute energy residuals from temperature."""
        comp_energy = self.mix_energy(temp)
        chemical_energy = self.energy
        diff = 1.0 - comp_energy / chemical_energy
        return diff

    def _default_thermo_database(self):
        """
        Initialize the thermodynamic database if none is provided.

        By default it is the AVBP standard species database.
        """
        thermo_db_file = pkg_resources.resource_filename(
            __name__, f"./INPUT/species_database.dat"
        )
        self.species = build_thermo_from_avbp(thermo_db_file)

    def _check_y_input(self, mass_fracs_dict):
        """
        Check if the names of the species are in the database
        the sum of mixture species mass fractions is unity

        :returns: None
        """
        y_tol = 1.0e-5
        not_one_msg = "Mass fraction sum is not unity at point %d"
        not_in_db_msg = "Species %s is not present in the database"

        # check species presence
        for specie in mass_fracs_dict:
            if specie not in self.species:
                msg = not_in_db_msg % specie
                raise ValueError(msg)

        # check sum
        sum_y = 0
        for specie in mass_fracs_dict:
            sum_y += mass_fracs_dict[specie]
        conds = np.abs(sum_y - 1.0) > y_tol
        is_not_one = np.any(conds)
        if is_not_one:
            index = np.where(conds)[0][0]
            msg = not_one_msg % index
            msg += "\n min:" + str(np.min(sum_y))
            msg += "\n max:" + str(np.max(sum_y))
            raise ValueError(msg)

# Deprecated ====================================================================

    def list_species(self):
        r"""
        *Return primitives species names*.

        :returns: **species_names** - A list( ) of primitives species names

        """
        warnings.simplefilter("ignore")
        msgwarn = "ms_thermo.state.list_species() is deprecated,"
        msgwarn += "use instead ms_thermo.state.list_spec"
        warnings.warn(msgwarn)
        print(msgwarn)
        return self.list_spec

    def mix_molecular_weight(self):
        r"""
        *Compute mixture molecular weight following the formula :*

        .. math:: W_{mix} = \left[ \sum_{k=1}^{N_{sp}} \frac{Y_k}{W_k} \right]^{-1}

        :returns: **mix_mw** (float) - Mixture molecular weight
        """
        warnings.simplefilter("ignore")
        msgwarn = "ms_thermo.state.mix_molecular_weight() is deprecated,"
        msgwarn += "use instead ms_thermo.state.mix_w"
        warnings.warn(msgwarn)
        print(msgwarn)
        return self.mix_w
