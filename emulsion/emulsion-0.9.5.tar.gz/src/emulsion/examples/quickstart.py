"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions defining agents involved for the Quickstart model.

"""

import numpy                    as     np
import pandas                   as     pd

from   sortedcontainers         import SortedDict

from   emulsion.tools.misc      import select_random
from   emulsion.agent.atoms     import AtomAgent
from   emulsion.agent.views     import AdaptiveView
from   emulsion.agent.managers  import MultiProcessManager, GroupManager



##----------------------------------------------------------------
## INDIVIDUALS

class Animal(AtomAgent):
    """The Animal class represents basic individuals.

    """
    @property
    def is_sick(self):
        """Return 1 if the animal is infected, 0 otherwise.

        """
        return self.statevars.health_state.name in ('E', 'I', 'Q')

    @property
    def is_adult(self):
        """Return True if the animal age is above the adult age, False
        otherwise."""
        return self.statevars.age >= self.model.get_value('adult_age')

    def evolve(self, machine):
        super().evolve()
        self.statevars.age += self.model.delta_t

    ### ACTIONS
    def produce_offspring(self, proba_infection=0, **_):
        """Increase the parity (number of calvings) of the cow."""
        status = 'infected_newborn' if np.random.binomial(1, proba_infection)\
                 else 'protected_newborn'
        newborn = self.clone(prototype=status)
        self.upper_level().add_atoms([newborn])

##----------------------------------------------------------------
## HERD

class Herd(MultiProcessManager):
    """This class defines the behavior, initialization and properties of a
    Herd.

    """
    def initialize_level(self, **others):
        # load the model
        self.disease = self.model.state_machines['health_state']
        # self.lifecycle = self.model.state_machines['life_cycle']
        # init variables
        self.mortality_probas = SortedDict()
        self.init_mortality_rates()
        self.init_herd()

    def init_herd(self):
        """Initialize the herd.
        """
        # retrieve prototypes from YAML file
        total_N = int(self.model.get_value('initial_herd_size'))
        total_I = int(self.model.get_value('initial_infected'))

        animals = [ self.new_atom(prototype='default',
                                  age=np.random.poisson(self.model.get_value('adult_age')))
                    for _ in range(total_N)]
        for animal in animals[:total_I]:
            animal.apply_prototype('infected')
        self.add_atoms(animals, init=True)

    def init_mortality_rates(self):
        """Initialize mortality rated per health state, based on parameters
        defined in the model.

        """
        for state in self.disease.states:
            self.mortality_probas[state.name] = \
              self.model.get_value('mortality_proba_sick')\
              if state.name in ('E', 'I', 'Q')\
              else self.model.get_value('mortality_proba_healthy')

    @property
    def total_I(self):
        """Return the number of infectious animals.

        """
        return self.counts['I']

    @property
    def total_N(self):
        """Return the number of animals in the herd.

        """
        return self.population

    @property
    def total_Q(self):
        """Return the number of animals in the quarantine zone.

        """
        return self.counts['Q']

    @property
    def room_in_quarantine(self):
        """Return 1 if the number of animals in the quarantine zone is
        strictly below the capacity of the quarantine zone, 0
        otherwise.

        """
        return int(self.total_Q < self.model.get_value('quarantine_size'))

    def mortality(self):
        """Apply a mortality process to all animals.

        """
        to_remove = []
        for (key, comp) in self['infection']._content.items():
            state = key[0]
            if state:
                nb = np.random.binomial(int(self.counts[state.name]),
                                        self.mortality_probas[state.name])
                to_remove += select_random(comp, nb)
        self.remove_atoms(to_remove)
