"""
Contains classes for managing and applying context to "actions" (functions).

`Action` is a function register which enables default arg/kwarg specification and retrieval of action by function name.

`ConfiguredAction` is an action that is configured to run (allows for multiple configurations of `Action` classes.

`TrackedAction` is an action that may be run with storage of context (duration, time started, function return,
args/kwargs that were used for execution, and error details if any).

"""

from .basic import Action, EvalAction, ActionList
from .configured import (ConfiguredAction, ConfiguredActionList, ThreadedTrackedAction, TrackedActionList,
                         TrackedAction, ConfigurableInstance
                         )
from .logic import ConfiguredDecision, TrackedDecision

__all__ = [
    'Action',
    'EvalAction',
    'ActionList',
    'ConfiguredAction',
    'ConfigurableInstance',
    'ConfiguredActionList',
    'ConfiguredDecision',
    'TrackedAction',
    'TrackedDecision',
    'ThreadedTrackedAction',
    'TrackedActionList',
]

# todo figure out how to trigger a pre-trigger event (e.g. turn on instrument and condition)
#   - executed contextually
#   - or rely on the user to specify pre-events in provided methods
