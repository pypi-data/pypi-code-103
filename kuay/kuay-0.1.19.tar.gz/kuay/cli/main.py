import argparse
from enum import Enum
from herre import Herre
from rich.console import Console
from rich.prompt import Prompt, Confirm
import os
import asyncio

directory = os.getcwd()


class KuayOptions(str, Enum):
    INIT = "init"
    DEPLOY = "dev"


def main(
    script=KuayOptions.INIT,
    name=None,
    path=".",
):

    console = Console()

    if path == ".":
        app_directory = os.getcwd()
        name = name or os.path.basename(app_directory)
    else:
        app_directory = os.path.join(os.getcwd(), path)
        name = name or path

    fakts_path = os.path.join(app_directory, "fakts.yaml")
    run_script_path = os.path.join(app_directory, "run.py")

    if script == KuayOptions.DEPLOY:

        if not os.path.isfile(run_script_path):
            console.print(f"Could't find a run.py in {app_directory} {run_script_path}")
            return
        if not os.path.isfile(fakts_path):
            console.print(f"{app_directory} does not have a valid fakts.yaml")
            return

    if script == KuayOptions.INIT:

        console.print("Initializing Arkitekt Started. Lets do this!")

        if not os.path.isfile(fakts_path):
            console.print(
                f"There seems to have been a previous App initialized at {app_directory}"
            )
            return


def entrypoint():
    parser = argparse.ArgumentParser(description="Say hello")
    parser.add_argument("script", type=KuayOptions, help="The Script Type")
    parser.add_argument("path", type=str, help="The Script Type")
    args = parser.parse_args()

    main(
        script=args.script,
        path=args.path,
    )


if __name__ == "__main__":
    entrypoint()
