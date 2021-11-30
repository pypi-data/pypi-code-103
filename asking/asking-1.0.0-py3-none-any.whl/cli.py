from argparse import ArgumentParser
from typing import List, Type

from cline import AnyTask, ArgumentParserCli

import asking.tasks


class AskingCLI(ArgumentParserCli):
    def make_parser(self) -> ArgumentParser:
        """
        Gets the argument parser.
        """

        parser = ArgumentParser(
            description="Asking script tester",
            epilog="Made with love by Cariad Eccleston: https://github.com/cariad/asking",
        )

        parser.add_argument("path", help="path", nargs="?")

        parser.add_argument(
            "--no-color",
            help="disables colourful output",
            action="store_true",
        )

        parser.add_argument(
            "--version",
            help="show version and exit",
            action="store_true",
        )
        return parser

    def register_tasks(self) -> List[Type[AnyTask]]:
        """
        Gets the tasks that this CLI can perform.
        ordered
        """

        return [
            asking.tasks.PerformTask,
        ]
