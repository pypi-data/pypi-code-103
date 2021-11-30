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
"""CLI application to generate a new OpenDiamond scope"""


import os
import sys
from datetime import datetime, timedelta

import click
from dateutil.tz import tzutc

from . import ScopeCookie
from .cli_options import CONTEXT_SETTINGS


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("-v", "--verbose", is_flag=True, help="be verbose")
@click.option(
    "-b",
    "--blaster",
    metavar="URL",
    help="JSON Blaster that can relay for the specified servers",
)
@click.option(
    "-s",
    "--server",
    "servers",
    metavar="HOST",
    multiple=True,
    required=True,
    help="server that accepts the cookie (can be repeated)",
)
@click.option(
    "-e",
    "--expires",
    metavar="TIME",
    default=3600,
    help="time in seconds until cookie expires (3600)",
)
@click.option(
    "-k",
    "--keyfile",
    type=click.File("rb"),
    help="X509 private key ($HOME/.diamond/key.pem)",
)
@click.option(
    "-u",
    "--scopeurl",
    "scopeurls",
    metavar="URL",
    multiple=True,
    help="URL from which scopelist can be retrieved (can be repeated)",
)
# pylint: disable=too-many-arguments
def generate(verbose, blaster, servers, expires, keyfile, scopeurls):
    """Generates an OpenDiamond® scope cookie.

    If no --scopeurl option is given, the list of scope URLs will be read
    from stdin.
    """
    if keyfile is None:
        app_dir = click.get_app_dir("diamond", force_posix=True)
        key_pem = os.path.join(app_dir, "key.pem")
        keyfile = click.open_file(key_pem, "rb")

    # Read private key
    with keyfile as fhandle:
        keydata = fhandle.read()

    # Gather scope data
    if len(scopeurls) == 0:
        scopeurl = [u.strip() for u in sys.stdin]

    # Calculate cookie expiration time
    expires = datetime.now(tzutc()) + timedelta(seconds=expires)

    # Build and sign the cookie
    cookie = ScopeCookie.generate(servers, scopeurl, expires, keydata, blaster=blaster)

    # Print decoded cookie to stderr if verbose
    if verbose:
        click.echo(str(cookie), err=True)

    # Print final cookie to stdout
    print(cookie.encode(), end=" ")
