#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pprint
import sys

import click

import airmailer

from ..logging import logger


@click.group(invoke_without_command=True)
@click.option('--version/--no-version', '-v', default=False, help="Print the current version and exit.")
@click.pass_context
def cli(ctx, version):
    """
    airmailer command line interface.
    """

    if version:
        print(airmailer.__version__)
        sys.exit(0)
