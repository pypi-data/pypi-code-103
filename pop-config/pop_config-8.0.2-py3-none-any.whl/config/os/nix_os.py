"""
Read in keys from *NIX like oses - AKA Environement variables
"""
import os

__virtualname__ = "system"


def __virtual__(hub):
    """
    Don't load on Windows, this is for *nix style platforms
    """
    # detect if on windows
    if os.name == "nt":
        return False, "This module isn't for windows"
    return (True,)


def collect(hub, key):
    """
    Collect the option from environment variable if present
    """
    key = key.upper()
    if key in os.environ:
        return os.environ[key]
    return None
