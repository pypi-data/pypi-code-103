#
#  The OpenDiamond Platform for Interactive Search
#
# SPDX-License-Identifier: EPL-1.0
#
#  Copyright (c) 2009-2021 Carnegie Mellon University
#  All rights reserved.
#
#  This software is distributed under the terms of the Eclipse Public
#  License, Version 1.0 which can be found in LICENSES/EPL-1.0.
#  ANY USE, REPRODUCTION OR DISTRIBUTION OF THIS SOFTWARE CONSTITUTES
#  RECIPIENT'S ACCEPTANCE OF THIS AGREEMENT
#
"""CLI app to validate an OpenDiamond scope"""

from pathlib import Path

import click

from . import ScopeCookie, ScopeError
from .cli_options import CONTEXT_SETTINGS


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument(
    "scope",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.argument(
    "server",
    required=False,
)
@click.argument(
    "certificates",
    required=False,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
def verify(scope, server, certificates):
    """Show content of a scope file and optionally verify the signature."""
    # certificate validation is optional
    if not certificates:
        app_dir = Path(click.get_app_dir("diamond", force_posix=True))
        certificates = app_dir / "CERTS"

    try:
        data = scope.read_text()
        cookies = [ScopeCookie.parse(c) for c in ScopeCookie.split(data)]
        print("\n\n".join([str(c) for c in cookies]))

        if server is not None:
            certdata = certificates.read_text()
            for cookie in cookies:
                cookie.verify([server], certdata)
            print("Cookies verified successfully")
    except ScopeError as exc:
        print(exc)
