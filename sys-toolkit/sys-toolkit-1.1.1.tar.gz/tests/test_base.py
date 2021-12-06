"""
Unit tests for sys_toolkit.base module
"""

from sys_toolkit.base import LoggingBaseClass


def test_logging_base_class_defaults(capsys):
    """
    Test attributes of LoggingBaseClass
    """
    obj = LoggingBaseClass()
    assert obj.__is_debug_enabled__ is False
    assert obj.__is_silent__ is False

    error = 'test error'
    debug = 'debug message'
    message = 'test message'
    obj.debug(debug)
    obj.error(error)
    obj.message(message)

    captured = capsys.readouterr()
    assert captured.err.splitlines() == [error]
    assert captured.out.splitlines() == [message]


def test_logging_base_class_silent_debug(capsys):
    """
    Test LoggingBaseClass with silent and debug flags set
    """
    obj = LoggingBaseClass(debug_enabled=True, silent=True)
    assert obj.__is_debug_enabled__ is True
    assert obj.__is_silent__ is True

    error = 'test error'
    debug = 'debug message'
    message = 'test message'
    obj.debug(debug)
    obj.error(error)
    obj.message(message)

    captured = capsys.readouterr()
    assert captured.err.splitlines() == [debug, error]
    assert captured.out == ''
