from argparse import ArgumentParser
from pathlib import Path
from typing import List, Optional, Tuple

from dinject.inject import inject_file
from dinject.version import get_version


def make_response(cli_args: Optional[List[str]] = None) -> Tuple[str, int]:
    """Makes a response to the given command line arguments."""

    parser = ArgumentParser(
        description="Executes Markdown code blocks and injects the results.",
        epilog="Made with love by Cariad Eccleston: https://github.com/cariad/dinject",
    )

    parser.add_argument("files", help="Markdown files", nargs="*")

    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="print the version",
    )

    args = parser.parse_args(cli_args)

    if args.version:
        return get_version(), 0

    if not args.files:
        return "You must specify at least one Markdown file.", 1

    for file in args.files:
        inject_file(path=Path(file))

    return "", 0
