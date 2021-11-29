# -*- coding: utf-8 -*-
"""
Simulations.
"""

import warnings
from itertools import groupby

import numpy as np

# Try to import the original SamplableSet,
# but if that doesn't work, use the mock version
# that's implemented in this package
try:
    from SamplableSet import SamplableSet
except ModuleNotFoundError as e: # pragma: no cover
    warnings.warn("Couldn't find the efficient implementation of `SamplableSet` (see github.com/gstonge/SamplableSet). Proceeding with less efficient implementation.")
    from vaccontrib.mock_samplable_set import MockSamplableSet as SamplableSet

from vaccontrib.mock_samplable_set import choice as _choice
from collections import Counter

from vaccontrib.main import get_2d_contribution_matrix, convert_4d_matrix_to_2d_block


class LinearSystem():
    """
    Object to simulate linear growth/decay as defined
    by a matrix of reproduction rates and a vector
    of decay rates.

    Parameters
    ==========
    reproduction_rate_matrix : numpy.ndarray of shape ``N x N``
        A matrix whose entry ``reproduction_rate_matrix[i,j]``
        contains the average `i`-offspring of a single "alive"
        `j`-individual per unit time.
    decay_rate_vector : numpy.ndarray of length ``N``
        Entry ``decay_rate_vector[i]`` contains the death rate
        of a single `i`-individual
    initial_conditions : int or numpy.ndarray, default = 20
        Total number of alive individuals (will
        distributed proportionally to the entries of the
        eigenvector of the system's next-generation matrix).
        Can also be a vector of length ``N`` whose `i`-th entry
        contains the initial number of `i`-individuals.


    Attributes
    ==========
    A : numpy.ndarray of shape ``N x N``
        Copy of ``reproduction_rate_matrix``.
        A matrix whose entry ``A[i,j]``
        contains the average `i`-offspring of a single "alive"
        `j`-individual per unit time.
    B : numpy.ndarray of length ``N``
        Copy of ``decay_rate_vector``.
        Entry ``B[i]`` contains the death rate
        of a single `i`-individual
    N : int
        number of species
    K : numpy.ndarray of shape ``N x N``
        Next generation matrix determined by ``A`` and ``B``.
        Entry ``K[i,j]`` contains the average `i`-offspring
        of a single `j`-individual.
    y : numpy.ndarray of length ``N``
        Normalized eigenvector of `K`. Entry ``y[i]``
        contains the theoretical probability that any
        living individual is an `i`-individual.
    C : numpy.ndarray of shape ``N x N``
        The system's contribution matrix.
        Entry ``C[i,j]`` contains the average number
        of `j`-induced `i`-offspring during exponential
        growth / decay.
    total_rates : numpy.ndarray of length ``N``
        Entry ``total_rates[i]`` contains the total
        reaction rate of a single `i`-individual.
    state_rates : numpy.ndarray of shape ``N x (N+1)``
        Entry ``state_rates[i,j]`` contains the rate
        with which a single `i`-individual generates
        a single `j`-individual (if `j < N`), or decays,
        respectively (if `j == N`).
    state_events : list of SamplableSet
        Each entry ``state_events[i]`` contains a SamplableSet
        instance from which events can be sampled according
        to the rates given in ``state_rates[i]``.
    S : SamplableSet
        Contains indices of individuals that are "alive" and can react with
        a total reaction rate according to their state.
    states : dict
        Dictionary that maps the index of an "alive" individual to its state
    leftover_indices : list of int
        contains integer indices of nodes that have decayed such that
        the indices can be reused by newborn individuals.
    max_index : int
        the maximum index that any alive node has at the moment.
    """

    def __init__(self, reproduction_rate_matrix, decay_rate_vector, initial_conditions=20):

        self.set_rate_matrices(reproduction_rate_matrix, decay_rate_vector)
        self.set_initial_conditions(initial_conditions)


    def set_rate_matrices(self, reproduction_rate_matrix, decay_rate_vector=None):
        """
        Define the system via a reproduction rate matrix and
        a decay rate matrix.

        Parameters
        ----------
        reproduction_rate_matrix : numpy.ndarray of shape ``N x N``
            A matrix whose entry ``reproduction_rate_matrix[i,j]``
            contains the average `i`-offspring of a single "alive"
            `j`-individual per unit time.
        decay_rate_vector : numpy.ndarray of length ``N``
            Entry ``decay_rate_vector[i]`` contains the death rate
            of a single `i`-individual
        """


        shape = reproduction_rate_matrix.shape
        assert(shape[0] == shape[1])
        if decay_rate_vector is None:
            decay_rate_vector = np.zeros(shape[0])
        assert(shape[0] == decay_rate_vector.shape[0])
        assert(not np.any(decay_rate_vector<=0))
        assert(np.all(reproduction_rate_matrix>=0))
        assert(np.any(reproduction_rate_matrix>0))

        nnz = reproduction_rate_matrix.nonzero()
        min_weight = np.min([np.amin(reproduction_rate_matrix[nnz]), np.amin(decay_rate_vector)])
        max_weight = np.max([np.amax(reproduction_rate_matrix), np.amax(decay_rate_vector)])

        self.A = np.array(reproduction_rate_matrix).astype(np.float64)
        self.B = np.array(decay_rate_vector).astype(np.float64)
        self.N = len(decay_rate_vector)

        self.K = self.A / self.B[None,:]
        self.C, self.y = get_2d_contribution_matrix(self.K,return_eigenvector_too=True)

        self.total_rates = reproduction_rate_matrix.sum(axis=0).flatten() + decay_rate_vector
        self.state_rates = np.vstack((self.A,self.B)).T

        #print(self.state_rates)
        assert(np.all(self.state_rates.sum(axis=1)==self.total_rates))

        self.state_events = []
        for i in range(self.N):
            min_weight = self.state_rates[i][self.state_rates[i]>0].min()
            max_weight = self.state_rates[i].max()
            S = SamplableSet(min_weight, max_weight,cpp_type='int')
            for j in self.state_rates[i].nonzero()[0]:
                S[j] = self.state_rates[i][j]
            self.state_events.append(S)

        #for ievent, events in enumerate(self.state_events):
        #    print(ievent)
        #    print([item for item in events])


    def set_initial_conditions(self, initial_conditions=20):
        """
        Initializes the node event set and index book keeping
        containers

        Parameters
        ----------
        initial_conditions : int or numpy.ndarray, default = 20
            Total number of alive individuals (will
            distributed proportionally to the entries of the
            eigenvector of the system's next-generation matrix).
            Can also be a vector of length ``N`` whose `i`-th entry
            contains the initial number of `i`-individuals.
        """

        min_weight = self.total_rates.min()
        max_weight = self.total_rates.max()

        if not hasattr(initial_conditions,'__len__'):
            self.y0 = (self.y * initial_conditions).astype(np.int32)
        else:
            self.y0 = np.array(initial_conditions).astype(np.int32)

        self.S = SamplableSet(min_weight=min_weight,max_weight=max_weight)
        i = 0

        self.states = {}

        for state, count in enumerate(self.y0):
            for j in range(int(count)):
                self.S[i] = self.total_rates[state]
                self.states[i] = state
                i += 1

        self.leftover_indices = []
        self.max_index = i - 1


    def simulate(self,t_start_measuring,t_stop_measuring,verbose=False):
        """
        Simulate the exponential growth/decay of individuals in this
        system while keeping track of offspring per individual
        during a measurement period

        Parameters
        ==========
        t_start_measuring : float
            Time point at which to begin to track the
            offspring per individual.
        t_stop_measuring : float
            Time point after which the offspring of newborn
            individuals will not be tracked anymore.
            After this time, newborns will not generate any
            offspring anymore.
            The simulation will end as soon as the last
            individual decays that was born during the
            measurement period
        verbose : bool
            print updates on the current simulation situation

        Returns
        =======
        t : list of float
            time points at which events happened
        y : list of int
            total number of "alive" individuals at time points
            corresponding to ``t``.
        counters : list of tuple of (int, :class:`collections.Counter`)
            Each entry of this list contains the offspring count
            of a single individual that was born during the
            measurement period.

            Will have a structure like this:

            .. code:: python

                >>> counters[0]
                ( state, Counter({ 
                                    offspring_state_0 : 3,
                                    offspring_state_1 : 2,
                                    ...
                                })
                )
            
            The individual whose offspring was tracked here was in
            state ``state``. During the time it was alive, it generated
            3 individuals of state ``offspring_state_0`` and 2
            individuals of ``offspring_state_1``.
        """
        t = 0.

        # active nodes are nodes that were born
        # during the measurement period
        # t in [t_start_measuring, t_stop_measuring
        active_nodes = {}

        # a list that will contain tuples
        counters = []
        ts = [t]
        total = np.sum(self.y0)
        ys = [total]

        # when this time is passed, a statement will be
        # printed if verbose = True
        new_tmax = 1.

        # this will triggered if no individuals are left
        # that can react
        simulation_ended = False

        # this will be triggered as soon as the time
        # passed ``t_stop_measuring``
        end_initialized = False

        while not simulation_ended:

            # perform 
            Lambda = self.S.total_weight()
            tau = np.random.exponential(scale=1/Lambda)
            t += tau
            node, _ = self.S.sample()
            state = self.states[node]

            event, _ = self.state_events[state].sample()

            # last event means decay
            if event == self.N:
                # see if the decaying node has a tracker counter
                # to save
                try:
                    counter = active_nodes.pop(node)
                    counters.append(( state, counter ))
                except KeyError as e:
                    pass

                # remove node from event set
                del self.S[node]

                # add node index to be recycled
                self.leftover_indices.append(node)

                # remove node from state tracking
                self.states.pop(node)

                total -= 1
            #birth of an individual in state `event`
            else:
                total += 1
                birth_state = event

                # recycle a dead index
                if len(self.leftover_indices) > 0:
                    new_index = self.leftover_indices.pop()
                else:
                    # if no indices left to be recycled, get a new index
                    new_index = self.max_index + 1
                    self.max_index = new_index

                #this is to check 
                #if new_index in self.S:
                #    raise ValueError("new_index is in S already")

                # Add the new individual to the event set
                # if the measuring period isn't over yet
                if not end_initialized:
                    self.S[new_index] = self.total_rates[birth_state]
                    self.states[new_index] = birth_state

                # if the measuring period has started yet
                if t > t_start_measuring:

                    # if we're still in measuring period,
                    # assign a tracker to the newborn node
                    if t < t_stop_measuring:
                        active_nodes[new_index] = Counter()

                    # also, try to track this birth event
                    # as an offspring for the reacting node
                    # (if it is currently tracked)
                    try:
                        active_nodes[node][birth_state] += 1
                    except KeyError as e:
                        pass

            # initialize the end period if the time passed t_stop_measuring
            if not end_initialized and t > t_stop_measuring:
                end_initialized = True

            # check wether the simulation is over
            simulation_ended = t > t_stop_measuring and len(active_nodes) == 0
            simulation_ended = simulation_ended or len(self.S) == 0

            # save time and total individual count
            ts.append(t)
            ys.append(total)

            if verbose and t > new_tmax:
                #print(t)
                print(t, node, state, total, "len(active_nodes) =", len(active_nodes))
                new_tmax = t + 1.


        return ts, ys, counters


def get_mean_contribution_matrix_from_simulation(N,counters):
    """
    Compute the mean contribution matrix from a simulation
    result.

    Parameters
    ==========
    N : int
        Number of species/states
    counters : list of tuple of (int, :class:`collections.Counter`)
        Each entry of this list contains the offspring count
        of a single individual that was born during the
        measurement period.

        Will have a structure like this:

        .. code:: python

            >>> counters[0]
            ( state, Counter({ 
                                offspring_state_0 : 3,
                                offspring_state_1 : 2,
                                ...
                            })
            )
        
        The individual whose offspring was tracked here was in
        state ``state``. During the time it was alive, it generated
        3 individuals of state ``offspring_state_0`` and 2
        individuals of ``offspring_state_1``.

    Returns
    =======
    C : numpy.ndarray of shape ``N x N``
        The simulation's contribution matrix.
        Entry ``C[i,j]`` contains the average number
        of `j`-induced `i`-offspring during exponential
        growth / decay. First, the relative contribution
        ``_C[i,j]`` is computed as the sum of all
        `j`-induced `i`-offspring per total offspring during
        the measurement period. Afterwards, the absolute
        contributions are computed by scaling the relative
        contribution with the average offspring per
        individual.
    """
    C = np.zeros((N,N)).astype(np.float64)

    total_offspring = 0
    for state, counter in counters:
        for reproduced_state, count in counter.items():
            C[reproduced_state, state] += count
            total_offspring += count
    R = total_offspring / len(counters)
    C /= total_offspring
    C *= R

    return C

def get_mean_next_generation_matrix_from_simulation(N,counters):
    """
    Compute the mean next generation matrix from a simulation
    result.

    Parameters
    ==========
    N : int
        Number of species/states
    counters : list of tuple of (int, :class:`collections.Counter`)
        Each entry of this list contains the offspring count
        of a single individual that was born during the
        measurement period.

        Will have a structure like this:

        .. code:: python

            >>> counters[0]
            ( state, Counter({ 
                                offspring_state_0 : 3,
                                offspring_state_1 : 2,
                                ...
                            })
            )
        
        The individual whose offspring was tracked here was in
        state ``state``. During the time it was alive, it generated
        3 individuals of state ``offspring_state_0`` and 2
        individuals of ``offspring_state_1``.

    Returns
    =======
    K : numpy.ndarray of shape ``N x N``
        Entry ``K[i,j]`` contains the average `i`-offspring
        of any `j`-individual. Is computed exactly like that.
    """
    K = [ [ [] for i in range(N) ] for j in range(N) ]

    total_offspring = 0
    for state, counter in counters:
        for reproduced_state in range(N):
            K[reproduced_state][state].append(counter[reproduced_state])

    _K = [ [ np.mean(K[j][i]) if len(K[j][i])>0 else 0 for i in range(N) ] for j in range(N) ]
    _K = np.array(_K)

    return _K


def get_mean_eigenstate_from_simulation(N, counters):
    """
    Compute the mean eigenstate from a simulation
    result.

    Parameters
    ==========
    N : int
        Number of species/states
    counters : list of tuple of (int, :class:`collections.Counter`)
        Each entry of this list contains the offspring count
        of a single individual that was born during the
        measurement period.

        Will have a structure like this:

        .. code:: python

            >>> counters[0]
            ( state, Counter({ 
                                offspring_state_0 : 3,
                                offspring_state_1 : 2,
                            })
            )
        
        The individual whose offspring was tracked here was in
        state ``state``. During the time it was alive, it generated
        3 individuals of state ``offspring_state_0`` and 2
        individuals of ``offspring_state_1``.

    Returns
    =======
    y : numpy.ndarray of length ``N``
        Entry ``y[i]``
        contains the fraction of active individuals that
        were `i`-individuals.
    """
    y = np.zeros((N,)).astype(np.float64)

    total_offspring = 0
    for state, counter in counters:
        y[state] += 1

    y /= sum(y)

    return y


def convert_4d_next_generation_matrix_and_relative_recovery_rates_for_simulation(K,b):
    """
    Get rate matrix and recovery rates from 4D
    next generation matrix and 2D recovery rates

    Parameters
    ==========
    K : numpy.ndarray of shape ``M, M, V, V``
        Next generation matrix.
        Entry ``K[i,j,v,w]`` contains the average `(i,v)`-offspring
        of a single `(j,w)`-individual.
    b : numpy.ndarray of shape ``M x V``
        relative recovery rate,
        Entry ``relative_recovery_rate[m,v]`` contains the
        recovery rate of individuals of
        vaccination status `v` and population group `m` relative
        to some base rate.

    Returns
    =======
    reproduction_rate_matrix : numpy.ndarray of shape ``(M*V) x (M*V)``
        A matrix whose entry ``reproduction_rate_matrix[i,j]``
        contains the average `i`-offspring of a single "alive"
        `j`-individual per unit time.
    decay_rate_vector : numpy.ndarray of length ``M*V``
        Entry ``decay_rate_vector[i]`` contains the death rate
        of a single `i`-individual
    """
    K_ = convert_4d_matrix_to_2d_block(K)
    b_ = b.flatten()
    return convert_next_generation_matrix_and_relative_recovery_rates_for_simulation(K_, b_)


def convert_next_generation_matrix_and_relative_recovery_rates_for_simulation(K,b):
    """
    Get rate matrix and recovery rates from
    next generation matrix and recovery rates

    Parameters
    ==========
    K : numpy.ndarray of shape ``N, N``
        Next generation matrix.
        Entry ``K[i,j]`` contains the average `i`-offspring
        of a single `j`-individual.
    b : numpy.ndarray of length ``N``
        Entry ``b[i]`` contains the death rate
        of a single `i`-individual


    Returns
    =======
    reproduction_rate_matrix : numpy.ndarray of shape ``N x N``
        A matrix whose entry ``reproduction_rate_matrix[i,j]``
        contains the average `i`-offspring of a single "alive"
        `j`-individual per unit time.
    decay_rate_vector : numpy.ndarray of length ``N``
        Entry ``decay_rate_vector[i]`` contains the death rate
        of a single `i`-individual
    """
    Binv = np.diag(b)
    A = K.dot(Binv)
    return A, b

if __name__=="__main__":


    A = np.arange(1,5).reshape(2,2)
    B = np.arange(1,3)
    L = LinearSystem(A, B)
    print(L.A, L.K, L.B)

    ts, ys, counters = L.simulate(1.,2.,verbose=True)


    K = A / B[None,:]
    C, y = get_2d_contribution_matrix(K,return_eigenvector_too=True)
    print("K_theory =")
    print(K)
    print("C_theory =")
    print(C)
    print("y_theory =")
    print(y)
    print("C_measured =")
    print(get_mean_contribution_matrix_from_simulation(K.shape[0],counters))
    print("y_measured =")
    print(get_mean_eigenstate_from_simulation(K.shape[0],counters))
    print("K_measured =")
    K_measured = get_mean_next_generation_matrix_from_simulation(K.shape[0],counters)
    print(K_measured)

    print()
    K = K_measured
    C, y = get_2d_contribution_matrix(K,return_eigenvector_too=True)
    print("K_false =")
    print(K)
    print("C_false =")
    print(C)
    print("y_false =")
    print(y)

    import matplotlib.pyplot as pl

    pl.plot(ts, ys)
    pl.show()
