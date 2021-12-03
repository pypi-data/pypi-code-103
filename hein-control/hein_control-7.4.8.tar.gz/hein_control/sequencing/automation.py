"""
Tools for executing a series of actions where the next action is determined by the previous one (linked by next_action).
Automation sequences may include conditional next actions governed by DecisionActions.
"""

import logging
import warnings
from typing import Union, Callable


from ..action.basic import Action
from ..action.configured import ConfiguredAction, ConfiguredActionList, TrackedActionList, ThreadedTrackedAction
from ..action.operators import run_automation

logger = logging.getLogger(__name__)


def build_automation_sequence(*actions: Union[str, Callable, Action, ConfiguredAction]) -> ConfiguredActionList:
    """
    Builds an automation sequence of actions based on the order provided.

    :param actions: actions to link
    :return: built automation sequence of actions
    """
    out = ConfiguredActionList()
    for ind, action in enumerate(actions):
        # if not a step, create a step instance
        if isinstance(action, ConfiguredAction) is False:
            action = ConfiguredAction(action)
        # if there is a previous step, set next step attribute
        if ind > 0:
            out[-1].next_action = action
        out.append(action)
    return out


class ConfiguredAutomation(ConfiguredAction):
    UUID_PREFIX = 'cauto-'

    def __init__(self,
                 first_action: Union[Callable, Action, str, ConfiguredAction],
                 automation_name: str = None,
                 **kwargs,
                 ):
        """
        A class for configuring an automation run

        :param first_action: first action to run
        :param automation_name: name for the automation
        :param kwargs:
        """
        ConfiguredAction.__init__(
            self,
            action=run_automation,
            configuration_name=automation_name,
            **kwargs
        )
        self._first_action: ConfiguredAction = None
        self.first_action = first_action
        # todo add check that each step in the sequence has a next step defined

    @property
    def first_action(self) -> ConfiguredAction:
        """the first action in the automation run"""
        return self._first_action

    @first_action.setter
    def first_action(self, value: ConfiguredAction):
        if isinstance(value, ConfiguredAction) is False:
            value = ConfiguredAction(value)
        self._first_action = value

    def get_tracked_from_config(self, **kwargs) -> "Automation":
        """
        Gets an automation instance from the configured automation

        :param kwargs: additional kwargs that differ from the instance configuration
        :return: automation instance
        """
        return Automation(configuration=self, **kwargs)


class Automation(ThreadedTrackedAction):
    UUID_PREFIX = 'auto-'

    def __init__(self,
                 configuration: Union[str, ConfiguredAutomation],
                 **kwargs,
                 ):
        """
            An Automation is used to run a sequence of Steps. For an Automation, you need to specify what the first step to
        run is.

        An Automation instance is callable. When called, it will run the first Step, get the next_step from
        that first step, and loop through running and retrieving the next Step to run, until there are no more Steps to run.

        The IfStep enables decision making in an Automation

        The Automation class is also important, because all the arguments for all the Steps must be passed into the
        Automation on instantiation, and these arguments may potentially be updated by the Steps. All these arguments for
        the CustomSteps must be passed into an Automation sequence as a dictionary, where the keys are the argument names
        and the values are the initial values for these arguments. These arguments get stored as self.kwargs in the
        Automation instance, and self.kwargs gets used as the arguments to run the CustomSteps. If the CustomStep run
        function has a return value, it MUST be a dictionary, where the keys are argument names (that must correspond to
        a key in the self.kwargs dictionary of the Automation instance), and the values are the new values for the
        arguments; and in this way the arguments for the Automation instance can be updated.

        In short for using the Automation and Steps classes:
        * An Automation instantiation MUST include a dictionary of arguments and initial values to be used by the Steps
            in the Automation, unless no variables need to be passed between/used by multiple Steps
        * The parameter names for all the functions of CustomSteps must be identical to the keys in the kwargs
            dictionary that get passed into an Automation instance on instantiation
        * The return value of any CustomStep must be a dictionary, with the keys being identical to the keys in the
            kwargs dictionary of the Automation instance, and the values are the updated values
        * All these functions for the CustomSteps must also have a **kwargs parameter, to catch arguments that get passed
            through that are not actually required by the functions.
        * An Automation instance must know what the first step to run is
        * Steps need to be 'chained' to each other

        :param Step, first_action: first step in the automation to run
        :param dict, kwargs: all the entry keys need to be identical to the parameter names for the callable actions
            for all the Steps in the automation
        """
        if isinstance(configuration, ConfiguredAutomation) is False:
            configuration = ConfiguredAutomation.class_instance_by_id(configuration)
        self._configuration: ConfiguredAutomation = None  # update type hint
        ThreadedTrackedAction.__init__(
            self,
            configuration=configuration,
            **kwargs,
        )

    def __repr__(self):
        return f'{self.__class__.__name__} first action: {self.configuration}'

    def __call__(self, **kwargs):
        logger.info(f'beginning execution of automation')
        super(Automation, self).__call__(
            self.configuration.first_action,
            **kwargs
        )

    @property
    def configuration(self) -> ConfiguredAutomation:
        """the configured sequence associated with the instance"""
        return self._configuration

    @configuration.setter
    def configuration(self, value: ConfiguredAutomation):
        if isinstance(value, ConfiguredAutomation) is False:
            raise TypeError(f'a ConfiguredSequence must be used as a configuration for {self.__class__.__name__}')
        self._configuration = value
        self.update_args(*self._configuration.args)
        self.update_kwargs(*self._configuration.kwargs)

    @property
    def first_step(self) -> ConfiguredAction:
        """The first step in the Automation run"""
        warnings.warn(  # v6.0.0
            'first_step has been deprecated, access and set first_action instead',
            DeprecationWarning,
            stacklevel=2,
        )
        return self.configuration.first_action

    @property
    def executed_actions(self) -> TrackedActionList:
        """executed actions of the automation run"""
        if self.complete is True:
            return self.action_return

    def run_automation(self,
                       **kwargs,
                       ):
        """
        Run the first step in the automation, and get the next step that results from it. then loop, running the next
        step after that and so on, until the end of the automation has been reached. Will get called when an
        Automation instance is called.

        :param dict, kwargs: dictionary of arguments to run the Steps in the automation. Nothing should need to be
            passed in here for this because the kwargs should have been passed in when the Automation instance was
            instantiated, but if they were not or need to be updated, they can be passed here
        :return:
        """
        warnings.warn(  # v6.0.0
            'the run_automation step as been deprecated, call the class instance directly',
            DeprecationWarning,
            stacklevel=2,
        )
        self.__call__(**kwargs)

    def copy_configuration(self) -> "Automation":
        """
        Copies the configuration of a Automation instance.

        :return: Automation instance with identical configuration
        """
        return self.__class__(
            self.configuration,
            **self.kwargs,
        )


