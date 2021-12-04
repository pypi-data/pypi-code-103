"""
Cline helps you build command line applications by separating the two concerns
of "understanding the command line arguments you receive" and "operating on
strongly-typed arguments", and helps you to write clean, testable tasks.

Homepage: https://github.com/cariad/cline

Documentation: https://cariad.github.io/cline/
"""

from importlib.resources import open_text

from cline.cli import ArgumentParserCli, Cli, RegisteredTasks
from cline.cli_args import CommandLineArguments
from cline.exceptions import CannotMakeArguments
from cline.tasks import AnyTask, AnyTaskType, Task

with open_text(__package__, "VERSION") as t:
    __version__ = t.readline().strip()

__all__ = [
    "AnyTask",
    "AnyTaskType",
    "ArgumentParserCli",
    "Cli",
    "CommandLineArguments",
    "CannotMakeArguments",
    "RegisteredTasks",
    "Task",
]
