# -*- coding: utf-8 -*-
"""
Functions handling covid data.
"""

import numpy as np
import vaccontrib.io as io

default_vacc = io.get_default_vaccination_statuses()
default_pop = io.get_default_populations()


from vaccontrib.linalg import get_spectral_radius_and_eigenvector
from vaccontrib import (
            get_next_generation_matrix_from_matrices,
            get_contribution_matrix,
            get_reduced_contribution_matrix,
            get_reduced_vaccinated_susceptible_contribution_matrix,
            get_reduced_population_contribution_matrix,
            get_eigenvector,
            get_homogeneous_eigenvector,
            get_homogeneous_contribution_matrix,
            get_homogeneous_next_generation_matrix,
        )

def get_covid_matrices(variant='alpha',
                       data_dir=None,
                       vaccination_statuses=default_vacc,
                       populations=default_pop,
                       ):
    """
    Load all relevant matrices regarding COVID-19
    vaccine efficacy from package data.

    Parameters
    ==========
    variant : str, default = "alpha"
        The variant for which to load data
        ('alpha' or 'delta)

    Returns
    =======
    matrices : dict
        contains

        - ``'gamma'`` : contact matrix, Entry ``contact_matrix[i,j]``
          contains the average number
          of contacts an average `j`-individual has towards
          `i`-individuals.
        - ``'S'`` : disease-free state, Entry ``S[m,v]`` contains
          the number of m-group individuals
          that are in vaccination state ``v``.
        - ``'N'`` :  population sizes,
          Entry ``population_size[m]`` contains the
          size of population `m`.
        - ``'s'`` : susceptibility reduction,
          Entry ``susceptibility_reduction[m,v]`` contains the
          relative susceptibility reduction of individuals of
          vaccination status `v` and population group `m`.
        - ``'r'`` : transmissibility reduction,
          Entry ``transmissibility_reduction[m,v]`` contains the
          relative transmissibility reduction of individuals of
        - ``'a'`` :
          Entry ``relative_infection_rate[m,v]`` contains the
          infection rate (think: shedding rate) of individuals of
          vaccination status `v` and population group `m` relative
          to some base rate.
        - ``'b'`` : relative_recovery rate,
          Entry ``relative_recovery_rate[m,v]`` contains the
          recovery rate of individuals of
          vaccination status `v` and population group `m` relative
          to some base rate.
    """

    gamma = io.get_contact_matrix(data_dir=data_dir,
                                  populations=populations,
                                  )
    S = io.get_disease_free_state(data_dir=data_dir,
                                  vaccination_statuses=vaccination_statuses,
                                  populations=populations,
                                  )
    N = io.get_population_sizes(data_dir=data_dir,
                                  populations=populations,
                                  )
    s = io.get_susceptibility_reduction(variant=variant,data_dir=data_dir,
                                  vaccination_statuses=vaccination_statuses,
                                  populations=populations,
                                  )
    r = io.get_transmissibility_reduction(variant=variant,data_dir=data_dir,
                                  vaccination_statuses=vaccination_statuses,
                                  populations=populations,
                                  )
    a = io.get_relative_infection_rate(variant=variant,data_dir=data_dir,
                                  vaccination_statuses=vaccination_statuses,
                                  populations=populations,
                                  )
    b = io.get_relative_recovery_rate(variant=variant,data_dir=data_dir,
                                  vaccination_statuses=vaccination_statuses,
                                  populations=populations,
                                  )

    return {
                'gamma' : gamma,
                'S' : S,
                'N' : N,
                's' : s,
                'r' : r,
                'a' : a,
                'b' : b,
            }


# ================= NGM ===================

def get_next_generation_matrix_covid(R0,
                                     variant='alpha',
                                     data_dir=None,
                                     vaccination_statuses=default_vacc,
                                     populations=default_pop,
                                    ):
    """
    Get the next generation matrix of a covid variant.

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    variant : string, default = 'alpha'
        load data for a covid variant from the package data

    Returns
    =======
    K : numpy.ndarray of shape ``M, M, V, V``
        Next generation matrix.
        Entry ``K[i,j,v,w]`` contains the average `(i,v)`-offspring
        of a single `(j,w)`-individual.
    """
    matrices = get_covid_matrices(variant,data_dir=data_dir,
                                  vaccination_statuses=vaccination_statuses,
                                  populations=populations,
                                )
    K = get_next_generation_matrix_from_matrices(R0, **matrices)

    return K

# ================== CONTRIB ===============

def get_contribution_matrix_covid(R0,
                                  variant='alpha',
                                  data_dir=None,
                                  vaccination_statuses=default_vacc,
                                  populations=default_pop,
                                  ):
    """
    Get the contribution matrix of a covid variant.

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    variant : string, default = 'alpha'
        load data for a covid variant from the package data

    Returns
    =======
    C : numpy.ndarray of shape ``M, M, V, V``
        The system's contribution matrix.
        Entry ``C[i,j,v,w]`` contains the average number
        of `(j,w)`-induced `(i,v)`-offspring during exponential
        growth / decay.
    """
    K = get_next_generation_matrix_covid(R0,variant,data_dir=data_dir,
                                          vaccination_statuses=vaccination_statuses,
                                          populations=populations,
                                         )
    C = get_contribution_matrix(K)
    return C

def get_reduced_contribution_matrix_covid(R0,
                                          variant='alpha',
                                          data_dir=None,
                                          vaccination_statuses=default_vacc,
                                          populations=default_pop,
                                         ):
    """
    Get the reduced contribution matrix of a covid variant
    (where populations were summed out and only
    vaccination stati remain).

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    variant : string, default = 'alpha'
        load data for a covid variant from the package data

    Returns
    =======
    C : numpy.ndarray of shape ``V, V``
        The system's contribution matrix.
        Entry ``C[v,w]`` contains the average number
        of `w`-induced `v`-offspring during exponential
        growth / decay.
    """
    K = get_next_generation_matrix_covid(R0,variant,data_dir=data_dir,
                                          vaccination_statuses=vaccination_statuses,
                                          populations=populations,
                                        )
    C = get_reduced_contribution_matrix(K)
    return C

def get_reduced_vaccinated_susceptible_contribution_matrix_covid(
                                              R0,
                                              variant='alpha',
                                              data_dir=None,
                                              vaccination_statuses=default_vacc,
                                              populations=default_pop,
                                          ):
    """
    Get the reduced contribution matrix of a covid variant
    where populations were summed over and active vaccination
    statuses where summed over, as well, such that only vaccinated/
    not vaccinated remains.

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    variant : string, default = 'alpha'
        load data for a covid variant from the package data

    Returns
    =======
    C : numpy.ndarray of shape ``2, 2``
        The system's contribution matrix.
        Entry ``C[v,w]`` contains the average number
        of `w`-induced `v`-offspring during exponential
        growth / decay where `w` and `v` can be either
        'vaccinated' or 'not vaccinated'
    """
    K = get_next_generation_matrix_covid(R0,variant,data_dir=data_dir,
                                          vaccination_statuses=vaccination_statuses,
                                          populations=populations,
                                         )
    C = get_reduced_vaccinated_susceptible_contribution_matrix(K)
    return C

def get_reduced_population_contribution_matrix_covid(R0,
                                                     variant='alpha',
                                                     data_dir=None,
                                                     vaccination_statuses=default_vacc,
                                                     populations=default_pop,
                                                     ):
    """
    Get the reduced contribution matrix of a covid variant
    (where vaccination stati were summed out and only
    population groups remain).

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    variant : string, default = 'alpha'
        load data for a covid variant from the package data

    Returns
    =======
    C : numpy.ndarray of shape ``M, M``
        The system's contribution matrix.
        Entry ``C[i,j]`` contains the average number
        of `i`-induced `j`-offspring during exponential
        growth / decay.
    """
    K = get_next_generation_matrix_covid(R0,variant,data_dir=data_dir,
                                          vaccination_statuses=vaccination_statuses,
                                          populations=populations,
                                        )
    C = get_reduced_population_contribution_matrix(K)
    return C

# ================== EIGENVEC ===============

def get_eigenvector_covid(R0,
                          variant='alpha',
                          data_dir=None,
                          vaccination_statuses=default_vacc,
                          populations=default_pop,
                          ):
    """
    Get the population eigenvector for a covid variant.

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    variant : string, default = 'alpha'
        load data for a covid variant from the package data

    Returns
    =======
    y : numpy.ndarray of shape ``M, V``
        The system's population eigenvector.
        Entry ``y[i,v]`` contains the relative fraction
        of `(i,v)`-individuals in the population.
    """
    K = get_next_generation_matrix_covid(R0,variant,data_dir=data_dir,
                                         vaccination_statuses=vaccination_statuses,
                                         populations=populations,
                                        )
    y = get_eigenvector(K)
    return y

def get_reduced_eigenvector_covid(
                          R0,
                          variant='alpha',
                          data_dir=None,
                          vaccination_statuses=default_vacc,
                          populations=default_pop,
                        ):
    """
    Get the population eigenvector for a covid variant
    (where populations were summed out and only
    vaccination stati remain).

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    variant : string, default = 'alpha'
        load data for a covid variant from the package data

    Returns
    =======
    y : numpy.ndarray of shape ``V,``
        The system's reduced vaccination status eigenvector.
        Entry ``y[v]`` contains the fraction of
        infected belonging to vaccination status v.
    """
    y = get_eigenvector_covid(R0,
                              variant,
                              data_dir=data_dir,
                              vaccination_statuses=vaccination_statuses,
                              populations=populations,
                             )
    y = y.sum(axis=0)
    return y

def get_reduced_vaccinated_susceptible_eigenvector_covid(
                                     R0,
                                     variant='alpha',
                                     data_dir=None,
                                     vaccination_statuses=default_vacc,
                                     populations=default_pop,
                                 ):
    """
    Get the reduced population eigenvector for a covid variant
    where populations were summed over and active vaccination
    statuses where summed over, as well, such that only vaccinated/
    not vaccinated remains.

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    variant : string, default = 'alpha'
        load data for a covid variant from the package data

    Returns
    =======
    y : numpy.ndarray of length ``2``
        The system's reduced vaccinated susceptible eigenvector.
        Entry ``y[v]`` contains the fraction of
        infected belonging to vaccination status v
        (0 = unvaccinated, 1 = vaccinated).
    """
    y = get_reduced_eigenvector_covid(R0,
                                      variant,
                                      data_dir=data_dir,
                                      vaccination_statuses=vaccination_statuses,
                                      populations=populations,
                                      )
    y = np.array([y[0], y[1:].sum()])
    return y

def get_reduced_population_eigenvector_covid(
                                            R0,
                                            variant='alpha',
                                            data_dir=None,
                                            vaccination_statuses=default_vacc,
                                            populations=default_pop,
                                           ):
    """
    Get the reduced population eigenvector for a covid variant
    (where vaccination stati were summed out and only
    population groups remain).

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    variant : string, default = 'alpha'
        load data for a covid variant from the package data

    Returns
    =======
    y : numpy.ndarray of shape ``M``
        The system's eigenvector in the population group-dimension.
        Entry ``y[i]`` contains the fraction of
        infected belonging to group i.
    """
    y = get_eigenvector_covid(R0,
                              variant,
                              data_dir=data_dir,
                              vaccination_statuses=vaccination_statuses,
                              populations=populations,
                              )
    y = y.sum(axis=1)
    return y

# ========== HOMOGENEOUS ===============

def get_homogeneous_contribution_matrix_covid(
                                              R0,
                                              variant,
                                              data_dir=None,
                                              vaccination_statuses=default_vacc,
                                              populations=default_pop,
                                        ):
    """
    Get the unvaccinated/vaccinated contribution matrix
    for a covid variant where fraction of
    vaccinated, susceptiblity reduction,
    and transmissibility reduction were all mapped
    to corresponding values in a homogeneous system.

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    variant : string, default = 'alpha'
        load data for a covid variant from the package data

    Returns
    =======
    C_hom : numpy.ndarray of length ``2, 2``
        The homogeneous system's next generation matrix.
        Entry ``C[v,w]`` contains the average number of
        `w`-induced `v`-offspring during exponential
        growth/decay.
    """
    v, s, r = io.get_homogeneous_vaccination_parameters(variant=variant,
                                                        data_dir=data_dir,
                                                        vaccination_statuses=vaccination_statuses,
                                                        populations=populations,
                                                        )
    C_hom = get_homogeneous_contribution_matrix(R0, v, s, r)
    return C_hom

def get_homogeneous_next_generation_matrix_covid(
                                              R0,
                                              variant,
                                              data_dir=None,
                                              vaccination_statuses=default_vacc,
                                              populations=default_pop,
                                          ):
    """
    Get the unvaccinated/vaccinated next generation matrix
    for a covid variant where fraction of
    vaccinated, susceptiblity reduction,
    and transmissibility reduction were all mapped
    to corresponding values in a homogeneous system.

    Parameters
    ==========
    R0 : float or list of float
        either global reproduction number or a vector
        of reproduction number values, each for in-
        dividuals of a different vaccination status.
    variant : string, default = 'alpha'
        load data for a covid variant from the package data

    Returns
    =======
    K_hom : numpy.ndarray of length ``2, 2``
        The homogeneous system's next generation matrix.
        Entry ``K[v,w]`` contains the average `v`-offspring
        of a single `w`-individual.
    """
    v, s, r = io.get_homogeneous_vaccination_parameters(variant=variant,
                                                        data_dir=data_dir,
                                                        vaccination_statuses=vaccination_statuses,
                                                        populations=populations,
                                                        )
    K_hom = get_homogeneous_next_generation_matrix(R0, v, s, r)
    return K_hom

def get_homogeneous_eigenvector_covid(
                                    variant,
                                    data_dir=None,
                                    vaccination_statuses=default_vacc,
                                    populations=default_pop,
                                ):
    """
    Get the unvaccinated/vaccinated eigenvector
    for a covid variant where fraction of
    vaccinated, susceptiblity reduction,
    and transmissibility reduction were all mapped
    to corresponding values in a homogeneous system.

    Parameters
    ==========
    variant : string, default = 'alpha'
        load data for a covid variant from the package data

    Returns
    =======
    y_hom : numpy.ndarray of length ``2``
        The homogeneous system's eigenvector.
        Entry ``y[v]`` contains the fraction of
        infected belonging to vaccination status v
        (0 = unvaccinated, 1 = vaccinated).
    """
    v, s, r = io.get_homogeneous_vaccination_parameters(variant=variant,
                                                        data_dir=data_dir,
                                                        vaccination_statuses=vaccination_statuses,
                                                        populations=populations,
                                                        )
    y_hom = get_homogeneous_eigenvector(v, s)
    return y_hom

if __name__=="__main__":

    R0 = np.array([4,4,4,4,4.])
    R0 = np.array([4,4,4,4,4.])
    K1 = get_next_generation_matrix_covid(R0,variant='delta')

    M, _, V, __ = K1.shape

    C = get_contribution_matrix(K1)

    print(C.sum())

    print()
    print()
    print()
    print(get_reduced_vaccinated_susceptible_contribution_matrix_covid(R0,variant='delta'))


