from argparse import ArgumentParser
from typing import List

from cline.cli.cli import Cli
from cline.cli_args import CommandLineArguments


class ArgumentParserCli(Cli[ArgumentParser]):
    """
    A command line interface that uses `argparse.ArgumentParser` to parse
    command line arguments.
    """

    def make_cli_args(self, args: List[str]) -> CommandLineArguments:
        """
        Parses `args` to make and return `CommandLineArguments`.

        To refer to this `CommandLineArguments` instance later, get
        `self.cli_args` rather than call this function multiple times.

        Arguments:
            args: Command line arguments

        Returns:
            Parsed command line arguments
        """

        known, unknown = self.parser.parse_known_args(args)
        return CommandLineArguments(
            known=vars(known),
            unknown=unknown,
        )

    def write_help(self) -> None:
        """
        Renders application help to the output writer.
        """

        self.parser.print_help(self.out)
