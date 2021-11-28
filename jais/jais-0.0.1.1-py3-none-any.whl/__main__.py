import os
import click
from jais.utils import load_config, ROOT_DIR, get_logger
from pyfiglet import Figlet

# Load project info
CONTEXT_SETTINGS = dict(auto_envvar_prefix='COMPLEX')
# Load Config file
CNF = load_config(os.getenv('JAIS_CNF_PATH'))


# ----------------------------------------> LOGGING :
# create logger
LOG = get_logger(CNF)
# #! Example logging
# LOG.debug('debug message')
# LOG.info('info message')
# LOG.warning('warn message')
# LOG.error('error message')
# LOG.critical('critical message')


# ----------------------------------------> CLI :
class ComplexCLI(click.MultiCommand):
    """CLI modules finder and loader"""

    def list_commands(self, ctx) -> list:
        """
        This function creates a list of command (`cli.py`) files

        Args:
            ctx: context manager.

        Returns:
            list of CLI files names.
        """
        cli_files_list = []
        # Look for modules that should be loaded with CLI
        for name in ROOT_DIR.iterdir():
            # Remove any __pycache__ like folders
            if str(name).startswith("__"):
                continue
            # Get full path of the module
            dirname = ROOT_DIR/name
            # Look for dtip and dkip like folders
            if dirname.is_dir():
                # name of the folder that contains `cli.py` file
                cli_files_list.append(name)
        cli_files_list.sort()
        return cli_files_list

    def get_command(self, ctx, name: str) -> click.core.Command:
        """This function imports commands from `cli.py` files

        Args:
            ctx: click context object
            name: name of the folder from which cli.py file should be loaded

        Returns:
            returns commands.
        """

        try:
            # {name} is the package like `dtip` and `dkip` and
            # `.cli` is the `cli.py` file inside these.
            mod = __import__(f"jais.{name}.cli", None, None, ["cli"])
        except ImportError:
            return

        return mod.cli


# * Entry point
@click.group(cls=ComplexCLI, invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        # * BANNER
        # Find more fonts here: http://www.figlet.org/examples.html
        f = Figlet(font='smslant')
        banner = 'J A I S'
        # banner = f"..._ {banner} _..."
        click.secho(f"{f.renderText(banner)}", fg='yellow')
        click.echo(f"""Welcome to {click.style('Just Artificial Intelligence Snippets (JAIS)', fg='yellow')} CLI.

    Type `{click.style(f"jais --help", fg='yellow')}` for usage details
    """)
        click.echo(ctx.get_help())

    else:
        click.secho(f"\n[@ {ctx.invoked_subcommand}]...", fg='cyan')

if __name__ == '__main__':
    cli()
