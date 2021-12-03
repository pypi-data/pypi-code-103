import logging

from typing import Union, Callable, Iterable

from .basic import Action
from .configured import ConfiguredAction, ConfiguredActionList, TrackedActionList, TrackedAction
from .operators import decision


logger = logging.getLogger(__name__)


class ConfiguredDecision(ConfiguredAction):
    UUID_PREFIX = 'cda-'

    def __init__(self,
                 *logic_checks: Union[Callable, Action, str, ConfiguredAction],
                 configuration_name: str = None,
                 **kwargs,
                 ):
        """
        Class for configuring a logic tree. The logic checks will iterate until an action return is True. When that
        condition is met, the next action of that logic check will be returned from the executor.

        :param logic_checks: logic check actions. These must return a bool
        :param configuration_name: name for the configuration
        """
        ConfiguredAction.__init__(
            self,
            action=decision,
            configuration_name=configuration_name,
            **kwargs,
        )
        self._logic_sequence: ConfiguredActionList = ConfiguredActionList()
        self.logic_sequence = logic_checks

    @property
    def logic_sequence(self) -> ConfiguredActionList:
        """list of logic check actions to be performed"""
        return self._logic_sequence

    @logic_sequence.setter
    def logic_sequence(self, value: Iterable):
        self._logic_sequence = ConfiguredActionList(*value)
        for action in self._logic_sequence:
            if action.action.returns_bool is False:
                logger.warning(
                    f'the action {action} does not type hint bool, using this action for decisions may result in '
                    f'unexpected errors'
                )

    def get_tracked_from_config(self, **kwargs) -> "TrackedDecision":
        """
        Generates a tracked instance from the configured action

        :param kwargs: additional kwargs that differ from the instance configuration
        :return: TrackedDecision instance.
        """
        return TrackedDecision(configuration=self, **kwargs)

    def as_dict(self) -> dict:
        dct = super(ConfiguredDecision, self).as_dict()
        dct['logic_sequence'] = self.logic_sequence.as_list()
        return dct


class TrackedDecision(TrackedAction):
    UUID_PREFIX = 'da-'

    def __init__(self,
                 configuration: Union[str, ConfiguredDecision],
                 **kwargs,
                 ):
        """
        When called, given multiple ConfiguredActions, each of which their action must return a bool, sequentially run
        each ConfiguredAction, and for the first ConfiguredAction that returns True, return the next_action of the
        ConfiguredAction

        :param args: ConfiguredActions that have actions that return a bool
        :param configuration_name: optional name for the configuration (for key retrieval)
        """
        if isinstance(configuration, ConfiguredDecision) is False:
            configuration = ConfiguredDecision.class_instance_by_id(configuration)
        self._configuration: ConfiguredDecision = None

        TrackedAction.__init__(
            self,
            configuration=configuration,
            **kwargs,
        )
        self._next_action: ConfiguredAction = None

    def __call__(self, *args, **kwargs):
        logger.info('beginning execution of logic tree')
        # convert configured actions to tracked actions
        actions = TrackedActionList(*self.configuration.logic_sequence)
        super(TrackedDecision, self).__call__(
            *actions,
            **kwargs,
        )
        logger.info(f'logic execution complete')

    @property
    def configuration(self) -> ConfiguredDecision:
        """the configured sequence associated with the instance"""
        return self._configuration

    @configuration.setter
    def configuration(self, value: ConfiguredDecision):
        if isinstance(value, ConfiguredDecision) is False:
            raise TypeError(f'a ConfiguredDecision must be used as a configuration for {self.__class__.__name__}')
        self._configuration = value
        self.update_args(*self._configuration.args)
        self.update_kwargs(*self._configuration.kwargs)

    def copy_configuration(self) -> "TrackedDecision":  # todo update docstring
        """
        Copies the configuration of a ExecutionSequence instance.

        :return: ExecutionSequence instance with identical configuration
        """
        return self.__class__(
            self.configuration,
            **self.kwargs,
        )

    @property
    def next_action(self) -> ConfiguredAction:
        """next action as determined by the logic tree"""
        return self._action_return

    def as_dict(self) -> dict:
        dct = super(TrackedDecision, self).as_dict()
        if self.triggered is True:
            dct['logic_checks'] = dct['arguments']
            del dct['arguments']
        return dct
