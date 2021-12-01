"""User-facing configuration variables."""

import os

from .text import parse_bool_str


# Environment variables and their defaults.
# Whether to operate in debug mode.  Informs whether to warn the user if a simulation
# result file will be overwritten by a run operation.
DEBUG_MODE = True
# DEBUG_MODE = parse_bool_str(os.environ.get("EAGERS_DEBUG_MODE", "False"))
# Path to user directory.
USER_DIR = os.environ.get("EAGERS_USER_DIR", "~/eagers-user")
# Directory name within which files at any level in the user directory will be ignored.
USER_DIR_EXCLUDE_NAME = os.environ.get(
    "EAGERS_USER_DIR_EXCLUDE_NAME", "IGNORED"
).replace(" ", "").splitlines()
