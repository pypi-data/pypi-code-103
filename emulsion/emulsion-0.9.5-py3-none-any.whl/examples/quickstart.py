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
        return int(self.statevars.health_state.name in ('E', 'I', 'Q'))


    @property
    def total_I(self):
        """Return the number of infectious animals

        ### NB: in future, the place to retrieve this value could be
        specified in the YAML config file, and the corresponding
        property implemented automatically.

        """
        return self.get_host(key='MASTER').get_host().total_I

    @property
    def total_N(self):
        """Return the number of animals in the herd.

        """
        return self.get_host(key='MASTER').get_host().total_N

    @property
    def total_Q(self):
        """Return the number of animals in the quarantine zone.

        """
        return self.get_host(key='MASTER').get_host().total_Q

    @property
    def is_adult(self):
        """Return True if the animal age is above the adult age, False
        otherwise."""
        return self.statevars.age >= self.model.get_value('adult_age')

    @property
    def room_in_quarantine(self):
        """Return 1 if the number of animals in the quarantine zone is
        strictly below the capacity of the quarantine zone, 0
        otherwise.

        """
        # return int(self.total_Q < self.model.get_value('quarantine_size'))
        return self.get_host(key='MASTER').get_host().room_in_quarantine

    def evolve(self, machine):
        super().evolve()
        self.statevars.age += self.model.delta_t

    ### ACTIONS
    def produce_offspring(self, proba_infection=0, **_):
        """Increase the parity (number of calvings) of the cow."""
        state = 'I' if np.random.binomial(1, proba_infection) else 'M'
        newborn = Animal(age=0,
                         health_state=self.model.state_machines['health_state'].states[state],
                         life_cycle=self.model.state_machines['life_cycle'].states['NP'])
        self.get_host('MASTER').get_host().add_atoms({newborn})


##----------------------------------------------------------------
## COMPARTMENTS

class ExampleAdaptiveView(AdaptiveView):
    """This compartment is aimed at containing individuals (Animals) and
    managing their health state. The observed variable is the health
    state

    ### NB: in future versions, this class should be removed, since
    the only properties used here are in charge of retrieving
    variables in the self.

    """
    @property
    def total_I(self):
        """Return the number of infectious animals

        ### NB: in future, the place to retrieve this value could be
        specified in the YAML config file, and the corresponding
        property implemented automatically.

        """
        return self.get_host().total_I

    @property
    def total_N(self):
        """Return the number of animals in the herd.

        """
        return self.get_host().total_N

    @property
    def total_Q(self):
        """Return the number of animals in the quarantine zone.

        """
        return self.get_host().total_Q

    @property
    def room_in_quarantine(self):
        """Return 1 if the number of animals in the quarantine zone is
        strictly below the capacity of the quarantine zone, 0
        otherwise.

        """
        # return int(self.total_Q < self.model.get_value('quarantine_size'))
        return self.get_host().room_in_quarantine


class ExampleGroupManager(GroupManager):
    """This compartment is in charge of managing Animals in several
    health states.

    ### NB: in future versions, this compartment should be removed,
    since the only properties used here are in charge of retrieving
    variables in the self. Besides, the aggregated values could be
    defined elsewhere and then added to the compartment.

    """
    @property
    def total_I(self):
        """Return the number of infectious animals

        ### NB: in future, the place to retrieve this value could be
        specified in the YAML config file, and the corresponding
        property implemented automatically.

        """
        return self.get_host().total_I

    @property
    def total_N(self):
        """Return the number of animals in the herd.

        """
        return self.get_host().total_N

    @property
    def total_Q(self):
        """Return the number of animals in the quarantine zone.

        """
        return self.get_host().total_Q

    @property
    def room_in_quarantine(self):
        """Return 1 if the number of animals in the quarantine zone is
        strictly below the capacity of the quarantine zone, 0
        otherwise.

        """
        # return int(self.total_Q < self.model.get_value('quarantine_size'))
        return self.get_host().room_in_quarantine

    def init_counts(self, index=0):
        super().init_counts(index=index)
        self.counts['N'] = [] if self.keep_history else 0

    def update_counts(self, index=0):
        super().update_counts(index=index)
        total = {}
        total['N'] = (self.get_host()['MASTER'].population)

        if self.keep_history:
            for key, value in total.items():
                self.counts[key].append(value)
        else:
            self.counts.update(total)



##----------------------------------------------------------------
## HERD

class Herd(MultiProcessManager):
    """This class defines the behavior, initialization and properties of a
    Herd.

    """
    def __init__(self, herd_id=0, keep_history=True, **others):
        super().__init__(herd_id=herd_id, keep_history=keep_history, **others)
        self.step = 0
        # load the model
        self.disease = self.model.state_machines['health_state']
        self.lifecycle = self.model.state_machines['life_cycle']
        # init variables
        self.mortality_probas = SortedDict()
        self.init_mortality_rates()
        self.init_herd()

    def init_herd(self, infected=True):
        """Initialize the herd.
        """
        # retrieve prototypes from YAML file
        prototypes = self.model.prototypes['individuals']
        # {name: features
        #               for list_item in \
        #                 self.model._description['prototypes']['individuals']
        #               for name, features in list_item.items()}
        total_N = int(self.model.get_value('initial_herd_size'))
        total_I = int(self.model.get_value('initial_infected'))
        animals = [Animal(
            health_state=self.disease.states[
                prototypes['susceptible']['health_state']
            ],
            life_cycle=self.lifecycle.get_random_state(),
            age=np.random.poisson(self.model.get_value('adult_age')))
                   for _ in range(total_N - total_I)]
        animals += [Animal(
            health_state=self.disease.states[
                prototypes['infected']['health_state']
            ],
            life_cycle=self.lifecycle.get_random_state(),
            age=np.random.poisson(self.model.get_value('adult_age')))
                    for _ in range(total_I)]
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
        nb_I = self.counts['I']
        # len(self['infection'][(self.disease.states['I'],)]._content)\
            # if (self.disease.states['I'],) in self['infection'] else 0
        # print(nb_I)
        return nb_I


    @property
    def total_N(self):
        """Return the number of animals in the herd.

        """
        return self['MASTER'].population

    @property
    def total_Q(self):
        """Return the number of animals in the quarantine zone.

        """
        return self.counts['Q']
        # return self['infection'][(self.disease.states['Q'],)].population\
        #     if (self.disease.states['Q'],) in self['infection'] else 0

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

    @property
    def counts(self):
        """Return a pandas DataFrame contains counts of each process if existing.

        NB: column steps need to be with one of process

        """
        res = {}
        for comp in self:
            try:
                res.update(comp.counts)
            except AttributeError:
                pass
        if self.keep_history:
            res.update({'steps': self.step})
            return pd.DataFrame(res)
        return pd.DataFrame(res, index=[0])
