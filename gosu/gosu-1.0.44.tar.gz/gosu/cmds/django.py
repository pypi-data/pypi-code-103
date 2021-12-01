import os

import typer
from plumbum import local

from gosu.cmds.python import _manage_env_vars, _run, build, fix

app = typer.Typer()


def _pm(*cmds):
    _manage_env_vars()
    _run("python", "-m", f"{get_project()}.manage", *cmds)


def get_project():
    if "DJANGO_SETTINGS_MODULE" not in local.env:
        return "example"
    else:
        return local.env["DJANGO_SETTINGS_MODULE"].split(".")[0]


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def pm(ctx: typer.Context):
    _pm(*ctx.args)


@app.command()
def migrate():
    _pm("makemigrations")
    _pm("migrate")


@app.command()
def test():
    _manage_env_vars()

    local.env["DEFAULT_CACHE"] = "locmemcache://"
    local.env["QUEUE_CACHE"] = "locmemcache://"
    rcfile = f"--rcfile={os.path.dirname(__file__)}/../.coveragerc_django"
    _run(
        "coverage",
        "run",
        "--concurrency=multiprocessing",
        "--parallel-mode",
        rcfile,
        f"{get_project()}/manage.py",
        "test",
        "--parallel=3",
        ".",
        get_project(),
    )
    _run("coverage", "combine", rcfile)
    _run("coverage", "report", rcfile)


@app.command()
def precommit():
    fix()
    test()
    build()


@app.command()
def notebook():
    local.env["DJANGO_ALLOW_ASYNC_UNSAFE"] = True
    _pm("shell_plus", "--notebook")
