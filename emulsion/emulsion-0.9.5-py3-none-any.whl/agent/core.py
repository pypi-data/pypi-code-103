"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for abstract agent management.

Part of this code is adapted from the PADAWAN framework (S. Picault,
Univ. Lille).

"""

import abc

from   functools            import total_ordering
from   sortedcontainers     import SortedSet

from   emulsion.tools.state import StateVarDict
from   emulsion.model       import EDGE_KEYWORDS


#  __  __      _                                 _
# |  \/  |    | |          /\                   | |
# | \  / | ___| |_ __ _   /  \   __ _  ___ _ __ | |_
# | |\/| |/ _ \ __/ _` | / /\ \ / _` |/ _ \ '_ \| __|
# | |  | |  __/ || (_| |/ ____ \ (_| |  __/ | | | |_
# |_|  |_|\___|\__\__,_/_/    \_\__, |\___|_| |_|\__|
#                                __/ |
#                               |___/

################################################################
# Metaclass for all agents
################################################################
class MetaAgent(abc.ABCMeta):
    """The Metaclass definition for all agents. When created, agents
    are stored in a class-specific dictionaries of agents. They are
    given an ID value (unique value within each class) and can be
    assigned to several agents families (by default, each agent is
    assigned to its own class).

    """
    @classmethod
    def __prepare__(mcs, name, bases, **kwds):
        families = SortedSet()
        families.add(name)
        attrs = {'agcount': 0,               # number of instances created
                 'agdict': {},               # dict of instances (ID -> agent)
                 'families': families}        # families where the class belongs
        # state NB: no need to keep information on passivity since it
        # depends on the families of the agent
        return attrs

    def __new__(mcs, name, bases, attrs, **_):
        attrs = dict(attrs)
        result = super(MetaAgent, mcs).__new__(mcs, name, bases, dict(attrs))
        result.members = tuple(attrs)
        return result



#           _         _                  _                            _
#     /\   | |       | |                | |     /\                   | |
#    /  \  | |__  ___| |_ _ __ __ _  ___| |_   /  \   __ _  ___ _ __ | |_
#   / /\ \ | '_ \/ __| __| '__/ _` |/ __| __| / /\ \ / _` |/ _ \ '_ \| __|
#  / ____ \| |_) \__ \ |_| | | (_| | (__| |_ / ____ \ (_| |  __/ | | | |_
# /_/    \_\_.__/|___/\__|_|  \__,_|\___|\__/_/    \_\__, |\___|_| |_|\__|
#                                                     __/ |
#                                                    |___/

################################################################
# superclass of all agents

@total_ordering
class AbstractAgent(object, metaclass=MetaAgent):
    """The Superclass for any multi-level agent. Due to the MetaAgent
    metaclass, all agents of the same class can be accessed through
    their ID, using the agdict class attribute. Agents are endowed
    with an automatic ID and possibly with a label. Agents also belong
    to families which can be chosen arbitrarily. By default, each
    agent belongs to the family named afer its own class.

    An agent is situated in one or more environments. Besides, agents
    can encapsulate environments where other agents can be
    situated. Agents are also endowed with State Variables, which can
    represent either properties of their own, or properties perceived
    from their inner environment or from the environments where they
    are situated.

    """
    @classmethod
    def from_dict(cls, dct):
        """Instantiate an agent using the specified dictionary."""
#        print('Instantiation of', cls.__name__, 'from dict:', dct)
        return cls(**dct)

    def _register_instance(self, key=None):
        """Register the instance in the instance dictionary of the
        class. If no key is specified, the agent ID is used.

        """
        if key is not None:
            self._agkey = key
        self.__class__.agdict[self._agkey] = self


    def __init__(self, envt=None, content=None, **others):
        """Instantiate an agent. The instance is automatically added
        to the agentset of its own class. An arbitrary label can be
        specified to give the agent a label (otherwise a label is
        automatically computed using the class name and the agent
        ID).

        """
        super().__init__()
        self.__class__.agcount = self.__class__.agcount + 1
        # agent id
        self.agid = self.__class__.agcount
        # key used to register agents (agent ID by default)
        self._agkey = self.agid
        # environments in which the agent is situated
        self._envt = envt
        # environment encapsulated by the agent
        self._content = content
        # simulation where the agent belongs
        self.simulation = None
        # model used to define simulation behaviors
        self.model = None
        # "true" state variables of the agent
        self.statevars = StateVarDict(**others)
        # refresh cache of class members
        self._reset_mbr_cache()

    def _reset_mbr_cache(self):
        # Build a cache of regular class members. This cache is used
        # to make the 'get_information' method as efficient as
        # possible, thus this operations should be performed at the
        # end of instance creation (after other attributes have been
        # initialized)
        self._mbr_cache = set(name for name in dir(self)
                              if not name.startswith('_'))


    def __hash__(self):
        """Return a hashcode for the agent. The hashcode is actually
        the hashcode of the internal id of the object.

        """
        return hash(id(self))


    def __str__(self):
        return '{} #{}'.format(self.__class__.__name__, self.agid)

    __repr__ = __str__

    def __eq__(self, other):
        """Two agents are considered equal if they belong to the same
        class and have the same agent ID. (This is consistent with the
        fact that all instances are stored by each class using the
        agent ID as key.)

        """
        return self.__class__ == other.__class__\
            and self.agid == other.agid

    def __lt__(self, other):
        """Return an order for sorting agents. In this simple method
        the order is defined by sorting classes, then agents IDs.

        """
        return self.agid < other.agid if self.__class__ == other.__class__\
            else self.__class__.__name__ < other.__class__.__name__

    def die(self):
        """Operation performed when the agent is removed from the
        simulation. Recursively destroy agents contained in the
        current agent if any, and remove the current agent from the
        agdict attribute of its class.

        """
        if self._content:
            for agent in self._content:
                agent.die()
        if self._agkey in self.__class__.agdict:
            del self.__class__.agdict[self._agkey]

    def get_information(self, name):
        """Return the value corresponding to the specified name in the
        agent. This value can be stored either as an attribute or a
        property-like descriptor (and thus accessed through an
        attribute-like syntax), or as a State Variable using a
        StateVarDict attribute named ``statevars``.

        Example:
        class Cow(Unit):
            ...
            @property
            def age(self):
                return self._age

        c = Cow()
        c.get_information('age')
        # -> access through property 'age'
        c.get_information('health_state')
        # -> access through statevar 'health_state' (present in any Unit),
        # unless a 'health_state' attribute or property is explicitly
        # redefined to override the state variable

        """
        # return getattr(self, name) if hasattr(self, name)\
        #     else getattr(self.statevars, name)
        # REWRITTEN for efficiency improvement
        return getattr(self, name)\
            if name in self._mbr_cache\
            else getattr(self.statevars, name)


    def set_information(self, name, value):
        """Set the specified value for the statevar/attribute."""
        # if hasattr(self, name):
        #     setattr(self, name, value)
        # else:
        #     setattr(self.statevars, name, value)
        # REWRITTEN for efficiency improvement
        if name in self._mbr_cache:
            setattr(self, name, value)
        else:
            setattr(self.statevars, name, value)

    def init_time_to_live(self, machine_name, value):
        """Initialize the time this agent is expected to stay in the
        current state of the specified state machine. If an offset is
        defined for this state machine, it is added to the specified
        value, then reset to 0.

        """
        key = '_time_spent_{}'.format(machine_name)
        keymax = '_time_to_live_{}'.format(machine_name)
        keyoff = '_time_offset_{}'.format(machine_name)
        if keyoff not in self.statevars:
            self.statevars[keyoff] = 0
        self.statevars[key] = 0
        # compute the time to live w.r.t. the time step duration
        # (deltat_t)
        self.statevars[keymax] = (value + self.statevars[keyoff]) // self.model.delta_t
        self.statevars[keyoff] = 0

    def increase_time_spent(self, machine_name):
        """Decrease the time this agent is expected to stay in the
        specified state of the specified state machine.

        """
        self.statevars['_time_spent_{}'.format(machine_name)] += 1

    def set_time_to_live_offset(self, machine_name, value):
        """Specify an additional value to the time this agent is
        expected to stay in the next state of the specified state
        machine.

        """
        self.statevars['_time_offset_{}'.format(machine_name)] = value


#  ______                 _     _                                      _
# |  ____|               | |   (_)               /\                   | |
# | |__   _ __ ___  _   _| |___ _  ___  _ __    /  \   __ _  ___ _ __ | |_
# |  __| | '_ ` _ \| | | | / __| |/ _ \| '_ \  / /\ \ / _` |/ _ \ '_ \| __|
# | |____| | | | | | |_| | \__ \ | (_) | | | |/ ____ \ (_| |  __/ | | | |_
# |______|_| |_| |_|\__,_|_|___/_|\___/|_| |_/_/    \_\__, |\___|_| |_|\__|
#                                                      __/ |
#                                                     |___/

class EmulsionAgent(AbstractAgent):
    """The EmulsionAgent is the base class for multi-level
    epidemiologic agents. An EmulsionAgent can represent any entity
    involved in the epidemiologic model (individual, compartment,
    herd, [meta]population, etc.). Thus it is endowed with a health
    state.

    Each agent contains a exchange box (in & out) which is composed by
    a list of messages. A message is generally a dictionary of
    Source/Destination (In/Out) and content of exchange with
    Source/Destination agent.

    """
    def __init__(self, health_state=None, name=None, host=None, **others):
        """Initialize the unit with a health state and a name."""
        super().__init__(**others)
        self.statevars.health_state = health_state
        self._name = name
        self._host = host
        if 'step' not in self.statevars:
            self.statevars.step = 0
        # exchange inbox/outbox
        self._inbox = []
        self._outbox = []


    @property
    def name(self):
        """Return the name of the unit. If no name was provided during
        instantiation, a combination of the class name and the health
        state is returned.

        """
        return self._name if self._name is not None\
            else '{}_{}'.format(self.__class__.__name__,
                                self.statevars.health_state)

    def __repr__(self):
        return '{} ({})'.format(self.name, super().__str__())


    def evolve(self, machine=None):
        """This method is aimed at defining what has systematically to
        be done in the unit at each time step (e.g. age change...). It
        has to be overriden if needed in subclasses.

        """
        self.statevars.step += 1

    def get_host(self, key=None):
        """Return the host of the current unit."""
        return self._host

    @abc.abstractmethod
    def get_content(self):
        """Return either the population (number) of the current unit,
        or the list of agents contained in the current unit. The
        output is a dictionary with a key = 'population' or 'agents'
        and the corresponding value.

        """
        pass

    def do_state_actions(self, event, state_machine, state_name,
                         population=None, agents=None, **_):
        """Perform the actions associated to the current state. If the
        unit is a ViewAgent, actions are actually performed by each
        unit of the specified agents list, in turn. Otherwise, the
        actions are performed according to the population, which is
        expected to be a number.

        """
        # if actions are actually associated to the current state of
        # the state machine...
           # ... and to the 'event' (enter/exit/stay)
        if state_name in state_machine.state_actions\
           and event in state_machine.state_actions[state_name]:
            # retrieve the list of actions
            l_actions = state_machine.state_actions[state_name][event]
            # ask the current unit to perform the actions with the
            # specified population
            for action in l_actions:
                action.execute_action(self, population=population, agents=agents)

    def do_edge_actions(self, actions=None, population=None, agents=None):
        """Perform the actions associated to a transition between
        states. If the unit is a ViewCompartment, actions are actually
        performed by each unit of the specified agents list, in
        turn. Otherwise, the actions are performed according to the
        population, which is expected to be a number.

        """
        # # if actions are actually associated to the current edge...
        #    # ... and to the 'event' (cross)
        # if from_ in state_machine.edge_actions\
        #    and to_ in state_machine.edge_actions[from_]\
        #    and event in state_machine.edge_actions[from_][to_]:
        #     # retrieve the list of actions
        #     l_actions = state_machine.edge_actions[from_][to_][event]
        #     # ask the current unit to perform the actions with the
        #     # specified population
        for action in actions:
#            print(action)
            action.execute_action(self, population=population, agents=agents)


    def next_states_from(self, initial_state, state_machine):
        """Return a list of tuples composed of:

        - each of the possible states reachable from the specified
        initial state (some depending on a condition)

        - the transition rate, probability or amount to each state in
        the specified state_machine (possible clauses: 'rate',
        'proba', 'amount', 'amoun-all-but' with the actual value)

        - a dictionary indicating who can cross the edge, depending on
        conditions

        - the list of actions to perform when crossing the edge (if
        any).

        The conditions, rates and probabilities may depend on the state
        variables or properties of the current unit.

        """
        result = []
        # remove unfulfilled 'when' clauses if any
        for (state, props) in state_machine.graph.edges_from(initial_state):
            if 'when' in props:
                when = state_machine.get_value(props['when'])
                fulfilled = when(self) if callable(when) else when
                if not fulfilled:
                    continue
            cond_result = self.get_content()
            # if any condition, evaluate it
            if 'cond' in props:
                cond = state_machine.get_value(props['cond'])
                # compute the content dictionary (key='population'
                # or 'agents') which fulfils the condition
                cond_result = self.evaluate_condition(cond)
            # only edges with condition fulfilled are taken into account
            if cond_result:
                flux = None
                for keyword in EDGE_KEYWORDS:
                    if keyword in props:
                        flux = keyword
                        break
                value = state_machine.get_value(props[flux])
                actions = props['actions'] if 'actions' in props else []
                if callable(value):
                    value = value(self)
                if value > 0 or flux == 'amount-all-but':
                    result.append((state, flux, value, cond_result, actions))
        return result

    def evaluate_condition(self, condition):
        """Return the content (dictionary with key = 'population' or
        'agents') if the condition is fulfilled, {} otherwise.

        """
        if callable(condition):
            condition = condition(self)
        return self.get_content() if condition else {}

    def evaluate_event(self, name):
        """Evaluate if the specified event name is fulfilled, using a
        calendar. The calendar is determined dynamically according to
        the name of the event.

        """
        # print(self, 'evaluating event', name, "at", self.statevars.step)
        return self.model.get_calendar_for_event(name)[name](self.statevars.step)

    def get_outbox(self):
        """Return the outbox"""
        return self._outbox

    def add_outbox(self, message):
        """Add a message in the outbox"""
        return self._outbox.append(message)

    def reset_outbox(self):
        """Reset outbox"""
        self._outbox = []

    def add_inbox(self, messages=[]):
        """Add the specified list of messges in the inbox"""
        self._inbox += messages

    def clean_inbox(self):
        """Remove non sticky messages in the inbox"""
        self._inbox = [message for message in self._inbox if message.get('sticky')]

    def checkout_inbox(self):
        """Pick up agent's inbox content

        """
        for message in self._inbox:
            for name, value in message.items():
                self.set_information(name, value)

#   _____                                               _
#  / ____|                        /\                   | |
# | |  __ _ __ ___  _   _ _ __   /  \   __ _  ___ _ __ | |_
# | | |_ | '__/ _ \| | | | '_ \ / /\ \ / _` |/ _ \ '_ \| __|
# | |__| | | | (_) | |_| | |_) / ____ \ (_| |  __/ | | | |_
#  \_____|_|  \___/ \__,_| .__/_/    \_\__, |\___|_| |_|\__|
#                        | |            __/ |
#                        |_|           |___/

class GroupAgent(EmulsionAgent):
    """An GroupAgent is a Unit which is aimed at representing
    a group of units. The underlying level may be either explicitly
    represented (using a ViewCompartment) or aggregated (using an
    Compartment). Each compartment is associated with keys,
    i.e. a tuple of state variables (possibly empty) which play a
    crucial role in this compartment.

    """
    def __init__(self, keys=(), **others):
        super().__init__(**others)
        self.keys = keys


    @abc.abstractmethod
    def add(self, population):
        """Add the specified population to the current compartment."""
        pass

    @abc.abstractmethod
    def remove(self, population):
        """Remove the specified population from the current
        compartment.

        """
        pass

    @abc.abstractmethod
    def _base_move(self, other_unit, **others):
        pass

    def _before_move(self, state_machine, old_state, new_state, **others):
        # execute actions when exiting current state (if any)
        self.do_state_actions('on_exit',
                              state_machine,
                              old_state,
                              **others)
        # execute actions when crossing edge (if any)
        self.do_edge_actions(**others)
        # update states of atom units
        if 'agents' in others:
            for unit in others['agents']:
                unit.statevars[state_machine.machine_name] =\
                  state_machine.states[new_state]

    def _after_move(self, state_machine, new_state, **others):
        # execute actions when entering new state (if any)
        self.do_state_actions('on_enter',
                              state_machine,
                              new_state,
                              **others)


    def move_to(self, other_unit, state_machine=None, **others):
        """Move the specified population from the current population
        of the compartment to the other unit. If a state machine is
        provided, executes the corresponding actions when
        entering/exiting nodes and crossing edges if needed.

        """
        if state_machine:
            #old_state = self.get_information(state_machine.machine_name).name
            old_state = self.statevars[state_machine.machine_name]
            new_state = other_unit.statevars[state_machine.machine_name].name
            if old_state is not None:
                self._before_move(state_machine, old_state.name,
                                  new_state, **others)
        # move population from current compartment to other unit
        self._base_move(other_unit, **others)
        if state_machine:
            other_unit._after_move(state_machine, new_state, **others)



#                                           _   _
#     /\                                   | | (_)
#    /  \   __ _  __ _ _ __ ___  __ _  __ _| |_ _  ___  _ __
#   / /\ \ / _` |/ _` | '__/ _ \/ _` |/ _` | __| |/ _ \| '_ \
#  / ____ \ (_| | (_| | | |  __/ (_| | (_| | |_| | (_) | | | |
# /_/    \_\__, |\__, |_|  \___|\__, |\__,_|\__|_|\___/|_| |_|
#           __/ | __/ |          __/ |
#          |___/ |___/          |___/


class Aggregation(GroupAgent):
    """An Aggregation is aimed at grouping units from the
    underlying level. Thus, aggregate information such as the total
    number of units in the compartment (population) is calculated from
    the actual content of the compartment. The evolution of a
    ViewCompartment, by default, consists in making the units
    contained in the compartment evolve themselves, unless
    `recursive=False` is specified during instantiation.

    """
    def __init__(self, recursive=True, **others):
        super().__init__(**others)
        self._content = None
        self.recursive = recursive

    @property
    def population(self):
        """Return the total population of the compartment. It is
        calculated either using a true 'population' statevar if any,
        or as the sum of the population of each unit contained in the
        compartment.

        """
        return self.statevars.population if 'population' in self.statevars\
            else sum([unit.get_information('population')
                      for unit in self])

    def add(self, population):
        """Add the specified population to the current compartment."""
        for unit in population:
            unit.add_host(self)

    def remove(self, population):
        """Remove the specified population from the current
        compartment.

        """
#        print([u.agid for u in population])
        for unit in population:
            unit.remove_host(self, keys=self.keys)


    def _base_move(self, other_unit, agents=[], **others):
        self.remove(agents)
        other_unit.add(agents)


    @abc.abstractmethod
    def __iter__(self):
        pass

    # TODO: shuffle content first
    def evolve(self, machine=None):
        """Ask each unit in the current compartment to make its
        content evolve according to its own capabilities. A specific
        state machine can be specified if needed.

        """
        super().evolve(machine=machine)
        if self.recursive:
            for unit in self:
                unit.evolve(machine=machine)
