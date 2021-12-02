"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for entities management.

"""


import numpy                     as np

from   emulsion.agent.core       import GroupAgent
# from   emulsion.tools.misc       import aggregate_probabilities


class InvalidCompartmentOperation(Exception):
    """Exception raised when a compartiment is asked for impossible
    operations, such as adding numbers to a list of units.

    """
    def __init__(self, source, operation, params):
        super().__init__(self)
        self.source = source
        self.operation = operation
        self.params = params

    def __str__(self):
        return "%s cannot execute '%s' with params: '%s'" %\
            (self.source, self.operation, self.params)



class Compartment(GroupAgent):
    """An Compartment is a compartment which does not
    represent the underlying level but with aggregate information such
    as the total population ('individuals' are not represented).

    """
    def __init__(self, population=0, stochastic=True, **others):
        """Create an Compartment with an initial population."""
        super().__init__(**others)
        self.statevars.population = population
        self.stochastic = stochastic

    def __len__(self):
        return self.statevars.population

    def get_content(self):
        """Return the population of the current unit.

        """
        return {'population': self.statevars.population}

    def add(self, population):
        """Add the specified population to the current population of
        the compartment.

        """
        self.statevars.population += population

    def remove(self, population):
        """Remove the specified population from the current population
        of the compartment (the population is kept positive).

        """
        self.statevars.population = max(0, self.statevars.population - population)


    def _base_move(self, other_unit, population=0, **others):
        self.remove(population)
        other_unit.add(population)


    def move_to(self, other_unit, population, state_machine=None, **others):
        """Move the specified population from the current population
        of the compartment (the population is kept positive) to the
        other unit. If a state machine is provided, executes the
        corresponding actions when entering/exiting nodes and crossing
        edges if needed.

        """
        quantity = min(population, self.statevars.population)
        super().move_to(other_unit, population=quantity, state_machine=state_machine, **others)

    def next_states(self, states, values, populations, actions, method=None):
        """Compute the population moving from the current compartment
        to each of the destination states, handling the values
        according the the specified method. Values can be handled
        either as absolute amounts ('amount' method), as proportions
        ('rate', in a deterministic approach) or as probabilities
        ('proba', in a stochastic approach). Actions are to be
        performed when changing state. The actual population affected
        by the transitions is stored in the first element of the
        `populations` parameter, as a dictionary: {'population':
        number, 'actions': actions}. Several edges can lead to the
        same state.

        """
        current_pop = populations[0]['population']
        if method == 'amount':
            # length of values is expected to be the number of output edges
            # retrieve the amount of population exiting
            total_value = sum(values)
            if total_value > current_pop:
                # restart with proportions instead
                return self.next_states(states,
                                        tuple(v / total_value for v in values) + (0,),
                                        populations, actions, method=None)
            evolution = values
        else:
            if self.stochastic:
                # length of values is expected to be the number of
                # output edges + 1 (last value = 1 - sum(values[:-1])
                evolution = np.random.multinomial(current_pop, values)
            else:
                # length of values is expected to be the number of
                # output edges
                evolution = [(np.exp(rate*self.model.delta_t) - 1) * current_pop
                             for rate in values]
        return [(self._host.state_machine.states[state],
                 {'population': qty, 'actions': act})
                for state, qty, act in zip(states[:-1], evolution, actions[:-1])
                if qty > 0]
