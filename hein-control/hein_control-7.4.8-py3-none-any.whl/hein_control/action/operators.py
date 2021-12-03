"""functions for execution of specific actions"""
import logging

from .basic import Action
from .configured import ConfiguredAction, TrackedActionList, TrackedAction

logger = logging.getLogger(__name__)


@Action.register_action
def execute_sequence_actions(*actions: TrackedAction, **kwargs):
    """
    Executes a series of actions with the provided kwargs.

    e.g. if there is a method named "do_this_thing" which expects the keyword argument "value", the expected syntax
    of kwargs would be

        {
            "do_this_thing": {"value": 42},
        }

    :param actions: tracked action instances
    :param kwargs: additional keyword arguments for those instances.
    """
    if any([isinstance(action, TrackedAction) is False for action in actions]):
        raise TypeError('a non-TrackedAction object was provided as an action')
    for action in actions:
        action_kwargs = {}
        if action.configuration.name in kwargs:
            action_kwargs.update(kwargs[action.configuration.name])
        elif action.configuration.action.name in kwargs:
            action_kwargs.update(kwargs[action.configuration.action.name])
        logger.debug(f'executing {action}')
        action(**action_kwargs)
        if action.error is True:
            details = f'an error was encountered executing {action}: {action.error_details}'
            logger.error(details)
            raise RuntimeError(details)


@Action.register_action
def decision(*logic_checks: TrackedAction) -> ConfiguredAction:
    """
    Iterates through the provided Evaluation Actions until a True return is retrieved. The function will then return
    the next_action of that action.

    :param logic_checks: TrackedAction instances
    :return: next action of the first ConfiguredAction execution where True is determined
    """
    for action in logic_checks:
        # todo consider a try/except here to allow the provided actions to error without issue
        action()  # execute the action
        # if the action return is True, return the next action
        if action.action_return is True:
            return action.next_action


@Action.register_action
def run_automation(first_action: ConfiguredAction, **kwargs):
    """
    Runs an automation sequence by referencing the next action of each action after execution.

    :param first_action: first step to execute
    :param kwargs: keyword arguments corresponding to the actions
    """
    logger.info(f'beginning automation sequence with first step {first_action}')
    executed_actions: TrackedActionList = TrackedActionList()
    next_action = first_action
    while next_action is not None:
        # todo kwargs
        next_action = next_action.get_tracked_from_config()  # convert to tracked action
        logger.debug(f'executing {next_action}')
        if next_action.configuration.name in kwargs:
            logger.debug('updating kwargs as specified')
            next_action.update_kwargs(**kwargs[next_action.configuration.name])
        next_action()
        # append to list of executed actions
        executed_actions.append(next_action)
        if next_action.error is True:
            details = f'an error was encountered executing {next_action}: {next_action.error_details}'
            logger.error(details)
            logger.error(f'The executed actions before encountering the error: {executed_actions}')
            raise RuntimeError(details, executed_actions)
        # retrieve next action and continue
        next_action = next_action.next_action
    logger.info(f'automation completed, ran {len(executed_actions)} actions')
    return executed_actions
