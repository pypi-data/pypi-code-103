import click
from simple_env_setup.utils.rc import update_rc
from simple_env_setup.utils.utils import (force, get_home_bin, get_home_dir,
                                          get_tmp_dir, no_root, overwrite,
                                          run_shell, should_install)

# ---------------------------------------------------------------------------- #
#                                      zsh                                     #
# ---------------------------------------------------------------------------- #


def install_zsh_no_root() -> None:
    tmp_dir = get_tmp_dir()
    run_shell(
        f"git clone https://gist.github.com/e11816b78ab5c33cbaffad96683b28f0.git {tmp_dir / 'gist'}")
    run_shell(
        f"bash {tmp_dir / 'gist' / 'install_zsh_no_root.sh'}")


def install_zsh_root() -> None:
    run_shell("sudo apt-get install -y zsh")
    run_shell(
        "wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | sh")


@click.command()
@no_root()
@force()
def install_zsh(no_root: bool, force: bool) -> None:
    if should_install("zsh", force):
        if no_root:
            install_zsh_no_root()
        else:
            install_zsh_root()
        overwrite("replace ~/.zshrc", get_home_dir(), ".zshrc")
        run_shell("mamba init --all")


# ---------------------------------------------------------------------------- #
#                                   starship                                   #
# ---------------------------------------------------------------------------- #


def install_starship_no_root() -> None:
    tmp_dir = get_tmp_dir()
    run_shell(
        f"wget -O {tmp_dir / 'starship_install.sh'} https://starship.rs/install.sh")
    home_bin = get_home_bin()
    run_shell(
        f"bash {tmp_dir / 'starship_install.sh'} -y -b {home_bin}")


def install_starship_root() -> None:
    tmp_dir = get_tmp_dir()
    run_shell(
        f"wget -O {tmp_dir / 'starship_install.sh'} https://starship.rs/install.sh")
    run_shell(
        f"bash {tmp_dir / 'starship_install.sh'} -y")


@click.command()
@no_root()
@force()
def install_starship(no_root: bool, force: bool) -> None:
    if should_install("starship", force):
        if no_root:
            install_starship_no_root()
        else:
            install_starship_root()
        overwrite("replace ~/.config/starship.toml",
                  get_home_dir() / ".config", "starship.toml")
        update_rc(["starship"])

# ---------------------------------------------------------------------------- #
#                                    bundle                                    #
# ---------------------------------------------------------------------------- #


@click.command()
@no_root()
@force()
def install_zsh_all(no_root: bool, force: bool) -> None:
    install_zsh.callback(no_root, force)
    install_starship.callback(no_root, force)
