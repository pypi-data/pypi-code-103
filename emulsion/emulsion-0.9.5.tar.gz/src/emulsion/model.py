
"""@package emulsion.model

A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for the definition of EMuLSion models.

"""

from   pathlib                 import Path
from   functools               import partial
from   datetime                import datetime, timedelta
from   copy                    import deepcopy

import yaml
import numpy                   as     np
import dateutil.parser         as     dup
from   sympy                   import sympify, lambdify, pretty, Symbol
from   sortedcontainers        import SortedSet, SortedDict
from   jinja2                  import Environment, PackageLoader

#import networkx                as     nx

import emulsion.tools.graph    as     nx
from   emulsion.agent.action   import AbstractAction
from   emulsion.tools.state    import StateVarDict, EmulsionEnum
from   emulsion.tools.misc     import read_from_file, load_module, load_class
from   emulsion.tools.calendar import EventCalendar

#  ______                    _   _
# |  ____|                  | | (_)
# | |__  __  _____ ___ _ __ | |_ _  ___  _ __  ___
# |  __| \ \/ / __/ _ \ '_ \| __| |/ _ \| '_ \/ __|
# | |____ >  < (_|  __/ |_) | |_| | (_) | | | \__ \
# |______/_/\_\___\___| .__/ \__|_|\___/|_| |_|___/
#                     | |
#                     |_|

class SemanticException(Exception):
    """Exception raised when a semantic error occurs during model parsing.

    """
    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message


#  ______                _   _
# |  ____|              | | (_)
# | |__ _   _ _ __   ___| |_ _  ___  _ __  ___
# |  __| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
# | |  | |_| | | | | (__| |_| | (_) | | | \__ \
# |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/

## Special strings for graphviz/dot formatting
#ACTION_SYMBOL = '&#9881;'
#ACTION_SYMBOL = '&#8623;'
ACTION_SYMBOL = '&#9670;'
WHEN_SYMBOL = 'odot'
UNLESS_SYMBOL = 'oinv'
COND_SYMBOL = 'tee'
CROSS_SYMBOL = 'diamond'
EDGE_KEYWORDS = ['rate', 'proba', 'amount', 'amount-all-but']

### INFORMATION TO ADD TO LEVEL DESCRIPTION WHEN USING aggregation_type
DEFAULT_LEVEL_INFO = {
    'IBM': {
        'level': {
            'class_name': 'IBMProcessManager',
            'module': 'emulsion.agent.managers',
            'master': {'class_name': 'SimpleView',
                       'module': 'emulsion.agent.views'}
        },
        'sublevels': {
            'class_name': 'EvolvingAtom',
            'module': 'emulsion.agent.atoms'
        }
    },
    'compartment': {
        'level': {
            'module': 'emulsion.agent.managers',
            'class_name': 'CompartProcessManager'
        }
    },
    'hybrid': {
        'level': {
            'module': 'emulsion.agent.managers',
            'class_name': 'MultiProcessManager',
            'master': {'module': 'emulsion.agent.views',
                       'class_name': 'SimpleView'}
        },
        'sublevels': {
            'module': 'emulsion.agent.atoms',
            'class_name': 'AtomAgent'
        }
    },
    'metapopulation': {
        'level': {
            'module': 'emulsion.agent.managers',
            'class_name': 'MetapopProcessManager',
            'master': {
                'module': 'emulsion.agent.views',
                'class_name': 'AutoStructuredView',
                'options': {'key_variable': 'population_id'}
            }
        },
    },
}

### INFORMATION TO ADD TO GROUPING DESCRIPTION WHEN USING aggregation_type
DEFAULT_GROUPING_INFO = {
    'hybrid': {
        'compart_manager': {
            'module': 'emulsion.agent.managers',
            'class_name': 'GroupManager'
        },
        'compart_class': {
            'module': 'emulsion.agent.views',
            'class_name': 'AdaptiveView'
        },
        'fallback_view': {
            'module': 'emulsion.agent.views',
            'class_name': 'StructuredViewWithCounts'
        },
    },
    'compartment': {
        'compart_manager': {
            'module': 'emulsion.agent.managers',
            'class_name': 'GroupManager'
        },
        'compart_class': {
            'module': 'emulsion.agent.comparts',
            'class_name': 'Compartment'
        }
    }
}



def make_function(expression,
                  dtype=float,
                  modules=['numpy', 'numpy.random', 'math']):
    """Transform the specified sympy expression into a function of an
    agent, which substitutes the specified symbols of the expression
    with an access to either attributes or state variables of the same
    name in the agent (through the ``get_information`` method) and
    returns a value of the specified dtype. The transformation uses
    the `lambdify` sympy function for better performances, with the
    specified modules.

    """
    symbs = tuple(expression.free_symbols)
    mods = [load_module(m) for m in modules]
    lambdified = lambdify(symbs,
                          expression,
                          modules=mods)
    def _func(agent):
        vals = [float(agent.get_information(str(s))) for s in symbs]
        return dtype(lambdified(*vals))
    return _func


def make_when_condition(expression,
                        dtype=bool,
                        modules=['numpy', 'numpy.random', 'math']):
    """Transform the specified sympy expression into a function of an
    agent, which substitutes the specified symbol of the expression
    with an access to the simulation calendar. The transformation uses
    the `lambdify` sympy function for better performances, with the
    specified modules.

    """
    ## General idea: expression should be a boolean test for a
    ## property in the agent -> simulation -> calendar,
    ## e.g. expressions such as 'breeding_period' or 'Not(vacation)'
    ## call a function associated with 'breeding_period' or 'vacation'
    ## strings in the calendar. The function are applied to simulation
    ## step and generated on the basis of the points or intervals
    ## defined in the 'calendar' section of the model. This implies
    ## that all agents must have access to the whole simulation (or at
    ## least to the calendar). This also means that an actual calendar
    ## is a subclass of a generic calendar, generated automatically to
    ## be endowed with those properties.
    symbs = tuple(expression.free_symbols)
    mods = [load_module(m) for m in modules]
    lambdified = lambdify(symbs,
                          expression,
                          modules=mods)
    def _func(agent):
        vals = [agent.evaluate_event(str(s)) for s in symbs]
        return dtype(lambdified(*vals))
    return _func




def make_TTL_condition(model, machine_name):
    """Build a duration condition associated to the specified state
    machine and add it to the model. A condition duration, which is
    intended to specify when an agent is allowed to leave the current
    state of the state machine, is of the form
    '_time_spent_MACHINE_NAME > _time_to_live_MACHINE_NAME', each of
    those variables being automatically stored in the state
    variables.

    """
    var_name = '_time_spent_{}'.format(machine_name)
    var_max_name = '_time_to_live_{}'.format(machine_name)
    model._namespace[var_name] = Symbol(var_name)
    model._namespace[var_max_name] = Symbol(var_max_name)
    model.statevars[var_name] = {
        'desc': 'time spent in current state of state machine {}'.format(machine_name)
    }
    model.statevars[var_max_name] = {
        'desc': 'time max to spend in current state of state machine {}'.format(machine_name)
    }
    return 'StrictGreaterThan({}, {})'.format(var_name, var_max_name)


def make_TTL_init_action(agent, value, machine_name=None, **_):
    """Action that initializes the 'time to live' of in the state of
    the specified state_machine.

    """

    agent.init_time_to_live(machine_name, value)

def make_TTL_increase_action(agent, machine_name=None, **_):
    """Action that increases the time spent by the agent in the
    current state of the specified state_machine.

    """

    agent.increase_time_spent(machine_name)



#  ______                 _     _             __  __           _      _
# |  ____|               | |   (_)           |  \/  |         | |    | |
# | |__   _ __ ___  _   _| |___ _  ___  _ __ | \  / | ___   __| | ___| |
# |  __| | '_ ` _ \| | | | / __| |/ _ \| '_ \| |\/| |/ _ \ / _` |/ _ \ |
# | |____| | | | | | |_| | \__ \ | (_) | | | | |  | | (_) | (_| |  __/ |
# |______|_| |_| |_|\__,_|_|___/_|\___/|_| |_|_|  |_|\___/ \__,_|\___|_|


class EmulsionModel(object):
    """Class in charge of the description of a multi-level
    epidemiological model. Such models are composed of several
    processes which may take place at different
    organization/observation levels. Some of those processes are
    reified through a function implemented within an agent, while
    others are represented by a state machine. The model is also in
    charge of handling symbolic expressions and pre-computing their
    values, e.g. concerning parameters, transmission functions,
    etc.

    """
    def __init__(self, filename=None, description=None):
        """Instantiate the model either from a configuration file or
        from a string. Both must contain a YAML-based description of
        the model.

        """
        if filename:
            self.filename = filename
            self.parse(read_from_file(filename))
        else:
            self.filename = None
            self.parse(description)

    def __repr__(self):
        return '%s "%s"' % (self.__class__.__name__, self.model_name)

    def normalize_format(self):
        """Return a YAML representation of the model, reformatted to to print
        lists and dicts using the flow style (no [], no {}) instead of
        the block style, especially for syntax checking where rules
        are defined only for flow style.

        """
        return yaml.dump(self._description, default_flow_style=False)

    def copy(self):
        """Return a copy of object (naif method).
        TODO: Find a way to avoid recharging compartment class when
        intentiate a MultiProcessManager class with a old model.

        """
        return deepcopy(self)

    def _reset_all(self):
        # namespace for all symbols used in the model
        # dict string -> sympy symbol
        self._namespace = {}
        # namespace for calendar periods in the model
        # dict string -> sympy symbol
        self._event_namespace = {}
        # cache for all expressions encountered in the model
        # dict string -> sympy expression
        self._expressions = {}
        # cache for all values encountered in the model
        # dict string -> value or function
        self._values = {}
        # the original description to parse (dict from YAML document)
        self._description = {}
        # default values for modules used in symbolic computing
        self.modules = ['numpy', 'numpy.random', 'math']
        # name of the model
        self.model_name = 'New Model'
        # time unit (used to specify parameter values)
        self.time_unit = 'days'
        # duration of a simulation time step (number of time_units)
        self.delta_t = 1
        # duration of a simulation time step ('true' duration)
        self.step_duration = timedelta(days=1)
        # origin date for the simulation
        self.origin_date = datetime.now()
        # dictionary of calendars (keyed by their name)
        self.calendars = SortedDict()
        # reverse dict event -> calendar name
        self._events = {}
        # list of the processes involved in the model
        self.processes = []
        # description of the compartment associated with some of the processes
        self.compartments = {}
        # description of the state machines associated with some of the processes
        self.state_machines = {}
        # dict of all 'parameters' encountered in the model
        self.parameters = StateVarDict()
        # dict of all 'statevars' encountered in the model
        self.statevars = StateVarDict()
        # dict of all conditions encountered in the model
        self.conditions = {}
        # dict of all actions encountered in the model
        self.actions = {}
        # dict of actions to run for state initialization
        self.init_actions = {}
        # dict of all distributions encountered in the model
        self.distributions = {}
        # dict of all prototypes encountered in the model
        self.prototypes = {}
        # dict of enumerate types used in special variables
        self.types = {}
        # dict of all states existing in state machines
        self.states = StateVarDict()

    def add_init_action(self, machine_name, state, action):
        """Add an action to be performed when initializing agents for
        the specified state of the state machine. Mainly used for
        durations.

        """
        if machine_name not in self.init_actions:
            self.init_actions[machine_name] = {}
        if state not in self.init_actions[machine_name]:
            self.init_actions[machine_name][state] = [action]
        else:
            self.init_actions[machine_name][state].append(action)


    def _init_namespace(self):
        """Init the list of all encountered symbols, which have to be
        either parameters or state variables. The association between
        the name and the corresponding Symbol is stored in the
        namespace attribute.

        """
        # name space for 'regular' symbols (i.e. parameters, statevars)
        self._namespace.clear()
        for keyword in ['parameters', 'statevars']:
            if keyword in self._description:
                self._namespace.update({param: Symbol(param)
                                        for param in self._description[keyword]})

    def get_value(self, name):
        """Return the value associated with the specified name."""
        return self._values[name]

    def change_parameter_values(self, changes):
        """Naive method to change several parameter values at the same time."""
        for name, value in changes.items():
            if name == 'delta_t':
                self._description['time_info']['delta_t'] = int(value)
            else:
                self._description['parameters'][name]['value'] = value
        self.parse(self._description)

    def set_value(self, name, value):
        """Naif method to change a parameter's value.
        Will be more efficient when treating several parameters at
        the same time.

        """
        self._description['parameters'][name]['value'] = value
        self.parse(self._description)

    def parse(self, description):
        """Build the EmulsionModel from the specified dictionary
        (expected to come from a YAML configuration file).

        """
        self._reset_all()
        # keep an exhaustive description
        self._description = description
        # retrieve the name of the model
        self.model_name = self._description['model_name']
        # build association between symbols names and true sympy symbols
        self._init_namespace()
        # parse time informations
        self.build_timeinfo()
        # parse output options
        self.build_outputs_options()
        # parse parameters, state variables and distributions
        self.build_parameters()
        self.build_statevars()
        self.build_levels()
        self.build_distributions()
        self.build_prototypes()
        # parse processes
        self.build_processes()
        # parse compartment description
        self.build_compartment_desc()
        # parse state machines
        self.build_state_machines()
        # parse actions
        self.build_actions()
        # calculate expressions from parameters
        self.calculate_compound_params()
        # replace expressions by values or lambdas
        self.compute_values()

    def build_outputs_options(self):
        """Parse the outputs options of the model.
        The agents will treat extra variables for outputs (TODO), and
        the simulation classes will treat period outputs.

        Example of YAML specification:
        ------------------------------
        outputs:
          # level
          herd:
            period:1
          # level
          metapop:
            period: 7
            extra_vars:
              - step
              - infection_date
        """
        if 'outputs' in self._description:
            self.outputs = self._description['outputs']
        else:
            self.outputs = {}

    def build_timeinfo(self):
        """Parse the description of the model and extract the
        information related to time management, i.e. time unit,
        duration of a simulation step, origin date, calendars for
        specific events, etc.

        Example of YAML specification:
        ------------------------------
        time_info:
        time_unit: days
        delta_t: 7
        origin: 'May 1'
        calendar:
          name:
          period: 52
          events:
            spring: {begin: 'April 8', end: 'April 23'}
            summer: {begin: 'July 8', end: 'September 3'}
            national: {date: 'July 14'}
        """
        self._event_namespace.clear()
        if 'time_info' in self._description:
            tinfo = self._description['time_info']
            # compute effective duration of one time step
            self.time_unit = tinfo['time_unit']
            self.delta_t = tinfo['delta_t']
            timedesc = {self.time_unit: self.delta_t}
            self.step_duration = timedelta(**timedesc)
            # origin date for the simulation
            if 'origin' in tinfo:
                self.origin_date = dup.parse(tinfo['origin'])
            # total duration for the simulation (in time units)
            if 'total_duration' in tinfo:
                self.parameters['total_duration'] =\
                        sympify(tinfo['total_duration'], locals=self._namespace)
            # handle calendars
            if 'calendars' in tinfo:
                self.build_calendar(tinfo['calendars'])

    def build_calendar(self, calendar_desc):
        """Build a representation of calendars."""
        # init name space for 'event' symbols (periods of
        # time) and handle period definitions
        for cal_name, cal in calendar_desc.items():
            events = {}
            if 'events' in cal:
                for event_name, definition in cal['events'].items():
                    self._event_namespace[event_name] = Symbol(event_name)
                    if 'date' in definition:
                        events[event_name] = (dup.parse(definition['date']),
                                              dup.parse(definition['date']))
                    else:
                        events[event_name] = (dup.parse(definition['begin']),
                                              dup.parse(definition['end']))
                        for keyword in ['begin', 'end']:
                            event_limit = keyword + '_' + event_name
                            self._event_namespace[event_limit] = Symbol(event_limit)
                            events[event_limit] = (dup.parse(definition[keyword]),
                                                   dup.parse(definition[keyword]))
            # cal_name = cal['name']
            self.calendars[cal_name] = EventCalendar(cal_name,
                                                     self.step_duration,
                                                     self.origin_date,
                                                     period=timedelta(**cal['period'])\
                                                       if 'period' in cal\
                                                       else None,
                                                     **events)
            for event in self.calendars[cal_name].get_events():
                self._events[event] = cal_name
                expression = sympify(event, locals=self._event_namespace)
                self._values[str(expression)] = make_when_condition(
                    expression, modules=self.modules)


    def get_calendar_for_event(self, name):
        """Return the calendar providing the specified event name."""
        return self.calendars[self._events[name]]

    def build_parameters(self):
        """Parse the description of the model and extract the
        parameters, either with their value, or with the expression to
        compute them.

        Example of YAML specification:
        ------------------------------
        parameters:
          p:
            desc: infection probability
            value: '(1-exp(-E_total)) * (1 - phi*vaccinated)'
          phi:
            desc: efficiency of vaccination
            value: 0.79

        """
        if 'modules' in self._description:
            self.modules = self._description['modules']
        if 'parameters' in self._description:
            for (key, val) in self._description['parameters'].items():
                self.parameters[key] = sympify(val['value'],
                                               locals=self._namespace)

    def build_statevars(self):
        """Parse the description of the model and extract the state
        variables that agents running this model must have.

        Example of YAML specification:
        ------------------------------
        statevars:
          E_total:
            desc: total bacteria deposited in the environment
          vaccinated:
            desc: 0/1 value describing the vaccination state

        """
        if 'statevars' in self._description:
            self.statevars = StateVarDict(self._description['statevars'])


    def build_distributions(self):
        """Parse the description of the model and extract the
        distributions, either with their value, or with the expression
        to compute them. A distribution is a dictionary of the form
        {quantity: probability}. It is stored as a list of tuples
        (quantity, probability) which is more convenient for
        subsequent processing.

        Example of YAML specification:
        ------------------------------
        distributions:
          - shedding_dist1:
              desc: distribution of shedding
              value:
                low_shedding: 0.85
                med_shedding: 0.15

        """
        if 'distributions' in self._description:
            for list_item in self._description['distributions']:
                for (key, val) in list_item.items():
                    self.distributions[key] = [
                        (sympify(quantity, locals=self._namespace),
                         sympify(probability, locals=self._namespace))
                        for quantity, probability in val['value'].items()]

    def build_prototypes(self):
        """Parse the description of the model and extract the
        prototypes, either with their value, or with the expression
        to compute them. A prototype is a dictionary of the form
        {statevar: value}..

        Example of YAML specification:
        ------------------------------
        prototypes:
          - newborn:
              desc: prototype for new calves
              health_state: M
              life_state: NP
              age: 0

        """
        if 'prototypes' in self._description:
            for level, prototypes in self._description['prototypes'].items():
                self.prototypes[level] = {}
                for list_item in prototypes:
                    for (key, val) in list_item.items():
                        self.prototypes[level][key] = {
                            variable: (value if value != 'random'\
                                       else '_random_' + variable)
                            for variable, value in val.items()
                            # if variable != 'desc'
                        }

    def get_prototype(self, level, name):
        """Return a ready-to-use prototype, i.e. a StateVarDict corresponding
        to the prototype for the specified level and name, where
        symbols associated to statevariables are already replaced by
        their value in the model.

        """
        return StateVarDict({
            var: self.get_value(val)
            for var, val in self.prototypes[level][name].items()
        })

    def build_levels(self):
        """Parse the description of different level of simulations.
        Most of time, there are tree differents levels:
        individual, herd, metapopulation.

        Example of YAML specification:
        ------------------------------
        levels:
          individuals:
            super:
              class: AtomAgent
            class_name: Cow
          herd:
            super:
              class: MultiProcessManager
            class_name: QfeverHerd
          metapop:
            super:
              class: MultiProcessManager
              master_class: StructuredView
            class_name: QfeverMetaPop

        """
        if 'levels' in self._description:
            self.levels = self._description['levels']
        # add default information if missing
        for level in self.levels:
            desc = self.levels[level]
            if ('aggregation_type' in desc) and\
               (not desc['module'].startswith('emulsion.agent')):
                default = DEFAULT_LEVEL_INFO[desc['aggregation_type']]
                if 'super' not in desc:
                    desc['super'] = default['level']
                if 'sublevels' in default:
                    if 'contains' in desc:
                        for sublevel in desc['contains']:
                            if (not self.levels[sublevel]['module'].startswith('emulsion.agent'))\
                               and ('super' not in self.levels[sublevel]):
                                self.levels[sublevel]['super'] = default['sublevels']
        # print(self.levels)
    def get_agent_class_for_level(self, level):
        return load_class(module=self.levels[level]['module'],
                          class_name=self.levels[level]['class_name'])

    def build_processes(self):
        """Parse the description of the model and retrieve the list of
        processes with different level.

        Example of YAML specification:
        ------------------------------
        processes:
          herd:
            - bacterial_dispersion
            - culling_process
            - infection
          metapop:
            - inbox_distribution
            - outbox_distribution
        """
        if 'processes' in self._description:
            self.processes = self._description['processes']


    def build_state_machines(self):
        """Parse the description of the model and build all the
        required state machines.

        """
        if 'state_machines' in self._description:
            for machine_name, description in self._description['state_machines'].items():
                self.state_machines[machine_name] = StateMachine(machine_name,
                                                                 description,
                                                                 self)

    def build_compartment_desc(self):
        """Inspect the `grouping` part of the model (if
        any) in order to store the corresponding information.

        """
        if 'grouping' in self._description:
            self.compartments = self._description['grouping']
            for level in self.levels.keys():
                if level not in self.compartments:
                    self.compartments[level] = {}
                if 'aggregation_type' in self.levels[level]:
                    agg_type = self.levels[level]['aggregation_type']
                    if agg_type in DEFAULT_GROUPING_INFO:
                        default = DEFAULT_GROUPING_INFO[agg_type]
                        for desc in self.compartments[level].values():
                            if 'compart_manager' not in desc:
                                desc['compart_manager'] = default['compart_manager']\
                                  if  'machine_name' in desc\
                                  else default['fallback_view']
                            if 'compart_class' not in desc:
                                desc['compart_class'] = default['compart_class']
            # print(self.compartments)

    def calculate_compound_params(self):
        """Inspect all edges of the health states graph and compute
        the actual probabilities associated to expressions.
        ### TODO: check that the ultimate symbols are declared properties.

        """
        for cond, expr in self.conditions.items():
            self.conditions[cond] = self.expand_expression(expr)


    def add_expression(self, expression):
        """Add the specified expression to the dictionary of known
        expressions.

        """
        if expression not in self.parameters\
           and expression not in self.statevars\
           and expression not in self._expressions:
            self._expressions[expression] = self.expand_expression(expression)
        return expression

    def expand_expression(self, expression):
        """Transform the specified expression so as to replace all
        parameters by actual values or state variables or
        attributes.

        """
        ### WARNING: expand_expressions should iterate over all
        ### expressions at the same time (halting when no change
        ### occurs) instead of iterating over each expression one by
        ### one
        result = sympify(expression, locals=self._namespace)
        expr = result
        symbs = {s: self.parameters[s.name]
                 for s in expr.free_symbols
                 if s.name in self.parameters}
        while symbs:
            result = expr.subs(symbs)
            expr = sympify(result, locals=self._namespace)
            symbs = {s: self.parameters[s.name]
                     for s in expr.free_symbols
                     if s.name in self.parameters}
        return result

    def build_actions(self):
        """Parse the description of the model and extract the actions
        that agents must have.

        Example of YAML specification:
        ------------------------------
        actions:
          say_hello:
            desc: action performed when entering the S state

        """
        if 'actions' in self._description:
            self.actions = StateVarDict(self._description['actions'])

    def compute_values(self):
        """Check parameters and calculated compound parameters, so as
        to make them computable. In the case of parameters, number
        values are left unchanged, but strings (representing an
        expression) are replaced by a function. Regarding calculated
        compound parameters, expressions corresponding to numbers are
        converted to float values, while other expressions are
        replaced by a function.

        """
        # collect 'true' values in the parameters
        for (param, expression) in self.parameters.items():
            value = self.expand_expression(expression)
            try:
                self._values[param] = float(value)
            except:
                self._values[param] = make_function(value,
                                                    modules=self.modules)
        for (param, expression) in self._expressions.items():
            value = self.expand_expression(expression)
            try:
                self._values[param] = float(value)
            except:
                self._values[param] = make_function(value,
                                                    modules=self.modules)
        for (cond, expression) in self.conditions.items():
            value = self.expand_expression(expression)
            if any([str(symb) in self.statevars
                    for symb in expression.free_symbols]):
                self._values[cond] = make_function(value,
                                                   dtype=bool,
                                                   modules=self.modules)
            else:
                self._values[cond] = bool(value)
        for (statename, state) in self.states.items():
            self._values[statename] = state

    def get_modifiable_parameters(self):
        """Return a dictionary containing all true parameters with their
        value.

        """
        true_params =  {p: self.get_value(p)
                        for p in self.parameters
                        if not callable(self.get_value(p))}
        true_params['delta_t'] = self.delta_t
        return true_params

    def describe_parameter(self, name):
        """Return the description of the parameter with the specified
        name.

        """
        return "{}:\n\t{}".format(pretty(sympify(name, locals=self._namespace)),
                                  self._description['parameters'][name]['desc'])

    def write_dot(self, parent_dir):
        """Write the graph of the each state machine in the
        specified directer name, according to the dot/graphviz format.

        """
        for name, statemachine in self.state_machines.items():
            name = self.model_name + '_' + name + '.dot'
            path = str(Path(parent_dir, name))
            statemachine.write_dot(path)

    def generate_skeleton(self, module):
        """Output a code skeleton to help writing specific pieces of code for
        the specified module to make the model work under Emulsion.

        """
        env = Environment(
            loader=PackageLoader('emulsion', 'templates'),
            extensions=['jinja2.ext.do']
        )
        template = env.get_template('specific_code.py')
        output = template.render(model=self, src_module=module)
        return output


#   _____ _        _       __  __            _     _
#  / ____| |      | |     |  \/  |          | |   (_)
# | (___ | |_ __ _| |_ ___| \  / | __ _  ___| |__  _ _ __   ___
#  \___ \| __/ _` | __/ _ \ |\/| |/ _` |/ __| '_ \| | '_ \ / _ \
#  ____) | || (_| | ||  __/ |  | | (_| | (__| | | | | | | |  __/
# |_____/ \__\__,_|\__\___|_|  |_|\__,_|\___|_| |_|_|_| |_|\___|



class StateMachine(object):
    """Class in charge of the description of biological or economical
    processes, modeled as Finite State Machines. The formalism
    implemented here is based on UML state machine diagrams, with
    adaptations to biology.

    """
    def __init__(self, machine_name, description, model):
        """Build a State Machine within the specified model, based on
        the specified description (dictionary).

        """
        self.model = model
        self.machine_name = machine_name
        self.parse(description)

    def _reset_all(self):
        self._statedesc = {}
        self._description = {}
        self.states = None
        self.graph = nx.MultiDiGraph()
        self.stateprops = StateVarDict()
        self.state_actions = {}
#        self.edge_actions = {}

    def parse(self, description):
        """Build the State Machine from the specified dictionary
        (expected to come from a YAML configuration file).

        """
        self._reset_all()
        # keep an exhaustive description
        self._description = description
        # build the enumeration of the states
        self.build_states()
        # build the graph based on the states and the transitions between them
        self.build_graph()
        # build actions associated with the state machine (states or edges)
        self.build_actions()

    def get_property(self, state_name, property_name):
        """Return the property associated to the specified state."""
        if state_name not in self.stateprops or\
           property_name not in self.stateprops[state_name]:
            return self.graph.node[state_name][property_name]\
                if property_name in self.graph.node[state_name]\
                   else None
        return self.stateprops[state_name][property_name]

    def build_states(self):
        """Parse the description of the state machine and extract the
        existing states. States are described as list items, endowed
        with key-value properties. It is recommended to define only
        one state per list item (especially to ensure that states are
        always stored in the same order in all executions).

        Example of YAML specification:
        ------------------------------
        states:
          - S:
              name: Susceptible
              desc: 'non-shedder cows without antibodies'
          - I+:
              name: Infectious plus
              desc: 'shedder cows with antibodies'
              fillcolor: orange
              on_stay:
                - increase: total_E
                  rate: Q1

        """
        states = []
        # retrieve information for each state
        for statedict in self._description['states']:
            for name, value in statedict.items():
                states.append(name)
                # provide a default fillcolor
                if 'fillcolor' not in value:
                    value['fillcolor'] = 'lightgray'
                # if properties are provided, add the corresponding
                # expression to the model
                if 'properties' in value:
                    self.stateprops[name] = {k: self.model.add_expression(v)
                                             for k, v in value['properties'].items()}
                # store other information
                self._statedesc[name] = value
                # and retrieve available actions if any
                for keyword in ['on_enter', 'on_stay', 'on_exit']:
                    if keyword in value:
                        self._add_state_actions(name, keyword, value[keyword])
        # build the enumeration of the states
        self.states = EmulsionEnum(self.machine_name.capitalize(),
                                   states, module=__name__)
        for state in self.states:
            if state.name in self.model.states:
                other_machine = self.model.states[state.name].__class__.__name__
                raise SemanticException(
                    'Conflict: State %s found in statemachines %s and %s' %
                    (state.name, other_machine, state.__class__.__name__))
            if state.name in self.model.parameters:
                raise SemanticException(
                    'Conflict: State %s of statemachines %s found in parameters'
                    % (state.name, state.__class__.__name__))
            self.model.states[state.name] = state
        self.model._values['_random_' + self.machine_name] = self.get_random_state

    def get_random_state(self, caller=None):
        """Return a random state for this state machine."""
        return np.random.choice(self.states)

    @property
    def state_colors(self):
        """Return a dictionary of state names associated with fill colors."""
        return {state.name: self._statedesc[state.name]['fillcolor']
                for state in self.states}


    def build_graph(self):
        """Parse the description of the state machine and extract the
        graph of the transitions between the states. Since a
        MultiDiGraph is used, each pair of nodes can be bound by
        several transitions if needed (beware the associated
        semantics).

        Example of YAML specification:
        ------------------------------
        transitions:
          - {from: S, to: I-, proba: p, cond: not_vaccinated}
          - {from: I-, to: S, proba: m}
          - {from: I-, to: I+m, proba: 'q*plp'}
          - {from: I-, to: I+, proba: 'q*(1-plp)'}

        """
        # add a node for each state
        for state in self.states:
            name = state.name
            self._statedesc[name]['tooltip'] = self.describe_state(name)
            self.graph.add_node(name, **self._statedesc[name])
        # build edges between states according to specified transitions
        if 'transitions' not in self._description:
            return
        for edge in self._description['transitions']:
            from_ = edge['from']
            to_ = edge['to']
            others = {k: v for (k, v) in edge.items()
                      if k != 'from' and k != 'to'}
            for kwd in EDGE_KEYWORDS:
                if kwd in others:
                    parm = pretty(sympify(others[kwd], locals=self.model._namespace))
                    label = '{}: {}'.format(kwd, parm)
            # label = ', '.join([pretty(sympify(x, locals=self.model._namespace))
            #                    for x in others.values()])
                    if str(parm) in self.model.parameters:
                        others['labeltooltip'] = self.model.describe_parameter(parm)
                    else:
                        others['labeltooltip'] = label
            # others['labeltooltip'] = ', '.join([self.model.describe_parameter(x)
            #                                     for x in others.values()
            #                                     if str(x) in self.model.parameters])
            # handle conditions if any on the edge
            cond, unless = None, False
            if 'cond' in others:
                cond = others['cond']
                others['truecond'] = others['cond']
            if 'unless' in others:
                cond = others['unless']
                unless = True
            if cond is not None:
                ### WARNING the operation below is not completely
                ### safe... it is done to replace conditions of the form
                ### 'x == y' by 'Eq(x, y)', but it is a simple
                ### substitution instead of parsing the syntax
                ### tree... Thus it is *highly* recommended to express
                ### conditions directly with Eq(x, y)
                if '==' in cond:
                    cond = 'Eq({})'.format(','.join(cond.split('==')))
                    # others['label'] = ', '.join(others.values()) if
            # duration specified for this state, handle it as an
            # additional condition
            if 'duration' in self._statedesc[from_]:
                duration_cond = make_TTL_condition(self.model, self.machine_name)
                if cond is None:
                    cond = duration_cond
                elif unless:
                    cond = 'And(Not({}),{})'.format(duration_cond, cond)
                else:
                    cond = 'And({},{})'.format(duration_cond, cond)
#                print(cond)
                others['cond'] = cond
            if cond is not None:
                self.model.conditions[cond] = sympify(cond,
                                                      locals=self.model._namespace)
            # handle 'when' clause if any on the edge
            self._parse_when(others)
            # handle 'duration', 'unless' and 'condition' clauses if
            # any on the edge
            self._parse_conditions_durations(from_, others)
            # parse actions on cross if any
            if 'on_cross' in others:
                l_actions = self._parse_action_list(others['on_cross'])
                others['actions'] = l_actions
            others['label'] = label
            self.graph.add_edge(from_, to_, **others)
            # register rate/proba/amount expressions in the model
            for keyword in EDGE_KEYWORDS:
                if keyword in others:
                    self.model.add_expression(others[keyword])

    def _parse_when(self, edge_desc):
        """Parse the edge description in search for a 'when'
        clause. This special condition is aimed at globally assessing
        a time period within the whole simulation.

        """
        if 'when' in edge_desc:
            expression = sympify(edge_desc['when'],
                                 locals=self.model._event_namespace)
            edge_desc['when'] = str(expression)
            self.model._values[str(expression)] = make_when_condition(
                expression, modules=self.model.modules)

    def _parse_conditions_durations(self, from_, edge_desc):
        """Parse the edge description in search for durations,
        escapement and conditions specifications. Durations
        ('duration' clause )are handled as an additional condition
        (agents entering the state are given a 'time to live' in the
        state, then they are not allowed to leave the state until
        their stay reaches that value). Escapements ('unless' clause)
        are also translated as a condition, allowing the agent to
        leave the state when the expression is true, only while the
        stay duration is below its nominal value.

        """
        cond, unless = None, False
        if 'cond' in edge_desc:
            cond = edge_desc['cond']
        if 'unless' in edge_desc:
            cond = edge_desc['unless']
            unless = True
        if cond is not None:
            ### WARNING the operation below is not completely
            ### safe... it is done to replace conditions of the form
            ### 'x == y' by 'Eq(x, y)', but it is a simple
            ### substitution instead of parsing the syntax
            ### tree... Thus it is *highly* recommended to express
            ### conditions directly with Eq(x, y)
            if '==' in cond:
                cond = 'Eq({})'.format(','.join(cond.split('==')))
                # edge_desc['label'] = ', '.join(edge_desc.values()) if
        # duration specified for this state, handle it as an
        # additional condition
        if 'duration' in self._statedesc[from_]:
            duration_cond = make_TTL_condition(self.model, self.machine_name)
            if cond is None:
                cond = duration_cond
            elif unless:
                cond = 'And(Not({}),{})'.format(duration_cond, cond)
            else:
                cond = 'And({},{})'.format(duration_cond, cond)
            edge_desc['cond'] = cond
        if cond is not None:
            self.model.conditions[cond] = sympify(cond, locals=self.model._namespace)

    def build_actions(self):
        """Parse the description of the state machine and extract the
        actions that agents running this state machine must have.

        Example of YAML specification:
        ------------------------------
        actions:
          say_hello:
            desc: action performed when entering the S state

        """
        for name, value in self._statedesc.items():
            for keyword in ['on_enter', 'on_stay', 'on_exit']:
                if keyword in value:
                    self._add_state_actions(name, keyword, value[keyword])
            if 'duration' in value:
                val = value['duration']
                self._add_state_duration_actions(name, val)

    def get_value(self, name):
        """Return the value associated with the specified name."""
        return self.model.get_value(name)


    def _add_state_duration_actions(self, name, value):
        """Add implicit actions to manage stay duration (time to live)
        in the state. The value can be either a parameter, a
        'statevar' or a distribution.

        """
        if name not in self.state_actions:
            self.state_actions[name] = {}
        lenter = self.state_actions[name]['on_enter']\
                   if 'on_enter' in self.state_actions[name] else []
        enter_action = partial(make_TTL_init_action,
                               machine_name=self.machine_name)
        enter_action.__name__ = 'init_TTL'
        enter_params = [self.model.add_expression(value)]
        init_action = AbstractAction.build_action('duration',
                                                  function=enter_action,
                                                  l_params=enter_params,
                                                  state_machine=self)
        lenter.insert(0, init_action)
        self.model.add_init_action(self.machine_name,
                                   self.states[name],
                                   init_action)
        lstay = self.state_actions[name]['on_stay']\
                  if 'on_stay' in self.state_actions[name] else []
        stay_action = partial(make_TTL_increase_action,
                              machine_name=self.machine_name)
        stay_action.__name__ = '+_time_spent'
        lstay.insert(0, AbstractAction.build_action('duration',
                                                    function=stay_action,
                                                    state_machine=self))
        # lexit = self.state_actions[name]['on_exit']\
        #           if 'on_exit' in self.state_actions[name] else []
        # exit_action = partial(make_TTL_delete_action,
        #                       machine_name = self.machine_name,
        #                       state_name = name)
        # exit_action.__name__ = 'del_TTL'
        # lexit.insert(0, AbstractAction.build_action('duration',
        #                                             function=exit_action))
        self.state_actions[name]['on_enter'] = lenter
        self.state_actions[name]['on_stay'] = lstay

    def _add_state_actions(self, name, event, actions):
        """Add the specified actions for the state with the given
        name, associated with the event (e.g. 'on_stay', 'on_enter',
        'on_exit'). Expressions contained in the parameters lists or
        dicts are automatically expanded.

        """
        if name not in self.state_actions:
            self.state_actions[name] = {}
        l_actions = self._parse_action_list(actions)
        self.state_actions[name][event] = l_actions

    def _parse_action_list(self, actions):
        """Parse the list of actions associated with a state."""
        l_actions = []
        for d_action in actions:
            if 'action' in d_action:
                action = d_action['action']
                l_params = [self.model.add_expression(expr)
                            for expr in d_action['l_params']]\
                                if 'l_params' in d_action\
                                else []
                d_params = {key: self.model.add_expression(expr)
                            for key, expr in d_action['d_params'].items()}\
                                if 'd_params' in d_action\
                                else {}
                l_actions.append(
                    AbstractAction.build_action('action',
                                                method=action,
                                                l_params=l_params,
                                                d_params=d_params,
                                                state_machine=self))
            else:
                understood = False
                for keyword in ['increase', 'decrease',
                                'increase_stoch', 'decrease_stoch']:
                    if keyword in d_action:
                        # assume that increase statevar with rate
                        l_actions.append(
                            AbstractAction.build_action(
                                keyword,
                                statevar_name=d_action[keyword],
                                parameter=self.model.add_expression(d_action['rate']),
                                delta_t=self.model.delta_t,
                                state_machine=self
                            )
                        )
                        understood = True
                if not understood:
                    print('ERROR !!!!') # but there is certainly a fatal error !
        return l_actions




    #----------------------------------------------------------------
    # Output facilities

    def describe_state(self, name):
        """Return the description of the state with the specified
        name.

        """
        desc = self._statedesc[name]
        return "{} ({}):\n\t{}".format(name, desc['name'], desc['desc'])

    def write_dot(self, filename, view_actions=True):
        """Write the graph of the current state machine in the
        specified filename, according to the dot/graphviz format.

        """

        output = '''digraph {
        \trankdir=LR;
        \tnode[fontsize=16, fontname=Arial, shape=box, style="filled,rounded"];
        \tedge[minlen=1.5, penwidth=1.5];

        '''
        for state in self.states:
            name = state.name
            name_lab = name
            if 'duration' in self._statedesc[name]:
                name_lab += '&nbsp;&#9719;'
            actions = 'shape="Mrecord", label="{}", '.format(name_lab)
            if view_actions:
                onenter = ACTION_SYMBOL+'|'\
                          if 'on_enter' in self._statedesc[name] else ''
                onstay = '|'+ACTION_SYMBOL\
                         if 'on_stay' in self._statedesc[name] else ''
                onexit = '|'+ACTION_SYMBOL\
                         if 'on_exit' in self._statedesc[name] else ''
                if onenter or onstay or onexit:
                    actions = 'shape="Mrecord", label="{%s{\ %s\ %s}%s}", ' % (
                        onenter, name_lab, onstay, onexit)
            output += '\t"{}" [{}tooltip="{}", fillcolor={}] ;\n'.format(
                name, actions,
                self._statedesc[name]['tooltip'],
                # '\n\tON ENTER: {}'.format(self.state_actions[name]['on_enter'])\
                # if onenter else '' +\
                # '\n\tON STAY: {}'.format(self.state_actions[name]['on_stay'])\
                # if onstay else '' +\
                # '\n\tON EXIT: {}'.format(self.state_actions[name]['on_exit'])\
                # if onexit else '',
                self._statedesc[name]['fillcolor'])
        for from_, to_ in SortedSet(self.graph.edges()):
            for desc in self.graph.edge[from_][to_].values():
                edgetip = ''
                tail = 'none'
                if 'when' in desc:
                    tail += WHEN_SYMBOL
                    edgetip += 'WHEN: {}'.format(desc['when'])
                if 'unless' in desc:
                    tail += UNLESS_SYMBOL
                    edgetip += 'UNLESS: {}'.format(desc['unless'])
                if 'truecond' in desc:
                    tail += COND_SYMBOL
                    edgetip += 'COND: {}'.format(desc['truecond'])
                head = 'normalnone'
                if 'on_cross' in desc:
                    head += CROSS_SYMBOL
                    # edgetip += 'ON CROSS: {}\\n'.format(desc['on_cross'])
                output += ('\t"{}" -> "{}" [label="{}", labeltooltip="{}", '
                           'arrowtail="{}", arrowhead="{}", dir=both, '
                           'edgetooltip="{}", minlen=3];\n').format(
                               from_, to_, desc['label'], desc['labeltooltip'],
                               tail, head, edgetip)
        output += '}'
        with open(filename, 'w') as f:
            f.write(output)
