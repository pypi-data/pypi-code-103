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
"""Functions to assist with handling application/x-diamond-scope files"""

import click

from .cli_generate import generate
from .cli_import import import_, install, uninstall
from .cli_options import CONTEXT_SETTINGS
from .cli_verify import verify


@click.group("scope", context_settings=CONTEXT_SETTINGS)
@click.version_option(package_name="opendiamond-scope")
def cli():
    """OpenDiamond® scope handling related functions"""


cli.add_command(generate)
cli.add_command(import_)
cli.add_command(install)
cli.add_command(uninstall)
cli.add_command(verify)
