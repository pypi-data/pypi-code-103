"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for actions.

"""

from   abc                 import abstractmethod
import numpy               as     np

from   emulsion.tools.misc import retrieve_value, rates_to_probabilities

class AbstractAction(object):
    """AbstractActions are aimed at describing actions triggered by a
    state machine.

    """
    def __init__(self, state_machine=None, **_):
        self.state_machine = state_machine

    @abstractmethod
    def execute_action(self, unit, **others):
        """Execute the action on the specified unit."""
#        print(self, 'executed by', unit)
        pass

    @classmethod
    def build_action(cls, action_name, **others):
        """Return an instance of the appropriate Action subclass,
        depending on its name. The appropriate parameters for this
        action should be passed as a dictionary.

        """
        return ACTION_DICT[action_name](**others)

    def __str__(self):
        return self.__class__.__name__

class ValueAction(AbstractAction):
    """ValueActions represent modifications of state variables or
    attributes.

    """
    def __init__(self, statevar_name=None, parameter=None, delta_t=1, **others):
        """Create a ValueAction aimed at modifying the specified
        statevar according to the paramter.

        """
        super().__init__(**others)
        self.statevar_name = statevar_name
        self.parameter = parameter
        self.delta_t = delta_t


class RateAdditiveAction(ValueAction):
    """A RateChangeAction is aimed at increasing or decreasing a
    specific state variable or attribute, according to a specific rate
    (i.e. the actual increase or decrease is the product of the
    `parameter` attribute and a population size).

    """
    def __init__(self, sign=1, **others):
        super().__init__(**others)
        self.sign = sign

    def execute_action(self, unit, population=None, agents=None):
        """Execute the action on the specified unit, with the
        specified population size.

        """
        super().execute_action(unit)
        if population is None:
            population = len(agents)
        rate_value = self.state_machine.get_value(self.parameter)
        rate = retrieve_value(rate_value, unit)
        current_val = unit.get_information(self.statevar_name)
        new_val = current_val + self.sign*rate*population*self.delta_t
        # print('Executing', self.__class__.__name__, 'for', unit,
        #       self.statevar_name, current_val, '->', new_val,
        #       self.sign, rate, population)
        unit.set_information(self.statevar_name, new_val)

    def __str__(self):
        return super().__str__() + ' ({}, {})'.format(self.statevar_name,
                                                      self.parameter)
    __repr__ = __str__


class RateDecreaseAction(RateAdditiveAction):
    """A RateDecreaseAction is aimed at decreasing a specific state
    variable or attribute, according to a specific rate (i.e. the
    actual decrease is the product of the `parameter` attribute and a
    population size).

    """
    def __init__(self, **others):
        super().__init__(sign=-1, **others)

class RateIncreaseAction(RateAdditiveAction):
    """A RateIncreaseAction is aimed at increasing a specific state
    variable or attribute, according to a specific rate (i.e. the
    actual increase is the product of the `parameter` attribute and a
    population size).

    """
    def __init__(self, **others):
        super().__init__(sign=1, **others)

class StochAdditiveAction(ValueAction):
    """A StochAdditiveAction is aimed at increasing or decreasing a
    specific state variable or attribute, according to a specific
    rate, using a *binomial sampling*.

    """
    def __init__(self, sign=1, **others):
        super().__init__(**others)
        self.sign = sign

    def execute_action(self, unit, population=None, agents=None):
        """Execute the action on the specified unit, with the
        specified population size.

        """
        super().execute_action(unit)
        if population is None:
            population = len(agents)
        rate_value = self.state_machine.get_value(self.parameter)
        rate = retrieve_value(rate_value, unit)
        # convert rate into a probability
        proba = rates_to_probabilities(rate, [rate], delta_t=self.delta_t)[0]
        current_val = unit.get_information(self.statevar_name)
        new_val = current_val + self.sign*np.random.binomial(population, proba)
        # print('Executing', self.__class__.__name__, 'for', unit,
        #       self.statevar_name, current_val, '->', new_val,
        #       self.sign, rate, population)
        unit.set_information(self.statevar_name, new_val)

    def __str__(self):
        return super().__str__() + ' ({}, {})'.format(self.statevar_name,
                                                      self.parameter)
    __repr__ = __str__


class StochDecreaseAction(StochAdditiveAction):
    """A StochDecreaseAction is aimed at decreasing a specific state
    variable or attribute, according to a specific rate, using a
    *binomial sampling*.

    """
    def __init__(self, **others):
        super().__init__(sign=-1, **others)

class StochIncreaseAction(StochAdditiveAction):
    """A StochIncreaseAction is aimed at increasing a specific state
    variable or attribute, according to a specific rate, using a
    *binomial sampling*.

    """
    def __init__(self, **others):
        super().__init__(sign=1, **others)


class MethodAction(AbstractAction):
    """A MethodAction is aimed at making an agent perform an action on
    a specific population. It requires a method name, and optionnally
    a list and a dictionary of parameters.

    """
    def __init__(self, method=None, l_params=[], d_params={}, **others):
        super().__init__(**others)
        self.method = method
        self.l_params = l_params
        self.d_params = d_params

    def __str__(self):
        return super().__str__() + ' ({!s}, {}, {})'.format(self.method,
                                                            self.l_params,
                                                            self.d_params)
    __repr__ = __str__

    def execute_action(self, unit, agents=None, **others):
        """Execute the action using the specified unit. If the
        `agents` parameter is a list of units, each unit of this list
        will execute the action.

        """
        if agents is None:
            agents = [unit]
        for agent in agents:
            action = getattr(agent, self.method)
            l_params = [retrieve_value(self.state_machine.get_value(expr), agent)
                        for expr in self.l_params]
            ### introduced to pass internal information such as population
            d_params = others
            d_params.update({key: retrieve_value(self.state_machine.get_value(expr), agent)
                             for key, expr in self.d_params.items()})
            action(*l_params, **d_params)

class FunctionAction(MethodAction):
    """A FunctionAction is aimed at making an agent perform an action
    on a specific population. It requires a function, and optionnally
    a list and a dictionary of parameters. A FunctionAction runs
    faster than a MethoAction since it does not require to retrieve
    the method in each agent.

    """
    def __init__(self, function=None, **others):
        super().__init__(**others)
        self.function = function
        self.method = function.__name__

    def execute_action(self, unit, agents=None, **others):
        """Execute the action using the specified unit. If the
        `agents` parameter is a list of units, each unit of this list
        will execute the action.

        """
        if agents is None:
            agents = [unit]
        for agent in agents:
            l_params = [retrieve_value(self.state_machine.get_value(expr),
                                       agent)
                        for expr in self.l_params]
            ### introduced to pass internal information such as population
            d_params = others
            d_params.update({key:\
                             retrieve_value(self.state_machine.get_value(expr),
                                            agent)
                             for key, expr in self.d_params.items()})
            self.function(agent, *l_params, **d_params)


ACTION_DICT = {
    'increase': RateIncreaseAction,
    'decrease': RateDecreaseAction,
    'increase_stoch': StochIncreaseAction,
    'decrease_stoch': StochDecreaseAction,
    'action': MethodAction,
    'duration': FunctionAction
}
