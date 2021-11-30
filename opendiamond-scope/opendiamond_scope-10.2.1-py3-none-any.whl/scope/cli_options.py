#
#  The OpenDiamond Platform for Interactive Search
#
# SPDX-License-Identifier: EPL-1.0
#
#  Copyright (c) 2021 Carnegie Mellon University
#  All rights reserved.
#
#  This software is distributed under the terms of the Eclipse Public
#  License, Version 1.0 which can be found in LICENSES/EPL-1.0.
#  ANY USE, REPRODUCTION OR DISTRIBUTION OF THIS SOFTWARE CONSTITUTES
#  RECIPIENT'S ACCEPTANCE OF THIS AGREEMENT
#
"""Common arguments and options for opendiamond CLI applications"""

import pathlib

import click

# use with '@click.command(context_settings=CONTEXT_SETTINGS)'
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

# installation path prefix
prefix_option = click.option(
    "--prefix",
    default=pathlib.Path.home() / ".local",
    type=click.Path(file_okay=False, path_type=pathlib.Path),
    show_default=True,
    help="installation prefix (/usr, /usr/local)",
)
