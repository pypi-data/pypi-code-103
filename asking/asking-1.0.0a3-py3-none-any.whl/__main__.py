from asking import __version__
from asking.cli import AskingCLI


def entry() -> None:
    AskingCLI.invoke_and_exit(app_version=__version__)


if __name__ == "__main__":
    entry()
