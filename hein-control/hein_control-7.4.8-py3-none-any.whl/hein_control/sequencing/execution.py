"""
Tools for executing a predefined (linear) series of actions.
"""

import logging
import datetime

from typing import Dict, Union, Iterable

from ..action.operators import execute_sequence_actions
from ..action.configured import ConfiguredAction, ThreadedTrackedAction, TrackedActionList, ConfiguredActionList, ensure_triggered

logger = logging.getLogger(__name__)


class ConfiguredSequence(ConfiguredAction):
    def __init__(self,
                 *actions: ConfiguredAction,
                 sequence_name: str = None,
                 next_action: Union[str, 'ConfiguredAction'] = None,
                 **kwargs,
                 ):
        """
        A class for configuring the execution of a sequence of actions

        :param actions: actions to execute in sequence
        :param sequence_name: name for the sequence
        :param next_action: next action to perform after completion of the sequence
        :param kwargs: kwargs for the actions
        """
        ConfiguredAction.__init__(
            self,
            action=execute_sequence_actions,
            configuration_name=sequence_name,  # todo add attribute for sequence name
            next_action=next_action,
            **kwargs,
        )
        self._sequence: ConfiguredActionList = ConfiguredActionList(*actions)

    def __str__(self):
        return f'{self.__class__.__name__} {self.name}'

    @property
    def action_sequence(self) -> ConfiguredActionList:
        """sequence of actions for the configuration"""
        return self._sequence

    @action_sequence.setter
    def action_sequence(self, value: Iterable):
        self._sequence = ConfiguredActionList(*value)

    def get_tracked_from_config(self, **kwargs) -> "ExecutionSequence":
        """
        Gets an execution sequence instance based on the configured sequence.

        :param kwargs: additional kwargs that differ from the instance configuration
        :return: execution sequence
        """
        return ExecutionSequence(configuration=self, **kwargs)

    def duplicate_configuration(self, new_name: str = None) -> 'ConfiguredSequence':
        """
        Duplicates the configuration of the sequence

        :param new_name: optional name for the new sequence
        :return:
        """
        if new_name is None:
            new_name = self._generate_unique_name(self.action)
        return self.__class__(
            *self.action_sequence,
            sequence_name=new_name,
            next_action=self.next_action,
            **self.kwargs,
        )


class ExecutionSequence(ThreadedTrackedAction):
    UUID_PREFIX = 'seq-'

    def __init__(self,
                 configuration: Union[str, ConfiguredSequence],
                 **kwargs,
                 ):
        """
        Executor class for a sequence of actions.

        :param actions: actions to execute when called (base actions or configured actions)
        """
        if isinstance(configuration, ConfiguredSequence) is False:
            configuration = ConfiguredSequence.class_instance_by_id(configuration)
        self._configuration: ConfiguredSequence = None  # update type hint
        ThreadedTrackedAction.__init__(
            self,
            configuration=configuration,
            **kwargs,
        )
        # todo disable args at the appropriate level (somewhere it breaks, figure out where that is)

    def __str__(self):
        # todo update to better represent instance
        return super(ExecutionSequence, self).__str__()

    def __call__(self, **kwargs):
        """
        Converts the configured actions to a tracked action list and passes those as arguments to the
        ThreadedTrackedAction call (configured to leverage the execute_sequence_actions operator action).

        :param kwargs:
        :return:
        """
        logger.debug(f'{self} sequence execution call starting')
        # convert configured actions to tracked actions
        actions = TrackedActionList(*self.configuration.action_sequence)
        super(ExecutionSequence, self).__call__(
            *actions,
            **kwargs,
        )
        logger.debug(f'{self} sequence execution call completed')

    @property
    def configuration(self) -> ConfiguredSequence:
        """the configured sequence associated with the instance"""
        return self._configuration

    @configuration.setter
    def configuration(self, value: ConfiguredSequence):
        if isinstance(value, ConfiguredSequence) is False:
            raise TypeError(f'a ConfiguredSequence must be used as a configuration for {self.__class__.__name__}')
        self._configuration = value
        self.update_args(*self._configuration.args)
        self.update_kwargs(*self._configuration.kwargs)

    def copy_configuration(self) -> "ExecutionSequence":
        """
        Copies the configuration of a ExecutionSequence instance.

        :return: ExecutionSequence instance with identical configuration
        """
        return self.__class__(
            self.configuration,
            **self.kwargs,
        )

    def as_dict(self) -> dict:
        """extra type cast for arguments"""
        dct = super(ExecutionSequence, self).as_dict()
        del dct['arguments']
        dct['triggered'] = self.triggered
        if self.triggered is True:
            actions = self.args
        else:
            actions = self.configuration.action_sequence
        dct['actions'] = [
            action.as_dict() for action in actions
        ]
        # todo decide how to include relative start times
        return dct

    @property
    @ensure_triggered
    def action_returns(self) -> dict:
        """retrieves the returned values from the actions. Only actions which have completed will have return values"""
        return {
            action.configuration.name: action.action_return for action in self.args
        }

    @property
    @ensure_triggered
    def actions_status(self) -> dict:
        """status of the actions of the instance"""
        # todo consider passing through configured status
        return {action.configuration.name: action.status for action in self.args}

    @property
    @ensure_triggered
    def action_start_times(self) -> dict:
        """times when the prescribed actions were started"""
        if self.triggered is True:
            return {
                action.configuration.name: action.time_started for action in self.args
            }

    @property
    @ensure_triggered
    def action_completion_times(self) -> dict:
        """times when the prescribed actions were completed"""
        if self.triggered is True:
            return {
                action.configuration.name: action.time_completed for action in self.args
            }

    @property
    @ensure_triggered
    def action_durations(self) -> dict:
        """execution durations for the prescribed actions"""
        if self.triggered is True:
            return {
                action.configuration.name: action.action_duration for action in self.args
            }

    @property
    @ensure_triggered
    def started_timestamps(self) -> Dict[str, datetime.datetime]:
        """timestamps for when actions were started"""
        if self.triggered is True:
            return {
                action.configuration.name: action.started_timestamp for action in self.args
            }

    @classmethod
    def build_from_first_action(cls, first_action: ConfiguredAction) -> "ExecutionSequence":
        """
        Builds an execution sequence from a first action and its linked action

        :param first_action: first action to reference
        :return: execution sequence
        """
        raise NotImplementedError  # todo
