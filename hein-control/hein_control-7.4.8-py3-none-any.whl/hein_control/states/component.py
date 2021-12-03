import warnings

import time
import logging
import threading
import operator

from typing import Union, MutableMapping, List, Callable, Type, Optional, Iterable
from functools import wraps
from abc import ABC

from ..mixin.reg import InstanceRegistry


from .abc import state_logger, OperationalState, GenericActionState, State, StateSet


class BadComponentState(Exception):
    def __init__(self, *components: 'ComponentState', threshold_state: StateSet):
        """
        Exception signifying that bad state was encountered on the provided components

        :param components: components which have a bad state
        :param threshold_state: threshold state
        """
        self.components = components
        super(BadComponentState, self).__init__(
            f'a bad state was encountered with the component{"s" if len(components) > 0 else ""}: ' +
            ', '.join([
                f'{component.component_name}: {component.current_operational_state.name}'
                for component in components
            ])
            + f'; threshold state: {threshold_state.name}'
        )


def ensure_component_online(fn: Callable):
    """class instance decorator which will check for an online state before executing the decorated function"""
    @wraps(fn)
    def decorated(self: 'ComponentState', *args, **kwargs):
        if self.current_operational_state <= 0:
            state_logger.error(
                f'the component {self.component_name} is in operational state {self.current_operational_state.name} '
                f'(required: {OperationalState.ONLINE}) '
                f'when calling {fn.__name__}'
            )
            raise BadComponentState(self, threshold_state=OperationalState.OFFLINE)
        return fn(self, *args, **kwargs)

    return decorated


def ensure_component_inactive(fn: Callable):
    """
    class instance decorator which will check that the component is inactive before
    executing the decorated function
    """
    @wraps(fn)
    def decorated(self: 'ComponentState', *args, **kwargs):
        if self.current_action_state != 0:
            # retrieve the expected idle state enumeration
            expected_idle_state = self.current_action_state.__class__(0)
            state_logger.error(
                f'the component {self.component_name} is in action state {self.current_action_state.name} '
                f'(required: {expected_idle_state.name}) when calling {fn.__name__}'
            )
            raise BadComponentState(self, threshold_state=expected_idle_state)
        return fn(self, *args, **kwargs)

    return decorated


class TemporaryCallbackSetter(ABC):
    # state set to temporarily assign callbacks to
    _state_set_attribute: str = None

    def __init__(self,
                 *components: 'ComponentState',
                 callbacks: Union[Callable, Iterable[Callable]] = None,
                 threshold_state: StateSet = OperationalState.OFFLINE,
                 pre_state_change: bool = True,
                 remove_configurations_on_exit: bool = False,
                 ):
        """
        Context manager for temporarily applying callbacks to the provided components

        :param components: components to monitor
        :param callbacks: custom callback(s) to apply
        :param threshold_state: threshold state to apply callbacks at and below
        :param pre_state_change: whether the callbacks should be added to pre- or post-state change callback lists
        :param remove_configurations_on_exit: option to remove configurations on exit
            (useful for one-off registered methods that will never be used again)
        """
        self.components = components
        self.threshold_state = threshold_state
        self.pre_state_change = pre_state_change
        self.remove_on_exit = remove_configurations_on_exit
        if callbacks is None:
            callbacks = []
        elif callable(callbacks):  # cast if it's only a single callback
            callbacks = [callbacks]
        self.callbacks: Iterable[Callable] = callbacks
        # internal flag in the event that the callback is triggered
        self._callback_encountered = threading.Event()

    def __enter__(self) -> 'TemporaryCallbackSetter':
        for component in self.components:
            for state in getattr(component, self._state_set_attribute):
                if state <= self.threshold_state:
                    state.register_callbacks(self.callback_capture, *self.callbacks, pre_state=self.pre_state_change)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for component in self.components:
            for state in getattr(component, self._state_set_attribute):
                if state <= self.threshold_state:
                    state.deregister_callbacks(self.callback_capture, remove_configurations=True)
                    state.deregister_callbacks(
                        *self.callbacks,
                        remove_configurations=self.remove_on_exit,
                    )

    @property
    def callback_encountered(self) -> bool:
        """whether a callback has been encountered"""
        return self._callback_encountered.is_set()

    def callback_capture(self):
        """a default callback which notes that the callback was called (useful for flag checking)"""
        self._callback_encountered.set()


class TemporaryOperationalCallback(TemporaryCallbackSetter):
    """context manager for temporarily applying callbacks to the operational states of the provided components"""
    _state_set_attribute = 'operational_states'


def TemporaryCallback(*args, **kwargs):
    warnings.warn(  # v7.1.7
        'TemporaryCallback was renamed TemporaryOperationalCallback',
        DeprecationWarning,
        stacklevel=2,
    )
    return TemporaryOperationalCallback(*args, **kwargs)


class TemporaryActionCallback(TemporaryCallbackSetter):
    """context manager for temporarily applying callbacks to the action states of the provided components"""
    _state_set_attribute = 'action_states'


class ComponentState(InstanceRegistry):

    # dedicated component-specific mapping
    _components: MutableMapping[str, 'ComponentState'] = {}

    # override this when subclassing to indicate more advanced component action states
    action_states: Type[StateSet] = GenericActionState

    # override this when subclassing to indicate more advanced component operational states
    #   negative values indicate error states, 0 is offline, and positive is an operational state
    operational_states: Type[StateSet] = OperationalState

    def __init__(self,
                 component_name: str,
                 current_operational_state: Union[int, str, StateSet] = None,
                 current_action_state: Union[int, str, StateSet] = None
                 ):
        """
        ABC for tracking a component's operational state

        :param component_name: reference name for the component being registered
        :param current_operational_state: current state of the component
        """
        # todo create an InstanceRegistry subclass which tracks subclass instances (i.e. all components)
        if component_name in ComponentState.class_registry:
            raise NameError(
                f'the component "{component_name}" is already defined, please retrieve using get_component_by_name or '
                f'choose a different name for the component'
            )
        InstanceRegistry.__init__(self)
        ComponentState._components[component_name] = self
        self.component_name = component_name
        self.logger = state_logger.getChild(self.component_name)
        self._current_operational_state: OperationalState = None
        self.current_operational_state = current_operational_state or 0
        self._current_action_state: StateSet = None
        self.current_action_state = current_action_state or 0

        # set state names as parent IDs of callback list
        for state_set in [self.operational_states, self.action_states]:
            for state in state_set:
                state: StateSet
                if isinstance(state.value, State):
                    # set parent identifier override to be the string of the state
                    state.value.pre_state_callbacks.parent_identifier_override = state.__class__.__name__
                    state.value.post_state_callbacks.parent_identifier_override = state.__class__.__name__

    @staticmethod
    def _match_instance_key(inst: "ComponentState", identifier: str) -> bool:
        """matches the provided identifier against the component name and standard identifiers"""
        if inst._uuid == identifier:
            return True
        elif inst.uuid == identifier:
            return True
        elif identifier == inst.component_name:
            # todo consider matching case-insensitive
            return True
        return False

    @property
    def current_operational_state(self) -> StateSet:
        """The current state of the component"""
        return self._current_operational_state

    @current_operational_state.setter
    def current_operational_state(self, value: Union[int, str, StateSet]):
        self.update_operational_state(value)

    def _get_state_from_key(self, value: Union[int, str, StateSet], state_set: str) -> StateSet:
        """
        Gets an operational state from the provided key. If an StateSet instance which is not the same
        class as the assigned operational state class of the instance, the equivalent state will be retrieved.

        :param value: value, name, or StateSet
        :param state_set: state set key to use for retrieval
        """
        state_set = getattr(self, state_set)
        if isinstance(value, state_set):
            return value
        elif isinstance(value, StateSet):
            try:
                return state_set(value.value)
            except ValueError as e:
                raise ValueError(f'the operational state {value} does not have an equivalent {state_set.__name__} value')
        elif type(value) is str:
            return state_set[value.upper()]
        elif type(value) is int or isinstance(value, State):
            return state_set(value)
        else:
            raise TypeError(f'the type {type(value)} is not supported for a current component operational state')

    def get_operational_state_from_key(self, value: Union[int, str, StateSet]) -> StateSet:
        """
        Gets an operational state from the provided key. If an StateSet instance which is not the same
        class as the assigned operational state class of the instance, the equivalent state will be retrieved.

        :param value: value, name, or StateSet
        """
        return self._get_state_from_key(
            value,
            'operational_states',
        )

    def get_action_state_from_key(self, value: Union[int, str, StateSet]) -> StateSet:
        """
        Gets an action state from the provided key. If an StateSet instance which is not the same
        class as the assigned operational state class of the instance, the equivalent state will be retrieved.

        :param value: value, name, or StateSet
        """
        return self._get_state_from_key(
            value,
            'action_states',
        )

    def update_operational_state(self, state: Union[int, str, StateSet]) -> Optional[List]:
        """
        Updates the current state of the Component

        :param state: value to set the state to
        :return: return value from defined callback functions
        """
        state = self.get_operational_state_from_key(state)
        # execute callbacks if any are specified
        try:
            if state.has_pre_state_change_callbacks:
                self.logger.info(
                    f'executing {len(state.value.pre_state_callbacks)} pre-state-change callbacks for {state.name}'
                )
            out = state.execute_pre_state_callbacks()
        finally:
            self._current_operational_state = state
        if state.has_post_state_change_callbacks:
            self.logger.info(
                f'executing {len(state.value.pre_state_callbacks)} post-state-change callbacks for {state.name}'
            )
            out.extend(state.execute_post_state_callbacks())
        return out

    @property
    def current_action_state(self) -> StateSet:
        """the current action state of the component"""
        return self._current_action_state

    @current_action_state.setter
    def current_action_state(self, value: Union[int, str, StateSet]):
        self.update_action_state(value)

    def update_action_state(self, state: Union[int, str, StateSet]) -> Optional[List]:
        """
        Updates the current action state of the component

        :param state: value to set the state to
        :return: return value from defined callback functions
        """
        if type(state) is int or isinstance(state, State):
            state = self.action_states(state)
        elif type(state) is str:
            state = self.action_states[state.upper()]
        elif isinstance(state, self.action_states) is False:
            raise TypeError(f'the type {type(state)} is not supported for a current component action state')
        try:
            # execute callbacks if they are specified
            if state.has_pre_state_change_callbacks:
                self.logger.info(
                    f'executing {len(state.value.pre_state_callbacks)} pre-state-change callbacks for {state.name}'
                )
            out = state.execute_pre_state_callbacks()
        finally:
            self._current_action_state = state
        if state.has_post_state_change_callbacks:
            self.logger.info(
                f'executing {len(state.value.post_state_callbacks)} post-state-change callbacks for {state.name}'
            )
            out.extend(state.execute_post_state_callbacks())
        return out

    @classmethod
    def check_component_states(cls,
                               threshold_state: Union[int, OperationalState],
                               *components: Union[str, 'ComponentState'],
                               ) -> List['ComponentState']:
        """
        Checks the provided components against the minimum component state value, returning any components which do not
        pass the check.

        :param threshold_state: Minimum state value (components with states lower than this will fail the check)
        :param components: components to check
        :return: list of failing components
        """
        components = cls.get_components_to_monitor(*components)
        return [
            component
            for component in components
            if component.current_operational_state <= threshold_state
        ]

    @classmethod
    def check_component_states_raise(cls,
                                     threshold_state: Union[int, OperationalState],
                                     *components: 'ComponentState',
                                     ):
        """
        Checks the list of components against the minimum state and raises an error if any fail the test

        :param threshold_state: the threshold state to monitor for
        :param components: components to check
        """
        bad_states = cls.check_component_states(threshold_state, *components)
        if len(bad_states) > 0:
            state_logger.error(
                f'a bad state was encountered on the following component{"s" if len(bad_states) == 1 else ""}: '
                + ", ".join([
                    f'{component.component_name} {component.current_operational_state.value} '
                    f'({component.current_operational_state.name})'
                    for component in bad_states
                ])
            )
            raise BadComponentState(*bad_states, threshold_state=threshold_state)

    @classmethod
    def components_from_names(cls, *components: Union[str, 'ComponentState']) -> List['ComponentState']:
        """
        Retrieves a list of ComponentState subclasses from the provided list.

        :param components: components to find
        :return: list of ComponentState instances
        """
        out = []
        for component in components:
            if isinstance(component, ComponentState) is True:
                out.append(component)
            elif type(component) is str:
                out.append(cls._components[component])
            else:
                raise TypeError(f'the component "{component}" is not recognized')
        return out

    @classmethod
    def get_components_to_monitor(cls, *components: Union[str, 'ComponentState']) -> List['ComponentState']:
        """
        Gets a list of components to monitor from the provided arguments. If no components are provided, the complete
        list of components is provided.

        :param components: components to monitor
        :return: list of ComponentState instances
        """
        if len(components) > 0:
            return cls.components_from_names(*components)
        return [component for _, component in cls._components.items()]

    @classmethod
    def components_state_monitor_sleep(cls,
                                       duration: float,
                                       *components: Union[str, 'ComponentState'],
                                       cycle_time: float = 0.1,
                                       threshold_state: Union[int, StateSet] = OperationalState.OFFLINE,
                                       ):
        """
        Executes a sleep while also monitoring the state of the specified components. If no components are provided,
        all components will be monitored.

        :param duration: duration to sleep (approximate)
        :param components: components to monitor for a bad state. Can be either the name of the component or the
            ComponentState instance itself.
        :param cycle_time: cycle frequency (s; a check for a bad state will be executed every this seconds)
        :param threshold_state: the state to monitor for (states less or equal to this will raise an error)
        """
        # retrieve components as specified
        monitored_components = cls.get_components_to_monitor(*components)
        state_logger.info(
            f'waiting for ~{duration} s while monitoring '
            + f'{len(monitored_components)} components'
            if len(monitored_components) > 0
            else monitored_components[0].component_name
        )
        end_time = time.time() + duration
        while time.time() < end_time:
            cls.check_component_states_raise(threshold_state, *monitored_components)
            time.sleep(cycle_time)
        logging.info(f'finished waiting, continuing')

    def state_monitor_sleep(self,
                            duration: float,
                            cycle_time: float = 0.1,
                            threshold_state: Union[int, StateSet] = OperationalState.OFFLINE,
                            ):
        """
        Executes a sleep while also monitoring the state of the component. To monitor the state of multiple components,
        use components_state_monitor_sleep.

        :param duration: duration to sleep (approximate)
        :param cycle_time: cycle frequency (s; a check for a bad state will be executed every this seconds)
        :param threshold_state: the state to monitor for (states less or equal to this will raise an error)
        """
        return self.components_state_monitor_sleep(
            duration,
            self.component_name,
            cycle_time=cycle_time,
            threshold_state=threshold_state,
        )

    @classmethod
    def components_state_monitor_flag_check(cls,
                                            flag_check: Callable,
                                            *components: Union[str, 'ComponentState'],
                                            target_flag_state=True,
                                            cycle_time: float = 0.1,
                                            threshold_state: Union[int, StateSet] = OperationalState.OFFLINE,
                                            timeout: float = None,
                                            **flag_check_kwargs
                                            ):
        """
        Monitors the provided flag check while also monitoring the state of the specified components. If no components
        are provided, all components will be monitored.

        :param flag_check: method which will return a value that will be checked against the target_flag_state
        :param components: components to monitor for a bad state. Can be either the name of the component or the
            ComponentState instance itself.
        :param cycle_time: cycle frequency (s; a check for a bad state will be executed every this seconds)
        :param threshold_state: the state to monitor for (states less or equal to this will raise an error)
        :param target_flag_state: target flag state to monitor for
        :param timeout: optional timeout (seconds) to use while monitoring flags. If the timeout is reached before the
            flag state is reached, an error is raised.
        :param flag_check_kwargs: keyword arguments for the flag check
        """
        # retrieve components as specified
        monitored_components = cls.get_components_to_monitor(*components)
        state_logger.info(
            f'waiting for {flag_check.__name__} to be {target_flag_state} while monitoring '
            + f'{len(monitored_components)} components' if len(monitored_components) > 0
            else monitored_components[0].component_name
            + f' (timeout: {timeout} s)' if timeout is not None else ''
        )
        if timeout is not None:
            timeout = time.time() + timeout
        while flag_check(**flag_check_kwargs) != target_flag_state:
            if timeout is not None and time.time() > timeout:
                raise TimeoutError(
                    f'the desired flag state "{target_flag_state}" was not encountered before the timeout elapsed '
                )
            cls.check_component_states_raise(threshold_state, *monitored_components)
            time.sleep(cycle_time)
        logging.info(f'finished waiting, continuing')

    def state_monitor_flag_check(self,
                                 flag_check: Callable,
                                 target_flag_state=True,
                                 cycle_time: float = 0.1,
                                 threshold_state: Union[int, StateSet] = OperationalState.OFFLINE,
                                 timeout: float = None,
                                 **flag_check_kwargs
                                 ):
        """
        Monitors the state of the component, waiting for the threshold state. To monitor multiple components, use
        components_state_monitor_flag_check.


        :param flag_check: method which will return a value that will be checked against the target_flag_state
        :param cycle_time: cycle frequency (s; a check for a bad state will be executed every this seconds)
        :param threshold_state: the state to monitor for (states less or equal to this will raise an error)
        :param target_flag_state: target flag state to monitor for
        :param timeout: optional timeout (seconds) to use while monitoring flags. If the timeout is reached before the
            flag state is reached, an error is raised.
        :param flag_check_kwargs: keyword arguments for the flag check
        """
        self.components_state_monitor_flag_check(
            flag_check,
            self.component_name,
            target_flag_state=target_flag_state,
            cycle_time=cycle_time,
            threshold_state=threshold_state,
            timeout=timeout,
            **flag_check_kwargs,
        )

    @classmethod
    def get_component_by_name(cls, component_name: str) -> 'ComponentState':
        """
        Retrieves a component by its name. If you need to retrieve a component that you know is already instantiated,
        use this method.

        :param component_name: name assigned to the component
        """
        try:
            return cls._components[component_name]
        except KeyError:
            raise KeyError(f'the component "{component_name}" is not a defined component')

    @classmethod
    def get_or_create_component(cls, *args, component_name: str = None, **kwargs) -> 'ComponentState':
        """
        Retrieves an existing component or instantiates it as needed. This is intended to be the primary factory for
        component instantiation.

        :param args: component arguments
        :param component_name: name for the component
        :param kwargs: component keyword arguments
        :return: instantiated components
        """
        if component_name is None:
            raise ValueError(f'a component name must be specified')
        if component_name in cls._components:
            return cls._components[component_name]
        return cls(
            *args,
            component_name=component_name,
            **kwargs,
        )

    def wait_for_component_operational_state(self,
                                             desired_state: Union[int, StateSet, str],
                                             cycle_time: float = 0.1,
                                             timeout: float = None,
                                             comparison_operator: Callable = operator.ge,
                                             ):
        """
        Waits for the specified components to be at or above the specified operational state.

        :param desired_state: desired operational state for the component to be in
        :param cycle_time: state check cycle time
        :param timeout: optional timeout while waiting for the operational state
        :param comparison_operator: optional override for the comparison operator used by the wait method. The operator
            should expect two arguments: the current and desired states respectively. The operator function should return
            False if the condition is not met and True if it is.
        """
        # todo create a generic method to wait for multiple components
        desired_state = self.get_operational_state_from_key(desired_state)
        if timeout is not None:
            max_time = time.time() + timeout
        self.logger.info(f'waiting for {desired_state.name} operational state')
        while comparison_operator(self.current_operational_state, desired_state) is False:
            if timeout is not None and time.time() > max_time:
                msg = f'timeout of {timeout} s elapsed while waiting for {self.component_name} to be {desired_state.name}'
                self.logger.error(msg)
                raise TimeoutError(msg)
            time.sleep(cycle_time)

    def wait_for_component_action_state(self,
                                        desired_state: Union[int, StateSet, str],
                                        cycle_time: float = 0.1,
                                        timeout: float = None,
                                        comparison_operator: Callable = operator.ge,
                                        ):
        """
        Waits for the specified components to be at or above the specified action state.

        :param desired_state: desired action state for the component to be in
        :param cycle_time: state check cycle time
        :param comparison_operator: optional override for the comparison operator used by the wait method. The operator
            should expect two arguments: the current and desired states respectively. The operator function should return
            False if the condition is not met and True if it is.
        """
        # todo create a generic method to wait for multiple components
        desired_state = self.get_action_state_from_key(desired_state)
        if timeout is not None:
            max_time = time.time() + timeout
        self.logger.info(f'waiting for {desired_state.name} action state')
        while comparison_operator(self.current_action_state, desired_state) is False:
            if timeout is not None and time.time() > max_time:
                msg = f'timeout of {timeout} s elapsed while waiting for {self.component_name} to be {desired_state.name}'
                self.logger.error(msg)
                raise TimeoutError(msg)
            time.sleep(cycle_time)
