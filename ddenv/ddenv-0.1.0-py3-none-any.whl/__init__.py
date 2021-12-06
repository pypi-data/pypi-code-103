"""Docker Dev Environment, easily develop your programs using containers"""

__version__ = "0.1.0"

import os
from typing import Optional

from click_spinner import spinner
from docker.errors import APIError, BuildError, ContainerError
from typer import Abort, Argument, Exit, Option, Typer, echo

from ddenv.managers.core import ManagerNotFoundError, get_manager

app = Typer()


@app.command()
def run(
    command: Optional[list[str]] = Argument(None, help="The command to run"),
    manager: str = Option(
        ..., "--manager", "-m", help="The project manager your project uses"
    ),
    version: Optional[str] = Option(
        None, "--version", "-v", help="The version of the project manager/runtime"
    ),
):
    """Run the command in a Docker container with all the dependencies and source code"""
    try:
        handler = get_manager(manager, version, os.getcwd())
    except ValueError:
        echo(f"Manager {manager} not found", err=True)
        raise Exit(code=1)
    except ManagerNotFoundError:
        echo(f"Manager class in {manager} module not found", err=True)
        raise Exit(code=1)

    echo(f"ddenv {__version__}, running {handler.name}:{handler.version}")

    try:
        if not handler.image_exists:
            echo("Image not found, building image")
            with spinner():
                try:
                    handler.build_base_image()
                except BuildError as e:
                    echo("Error building the image", err=True)
                    echo(e.msg, err=True)
                    raise Abort()
        else:
            echo("Image found")

        echo("Running command\n")
        try:
            container = handler.run_command(command)
            try:
                for output in container.logs(stream=True):
                    echo(output.rstrip())
            except KeyboardInterrupt:
                container.stop()
                raise KeyboardInterrupt()
        except ContainerError as e:
            echo("Error running container", err=True)
            echo(e.stderr, err=True)
            raise Abort

    except APIError:
        echo("Error reaching the docker API", err=True)
        raise Abort()


def main():
    app()
