import logging
import os
import time
import traceback
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def timed(name="Task"):
    """Timer block for long-running operations."""
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        logging.info("Task '%s' completed in %.3f seconds", name, duration)


@contextmanager
def silent():
    """Suppress messages from logging module within block."""
    logger = logging.getLogger()
    previous = logger.getEffectiveLevel()
    try:
        logger.setLevel(logging.CRITICAL + 1)
        yield
    finally:
        logger.setLevel(previous)


def debug_traceback():
    """Log traceback if DEBUG level is enabled."""
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        traceback.print_exc()


def path_to_name(path):
    """Convert relative path to Robot Framework import name."""
    if path.parent != Path("."):
        namespace = str(path.parent).replace(os.sep, ".")
        return "{}.{}".format(namespace, path.stem)
    else:
        return path.stem
