"""User-facing configuration variables."""

import os


# Environment variables and their defaults.
# Path to user directory.
USER_DIR = os.environ.get("BUILDINGPLUS_USER_DIR", "~/buildingplus-user")
