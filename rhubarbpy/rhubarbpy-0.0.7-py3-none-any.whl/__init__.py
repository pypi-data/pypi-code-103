from .loopsum import loopsum, fibonacci
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("rhubarbpy")
except PackageNotFoundError:
    pass
