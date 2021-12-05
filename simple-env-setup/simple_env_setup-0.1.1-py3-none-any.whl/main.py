from os import environ

import click

from simple_env_setup.recipes.rust import (install_rust, install_rust_all,
                                           install_rust_libs)
from simple_env_setup.recipes.zsh import (install_starship, install_zsh,
                                          install_zsh_all)
from simple_env_setup.utils.utils import force, no_root


@click.group()
def main():
    pass


@click.command()
@no_root()
@force()
def install(no_root: bool, force: bool) -> None:
    install_zsh_all.callback(no_root, force)
    install_rust_all.callback(force)


main.add_command(install)
main.add_command(install_zsh_all)
main.add_command(install_zsh)
main.add_command(install_starship)
main.add_command(install_rust_all)
main.add_command(install_rust)
main.add_command(install_rust_libs)
