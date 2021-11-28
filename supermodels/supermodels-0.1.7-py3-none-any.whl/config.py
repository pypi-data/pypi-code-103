"""Provides configuration options for the supermodels package."""
import enum
import logging
import os


class Environment(enum.Enum):
    """Provides an enumeration of the available environments."""

    DEVELOPMENT = "dev"
    PRODUCTION = "pro"
    STAGING = "stag"


ENVIRONMENT_DEFAULT = Environment.DEVELOPMENT
LOG_FORMAT_DEFAULT = "%(asctime)s - %(levelname)s: [%(name)s] %(message)s"
LOG_LEVEL_DEFAULT = logging.DEBUG if os.getenv("ENV") == "dev" else logging.INFO
TIMESTAMP_FORMAT_DEFAULT = "%Y-%m-%dT%H:%M:%SZ"

ENVIRONMENT = Environment(os.getenv("ENVIRONMENT", ENVIRONMENT_DEFAULT.value))
LOG_FORMAT = os.getenv("LOG_FORMAT", LOG_FORMAT_DEFAULT)
LOG_LEVEL = os.getenv("LOG_LEVEL", LOG_LEVEL_DEFAULT)
TIMESTAMP_FORMAT = os.getenv("TIMESTAMP_FORMAT", TIMESTAMP_FORMAT_DEFAULT)
