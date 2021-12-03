"""
Module for managing time points in a sequence. `TimePoint` simply manages a time point relative to some start,
and `ActionTimePoint` manages context, sequences of actions, and execution of those actions when desired.
"""
import datetime
import uuid
import logging
import warnings
import time

from typing import Union, Callable, Iterable
from .mixin import InstanceRegistry, DumpableState
from .action import Action, ConfiguredAction, ConfiguredActionList
from .sequencing import ExecutionSequence, ConfiguredSequence
from .action.configured import ensure_triggered

logger = logging.getLogger(__name__)


class TimePoint(InstanceRegistry, DumpableState):
    UUID_PREFIX = 'tp-'

    def __init__(self,
                 time_delta: float,
                 name: str = None,
                 description: str = None,
                 parent_sequence_id: str = None,
                 ):
        """
        A class for describing and tracking an event time point relative to some start time.

        :param time_delta: time delta for the time point (seconds; relative to some other time)
        :param name: convenience name for time point differentiation
        :param description: extended description for differentiation
        :param parent_sequence_id: uuid of parent SamplingScheduler (if applicable)
        """
        InstanceRegistry.__init__(self)
        # time delta from trigger time
        self.time_delta: float = float(time_delta)
        # storage for start time
        self.sequence_time_started: float = None
        # name for convenience
        self.name: str = name
        # description
        self.description: str = description
        # parent uuid
        self.parent_sequence_id: str = parent_sequence_id

        self._uuid = str(uuid.uuid4())  # assign unique identifier
        # todo add description attribute
        # todo create association between time point and parent scheduler
        # todo finish refactor
        #   - move as_dict, update as necessary

    def __str__(self):
        return (
            f'{self.__class__.__name__} {self.time_delta} s '
        )

    def __repr__(self):
        return self.__str__()

    @property
    def uuid(self) -> str:
        """uuid for the time point"""
        return self.UUID_PREFIX + self._uuid

    @classmethod
    def get_instance(cls, key: str) -> "TimePoint":
        """
        Retreives a timepoint instance by key. The key may be a uuid, or class-uuid

        :param key: key to search by
        :return: TimePoint (or subclass) instance
        """
        warnings.warn(
            'the get_instance method has been deprecated, use class_instance_by_id',
            DeprecationWarning,
            stacklevel=2,
        )
        return cls.class_instance_by_id(key)

    def as_dict(self) -> dict:
        """Returns a key: value representation of the instance"""
        dct = super(TimePoint, self).as_dict()
        dct.update({
            'time_delta': self.time_delta,
            'uuid': self.uuid,
            'name': self.name,
            'class': self.__class__.__name__,
        })
        return dct

    def sample_time_from_reference(self, reference_time: float):
        """
        Returns the sample time for the time point from the reference time (in seconds)

        :param reference_time: reference time to calculate from
        :return: time to trigger (seconds)
        """
        return self.time_delta + reference_time

    def __lt__(self, other: Union[float, "TimePoint"]):
        if isinstance(other, TimePoint):
            other = other.time_delta
        return self.time_delta < other

    def __eq__(self, other: Union[float, "TimePoint"]):
        if isinstance(other, TimePoint):
            other = other.time_delta
        return self.time_delta == other

    def __gt__(self, other: Union[float, "TimePoint"]):
        if isinstance(other, TimePoint):
            other = other.time_delta
        return self.time_delta > other

    def __le__(self, other: Union[float, "TimePoint"]):
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other: Union[float, "TimePoint"]):
        return self.__gt__(other) or self.__eq__(other)


class ActionTimePoint(TimePoint, ExecutionSequence):
    UUID_PREFIX = 'atp-'

    def __init__(self,
                 time_delta: float,
                 configuration: Union[str, ConfiguredSequence],
                 name: str = None,
                 **action_kwargs,
                 ):
        """
        A class for describing and tracking an event time point relative to some other time where actions
        (e.g. a sampling sequence) are to be triggered. The sequence of actions is stored in a ConfiguredSequence
        instance.

        :param time_delta: time delta for the time point (relative to some other time)
        :param name: convenience name for time point differentiation
        :param actions: action methods to call. These methods will be called in the order provided
        :param action_kwargs: action kwargs to associate with list of actions (primary keys must map to function names)
        """
        # todo create abstract class with context
        #   - individual methods for pre-step, main, and post-step (e.g. turn on pump, run experiment, process data)
        # todo associate timepoint with parent scheduler instance (by UUID)
        # todo create passthrough for sequence_time_started on init
        TimePoint.__init__(
            self,
            time_delta=time_delta,
            name=name,
        )
        ExecutionSequence.__init__(
            self,
            configuration=configuration,
            **action_kwargs,
        )

    def __str__(self):
        out = f'{self.__class__.__name__} {self.string_time_delta}'
        if self.complete is True:
            out += ' COMPLETE'
        elif self.triggered is True:
            out += ' TRIGGERED'
        return out

    def _executor(self, *args, **kwargs):
        """
        Target method for the internal thread.
        The ThreadedTrackedAction _executor method is leveraged with the start and completion points noted in the log.
        """
        logger.info(f'{self} sequence starting')
        super(ActionTimePoint, self)._executor(*args, **kwargs)
        logger.info(f'{self} sequence completed, duration: {self.action_duration}')

    def remove_action(self,
                      action: Union[str, Callable, Action],
                      ):
        """
        Removes an action from the list of actions associated with a timepoint.

        :param action: action identifier
        :return:
        """
        raise NotImplementedError()
        # todo implement
        #   - determine identifier
        #   - remove from _actions list

    def trigger(self,
                wait: bool = None,
                **kwargs,
                ):
        """
        Triggers (starts execution of) the action sequence of the ActionTimePoint.
        Keyword arguments will be passed through to their respective action methods by the name of the action.
        This method executes the built-in __call__ of ExecutionSequence and it will block until the thread of the
        ExecutionSequence has started.

        e.g. if there is a method named "do_this_thing" which expects the keyword argument "value", the expected syntax
        of kwargs would be

            {
                "do_this_thing": {"value": 42},
            }

        Execution Tree:
        1. Execution sequence __call__
        2. ThreadedTrackedAction using operators.execute_sequence_actions action
        3. Waits until the thread starts (prevents double-triggering
        4. waits for completion if specified


        :param wait: whether to wait for completion before returning
        :param kwargs: keyword arguments for the actions. Keyword arguments will be passed through to their respective
            methods.

        """
        # todo refactor to trigger_and_wait (separate so that signatures match)
        self.__call__(**kwargs)
        # block until triggered flag is set (prevents double-triggering in the same loop)
        while self._triggered is False:
            time.sleep(0.001)
        if wait is True:
            self.wait_for_completion()

    @property
    def string_time_delta(self) -> str:
        """formatted string version of time delta"""
        return str(
            datetime.timedelta(seconds=self.time_delta)
        )

    @property
    @ensure_triggered
    def relative_start_times(self) -> dict:
        """relative start times for actions"""
        if self.sequence_time_started is None:
            raise ValueError(f'sequence_start_time is not set for the {self.__class__.__name__} instance')
        return {
            action.configuration.name: action.time_started - self.sequence_time_started
            for action in self.args
            if action.time_started is not None
        }

    def copy_configuration(self) -> "ActionTimePoint":
        """
        Copies the configuration of an ActionTimePoint instance.

        :return: ActionTimePoint instance with identical configuration
        """
        out = self.__class__(
            time_delta=self.time_delta,
            name=self.name,
            configuration=self.configuration,
        )
        out.update_kwargs(**self.kwargs)
        return out

    @classmethod
    def create_from_actions(cls,
                            time_delta: float,
                            actions: Iterable[Union[str, 'ConfiguredAction']],
                            name: str = None,
                            ) -> "ActionTimePoint":
        """
        Creates an instance from a list of configured actions. This differs from calling init by accepting
        an iterable argument containing actions which are used to create the ConfiguredSequence required by
        init.

        :param time_delta: time delta for the time point (relative to some other time)
        :param actions: configured actions or named configurations
        :param name: name for the time point (optional)
        :return: configured instance
        """
        config = ConfiguredSequence(
            *ConfiguredActionList(*actions)
        )
        return cls(
            time_delta=time_delta,
            configuration=config,
            name=name,
        )

    def as_dict(self) -> dict:
        """Returns a key: value representation of the instance"""
        # todo decide how to include relative start times
        return super(ActionTimePoint, self).as_dict()

