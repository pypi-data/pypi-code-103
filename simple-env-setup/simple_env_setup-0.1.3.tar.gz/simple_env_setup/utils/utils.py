import atexit
import shutil
from functools import partial, wraps
from importlib.resources import read_text
from os import environ, popen
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from typing import (Callable, Concatenate, Iterable, Optional, ParamSpec,
                    TypeVar, Union)

import click
from simple_env_setup import resources
from termcolor import colored

# ---------------------------------------------------------------------------- #
#                                 Click Options                                #
# ---------------------------------------------------------------------------- #
force = partial(click.option, "--force", "-f", "force",
                is_flag=True, help="Force resinstallation.")
no_root = partial(click.option, "--no-root", "-n", "no_root",
                  is_flag=True, help="No sudo premission.")


# ---------------------------------------------------------------------------- #
#                                    Logging                                   #
# ---------------------------------------------------------------------------- #


def log_section(section: str):
    print(colored(section.upper(), color="magenta", attrs=["bold"]))


def log_msg(title: Optional[str], msg: str):
    if title is None:
        title = ""
    else:
        title += ": "
    print(f"{colored(title, color='magenta', attrs=['bold'])}{msg}")


def log_start(name: str):
    print(colored("  running:", color="cyan", attrs=["bold"]), name, end="")


def log_done():
    print(colored(" (SUCCESS)", color="green", attrs=["bold"]))


def log_error(logs: Union[str, Iterable[str]]):
    print(colored(" (ERROR)", color="red", attrs=["bold"]))
    if isinstance(logs, str):
        logs = [logs]
    for log in logs:
        print(log)
    exit(1)


def last_words(logs: str | Iterable[str]):
    print(colored("\nERROR:", color="red", attrs=["bold"]))
    if isinstance(logs, str):
        logs = [logs]
    for log in logs:
        print(log)
    exit(1)


# ---------------------------------------------------------------------------- #
#                                   Execution                                  #
# ---------------------------------------------------------------------------- #


def run_shell(cmd: str) -> str:
    log_start(cmd)
    if environ.get("ENV_SETUP_DRY_RUN"):
        log = ""
        status = None
    else:
        proc = popen(cmd)
        log = proc.read()
        status = proc.close()
    if status is None:
        log_done()
        return log
    else:
        log_error(log)


T = TypeVar("T")
P = ParamSpec("P")


def run_python(fn: Callable[P, T]) -> Callable[Concatenate[str, P], T]:
    @ wraps(fn)
    def wrapped(name: str, *args: P.args, **kwargs: P.kwargs) -> T:
        log_start(name)
        try:
            out = fn(*args, **kwargs)
            log_done()
            return out
        except Exception as e:
            log_error(str(e))
    return wrapped


# ---------------------------------------------------------------------------- #
#                                    checks                                    #
# ---------------------------------------------------------------------------- #


def is_installed(cmd: str):
    return shutil.which(cmd) is not None


def should_install(cmd: str, force: bool):
    installed = is_installed(cmd)
    if installed:
        if force:
            log_section(f"Reinstall {cmd}")
            return True
        else:
            log_section(f"{cmd} already installed")
            return False
    else:
        log_section(f"Install {cmd}")
        return True

# ---------------------------------------------------------------------------- #
#                              Resource Management                             #
# ---------------------------------------------------------------------------- #


def read(filename: str) -> str:
    return read_text(resources, filename)


@run_python
def overwrite(dir: Path, filename: str) -> None:
    # Check existence
    dir.mkdir(exist_ok=True, parents=True)
    content = read(filename)
    with(open(dir / filename, "w")) as f:
        f.write(content)


# ---------------------------------------------------------------------------- #
#                                Dir Management                                #
# ---------------------------------------------------------------------------- #


def get_tmp_dir() -> Path:
    tmp_dir_path = environ.get("ENV_SETUP_TMP_DIR")
    if tmp_dir_path and Path(tmp_dir_path).is_dir():
        return Path(tmp_dir_path)
    else:
        tmp_dir_path = mkdtemp()
        environ["ENV_SETUP_TMP_DIR"] = tmp_dir_path
        return Path(tmp_dir_path)


def get_home_dir() -> Path:
    home_dir_path = environ.get("HOME")
    if not home_dir_path:
        last_words("Hmmm... weird... you don't seem to have a home directory")
    else:
        return Path(home_dir_path)


def get_home_bin() -> Path:
    home_bin = get_home_dir() / ".local" / "bin"
    home_bin.mkdir(parents=False, exist_ok=True)
    return home_bin


@atexit.register
def rm_temp_dir():
    tmp_dir_path = environ.get("ENV_SETUP_TMP_DIR")
    if tmp_dir_path is not None and Path(tmp_dir_path).is_dir():
        rmtree(Path(tmp_dir_path))
