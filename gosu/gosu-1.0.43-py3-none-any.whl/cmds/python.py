import glob
import json
import os
import subprocess

import typer
from plumbum import FG, ProcessExecutionError, local

app = typer.Typer()


def env_from_sourcing(source_path, include_unexported_variables=True):
    source = "{}source {}".format(
        "set -a && " if include_unexported_variables else "", source_path
    )
    dump = 'python3 -c "import os, json; print(json.dumps(dict(os.environ)))"'
    with subprocess.Popen(
        ["/bin/bash", "-c", f"{source} && {dump}"], stdout=subprocess.PIPE
    ) as pipe:
        return json.loads(pipe.stdout.read())


def _manage_env_vars():
    try:
        from dotenv import dotenv_values

        env_vars = dotenv_values(".env")
        for name, value in env_vars.items():
            local.env[name] = value
        return env_vars
    except ModuleNotFoundError:
        print("dotenv not found, dotenv autoloading disabled")  # noqa


def _run(*cmds):
    _manage_env_vars()
    print(cmds)  # noqa
    try:
        local.get(f".venv/bin/{cmds[0]}")[cmds[1:]] & FG
    except ProcessExecutionError:
        exit(1)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def run(ctx: typer.Context):
    _run(*ctx.args)


@app.command()
def sh():
    _manage_env_vars()
    for k, v in env_from_sourcing(".venv/bin/activate").items():
        local.env[k] = v
    local.get(local.env["SHELL"].split("/")[-1]) & FG


@app.command()
def venv(requirements: str = typer.Argument("requirements.txt")):
    _manage_env_vars()
    local["python3"]["-m", "venv", ".venv"] & FG
    _run("pip", "install", "-U", "pip", "wheel", "gosu")
    if os.path.isfile(requirements):
        _run("pip", "install", "-r", requirements)


def _get_pkg_pyfiles():
    files = list(
        filter(
            lambda e: all(
                [not (x in e) for x in ["node_modules", "migrations", "build"]]
            ),
            glob.glob("**/*.py", recursive=True),
        )
    )
    print(files)  # noqa
    return files


@app.command()
def fix():
    _run("pyupgrade", "--py38-plus", "--exit-zero-even-if-changed", *_get_pkg_pyfiles())
    _run("isort", "--profile", "black", *_get_pkg_pyfiles())
    _run("black", *_get_pkg_pyfiles())
    _run("flake8", "--config", f"{os.path.dirname(__file__)}/../.flake8")


@app.command()
def lint():
    _run("pyupgrade", "--py38-plus", *_get_pkg_pyfiles())
    _run("isort", "--profile", "black", "-c", *_get_pkg_pyfiles())
    _run("black", "--check", *_get_pkg_pyfiles())
    _run("flake8", "--config", f"{os.path.dirname(__file__)}/../.flake8")


@app.command()
def test():
    rcfile = f"--rcfile={os.path.dirname(__file__)}/../.coveragerc_python"
    local.env["PYTHONGPATH"] = "./src"
    _run(
        "coverage",
        "run",
        rcfile,
        "-m",
        "pytest",
        "-o",
        "console_output_style=progress",
    )
    _run("coverage", "report", rcfile)


@app.command()
def build():
    _run("python3", "setup.py", "sdist", "bdist_wheel")


@app.command()
def precommit():
    fix()
    test()
    build()
