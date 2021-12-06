#!/usr/bin/env python3

try:
    from .version import version as __version__
except ImportError:
    __version__ = "UNKNOWN"


if __name__ == '__main__':
    from . import __main__
    __main__.main()
