import argparse
from typing import Any, List, Sequence, Union

from .subcommand import BaseSubcommand


class Engine:
    def __init__(self, name: str, subcommands: List[BaseSubcommand], *args, **kwargs):
        """Main engine for setting up, evaluating, and then running
        subcommands. This should generally be instantiated with all of your
        subcommands and then `run` should be called to execute the correct
        subcommand.

        :param name: name of the command line tool you are creating
        :type subcommands: str
        :param subcommands: subcommands you wish to register for the command line tool.
        :type subcommands: List[BaseSubcommand]
        :raises ValueError: if any subcommand does not inherit from the BaseSubcommand
                            class.
        """

        if not subcommands:
            raise ValueError("Engine must contain at least one subcommand!")

        for subcmd in subcommands:
            if not isinstance(subcmd, BaseSubcommand):
                raise ValueError(f"{subcmd} does not inherit from BaseSubcommand.")

        self.subcommands = subcommands
        self.parser = argparse.ArgumentParser(*args, **kwargs)

        self.subparser = self.parser.add_subparsers(dest="subcommand", required=True)
        for subcmd in subcommands:
            action = self.subparser.add_parser(subcmd.name())
            subcmd.register_args(action)

    def run(self, args: Union[Sequence[str], None] = None):
        """Runs the execution engine by (a) identifying the correct subcommand to run
        and (b) running that subcommand with the registered arguments."""
        _args = vars(self.parser.parse_args(args))

        for subcmd in self.subcommands:
            if _args.get("subcommand") == subcmd.name():
                return subcmd.run(_args)

        self.parser.print_help()
