# __version__ is placeholder
# It gets set in the build/publish process (publish_with_credentials.sh)
__version__ = "0.5.1-dev202112021638484585"

from jetpack._remote.interface import remote
from jetpack._task.interface import function, schedule
from jetpack.cmd import root
from jetpack.redis import redis


def run() -> None:
    root.cli()
