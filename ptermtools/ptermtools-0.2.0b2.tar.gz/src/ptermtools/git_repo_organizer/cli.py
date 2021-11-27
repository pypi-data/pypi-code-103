"""
The Git Repo Organizer (GRO) CLI
"""
import sys
import click


@click.group()
def main(args=None):
    """Console script for gro"""
    click.echo("Hello from gro!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
