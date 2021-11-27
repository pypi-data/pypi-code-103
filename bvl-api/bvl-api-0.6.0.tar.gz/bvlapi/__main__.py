#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This script is run when using `python3 -m bvlapi <|club guid|search query>`.

import sys

from bvlapi.cli.search import do_search
from bvlapi.cli.teams import do_teams


def run_script(args):
    """ Main part of script that delegates control to proper handler.
    """
    if len(args) == 0:
        args = ["help"]
    command = args[0]
    if command == "help":
        exit_code = 0
        output = print_help()
    elif command == "search":
        exit_code, output = do_search(args[1:])
    elif command == "teams":
        exit_code, output = do_teams(args[1:])
    else:
        exit_code = 1
        output = "unknown command"
    print(output)
    exit(exit_code)


def print_help():
    """ Prints instructions on how to use script.
    """
    return "\n".join([
        "This CLI tool is used to determine the GUIDs of a club or its teams.",
        "You can use the `search` command to search for a club's GUID:",
        "",
        "    $ python3 -m bvlapi search \"Antwerp\"",
        "",
        "If you know the GUID or stamnr of a club, you can use the `teams`",
        "command to list all the teams of that club:",
        "",
        "    $ python3 -m bvlapi teams \"BVBL1004\"",
        " or ",
        "    $ python3 -m bvlapi teams \"71\"",
        "",
    ])


if __name__ == "__main__":
    run_script([str(arg) for arg in sys.argv[1:]])
