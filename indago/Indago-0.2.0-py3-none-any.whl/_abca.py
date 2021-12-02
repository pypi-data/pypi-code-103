# Source: https://github.com/rwuilbercq/Hive/blob/master/Hive/Hive.py

import random
import sys
import numpy as np
from copy import deepcopy
from ._optimizer import Optimizer, CandidateState 


class ABC(Optimizer):
    """Artificial Bee Colony Algorithm class"""

    def __init__(self):
        """Initialization"""
        super(ABC, self).__init__()

        self.dimensions = None
        self.population_size = None
        self.iterations = None
        self.max_trials = None

    class Bee():
        """Bee object"""

        def __init__(self, lb, ub, objective):
            self.vector = np.zeros(len(lb))

            self.objective = objective

            for i in range(len(lb)):
                self.vector[i] = lb[i] + random.random() * (ub[i] - lb[i])

            self.evaluate()

            # Initialises trial limit counter
            self.counter = 0

        def evaluate(self):
            self.value = self.objective(self.vector)

            if self.value >= 0:
                self.fitness = 1 / (1 + self.value)
            else:
                self.fitness = 1 + abs(self.value)

    def _init_optimizer(self):
        """
        Instantiates a bee hive object.

        1. INITIALISATION PHASE.
        -----------------------
        The initial population of bees should cover the entire search space as much as possible by randomizing individuals within the search space constrained by the prescribed lower and upper bounds.
        """

        # Calculate number of employees
        self.hive_size = int(self.population_size + self.population_size % 2)

        # initialises current best and its a solution vector
        self.best = sys.float_info.max
        self.solution = None

        # Create a bee hive
        self.population = [self.Bee(self.lb, self.ub, self.objective) for _ in range(self.hive_size)]

        # Find best bee candidate
        self.__find_best_bee()

        # Compute selection probability
        self.__compute_probability()

    def run(self, seed=None):
        super(LegacyPSO, self).run(seed=seed)
        self._init_optimizer()

        cost = {}
        cost["best"] = np.zeros(self.iterations)
        cost["mean"] = np.zeros(self.iterations)

        for i in range(self.iterations):
            # Employees phase
            for j in range(self.hive_size):
                self.__send_employee(j)

            # Onlookers phase
            self.__send_onlookers()

            # Scouts phase
            self.__send_scout()

            # Compute best solution
            self.__find_best_bee()

            # Convergence information
            cost["best"][i] = self.best
            cost["mean"][i] = sum([bee.value for bee in self.population]) / self.hive_size

        return self.best

    def __find_best_bee(self):
        vals = [bee.value for bee in self.population]
        ind = vals.index(min(vals))

        if vals[ind] < self.best:
            self.best = vals[ind]
            self.solution = self.population[ind].vector

    def __compute_probability(self):
        """
        Computes the relative chance that a given solution vector is chosen by an onlooker bee after the Waggle dance ceremony when employed bees are back within the hive.
        """

        # Rtrieves fitness of bees within the hive
        values = [bee.fitness for bee in self.population]
        max_value = max(values)

        # computes probalities the way Karaboga does in his classic ABC implementation
        self.probabilities = [0.9 * v / max_value + 0.1 for v in values]

        # Returns intervals of probabilities
        return [sum(self.probabilities[:i + 1]) for i in range(self.hive_size)]

    def __send_employee(self, ind):
        """
        2. SEND EMPLOYED BEES PHASE.
        ---------------------------
        During this 2nd phase, new candidate solutions are produced for each employed bee by cross-over and mutation of the employees. If the modified vector of the mutant bee solution is better than that of the original bee, the new vector is assigned to the bee.
        """

        # Copying current bee solution vector
        zombee = deepcopy(self.population[ind])

        # Draws a dimension to be crossed-over and mutated
        d = random.randint(0, self.dimensions - 1)

        # Select another bee
        bee_ind = ind
        while bee_ind == ind:
            bee_ind = random.randint(0, self.hive_size - 1)

        # Produces a mutant based on a current bee and bee's friend
        zombee.vector[d] = self.__mutate(d, ind, bee_ind)

        # Evaluate mutation
        zombee.evaluate()

        if zombee.fitness > self.population[ind].fitness:
            self.population[ind] = deepcopy(zombee)
            self.population[ind].counter = 0
        else:
            self.population[ind].counter += 1

    def __mutate(self, dim, current_bee, other_bee):
        """Mutates a given solution vector"""
        value = self.population[current_bee].vector[dim] + (random.random() - 0.5) * 2 * (self.population[current_bee].vector[dim] - self.population[other_bee].vector[dim])

        if value < self.lb[dim]:
            return self.lb[dim]

        if value > self.ub[dim]:
            return self.ub[dim]

        return value

    def __send_onlookers(self):
        """
        3. SEND ONLOOKERS PHASE.
        -----------------------
        We define as many onlooker bees as there are employed bees in the hive since onlooker bees will attempt to locally improve the solution path of the employed bee they have decided to follow after the waggle dance phase.
        If they improve it, they will communicate their findings to the bee they initially watched "waggle dancing".
        """

        num_onlookers = 0
        beta = 0
        while num_onlookers < self.hive_size:
            # Random number from U[0, 1]
            phi = random.random()

            # Increments roulette wheel parameter beta
            beta += phi * max(self.probabilities)
            beta %= max(self.probabilities)

            # Selects a new onlooker based on waggle dance
            index = self.__waggle_dance(beta)

            # Sends new onlooker
            self.__send_employee(index)

            # Increments number of onlookers
            num_onlookers += 1

    def __waggle_dance(self, beta):
        """
        4. WAGGLE DANCE PHASE.
        ---------------------
        During this 4th phase, onlooker bees are recruited using a roulette wheel selection.
        This phase represents the "waggle dance" of honey bees (i.e. figure- eight dance). By performing this dance, successful foragers (i.e. "employed" bees) can share, with other members of the colony, information about the direction and distance to patches of flowers yielding nectar and pollen, to water sources, or to new nest-site locations.
        During the recruitment, the bee colony is re-sampled in order to mostly keep, within the hive, the solution vector of employed bees that have a good fitness as well as a small number of bees with lower fitnesses to enforce diversity.
        """

        probs = self.__compute_probability()

        for i in range(self.hive_size):
            if beta < probs[i]:
                return i

    def __send_scout(self):
        """
        5. SEND SCOUT BEE PHASE.
        -----------------------
        Identifies bees whose abandonment counts exceed preset trials limit, abandons it and creates a new random bee to explore new random area of the domain space.
        In real life, after the depletion of a food nectar source, a bee moves on to other food sources.
        By this means, the employed bee which cannot improve their solution until the abandonment counter reaches the limit of trials becomes a scout bee. Therefore, scout bees in ABC algorithm prevent stagnation of employed bee population.
        Intuitively, this method provides an easy means to overcome any local optima within which a bee may have been trapped.
        """


        # Retrieves the number of trials for all bees
        trials = [self.population[i].counter for i in range(self.hive_size)]

        # Identifies the bee with the greatest number of trials
        ind = trials.index(max(trials))

        # Checks if its number of trials exceeds the pre-set maximum number of trials
        if trials[ind] > self.max_trials:
            # Creates a new scout bee randomly
            self.population[ind] = self.Bee(self.lb, self.ub, self.objective)

            # sends scout bee to exploit its solution vector
            self.__send_employee(ind)
