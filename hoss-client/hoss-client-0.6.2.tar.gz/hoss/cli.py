import click

from hoss.commands.upload import upload
from hoss.commands.version import version

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(help="A Command Line Interface to interact with a Hoss server.",
             context_settings=CONTEXT_SETTINGS)
def cli():
    pass


# Add commands from package
cli.add_command(upload)
cli.add_command(version)


if __name__ == '__main__':
    cli()
