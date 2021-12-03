"""Interface for creating a db-contrib-tool plugin."""

import abc


class Subcommand(abc.ABC):
    """A db-contrib-tool subcommand to execute."""

    def execute(self):
        """Execute the subcommand."""
        raise NotImplementedError()


class PluginInterface(abc.ABC):
    """Subcommand/plugin interface."""

    def add_subcommand(self, subparsers):
        """
        Add parser options for this plugin.

        :param subparsers: argparse subparsers
        """
        raise NotImplementedError()

    def parse(self, subcommand, parser, parsed_args, **kwargs):
        """
        Resolve command-line options to a Subcommand or None.

        :param subcommand: equivalent to parsed_args.command
        :param parser: parser used
        :param parsed_args: output of parsing
        :param kwargs: additional args
        :return: None or a Subcommand
        """
        raise NotImplementedError()
