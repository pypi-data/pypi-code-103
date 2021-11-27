"""Logging functions and elements."""

import logging
from typing import Any

import colorlog


def setup_logging(log_level: int) -> None:
    """Setup the logging config."""

    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(asctime)s [pid %(process)d] %(log_color)s%(levelname)s: %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S",
        )
    )

    logging.basicConfig(
        level=log_level,
        handlers=[handler],
    )


class DisableLogger:
    """Disable the logging for a few lines."""

    current_state: int

    def __enter__(self) -> None:
        self.current_state = logging.root.level
        logging.disable(logging.CRITICAL)

    def __exit__(self, exit_type: Any, exit_value: Any, exit_traceback: Any) -> None:
        logging.disable(self.current_state - 1)
