from argparse import ArgumentParser

from cline import ArgumentParserCli, RegisteredTasks

import edition.tasks
from edition.presses import keys


class Cli(ArgumentParserCli):
    def make_parser(self) -> ArgumentParser:
        parser = ArgumentParser(
            description="Lightweight documentation generator",
            epilog="Made with love by Cariad Eccleston: https://github.com/cariad/edition",
        )

        parser.add_argument("source", help="source document", nargs="?")
        parser.add_argument(
            "output",
            help="output document (will emit to stdout if omitted)",
            nargs="?",
        )

        parser.add_argument("--log-level", help="log level", nargs="?")

        parser.add_argument(
            "--press",
            help="output format",
            metavar=f"{{{','.join(keys())}}}",
        )

        parser.add_argument(
            "--version",
            help="show version and exit",
            action="store_true",
        )

        return parser

    def register_tasks(self) -> RegisteredTasks:
        return [
            edition.tasks.PressTask,
        ]
