"""
`cline.cli` contains CLI implementations, which are the entry points and task
orchestrators of the host application.

If you're happy using Python's baked-in `argparse.ArgumentParser` to parse
arguments then create a CLI that inherits from `ArgumentParserCli`.

To create a CLI with a custom argument parser then inherit from `Cli`.
"""

from cline.cli.argument_parser_cli import ArgumentParserCli
from cline.cli.cli import Cli, RegisteredTasks

__all__ = [
    "ArgumentParserCli",
    "Cli",
    "RegisteredTasks",
]
