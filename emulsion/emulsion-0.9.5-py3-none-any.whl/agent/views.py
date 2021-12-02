"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for entities management.

"""

from   collections               import OrderedDict
import numpy                     as np

from   sortedcontainers          import SortedSet

from   emulsion.agent.core       import Aggregation
from   emulsion.tools.misc       import select_random


#   _____ _                 _   __      ___
#  / ____(_)               | |  \ \    / (_)
# | (___  _ _ __ ___  _ __ | | __\ \  / / _  _____      __
#  \___ \| | '_ ` _ \| '_ \| |/ _ \ \/ / | |/ _ \ \ /\ / /
#  ____) | | | | | | | |_) | |  __/\  /  | |  __/\ V  V /
# |_____/|_|_| |_| |_| .__/|_|\___| \/   |_|\___| \_/\_/
#                    | |
#                    |_|

class SimpleView(Aggregation):
    """A SimpleView uses a set to store the underlying
    units. It is rather aimed at storing AtomAgents. All units are
    considered in the same state, thus conditions in the state
    machines are evaluated for the whole compartment, not for
    individuals.

    """
    def __init__(self, **others):
        super().__init__(**others)
        self._content = SortedSet()
        self.stochastic = True

    def __iter__(self):
        return self._content.__iter__()

    def get_content(self):
        """Return the units contained in the current unit.

        """
        return {'agents': list(self._content)}

    def add(self, population):
        """Add the specified population to the current compartment."""
        super().add(population)
        self._content |= SortedSet(population)

    def remove(self, population):
        """Remove the specified population from the current
        compartment.

        """
        super().remove(population)
        self._content -= SortedSet(population)

    def next_states(self, states, values, populations, actions, method=None):
        """Compute stochastically the population moving from the
        current compartment to each of the destination states,
        according to the values interpreted as probabilities. Actions
        are to be performed when changing state. The population
        affected by the transitions is stored in the first element of
        the `populations` parameter, as a dictionary: {'agents':
        list_of_agents}. Several edges can lead to the same state.

        """
        origin = populations[0]['agents']
        modified = SortedSet()
        if method == 'amount':
            # length of values is expected to be the number of output edges
            total_value = sum(values)
            if total_value > len(origin):
                # restart with proportions instead
                return self.next_states(states,
                                        tuple(v / total_value for v in values) + (0,),
                                        populations, actions, method=None)
            evolution = [int(v) for v in values]
            print(states, evolution)
        else:
            # values is expected to be the number of output edges + 1
            evolution = np.random.multinomial(len(origin), values)[:-1]
        next_ = []
        for state, qty, act in zip(states[:-1], evolution, actions[:-1]):
            if qty > 0:
                moving = select_random(origin, qty, exclude=modified)
                modified |= SortedSet(moving)
                next_.append((self._host.state_machine.states[state],
                              {'agents': moving, 'actions': act}))
        return next_



#              _             _   _        __      ___
#     /\      | |           | | (_)       \ \    / (_)
#    /  \   __| | __ _ _ __ | |_ ___   ____\ \  / / _  _____      __
#   / /\ \ / _` |/ _` | '_ \| __| \ \ / / _ \ \/ / | |/ _ \ \ /\ / /
#  / ____ \ (_| | (_| | |_) | |_| |\ V /  __/\  /  | |  __/\ V  V /
# /_/    \_\__,_|\__,_| .__/ \__|_| \_/ \___| \/   |_|\___| \_/\_/
#                     | |
#                     |_|

class AdaptiveView(SimpleView):
    """An AdaptiveView is able to evaluate conditions on individuals
    (AtomAgents) for state transitions, and to detect changes in its
    content and automatically report it to the upper level. Each
    compartment is associated with a particular value of a specific
    state variable or attribute of the units in its content. At the
    end of the evolve step, the compartment checks the values of the
    units in its content and reports units where changes occured.

    """
    def __init__(self, observables=(None,), values=(None,), **others):
        """Specify the state variables or attributes associated with
        this compartment (``observables``) and the expected values.

        """
        super().__init__(**others)
        self.statevars.observables = observables
        for (observable, value) in zip(observables, values):
            self.statevars[observable] = value


    def evaluate_condition(self, condition):
        """Return the population of the compartment if the condition
        is fulfilled, 0 otherwise.

        """
        if not callable(condition):
            return self.get_content() if condition else {}
        result = list(filter(condition, self._content))
        return {'agents': result} if result else {}

    def next_states(self, states, values, populations, actions, method=None):
        """Compute stochastically the population moving from each
        population (dict {'agents': list_of_agents}) in the
        `compart_pop` parameter, to each of the possible destination
        states, according to each of the values interpreted as
        probabilities. Actions are to be performed when changing
        state. Several edges can lead to the same state.

        """
        modified = SortedSet()
        if len(populations) == 1:
            if method == 'amount':
                # length of values is expected to be the number of output edges
                total_value = sum(values)
                if total_value > len(populations[0]['agents']):
                    # restart with proportions instead
                    return self.next_states(states,
                                            tuple(v / total_value
                                                  for v in values) + (0,),
                                            populations, actions, method=None)
                values = values + (total_value,)
            populations *= len(states)-1
        next_ = []
        for state, value, population, act\
          in zip(states[:-1], values[:-1], populations, actions[:-1]):
            if method == 'amount':
                evolution = int(value)
            else:
                evolution = np.random.binomial(len(population['agents']), value)
            if evolution > 0:
                moving = select_random(population['agents'],
                                       evolution, exclude=modified)
                modified |= SortedSet(moving)
                next_.append((self._host.state_machine.states[state],
                              {'agents': moving, 'actions': act}))
        return next_


    def evolve(self, machine=None):
        """After the ordinary ``evolve`` step, check units which have
        changed their value(s) of the compartment-specific
        observable(s). The corresponding units are reported to the
        upper level.

        """
        super().evolve(machine=machine)
        self.check_consistency()

    def check_consistency(self):
        """Check the value of the observables of the current
        compartment. Units which do not have the expected values are
        notified to the upper level.

        """
        # intruders = [unit for unit in self
        #              if any(unit.get_information(observable)\
        #                       != self.statevars[observable]
        #                     for observable in self.statevars.observables)]
        intruders = SortedSet()
        for unit in self:
            for observable in self.statevars.observables:
                if unit.get_information(observable) !=\
                   self.statevars[observable]:
                    intruders.add(unit)
                    break
        if intruders:
            self._host.notify_changed_units(self, intruders)

    def clone(self, **others):
        """Make a copy of the current compartment with the specified
        observable/value settings. The new content is empty.

        """
        # new_comp = copy.copy(self)
        # new_comp._content = SortedSet()
        # new_comp.statevars = StateVarDict(self.statevars)
        new_comp = self.__class__.from_dict(self.statevars)
        new_comp.model = self.model
        new_comp._content = SortedSet()
        new_comp._host = self._host
        new_comp.statevars.update(**others)
        # new_comp.statevars.step = self.statevars.step
        new_comp.recursive = self.recursive
#        new_comp.set_information(observable, value)
        return new_comp



#   _____ _                   _                      ___      ___
#  / ____| |                 | |                    | \ \    / (_)
# | (___ | |_ _ __ _   _  ___| |_ _   _ _ __ ___  __| |\ \  / / _  _____      __
#  \___ \| __| '__| | | |/ __| __| | | | '__/ _ \/ _` | \ \/ / | |/ _ \ \ /\ / /
#  ____) | |_| |  | |_| | (__| |_| |_| | | |  __/ (_| |  \  /  | |  __/\ V  V /
# |_____/ \__|_|   \__,_|\___|\__|\__,_|_|  \___|\__,_|   \/   |_|\___| \_/\_/


class StructuredView(Aggregation):
    """A StructuredView uses ad dict list to store the underlying
    units. It is rather aimed at storing other compartiments.

    """
    def __init__(self, keep_history=True, **others):
        super().__init__(**others)
        self.keep_history = keep_history
        self._content = OrderedDict()
        self._notifications = {}

    def __iter__(self):
        return self._content.values().__iter__()

    def __getitem__(self, name):
        return self._content[name]

    def get_content(self):
        """Return the units contained in the current unit.

        """
        print('WARNING, should not enter here !!!')
        return {'agents': list(self._content.values())}

    def add(self, population):
        """Add the specified population to the current
        compartment. The population is expected to be a dictionary
        with names as keys and compartments as values.

        """
        for key, pop in population.items():
            if key in self._content:
                self._content[key].add(pop._content)
            else:
                self._content[key] = pop

    def remove(self, population):
        """Remove the specified population from the current
        compartment.  The population is expected to be a dictionary
        with names as keys and compartments as values.

        """
        for key, pop in population.items():
            if key in self._content:
                self._content[key].remove(pop._content)

    def notify_changed_units(self, source_compartment, units):
        """Receive a change notification concerning several units
        which cannot be stored anymore in the source compartment.

        """
        if source_compartment in self._notifications:
            self._notifications[source_compartment] |= units
        else:
            self._notifications[source_compartment] = SortedSet(units)

    def handle_notifications(self):
        """Handle all notifications received during the time step."""
        for source_compartment, units in self._notifications.items():
            source_observables = source_compartment.statevars.observables
            new_pop = {}
 #           pop_values = {}
            for unit in units:
                key = tuple(unit.get_information(k) for k in source_observables)
                if key not in new_pop:
                    new_pop[key] = [unit]
#                    pop_values[key] = unit.get_information(source_observable)
                else:
                    new_pop[key].append(unit)
            for key, unit in new_pop.items():
                new_comp = self.get_or_build(key, model=source_compartment)
#                print('Moving to:', new_comp, '\n\t', [u._agid for u in unit])
                source_compartment.move_to(new_comp, agents=unit)
        self._notifications.clear()

    def get_or_build(self, key, model=None):
        """Return the compartment with the specified key if any, or
        build one by cloning the model if not found.

        """
        if key not in self._content:
            key_infos = dict(zip(self.keys, key))
#            print('Adding new comp:', key, key_infos)
            new_compart = model.clone(host=self, **key_infos)
            new_compart.keys = key
#            print(new_compart.statevars)
            self.add({key: new_compart})
        return self[key]

    def evolve(self, machine=None):
        super().evolve(machine=machine)
        self.handle_notifications()


#                _        _____ _                   _                      _
#     /\        | |      / ____| |                 | |                    | |
#    /  \  _   _| |_ ___| (___ | |_ _ __ _   _  ___| |_ _   _ _ __ ___  __| |
#   / /\ \| | | | __/ _ \\___ \| __| '__| | | |/ __| __| | | | '__/ _ \/ _` |
#  / ____ \ |_| | || (_) |___) | |_| |  | |_| | (__| |_| |_| | | |  __/ (_| |
# /_/    \_\__,_|\__\___/_____/ \__|_|   \__,_|\___|\__|\__,_|_|  \___|\__,_|
# __      ___
# \ \    / (_)
#  \ \  / / _  _____      __
#   \ \/ / | |/ _ \ \ /\ / /
#    \  /  | |  __/\ V  V /
#     \/   |_|\___| \_/\_/


class AutoStructuredView(StructuredView):
    """An AutoStructuredView stores agents in an OrderedDict, using a
    specific statevar as key.

    """
    def __init__(self, key_variable=None, **others):
        super().__init__(**others)
        self.key_variable = key_variable


    def add(self, population):
        """Add the specified population (SortedSet or list) to the
        current view.

        """
        for agent in population:
            self._content[agent.statevars[self.key_variable]] = agent

    def remove(self, population):
        """Remove the specified population from the current view. The
        population is expected to be a SortedSet or list.

        """
        for agent in population:
            key = agent.statevars[self.key_variable]
            if key in self._content:
                del self._content[key]
