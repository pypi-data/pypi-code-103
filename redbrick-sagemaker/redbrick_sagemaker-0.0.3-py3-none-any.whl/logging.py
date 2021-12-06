"""Logging for redbrick_sagemaker."""

import logging


class Logger:
    """Custom logger."""

    def __init__(self):
        """Construct logging object."""
        # Create a custom logger
        logger_ = logging.getLogger(__name__)
        logger_.setLevel(logging.INFO)

        # Create handlers
        console = logging.StreamHandler()

        # Create formatters and add it to handlers
        console.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

        # Add handlers to the logger
        logger_.addHandler(console)

        self.logger = logger_


logger = Logger().logger
