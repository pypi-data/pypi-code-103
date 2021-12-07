from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("qwilfish")
except PackageNotFoundError:
    print("No qwilfish installation found!")
    pass
