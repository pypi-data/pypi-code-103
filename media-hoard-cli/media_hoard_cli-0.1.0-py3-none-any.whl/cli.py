"""Console script for Media Hoard CLI."""

import sys

import click


@click.command()
def main():
    """Console script for media_hoard_cli."""
    click.echo("Replace this message by putting your code into "
               "media_hoard_cli.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
