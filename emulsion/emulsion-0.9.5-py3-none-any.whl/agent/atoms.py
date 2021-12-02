"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for entities management.

"""

from   collections               import OrderedDict

import numpy                     as np

from   emulsion.agent.core       import EmulsionAgent
from   emulsion.tools.misc       import rates_to_probabilities, aggregate_probabilities


#          _                                           _
#     /\  | |                    /\                   | |
#    /  \ | |_ ___  _ __ ___    /  \   __ _  ___ _ __ | |_
#   / /\ \| __/ _ \| '_ ` _ \  / /\ \ / _` |/ _ \ '_ \| __|
#  / ____ \ || (_) | | | | | |/ ____ \ (_| |  __/ | | | |_
# /_/    \_\__\___/|_| |_| |_/_/    \_\__, |\___|_| |_|\__|
#                                      __/ |
#                                     |___/

class AtomAgent(EmulsionAgent):
    """The AtomAgent is aimed at representing an 'individual', i.e. the
    smallest organization level to be modeled as an entity in the
    simulation. An AtomAgent may be situated in several hosts, each one
    associated with a specific tuple of state variables.

    """
    def __init__(self, **others):
        super().__init__(**others)
        self.statevars.population = 1
        self._host = OrderedDict()
        if 'host' in others:
            self.add_host(others['host'])
    def __len__(self):
        return 1

    def get_content(self):
        """Return the population (1) of the current unit.

        """
        return {'population': 1}

    def add_host(self, host):
        """Add the specified host to the current AtomAgent, associated
        with the specified key.

        """
        self._host[host.keys] = host
        self.simulation = host.simulation

    def remove_host(self, host, keys=None):
        """Remove the specified host from the current AtomAgent,
        associated with the specified key.

        """
        if keys is None:
            del self._host[host.keys]
        else:
            del self._host[keys]

    def get_host(self, key=()):
        """Retrieve the host of the current AtomAgent identified by the
        specific key.

        """
        return self._host[key]


#  ______          _       _                     _
# |  ____|        | |     (_)               /\  | |
# | |____   _____ | |_   ___ _ __   __ _   /  \ | |_ ___  _ __ ___
# |  __\ \ / / _ \| \ \ / / | '_ \ / _` | / /\ \| __/ _ \| '_ ` _ \
# | |___\ V / (_) | |\ V /| | | | | (_| |/ ____ \ || (_) | | | | | |
# |______\_/ \___/|_| \_/ |_|_| |_|\__, /_/    \_\__\___/|_| |_| |_|
#                                   __/ |
#                                  |___/

class EvolvingAtom(AtomAgent):
    """An EvolvingAtom is able to change state according to its
    own statemachines.

    """
    def __init__(self, statemachines=[], **others):
        super().__init__(**others)
        self.statemachine_dict = {sm.machine_name: sm
                                  for sm in statemachines}

    def get_machine(self, name):
        """Return the state machine with the specified name."""
        return self.statemachine_dict[name]

    def evolve(self, machine=None):
        super().evolve(machine=machine)
        self.evolve_states()

    def evolve_states(self, machine=None):
        """Change the state of the current unit according to the
        specified state machine name. If no special state machine is
        provided, executes all the machines.

        """
        # retrieve the iterable containing the machines to apply
        state_machines = [self.statemachine_dict[machine]] if machine\
                         else self.statemachine_dict.values()
        # iterate over each machine
        for state_machine in state_machines:
            # retrieve the name of the statevar/attribute where the
            # current state is stored
            statevar = state_machine.machine_name
            # retrieve the value of the current state
            #current_state = self.get_information(statevar).name
            current_state = self.statevars[statevar].name
            # perform actions associated to the current state
            self.do_state_actions('on_stay', state_machine, current_state, population=1)
            # retrieve all possible transitions from this state
            transitions = self.next_states_from(current_state, state_machine)
            # skip this machine if no available transitions
            if not transitions:
                continue
            states, flux, values, _, actions = zip(*transitions)
            total_value = sum(values)
            states = states + (current_state,)
            actions = actions + ([], )
            available_flux = set(flux)
            if 'amount' in available_flux or 'amount-all-but' in available_flux:
            # handle amounts
                # compute proper values (bounded by 0/1) and when
                # needed, invert 'amount-all-but' values
                values = [max(min(1-v, 1), 0) if f == 'amount-all-but'\
                            else max(min(v, 1), 0)
                          for (f, v) in zip(flux, values)]
                # recompute total value
                total_value = sum(values)
                # normalize to have probabilities
                if total_value == 0:
                    values = (0,)*len(values) + (1,)
                else:
                    values = tuple(v / total_value for v in values) + (1- total_value,)
            elif 'proba' in available_flux:
                # handle probabilities
                values = aggregate_probabilities(values,
                                                 self.model.delta_t)
                values += (1 - sum(values),)
            else:
                # transform rates into probabilities
                values = rates_to_probabilities(total_value, values,
                                                delta_t=self.model.delta_t)
            index = np.nonzero(np.random.multinomial(1, values))[0][0]
            next_state = states[index]
            next_action = actions[index]
            if next_state != current_state:
                self.do_state_actions('on_exit', state_machine, current_state, population=1)
                self.set_information(statevar, state_machine.states[next_state])
                # self.do_edge_actions('on_cross', state_machine,
                #                      current_state, next_state, population=1)
                if next_action:
                    self.do_edge_actions(actions=next_action, population=1)
                self.do_state_actions('on_enter', state_machine, next_state, population=1)
