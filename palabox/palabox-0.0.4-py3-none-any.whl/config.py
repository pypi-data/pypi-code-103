"""Config file."""

import os


# pylint: disable=too-few-public-methods
class Config:
    """Configuration object."""

    ROOT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
