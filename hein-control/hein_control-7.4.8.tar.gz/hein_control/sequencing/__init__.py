"""
Tools for managing sequences of actions (execution) or linked chains of actions (automation).

For linear sequences of actions, it is recommended to use the `.sequencing.execution` module. For linked actions
which are linked by `.next_action` attributes use the `.sequencing.automation` module.
"""
from .execution import ExecutionSequence, ConfiguredSequence
from .automation import Automation, ConfiguredAutomation

__all__ = [
    'ConfiguredSequence',
    'ExecutionSequence',
    'ConfiguredAutomation',
    'Automation',
]
