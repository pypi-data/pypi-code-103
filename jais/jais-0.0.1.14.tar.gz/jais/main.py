from email.policy import default
import click
from typing import Any, Union
from pathlib import Path
from pyfiglet import Figlet
from rich.panel import Panel
from rich import print
from jais.__init__ import NAME, VERSION, DESCRIPTION, ROOT_DIR
from jais.utils import load_default_configs

# Load project info
CONTEXT_SETTINGS = dict(auto_envvar_prefix='COMPLEX')

# ----------------------------------------> CLI ENTRY and INITIAL SETTINGS :
# Check environment variables


def check_required_settings() -> None:
    from jais.utils.fileloader import load_json
    JAIS_CNF = load_json(ROOT_DIR/'configs/jais_settings.json')
    if 'JAIS_CWD' not in JAIS_CNF.keys():
        _msg = ("JAIS's current working directory path is not set. "
                "This is required if `[bold].yaml[/bold]` configuration files "
                "contains `[bold]!cwd[/bold]` tag which renders as current working "
                "directory path."
                "\nRun [yellow]jais set-cwd /path/to/project/folder[/yellow] "
                "command to set this path."
                )
        print(Panel.fit(_msg, border_style="red"))
    else:
        click.secho("OK", fg='green')

# ENTRY POINT


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        # * BANNER
        # Find more fonts here: http://www.figlet.org/examples.html
        f = Figlet(font='smslant')
        banner = ' '.join(NAME)
        # banner = f"..._ {banner} _..."
        click.secho(f"{f.renderText(banner)}\nv{VERSION}", fg='yellow')
        # Check required settings
        check_required_settings()
        # CLI message
        click.echo(f"""Welcome to {click.style(DESCRIPTION, fg='yellow')} CLI.

    Type `{click.style(f"{NAME.lower()} --help", fg='yellow')}` for usage details
    """)
        click.echo(ctx.get_help())

    else:
        click.secho(f"\n[Running {ctx.invoked_subcommand}]...", fg='cyan')


@cli.command()
@click.argument('key')
@click.argument('value')
@click.option('--is_path',
              default=False,
              type=bool,
              is_flag=True,
              help="Use to convert relative path to absolute path if the `value` argument is a path.")
def add_item(key: Union[int, tuple, str], value: Any, is_path: bool):
    """Add key:value pair/item to jais_settings.json"""
    if is_path:
        value = str(Path(value).resolve())
    from jais.utils.fileloader import load_json, save_json
    jais_settings_path = ROOT_DIR/'configs/jais_settings.json'
    # Load settings from file or create empty dict
    JAIS_CNF = load_json(
        jais_settings_path) if jais_settings_path.exists() else {}
    # Add Current Working Directory path to settings
    JAIS_CNF[key] = value
    # Save back
    save_json(JAIS_CNF, jais_settings_path)
    print(f"Added [bold]{key}:{value}[/bold]")


@cli.command()
@click.argument('path', type=click.Path(exists=True))
def set_cwd(path: Union[str, Path]):
    """Add Current Working Directory path to settings"""
    import subprocess
    subprocess.run([NAME.lower(), 'add-item', 'JAIS_CWD', path, '--is_path'])

# ----------------------------------------> ADDITIONAL INFORMATION :


@cli.command()
def default_configs():
    """Show default configuration settings from jais/configs/default.yaml"""
    CNF, _ = load_default_configs()
    print("Default package config file is present @", end=' ')
    print(f"`[yellow]{ROOT_DIR}/configs/default.yaml[/yellow]`")
    print("\nThis file contains the following settings:")
    print(CNF)

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
