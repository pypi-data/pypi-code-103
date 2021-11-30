from edition import __version__
from edition.cli import Cli


def entry() -> None:
    Cli.invoke_and_exit(app_version=__version__)


if __name__ == "__main__":
    entry()
