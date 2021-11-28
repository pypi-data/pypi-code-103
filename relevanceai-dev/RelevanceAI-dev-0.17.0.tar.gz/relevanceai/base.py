import sys
import time

from relevanceai.config import CONFIG
from relevanceai.transport import Transport
from relevanceai.logger import LoguruLogger


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


class Base(Transport, LoguruLogger):
    """Base class for all relevanceai utilities"""

    def __init__(self, project: str, api_key: str, base_url: str):
        self.project = project
        self.api_key = api_key
        self.base_url = base_url
        self.config = CONFIG
        # Initialize logger
        super().__init__()
