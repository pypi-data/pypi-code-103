"""
`cline.tasks` contains task implementations, which are the units of work that a
Cline-enabled application can invoke.

All tasks must inherit from `Task`.
"""

from cline.tasks.help import HelpTask
from cline.tasks.task import AnyTask, AnyTaskType, Task
from cline.tasks.version import VersionTask

__all__ = [
    "AnyTask",
    "AnyTaskType",
    "HelpTask",
    "Task",
    "VersionTask",
]
