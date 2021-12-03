"""Module for describing and controlling actions which are configured for execution. """
import re
import datetime
import logging
import threading
import time
import warnings
from functools import wraps
from typing import List, Union, Callable, Tuple, Optional

from .basic import Action, ActionList
from ..mixin import Status, Configuration, InstanceRegistry, DumpableList, make_iterable_serializable, make_mapping_serializable, serializable_cast


logger = logging.getLogger(__name__)


class ConfiguredAction(InstanceRegistry, Configuration, Status):
    UUID_PREFIX = 'ca-'

    def __init__(self,
                 action: Union[Callable, Action, str],
                 *args,
                 configuration_name: str = None,
                 next_action: Union[str, 'ConfiguredAction'] = None,
                 condition: Union[Tuple[object, str], Callable] = None,
                 aliases: List[str] = None,
                 use_unique_action: bool = False,
                 parent_identifier_override: str = None,
                 **kwargs,
                 ):
        """
        An action that is configured for execution. Arguments and Keyword arguments may be specified and will
        be handed to the action on execution unless overridden by the user. (Using kwargs over args is strongly
        recommended.)

        :param action: action to perform (callable)
        :param args: arguments for the action
        :param configuration_name: optional name for the configuration (for key retrieval). This can be a useful way of
            differentiating specific configurations of an action if there are multiple configurations for that action.
        :param next_action: optional next action for sequence building
        :param condition: a condition evaulation which must be True for the execution to proceed. This may either be
            a callable which can be evaluated, or a pointer to some attribute of an object which will be checked
            at runtime for a bool.
        :param kwargs: keyword arguments for the action
        :param aliases: list of aliases which refer to the configured action instance
        :param use_unique_action: whether to register action as a unique action (usually in cases where actions have
            stateful instance dependencies and there may be more than one action of the same name registered).
        :param parent_identifier_override: Optional override for the parent identifier used for unique configured action
            generation.
        """
        # todo ability to retrieve the executions of a given configured action
        InstanceRegistry.__init__(self)
        self._action: Action = None
        self._config_name: str = None
        self._next_action = None
        self._use_unique_action = True if parent_identifier_override is not None else use_unique_action
        self.parent_identifier_override: Optional[str] = parent_identifier_override
        # list of aliases for the configuration
        if aliases is None:
            aliases = []  # prevent mutation
        self.aliases: List[str] = aliases
        # register action and store attribute
        self.action = action
        self.condition: Union[Tuple[object, str], Callable, None] = condition
        Configuration.__init__(
            self,
            *self.action.default_args,
            **self.action.default_kwargs,
        )
        Status.__init__(self)
        self.update_args(*args)
        self.update_kwargs(**kwargs)
        # generate name if not specified
        if configuration_name is None:
            configuration_name = self._generate_unique_name(self.action)
        else:
            # ensure configuration name is unique
            configuration_name = self._generate_unique_name(configuration_name)
        self.name = configuration_name
        if next_action is not None:
            self.next_action = next_action

    def __str__(self):
        return f'{self.__class__.__name__} {self.name}'

    def __repr__(self):
        return self.__str__()

    def __call__(self, *args, **kwargs):
        return self.action(*args, **kwargs)

    def __copy__(self):
        return self.__class__(
            self.action,
            self.next_action,
            self.args,
            self.name,
            self.kwargs,
        )

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    @property
    def action(self) -> Action:
        """the action which is configured for execution"""
        return self._action

    @action.setter
    def action(self, value: Union[Callable, Action, str]):
        if value is not None:
            # retrieve appropriate parent identifier
            if self._use_unique_action is True:
                if self.parent_identifier_override is not None:
                    parent_id = self.parent_identifier_override
                else:
                    parent_id = self._uuid
            else:
                parent_id = None
            self._action = Action.register_action(
                value,
                parent_identifier=parent_id,
            )

    @property
    def name(self) -> str:
        """name for the configuration (useful for identifying a specific configuration of an action)"""
        return self._config_name

    @name.setter
    def name(self, value: str):
        if value == self.name:
            return
        if value is not None:
            # check if already defined
            if value in self.get_configuration_names():
                raise NameError(f'The configuration name "{value}" is already used, please choose a '
                                f'unique name for the configuration. ')
            self._config_name = value

    @property
    def next_action(self) -> 'ConfiguredAction':
        """The next action in the sequence (for contextual action linking)"""
        return self._next_action

    @next_action.setter
    def next_action(self,
                    value: Union[str, 'ConfiguredAction'],
                    ):
        if value is None:
            self._next_action = None
            return
        # retrieve instance by key if not defined
        if isinstance(value, ConfiguredAction) is False:
            value = self.class_instance_by_id(value)
        self._next_action = value

    @next_action.deleter
    def next_action(self):
        self._next_action = None

    @property
    def previous_actions(self) -> List['ConfiguredAction']:
        """returns a list of configured actions which have this instance as a next step"""
        return [
            config
            for config in self.class_registry
            if config.next_action is self
        ]

    @classmethod
    def _generate_unique_name(cls, name: Union[Action, str]) -> str:
        """
        Generates a unique numbered name based on an Action instance. The resulting name will be unique in the
        registry.

        :param name: name to base off of
        :return: generated name
        """
        if isinstance(name, Action):
            name = name.name
        elif re.match('.+[_\s]\d+', name) is not None:
            name = re.match('(?P<base_name>.+)[_\s]\d+', name).group('base_name')
        i = 2
        current_names = cls.get_configuration_names()
        if name not in current_names:
            return name
        while True:
            target_name = f'{name}_{i}'
            if f'{name}_{i}' not in current_names:
                return target_name
            i += 1

    def add_alias(self, alias: str):
        """adds a configuration name alias to the instance"""
        alias = alias.lower()  # enforces lower case
        if alias not in self.aliases:
            # if not already defined, add alias
            self.aliases.append(alias)

    def remove_alias(self, alias: str):
        """removes an alias from the instance"""
        alias = alias.lower()
        if alias in self.aliases:
            self.aliases.remove(alias)

    def evaluate_condition(self) -> bool:
        """Evaluates the condition (if specified) for the configuration"""
        if self.condition is None:
            return True
        elif type(self.condition) is tuple:
            obj, attr = self.condition
            return getattr(obj, attr)
        else:
            return self.condition()

    @staticmethod
    def _match_instance_key(inst: "ConfiguredAction", identifier: str) -> bool:
        """
        Checks the provided identifier key against the instance provided, returning True if matching and False if not

        :param inst: InstanceRegistry instance
        :param identifier: string identifier
        :return: match
        """
        if inst._uuid == identifier:
            return True
        elif inst.uuid == identifier:
            return True
        elif inst.name == identifier:  # match configuration name
            return True
        elif type(identifier) is str and identifier.lower() in inst.aliases:
            return True  # match alias
        return False

    def match_name_and_parent(self,
                              name: Union[Callable, str, 'ConfiguredAction'],
                              parent_identifier: str = None,
                              ) -> bool:
        """
        Compares the provided name and parent identifier against the Configured Action instance (in effect an
        equality check)

        :param name: name to use
        :param parent_identifier: parent identifier (optional)
        :return: whether the name and parent identifier match
        """
        name_match = False

        if isinstance(name, ConfiguredAction) and name is self:
            return True
        if callable(name) is True and name == self.action.action:  # todo figure out why "is" doesn't work here
            name_match = True
        elif type(name) is str and self.action.name == name:
            name_match = True
        elif self.name == name:
            name_match = True
        # if there is a name match and the parent identifier was specified, ensure match
        if name_match and parent_identifier is not None:
            if self.action.parent_identifier == parent_identifier:
                return True
            return False
        elif name_match and self.parent_identifier_override is not None:
            return False  # parent identifier did not match
        return name_match

    @classmethod
    def get_configuration_by_name(cls, configuration_name: str) -> 'ConfiguredAction':
        """
        Retrieves a ConfiguredAction by name

        :param configuration_name: name identifier of configuration
        :return: ConfiguredAction
        """
        warnings.warn(
            'the get_configuration_by_name method has been deprecated, use class_instance_by_id',
            DeprecationWarning,
            stacklevel=2,
        )
        return cls.class_instance_by_id(configuration_name)

    @classmethod
    def get_configuration_names(cls) -> List[str]:
        """
        Retrieves the names of all configurations.

        Warning: return will be sorted, but order does not correspond to order in registry (indexing based on this
        return is not recommended).
        """
        return sorted([config.name for config in cls.class_registry if config.name is not None])

    @classmethod
    def get_configurations_of_action(cls, action: Union[str, Action]) -> List['ConfiguredAction']:
        """
        Retrieves all of the Configurations associated with the specified action

        :param action: action to reference
        :return: list of ConfiguredAction instances
        """
        if isinstance(action, Action) is False:
            action = Action.register_action(action)
        return [
            config
            for config in cls.class_registry
            if config.action is action
        ]

    @classmethod
    def remove_configuration_from_registry(cls,
                                           configuration: Union[str, 'ConfiguredAction'],
                                           parent_identifier: str = None,
                                           ):
        """
        Removes the specified configuration from the configuration registry

        :param configuration: name or instance of the configuration
        :param parent_identifier: optional parent identifier
        """
        for inst in cls.class_registry:
            if inst.match_name_and_parent(name=configuration, parent_identifier=parent_identifier):
                cls.class_registry.remove(inst)
                del inst  # removes the instance

    @classmethod
    def ensure_configuration(cls,
                             configuration: Union[str, Callable, Action, 'ConfiguredAction'],
                             ) -> 'ConfiguredAction':
        """
        Ensures that the provided configuration is a class instance, instantiating or converting as necessary.

        :param configuration: configuration instance, name, or key
        :raises ValueError: if a string is provided and an action is not registered
        :return: associated ConfiguredAction
        """
        # if already a configuration, return
        if isinstance(configuration, ConfiguredAction):
            return configuration
        # if a string key, retrieve
        elif type(configuration) is str:
            try:
                # try to retrieve configuration by name
                return ConfiguredAction.class_instance_by_id(configuration)
            except NameError:
                try:
                    action = Action.register_action(configuration)
                except TypeError:
                    raise ValueError(f'the action "{configuration}" is not registered')
                # attempt to create a configuration from a registered action
                return ConfiguredAction(action)
        # if an action, create
        elif isinstance(configuration, Action):
            # if an action was provided, create configuration
            return ConfiguredAction(configuration)
        # if a callable, create an action
        elif callable(configuration):
            try:  # attempt to return an existing configuration of the function
                return ConfiguredAction.class_instance_by_id(configuration.__name__)
            except NameError:  # if undefined, register action and create configuration
                # if a callable was provided, register
                return ConfiguredAction(Action.register_action(configuration))
        raise ValueError(f'the value {configuration} could not be interpreted as a configuration')

    def duplicate_configuration(self, new_name: str = None) -> 'ConfiguredAction':
        """
        Duplicates a configuration with the provided name.

        :param new_name: new name for the generated ConfiguredAction instance
        :return: duplicated configuration
        """
        if new_name is None:
            new_name = self._generate_unique_name(self.action)
        return self.__class__(
            action=self.action,
            configuration_name=new_name,
            next_action=self.next_action,
            **self.kwargs,
        )

    def get_tracked_from_config(self, **kwargs) -> "TrackedAction":
        """
        Generates a tracked instance from the configured action

        :param kwargs: additional kwargs that differ from the instance configuration
        :return: TrackedAction (or subclass) instance.
        """
        return TrackedAction(
            configuration=self,
            **kwargs,
        )

    def as_dict(self) -> dict:
        """dictionary of relevant information"""
        dct = super(ConfiguredAction, self).as_dict()
        if self.next_action is not None:
            next_action_name = self.next_action.name
        else:
            next_action_name = None
        dct.update({
            'name': self.name,
            'arguments': self.args,
            'keyword_arguments': self.kwargs,
            'next_action': next_action_name,
        })
        return dct

    @classmethod
    def class_instance_by_id(cls, identifier: str, parent_id: Union[str] = None) -> 'ConfiguredAction':
        """
        Retrieves the instance of the current class by UUID

        :param identifier: unique identifier
        :raises NameError: if no matching instance could be found
        :param parent_id: optional specification of parent ID to retrieve instances specifically registered to
            a parent identifier.
        :return: registered class instance
        """
        try:
            for inst in cls._registry[cls.__name__]:
                inst: ConfiguredAction
                if parent_id is None and cls._match_instance_key(inst, identifier) is True:
                    return inst
                elif inst.match_name_and_parent(identifier, parent_identifier=parent_id) is True:
                    return inst
        except KeyError:  # if there are no registered instances of the class, raise a consistent error
            pass
        raise NameError(f'the uuid "{identifier}" could not be found in the registry of {cls.__name__}')


class ConfiguredActionList(ActionList, DumpableList):
    def __init__(self,
                 *actions: Union[Action, ConfiguredAction],
                 use_unique_action: bool = False,
                 parent_identifier_override: str = None,
                 ):
        """
        A manager for a list of Configured Actions.

        :param actions: actions to sequence
        :param use_unique_action: whether to use unique actions for any action added to this list
        :param parent_identifier_override: optional override for parent identifier used in ConfiguredAction
            unique identifier association.
        """
        self._action_list: List[ConfiguredAction] = []
        self.use_unique_action: bool = True if parent_identifier_override is not None else use_unique_action
        self.parent_identifier_override: Optional[str] = None
        super().__init__(*actions)

    def _ensure_type(self, action: Union[str, Action, ConfiguredAction]) -> ConfiguredAction:
        """Ensures that the provided action is of the correct type for the list"""
        if isinstance(action, ConfiguredAction):
            return action
        elif type(action) is str:
            return ConfiguredAction.class_instance_by_id(action)
        else:
            return ConfiguredAction(
                action,
                use_unique_action=self.use_unique_action,
                parent_identifier_override=self.parent_identifier_override,
            )

    def as_list(self) -> list:
        """returns a serializable list of relevant information about the configured actions"""
        return [
            action.as_dict()
            for action in self._action_list
        ]

    def get_ca_by_action(self, action: Callable) -> Optional[ConfiguredAction]:
        """
        Gets the corresponding ConfiguredAction instance

        :param action: gets a configured action from
        :return:
        """
        for inst in self:
            inst: ConfiguredAction
            if inst.match_name_and_parent(action, self.parent_identifier_override):
                return inst
        raise NameError(f'the action {action} is not a member of the {self.__class__.__name__} instance')

    def action_registered_in_list(self, action: Callable) -> bool:
        """
        Checks whether the provided action is the associated action of any actions registered in the Configured List

        :param action: action to check against
        """
        try:
            inst = self.get_ca_by_action(action)
            return True
        except NameError:
            return False


class ConfigurableInstance:
    methods_to_register: List[str] = []

    def __init__(self, instance_specific_actions: bool = False):
        """
        A base class which will register a class instance's methods as ConfiguredActions. The method names in the
        methods_to_register list will be registered as configured actions upon instantiation.

        Subclasses should overwrite the list of methods to register and call init.

        :param instance_specific_actions: whether the configured instance should use instance-specific actions (e.g. the
            action depends on the state of the instance)
        """
        self.instance_specific_actions = instance_specific_actions
        self._register_instance_actions()

    def _register_instance_actions(self):
        """registers instance actions as ConfiguredActions"""
        for method_name in self.methods_to_register:
            if isinstance(getattr(self, method_name), ConfiguredAction) is False:
                ca = ConfiguredAction(
                    getattr(self, method_name),
                    use_unique_action=self.instance_specific_actions,
                )
                setattr(
                    self,
                    method_name,
                    ca,
                )

    def execute_action(self, action: str, *args, **kwargs) -> 'TrackedAction':
        """
        Executes an action associated with the instance with the provided args and kwargs.

        :param action: action name to execute (must be a registered method of the instance)
        :param args: arguments to provide for the execution
        :param kwargs: keyword arguments to provide for the execution
        :return: the generated TrackedAction instance
        """
        if action not in self.methods_to_register:
            raise KeyError(f'the method "{action}" is not a registered method of this {self.__class__.__name__} instance')
        ta = TrackedAction(configuration=getattr(self, action))
        ta(*args, **kwargs)
        return ta

    def execute_action_threaded(self, action: str, *args, **kwargs) -> 'ThreadedTrackedAction':
        """
        Executes an action in a thread associated with the instance with the provided args and kwargs. This
        method is non-blocking.

        :param action: action name to execute (must be a registered method of the instance)
        :param args: arguments to provide for the execution
        :param kwargs: keyword arguments to provide for the execution
        :return: the generated ThreadedTrackedAction instance
        """
        if action not in self.methods_to_register:
            raise KeyError(
                f'the method "{action}" is not a registered method of this {self.__class__.__name__} instance')
        tta = ThreadedTrackedAction(configuration=getattr(self, action))
        tta(*args, **kwargs)
        return tta


def ensure_triggered(fn: Callable):
    """a decorator which ensures that the instance has been triggered"""
    @wraps(fn)
    def decorated(self: 'TrackedAction', *args, **kwargs):
        if self.triggered is False:
            raise AttributeError(
                f'{fn.__name__} may not be accessed until after the {self.__class__.__name__} instance '
                f'is triggered or called'
            )
        return fn(self, *args, **kwargs)
    return decorated


class TrackedAction(InstanceRegistry, Configuration, Status):
    UUID_PREFIX = 'ta-'

    def __init__(self,
                 configuration: Union[str, Callable, Action, ConfiguredAction],
                 *args,
                 **kwargs,
                 ):
        """
        Creates a wrapped action which will track the time of start, completion, and return of the action.

        :param configuration: configuration to reference or action to perform (callable)
        :param args: arguments for the instance's action execution
        :param kwargs: keyword arguments for the instance's action execution
        """
        if isinstance(configuration, TrackedAction):
            raise ValueError('a TrackedAction instance may not be created from another TrackedAction instance, '
                             'use .copy_configuration instance method')
        InstanceRegistry.__init__(self)
        Configuration.__init__(self)
        Status.__init__(self)
        self._triggered = False
        self._configuration: ConfiguredAction = None
        self.configuration = configuration
        self.update_args(*args)
        self.update_kwargs(**kwargs)

        # error state tracker
        self.error: bool = False
        self.error_details = None
        self._time_started = None
        self._time_completed = None
        self._action_return = None
        self._condition_evaluation = None

    def __call__(self, *args, **kwargs):
        """
        Execution method for a TrackedAction instance. Use extreme care when modifying this method in subclasses.
        The general order of operations of this method are:

        1. set the triggered flag (prevents multiple executions of the same instance)
        2. update stored arguments and keyword arguments for the execution of the action
        3. set the instance as frozen (does not allow updating after this point)
        4. tracks the start time of the execution
        5. executes the action, storing the return value
        6. if an error was encountered, the details of that error are stored
        7. notes the end time of the execution

        :param args: arguments which will be passed through to the action
        :param kwargs: keyword arguments which will be passed through to the action
        """
        if self._triggered is True:
            raise RuntimeError(f'multiple executions of a {self.__class__.__name__} instance is not permitted')
        self._triggered = True
        # update args and kwargs and store
        self.update_args(*args)
        self.update_kwargs(**kwargs)
        logger.debug('beginning action execution')
        self.freeze = True   # freeze settings
        self._time_started = time.time()  # set start time
        try:
            self._condition_evaluation = self._configuration.evaluate_condition()
            if self._condition_evaluation is False:
                logger.debug(
                    f'condition for action {self.configuration.action.name} evaluated to False, bypassing execution'
                )
            else:
                self._action_return = self.configuration.action(
                    *self.args,
                    **self.kwargs
                )
                logger.debug(f'action {self.configuration.action.name} completed successfully')
        except Exception as e:
            logger.error(f'error encountered when executing action {self.configuration.name}: {e}')
            self.error = True
            self.error_details = e
        self._time_completed = time.time()  # save completed time

    def __repr__(self):
        # todo have a separate str which indicates pending/triggered/complete as in timepoint
        strings = []
        args = self._arg_string
        if args != '':
            strings.append(args)
        kw = self._kwarg_string
        if kw != '':
            strings.append(kw)
        return f'{self.__class__.__name__}: {self.configuration.action.name}({", ".join(strings)})'

    def trigger(self, *args, **kwargs):
        """trigger execution of the tracked action"""
        self.__call__(*args, **kwargs)

    @property
    def triggered(self) -> bool:   # todo decide which of these to keep
        """whether the time point has been triggered"""
        return self._triggered

    @property
    def started(self) -> bool:
        """whether the timepoint has been started"""
        return self._triggered

    @property
    def action(self) -> Action:
        """configured action associated with the TrackedAction instances"""
        warnings.warn(  # v 6.0.0
            'the action attribute has been deprecated, access .configuration.action instead',
            DeprecationWarning,
            stacklevel=2,
        )
        return self.configuration.action

    @property
    def configuration(self) -> ConfiguredAction:
        """the configuration associated with the tracked action"""
        return self._configuration

    def _ensure_unfrozen(fn: Callable):
        """ensures that the instance is not frozen (locked for execution) before performing the specified action"""
        @wraps(fn)
        def decorated(self: 'TrackedAction', *args, **kwargs):
            if self._freeze is True:
                raise ValueError(f'the instance is frozen and setting or updating of the args or kwargs is disabled')
            return fn(self, *args, **kwargs)
        return decorated

    @configuration.setter
    @_ensure_unfrozen
    def configuration(self, value: Union[str, Callable, Action, ConfiguredAction]):
        value = ConfiguredAction.ensure_configuration(value)
        self._configuration = value
        self.update_args(*self._configuration.args)
        self.update_kwargs(**self._configuration.kwargs)

    @property
    def time_started(self) -> float:
        """time stamp when the action was started"""
        return self._time_started

    @property
    def time_completed(self) -> float:
        """time stamp when the action was completed"""
        return self._time_completed

    @property
    def started_timestamp(self) -> datetime.datetime:
        """timestamp for when the action was started"""
        if self.time_started is not None:
            return datetime.datetime.fromtimestamp(self.time_started)

    @property
    def action_duration(self) -> float:
        """task total duration (seconds)"""
        if self._time_completed is not None:
            return self._time_completed - self._time_started

    @property
    def method_return(self):
        """DEPRECATED retrieve action return"""
        warnings.warn(  # v 5.5.0
            'method_return is deprecated, use action_return instead',
            DeprecationWarning,
            stacklevel=2,
        )
        return self._action_return

    @property
    @ensure_triggered
    def action_return(self):
        """the return of the method once complete"""
        return self._action_return

    @property
    def next_action(self) -> ConfiguredAction:
        """next action to execute based on the configuration"""
        return self.configuration.next_action

    @property
    def status_code(self) -> int:
        """returns a status code representative of the state of the Action"""
        if self.error is True:
            code = -1
        elif self.time_started is None:
            code = 1
        elif self.time_completed is None:
            code = 2
        else:
            code = 3
        return code

    def as_dict(self) -> dict:
        """dictionary of relevant information"""
        out = super(TrackedAction, self).as_dict()

        out.update({
            'name': self.configuration.name,
            'configuration': self.configuration.as_dict(),
            'arguments': make_iterable_serializable(*self.args),
            'keyword_arguments': make_mapping_serializable(**self.kwargs),
        })

        if self.time_started is not None:
            out['time_started'] = self.time_started
            out['timestamp'] = str(self.started_timestamp)
        if self.time_completed is not None:
            out['time_completed'] = self.time_completed
            out['duration'] = self.time_completed - self.time_started
            if self.error is True:
                out['error_during_execution'] = True
                out['error_details'] = str(self.error_details)
            else:  # if completed and no error, include the method return
                out['action_return'] = serializable_cast(self.action_return)
                out['condition_evaluation'] = self._condition_evaluation
        return out

    def copy_configuration(self) -> "TrackedAction":
        """
        Copies the configuration of a TrackedAction instance.

        :return: TrackedAction instance with identical configuration
        """
        return self.__class__(
            self.configuration,
            *self.args,
            **self.kwargs,
        )

    @classmethod
    def create_from_configured(cls, source: Union[Action, ConfiguredAction]) -> "TrackedAction":
        """
        Creates a TrackedAction instance from a provided Action or ConfiguredAction

        :param source: action to generate from
        :return: instantiated TrackedAction
        """
        warnings.warn(
            'creating TrackedAction instances from ConfiguredAction instances is now the intended method of '
            'instantiation, please update your code to instantiate directly',
            DeprecationWarning,
            stacklevel=2,
        )
        return cls(source)

    _ensure_unfrozen = staticmethod(_ensure_unfrozen)


class ThreadedTrackedAction(TrackedAction):
    UUID_PREFIX = 'tta-'

    def __init__(self,
                 configuration: Union[str, Callable, Action, ConfiguredAction],
                 *args,
                 **kwargs,
                 ):
        """
        A threaded version of a tracked action. This action may be executed asynchronously.

        :param configuration: action to perform (callable)
        :param Action, ConfiguredAction, next_step: for creating a sequence of actions, the next_action is the action
            that should be executed after this action has been executed
        :param args: arguments for the action
        :param kwargs: keyword arguments for the action
        """
        TrackedAction.__init__(
            self,
            configuration=configuration,
            *args,
            **kwargs,
        )
        self._lock = threading.Lock()
        self._thread: threading.Thread = None

    def _executor(self, *args, **kwargs):
        """Target method for the internal thread. Modify this method in subclasses to affect behaviour of execution"""
        with self._lock:  # allows checking of whether the action is in progress
            super(ThreadedTrackedAction, self).__call__(*args, **kwargs)

    def _trigger(self, *args, **kwargs):
        """
        Triggers the action execution. This method was not intended to be overridden. This method also prevents multiple
        executions of the same instance.

        :param args: arguments for the call
        :param kwargs: kwargs for the call
        """
        # todo double check why this is separate from _executor and whether they can be consolidated
        if self.triggered is True:
            raise SystemError(f'multiple executions of the same {self.__class__.__name__} are not supported')
        logger.debug(f'triggering execution of {self.__str__()}')
        self.update_args(*args)
        self.update_kwargs(**kwargs)
        self._thread = threading.Thread(
            target=self._executor,
            name=f'{self.uuid} executor',
            daemon=True,
            args=self.args,
            kwargs=self.kwargs,
        )
        self._thread.start()

    def trigger(self, *args, **kwargs):
        """
        Triggers the action execution. Call order:

        1. _trigger
        2. _executor
        3. TrackedAction superclass __call__

        :param args: arguments for the call
        :param kwargs: kwargs for the call
        """
        self._trigger(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """redirects the call function to operate through _trigger"""
        self._trigger(*args, **kwargs)

    @property
    def in_progress(self) -> bool:
        """
        whether the action is in progress (the action is in the process of being executed)
        """
        if self.triggered is True:
            return self._lock.locked()
        return False

    @property
    def complete(self) -> bool:
        """whether the actions have completed"""
        if self.triggered is True:  # if instance has been triggered, check lock state
            return not self._lock.locked()
        return False

    def wait_for_completion(self):
        """
        Waits for the completion of the time point
        """
        if self.in_progress is True:
            logger.info('waiting for action to complete')
            self._thread.join()  # todo support timeout


class TrackedActionList(ActionList, DumpableList):
    def __init__(self, *actions: Union[Action, ConfiguredAction, TrackedAction]):
        """
        A manager for a list of Tracked Actions.

        :param actions: actions to sequence
        """
        self._action_list: List[TrackedAction] = []
        super().__init__(*actions)
        # todo define what happens when you copy the list (should create unexecuted trackedactions)

    @staticmethod
    def _ensure_type(action: Union[str, Action, ConfiguredAction, TrackedAction]) -> TrackedAction:
        """Ensures that the provided action is of the correct type for the list"""
        if isinstance(action, TrackedAction):
            return action
        else:
            return TrackedAction(action)

    def as_list(self) -> list:
        return [
            action.as_dict()
            for action in self._action_list
        ]
