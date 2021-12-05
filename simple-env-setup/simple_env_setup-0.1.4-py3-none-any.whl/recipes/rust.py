import click
from simple_env_setup.utils.utils import (force, get_home_dir, get_tmp_dir,
                                          log_section, overwrite, run_shell,
                                          should_install)

# ---------------------------------------------------------------------------- #
#                                    rustup                                    #
# ---------------------------------------------------------------------------- #


@click.command()
@force()
def install_rust(force: bool) -> None:
    if should_install("rustup", force):
        tmp_dir = get_tmp_dir()
        run_shell(
            f"wget -O {tmp_dir / 'rust_install.sh'} https://sh.rustup.rs")
        run_shell(
            f"bash {tmp_dir / 'rust_install.sh'} -y")
        run_shell(
            "rustup default nightly")


# ---------------------------------------------------------------------------- #
#                                rust libraries                                #
# ---------------------------------------------------------------------------- #

@click.command()
def install_rust_libs() -> None:
    log_section("Install rust libraries")
    run_shell(
        "cargo install bat tidy-viewer ripgrep fd-find macchina procs du-dust git-delta exa sd grex bandwhich")
    overwrite("replace ~/.gitconfig", get_home_dir(), ".gitconfig")


# ---------------------------------------------------------------------------- #
#                                    bundle                                    #
# ---------------------------------------------------------------------------- #


@click.command()
@force()
def install_rust_all(force: bool) -> None:
    install_rust.callback(force)
    install_rust_libs.callback()
