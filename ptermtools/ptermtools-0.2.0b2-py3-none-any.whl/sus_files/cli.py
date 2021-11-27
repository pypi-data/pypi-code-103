"""
The Suspecious File Marker (sus-files) 
"""
import sys

import click

from .sus_files import SuspiciousFileDatabase

SUS_FILES_DB = SuspiciousFileDatabase()


@click.group()
@click.version_option()
def main(args=None):
    """Console script for sus-files"""
    click.echo("Hello from sus-files!")
    return 0


@main.command()
@click.argument("fname")
def add(fname):
    SUS_FILES_DB.add(fname)


@main.command()
@click.argument("fname")
def remove(fname):
    SUS_FILES_DB.remove(fname)


@main.command()
def list():
    SUS_FILES_DB.list()


if __name__ == "__main__":
    sys.exit(main())
