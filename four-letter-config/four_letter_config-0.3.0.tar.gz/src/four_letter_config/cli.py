# -*- coding: utf-8 -*-

"""

four_letter_config.cli

Command line interface

Copyright (C) 2021 Rainer Schwarzbach

This file is part of four_letter_config.

four_letter_config is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

four_letter_config is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import argparse
import datetime
import difflib
import logging
import os
import sys

from four_letter_config import __version__
from four_letter_config import file_handler


#
# Constants
#


RETURNCODE_OK = RETURNCODE_EQUAL = 0
RETURNCODE_DIFFERENT = 1
RETURNCODE_ERROR = 2


#
# Functions
#


def compare_data(arguments):
    """Compare data in the files by dumping both
    to the comparable form and comparing the strings.
    If the --diff switch was specified, write a unified diff of the
    JSON representations.
    """
    file_data = []
    labels = []
    times = []
    for current_file_name in arguments.file_name:
        file_data.append(
            file_handler.comparable_form(
                file_handler.read_file(current_file_name)
            )
        )
        labels.append(f"Data from {current_file_name}")
        times.append(
            datetime.datetime.fromtimestamp(
                os.stat(current_file_name).st_mtime
            )
        )
    #
    if file_data[0] == file_data[1]:
        comparison_result = RETURNCODE_EQUAL
    else:
        comparison_result = RETURNCODE_DIFFERENT
    #
    if arguments.diff:
        sys.stdout.writelines(
            difflib.unified_diff(
                file_data[0].splitlines(keepends=True),
                file_data[1].splitlines(keepends=True),
                fromfile=labels[0],
                tofile=labels[1],
                fromfiledate=times[0].isoformat(),
                tofiledate=times[1].isoformat(),
            )
        )
    else:
        if comparison_result == RETURNCODE_EQUAL:
            logging.debug("Equal data in both files.")
        else:
            logging.debug(
                "Different data in the files - use --diff to show details."
            )
        #
    #
    return comparison_result


def translate_files(arguments):
    """Translate data from the input file to the output file format.
    Overwrite existing files only if the --overwrite option was specified.
    """
    if os.path.exists(arguments.output_file_name):
        if not arguments.overwrite:
            print(
                f"The output file {arguments.output_file_name!r}"
                " already exists. Please use the --overwrite option"
                " to overwrite existing files."
            )
            return RETURNCODE_ERROR
        #
        logging.debug(
            "Overwriting the existing file %r as requested",
            arguments.output_file_name,
        )
    #
    file_handler.write_to_file(
        arguments.output_file_name,
        file_handler.read_file(arguments.input_file_name),
    )
    return RETURNCODE_OK


def main():
    """Parse command line arguments and execute the matching function"""
    main_parser = argparse.ArgumentParser(
        prog="four_letter_config",
        description="Handle four letter config files",
    )
    main_parser.set_defaults(loglevel=logging.INFO)
    main_parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.DEBUG,
        dest="loglevel",
        help="output all messages including debug level",
    )
    main_parser.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const=logging.WARNING,
        dest="loglevel",
        help="limit message output to warnings and errors",
    )
    main_parser.add_argument(
        "--version",
        action="store_true",
        help="print version and exit",
    )
    subparsers = main_parser.add_subparsers()
    #
    # Compare files
    parser_compare = subparsers.add_parser(
        "compare", help="Compare the data stored in two files."
    )
    parser_compare.add_argument(
        "--diff",
        action="store_true",
        help="Produce a unified diff output over a representation of data"
        " in each file",
    )
    parser_compare.add_argument(
        "file_name", nargs=2, help="The files to be compared"
    )
    parser_compare.set_defaults(execute_function=compare_data)
    # Translate files
    parser_translate = subparsers.add_parser(
        "translate",
        help="Translate data stored in the input file"
        " to the output file format.",
    )
    parser_translate.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the output file if it exists",
    )
    parser_translate.add_argument("input_file_name", help="The input file")
    parser_translate.add_argument("output_file_name", help="The output file")
    parser_translate.set_defaults(execute_function=translate_files)
    #
    arguments = main_parser.parse_args()
    if arguments.version:
        print(__version__)
        return RETURNCODE_OK
    #
    logging.basicConfig(
        format="%(levelname)-8s\u2551 %(message)s", level=arguments.loglevel
    )
    try:
        return arguments.execute_function(arguments)
    except AttributeError:
        logging.error("Please specify --version or a subcommand:")
        main_parser.print_help()
    #
    return RETURNCODE_ERROR


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
