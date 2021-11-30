#!/usr/bin/env python3
"""Robot Framework documentation finder and generator.

Example usage:
> docgen -f html Process
> docgen RPA.*

"""
import argparse
import fnmatch
import logging
import platform
import sys
from pathlib import Path

import robot
from docgen import finder, loader, patcher, converter
from docgen.utils import timed, debug_traceback


DEFAULT_EXCLUDE = [
    r"_*",
    r"*.setup",
    r"*.main",
    r"antigravity",
    r"robot.libraries.Remote",
    r"robot.libraries.Reserved",
]


def filter_include(matches, patterns):
    output = []
    for match in matches:
        for pattern in patterns:
            if fnmatch.fnmatch(match, pattern):
                output.append(match)
                break
    return output


def filter_exclude(matches, patterns):
    output = []
    for match in matches:
        for pattern in patterns:
            if fnmatch.fnmatch(match, pattern):
                logging.debug("Ignoring: %s", match)
                break
        else:
            output.append(match)
    return output


def find(args):
    if args.pattern == "robotframework":
        logging.info("Finding Robot Framework built-in libraries")
        matches = finder.builtins()
        include = "*"
    elif args.pattern == "rpaframework":
        logging.info("Finding RPA Framework libraries")
        matches = finder.rpaframework()
        include = "*"
    else:
        logging.info("Finding libraries with pattern: %s", args.pattern)
        matches = finder.find_all(curdir=(not args.no_curdir))
        include = args.pattern
    return matches, include


def convert(args, match):
    logging.debug("Converting: %s", match)
    try:
        lib = loader.load(match)
        if not args.no_patches:
            patcher.apply_all(lib)
        converter.convert(
            lib, fmt=args.format, output=args.output, relative=args.relative_source
        )
        return True
    except ImportError:
        debug_traceback()
        return False


def create_parser():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "pattern",
        help="library name pattern (default: %(default)s)",
        nargs="?",
        default="*",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output directory (default: %(default)s)",
        type=Path,
        default="dist",
    )
    parser.add_argument(
        "-f",
        "--format",
        help="output format (default: %(default)s)",
        choices=converter.CONVERTERS,
        default="json-html",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        help="pattern to exclude",
        action="append",
        default=DEFAULT_EXCLUDE,
    )
    parser.add_argument(
        "--no-patches",
        action="store_true",
        help="Don't apply automatic patches to generated output",
    )
    parser.add_argument(
        "--no-curdir",
        action="store_true",
        help="Don't parse resources from current directory",
    )
    parser.add_argument(
        "--template", help="HTML template for library documentation page"
    )
    parser.add_argument(
        "-v", "--verbose", help="be more talkative", action="store_true"
    )
    parser.add_argument(
        "--relative-source",
        action="store_true",
        help="Set keyword source as a relative directory",
    )
    return parser


def run(raw_args=None):
    parser = create_parser()
    args = parser.parse_args(raw_args)

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        stream=sys.stdout,
        level=level,
        format="%(asctime)s %(levelname)-8s %(message)s",
    )

    if args.template:
        template = Path(args.template).resolve()
        if not template.is_file():
            parser.error("Template is not a file")

        logging.info("Using HTML template: %s", template)
        robot.htmldata.LIBDOC = str(template)
        robot.libdocpkg.htmlwriter.LIBDOC = str(template)

    with timed("All"):
        with timed("Find"):
            matches, include = find(args)
            matches = filter_include(matches, [include])
            matches = filter_exclude(matches, args.exclude)
            matches.sort()

        if not matches:
            logging.warning("No matches found")
            return

        args.output.mkdir(parents=True, exist_ok=True)

        with timed("Convert"):
            count = 0
            for match in matches:
                if convert(args, match):
                    count += 1
            logging.info("Created %d file(s)", count)
