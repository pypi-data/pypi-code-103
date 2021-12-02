"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for process management in
MultiProcessCompartments.

"""

from   abc                       import abstractmethod

import numpy                     as np

from   emulsion.tools.misc       import rates_to_probabilities, aggregate_probabilities

class AbstractProcess(object):
    """An AbstractProcess is aimed at controlling a specific activity
    in a compartment, and is identified by its name.

    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Process "{}"'.format(self.name)

    __str__ = __repr__

    @abstractmethod
    def evolve(self):
        """Define the actions that the process must perform."""
        pass


class MethodProcess(AbstractProcess):
    """A MethodProcess is aimed at running a specific method (and
    possibly any function or even any callable object).

    """
    def __init__(self, name, method, lparams=[], dparams={}):
        super().__init__(name)
        self.method = method
        self.lparams = lparams
        self.dparams = dparams

    def evolve(self):
        """Define the actions that the process must perform. In a
        MethodProcess, those actions consist in running the method of
        the target compartment.

        """
        self.method(*self.lparams, **self.dparams)


class StateMachineProcess(AbstractProcess):
    """A StateMachineProcess is aimed at running a specific state machine
    within the agent (not within a grouping).

    """
    def __init__(self, name, agent, state_machine):
        super().__init__(name)
        self.agent = agent
        self.state_machine = state_machine

    def evolve(self):
        """Define the actions that the process must perform. In a
        StateMachineProcess, those actions consist in executing the
        transitions of the state machine.

        """
        # retrieve the name of the statevar/attribute where the
        # current state is stored
        statevar = self.state_machine.machine_name
        # retrieve the value of the current state
        #current_state = self.get_information(statevar).name
        current_state = self.agent.statevars[statevar].name
        # perform actions associated to the current state
        self.agent.do_state_actions('on_stay', self.state_machine,
                                    current_state, population=1)
        # retrieve all possible transitions from this state
        transitions = self.agent.next_states_from(current_state,
                                                  self.state_machine)
        # skip this machine if no available transitions
        if transitions:
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
                    values = tuple(v / total_value
                                   for v in values) + (1- total_value,)
            elif 'proba' in available_flux:
                # handle probabilities
                values = aggregate_probabilities(values,
                                                 self.agent.model.delta_t)
                values += (1 - sum(values),)
            else:
                # transform rates into probabilities
                values = rates_to_probabilities(total_value, values,
                                                delta_t=self.agent.model.delta_t)
            index = np.nonzero(np.random.multinomial(1, values))[0][0]
            next_state = states[index]
            next_action = actions[index]
            if next_state != current_state:
                self.agent.do_state_actions('on_exit', self.state_machine,
                                            current_state, population=1)
                self.agent.set_information(statevar,
                                           self.state_machine.states[next_state])
                # self.agent.do_edge_actions('on_cross', state_machine,
                #                      current_state, next_state, population=1)
                if next_action:
                    self.agent.do_edge_actions(actions=next_action, population=1)
                self.agent.do_state_actions('on_enter', self.state_machine,
                                            next_state, population=1)
