"""test_logger module

This module exports functions intended to test the logger.py module.

Unfortunately the functions cannot be tested as thoroughly as I would
like since they all use the print function.
"""

from os import path, remove

import covid19dashboard.config as config
import covid19dashboard.logger as logger

def reset_test_environment():
    """
    This function resets the environment to ensure test isolation
    """
    config.config_cache = None
    config_obj = config.fetch_config("./test-data/test-config.json")
    logging_config = config_obj['logging']

    logger.debug_messages = []

    if path.isfile(logging_config['path']):
        remove(logging_config['path'])


def test_log_debug():
    """
    This test ensures the log_debug function appends a message to the debug messages array
    """
    reset_test_environment()

    logger.log_debug("Testing")

    assert len(logger.debug_messages) == 1

def test_log_debug_not_enabled():
    """
    This test ensures the log_debug function does not append the debug message to an array
    if logging is not enabled.
    """
    reset_test_environment()

    # Abuse the fact the config is cached to make changes without loading a separate file
    config.get_config("logging")["enabled"] = False

    logger.log_debug("testing")

    assert len(logger.debug_messages) == 0

def test_log_info_makes_file():
    """
    This test ensures that the log_info function writes to a log file.
    It assumes the use_file config option is true
    """
    reset_test_environment()

    log_file = config.get_config("logging")["path"]

    assert not path.isfile(log_file)

    logger.log_info("test")

    assert path.isfile(log_file)

def test_log_info_not_enabled():
    """
    This test ensures that the log_info function doesn't create a file
    if logging is disabled.
    """
    reset_test_environment()

    logging_config = config.get_config("logging")

    log_file = logging_config["path"]

    logging_config["enabled"] = False

    assert not path.isfile(log_file)

    logger.log_info("test")

    assert not path.isfile(log_file)

def test_log_info_use_file_disabled():
    """
    This test ensures that log_info doesn't create a file if use_file
    is False.
    """
    reset_test_environment()

    logging_config = config.get_config("logging")

    log_file = logging_config["path"]

    logging_config["use_file"] = False

    assert not path.isfile(log_file)

    logger.log_info("test")

    assert not path.isfile(log_file)

def test_log_error_makes_file():
    """
    This test ensures that the log_error function writes to a log file.
    It assumes the use_file config option is true
    """
    reset_test_environment()

    log_file = config.get_config("logging")["path"]

    assert not path.isfile(log_file)

    logger.log_error("test")

    assert path.isfile(log_file)

def test_log_error_not_enabled():
    """
    This test ensures that the log_error function doesn't create a file
    if logging is disabled.
    """
    reset_test_environment()

    logging_config = config.get_config("logging")

    log_file = logging_config["path"]

    logging_config["enabled"] = False

    assert not path.isfile(log_file)

    logger.log_error("test")

    assert not path.isfile(log_file)

def test_log_error_use_file_disabled():
    """
    This test ensures that log_error doesn't create a file if use_file
    is False.
    """
    reset_test_environment()

    logging_config = config.get_config("logging")

    log_file = logging_config["path"]

    logging_config["use_file"] = False

    assert not path.isfile(log_file)

    logger.log_error("test")

    assert not path.isfile(log_file)

def test_log_error_dump_debug():
    """
    This test ensures that log_error will dump debug history
    """
    reset_test_environment()

    logging_config = config.get_config("logging")

    log_file = logging_config["path"]

    assert not path.isfile(log_file)

    logging_config["use_file"] = True
    logging_config["dump_debug_on_error"] = True
    logging_config["dump_debug_count"] = 10
    logger.debug_messages = [ 'examplar test message' for _ in range(0, 20) ]

    logger.log_error("Examplar Error")

    assert path.isfile(log_file)

    with open(log_file, 'r', encoding='UTF-8') as file:
        data = file.read()

    assert data.find("examplar test message\n"*10) != -1
    assert data.find("examplar test message\n"*11) == -1
