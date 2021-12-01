import os
import re
import subprocess

import semver
import typer
from plumbum import FG, ProcessExecutionError
from plumbum import local as lr

app = typer.Typer()


def git(*args, output=True):
    r = subprocess.check_output(["git"] + list(args))
    if output:
        print(args)  # noqa
        print(r)  # noqa
    return r


def git_num_changes():
    return len(git("status", "--porcelain").splitlines())


def get_version():
    return git("describe", "--tags").decode().strip()


@app.command()
def push_repo():
    git(
        "remote",
        "set-url",
        "--push",
        "origin",
        re.sub(r".+@([^/]+)/", r"git@\1:", os.environ["CI_REPOSITORY_URL"]),
    )
    git("push", "-o", "ci.skip", "origin", get_version())


@app.command()
def bump_version():
    git("tag")
    try:
        v = get_version()
        n = semver.bump_patch(v)
    except (subprocess.CalledProcessError, ValueError):
        print("initialise versioning with 1.0.0")  # noqa
        git("tag", "1.0.0")
        return

    if "-" not in v:
        return

    print(f"bump from {v} to {n}")  # noqa
    git("tag", n)


@app.command()
def local(pipeline: str = typer.Argument("build")):
    has_changes = git_num_changes() > 0
    try:
        if has_changes:
            git("add", ".")
            git("commit", "-m", "local debug commit")
        (
            lr["gitlab-runner"][
                "exec",
                "docker",
                "--docker-extra-hosts",
                "docker:192.168.0.1",
                "--docker-privileged=true",
                pipeline,
            ]
            & FG
        )
    except ProcessExecutionError:
        exit(1)
    finally:
        if has_changes:
            git("reset", "HEAD~1")
