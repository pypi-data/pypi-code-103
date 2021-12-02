from email.policy import default
from typing import ValuesView
import click
from jais.utils import load_default_configs
from pyfiglet import Figlet
from rich import print
from jais.__init__ import ROOT_DIR

# Load project info
CONTEXT_SETTINGS = dict(auto_envvar_prefix='COMPLEX')
# Load project config file and logger, CNF0 means default configuration
CNF0, LOG = load_default_configs()

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
@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        # * BANNER
        # Find more fonts here: http://www.figlet.org/examples.html
        f = Figlet(font='smslant')
        banner = 'J  A I  S'
        # banner = f"..._ {banner} _..."
        click.secho(f"{f.renderText(banner)}", fg='yellow')
        click.echo(f"""Welcome to {click.style('Just Artificial Intelligence Snippets (JAIS)', fg='yellow')} CLI.

    Type `{click.style(f"jais --help", fg='yellow')}` for usage details
    """)
        click.echo(ctx.get_help())

    else:
        click.secho(f"\n[@ {ctx.invoked_subcommand}]...", fg='cyan')


# ----------------------------------------> ADDITIONAL INFORMATION :

@cli.command()
def default_configs():
    """Show default configuration settings from jais/configs/default.yaml"""
    print("Default package config file is present @", end=' ')
    print(f"`[yellow]{ROOT_DIR}/configs/default.yaml[/yellow]`")
    print("\nThis file contains the following settings:")
    print(CNF0)

# ----------------------------------------> RUN EXAMPLES :
@cli.command()
@click.option(
    '-t',
    '--example_task_name', 
    type=click.Choice(['cifar10', 'cifar100'], case_sensitive=False),
    default=None,
    required=True,
    show_default=None,
    help='name of example task out of the given choices.'
)
def run_example(example_task_name):
    """Run example training tasks"""
    import subprocess
    if example_task_name == 'cifar10':
        subprocess.run(['python', f"{ROOT_DIR}/examples/cifar10.py"])
    

if __name__ == '__main__':
    cli()
