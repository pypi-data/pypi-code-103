#!/usr/bin/env python

# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import spliced
from spliced.logger import setup_logger
import argparse
import sys
import os


def get_parser():
    parser = argparse.ArgumentParser(
        description="Spliced",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Global Variables
    parser.add_argument(
        "--debug",
        dest="debug",
        help="use verbose logging to debug.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--quiet",
        dest="quiet",
        help="suppress additional output.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--version",
        dest="version",
        help="show software version.",
        default=False,
        action="store_true",
    )

    description = "actions for spliced"
    subparsers = parser.add_subparsers(
        help="spliced actions",
        title="actions",
        description=description,
        dest="command",
    )

    # print version and exit
    subparsers.add_parser("version", description="show software version")

    splice = subparsers.add_parser(
        "splice",
        description="generate predictions for a splice.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    # Generate matrix of splice commands and outputs, etc.
    matrix = subparsers.add_parser(
        "matrix",
        description="generate matrix of splices (intended for GitHub actions or similar)",
    )
    matrix.add_argument(
        "-g",
        "--generator",
        dest="generator",
        help="generator to use (defaults to spack)",
        choices=["spack"],
        default="spack",
    )

    matrix.add_argument(
        "-o",
        "--outfile",
        help="output matrix to this json file (default will set to GitHub workflow output for matrix).",
        action="store_true",
        default=False,
    )

    matrix.add_argument(
        "-c",
        "--container",
        help="container base to use.",
        default="ghcr.io/buildsi/spack-ubuntu-20.04",
    )

    for command in [matrix, splice]:
        command.add_argument(
            "config_yaml",
            help="A configuration file to run a splice prediction.",
        )

    return parser


def run_spliced():
    """run_spliced to perform a splice!"""

    parser = get_parser()

    def help(return_code=0):
        version = spliced.__version__

        print("\nSpliced Client v%s" % version)
        parser.print_help()
        sys.exit(return_code)

    # If the user didn't provide any arguments, show the full help
    if len(sys.argv) == 1:
        help()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    if args.debug is True:
        os.environ["MESSAGELEVEL"] = "DEBUG"

    # Show the version and exit
    if args.command == "version" or args.version:
        print(shpc.__version__)
        sys.exit(0)

    setup_logger(
        quiet=args.quiet,
        debug=args.debug,
    )

    # retrieve subparser (with help) from parser
    helper = None
    subparsers_actions = [
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ]
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            if choice == args.command:
                helper = subparser
                break

    # Does the user want a shell?
    if args.command == "splice":
        from .splice import main
    if args.command == "matrix":
        from .matrix import main

    # Pass on to the correct parser
    return_code = 0
    try:
        main(args=args, parser=parser, extra=extra, subparser=helper)
        sys.exit(return_code)
    except UnboundLocalError:
        return_code = 1

    help(return_code)


if __name__ == "__main__":
    run_spliced()
