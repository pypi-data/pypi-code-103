import click
from typing import Union
from pathlib import Path
from pyfiglet import Figlet
from rich.panel import Panel
from rich import print
from jais.__init__ import NAME, VERSION, DESCRIPTION, ROOT_DIR

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
@click.argument('path', type=click.Path(exists=True))
def set_cwd(path: Union[str, Path]):
    """Add Current Working Directory path to settings"""
    from jais.utils.fileloader import load_json, save_json
    path = str(Path(path).resolve())
    jais_settings_path = ROOT_DIR/'configs/jais_settings.json'
    # Load settings from file or create empty dict
    JAIS_CNF = load_json(jais_settings_path) if jais_settings_path.exists() else {}
    # Add Current Working Directory path to settings
    JAIS_CNF['JAIS_CWD'] = path
    # Save back
    save_json(JAIS_CNF, jais_settings_path)
    print(f"Added [bold]JAIS_CWD={path}[/bold].")

if __name__ == '__main__':
    cli()