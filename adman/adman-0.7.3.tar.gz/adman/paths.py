import os
from pathlib import Path

def default_datadir():
    # TODO: How would this work on Windows?
    if os.getuid() == 0:
        p = Path("/var/lib")
    else:
        p = Path.home() / '.local/share'
    p /= 'adman'
    p.mkdir(mode=0o700, parents=True, exist_ok=True)
    return p


def default_confdir():
    # TODO: How would this work on Windows?
    if os.getuid() == 0:
        p = Path("/etc")
    else:
        p = Path.home() / '.config'
    p /= 'adman'
    return p


def default_confpath():
    return default_confdir() / 'config.yml'
