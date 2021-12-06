"""
Test unit test mock classes
"""

import pytest

from sys_toolkit.tests.mock import (
    MockCalledMethod,
    MockCheckOutput,
    MockException,
    MOCK_ERROR_MESSAGE
)

MOCK_KWARGS = {
    'demo': 'Demo arguments',
    'errortype': ValueError,
}


class MockError(Exception):
    """
    Test raising custom exception with custom argument processing
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.call_args = args
        self.call_kwargs = kwargs


def test_tests_mock_called_method_no_args():
    """
    Test initializing and calling MockCalledMethod with no arguments
    """
    mock_method = MockCalledMethod()
    value = mock_method()
    assert value is None
    assert mock_method.call_count == 1
    assert mock_method.args == [()]
    assert mock_method.kwargs == [{}]

    mock_method()
    assert mock_method.call_count == 2
    assert mock_method.args == [(), ()]
    assert mock_method.kwargs == [{}, {}]


def test_tests_mock_called_method_args_and_value():
    """
    Test using MockCalledMethod to mock calls
    """
    mock_method = MockCalledMethod(return_value=MOCK_ERROR_MESSAGE)
    value = mock_method()
    assert value == MOCK_ERROR_MESSAGE
    assert mock_method.call_count == 1
    assert mock_method.args == [()]
    assert mock_method.kwargs == [{}]

    value = mock_method(MOCK_ERROR_MESSAGE)
    assert value == MOCK_ERROR_MESSAGE
    assert mock_method.call_count == 2
    assert mock_method.args == [(), (MOCK_ERROR_MESSAGE,)]
    assert mock_method.kwargs == [{}, {}]

    value = mock_method(called=mock_method)
    assert value == MOCK_ERROR_MESSAGE
    assert mock_method.call_count == 3
    assert mock_method.args == [(), (MOCK_ERROR_MESSAGE,), ()]
    assert mock_method.kwargs == [{}, {}, {'called': mock_method}]


def test_tests_mock_exception_no_args():
    """
    Mock raising generic exception without specifying any arguments
    """
    mock_error = MockException()
    with pytest.raises(Exception) as raised_error:
        mock_error()
    assert mock_error.call_count == 1
    assert mock_error.args == [()]
    assert mock_error.kwargs == [{}]
    # pylint: disable=protected-access
    exception = raised_error._excinfo[1]
    assert str(exception) == MOCK_ERROR_MESSAGE


def test_tests_mock_check_output():
    """
    Test utility callback to mock subprocess.check_output. Look for this known
    line (this function's signature) from output
    """
    mock_check_output = MockCheckOutput(__file__)
    stdout = mock_check_output()
    assert mock_check_output.call_count == 1
    assert isinstance(stdout, bytes)

    line = 'def test_tests_mock_check_output():'
    assert line in str(stdout, 'utf-8').splitlines()


def test_tests_mock_exception_no_args_no_default_message():
    """
    Mock raising generic exception without default error message
    """
    mock_error = MockException(default_message=False)
    with pytest.raises(Exception) as raised_error:
        mock_error()
    assert mock_error.call_count == 1
    assert mock_error.args == [()]
    assert mock_error.kwargs == [{}]
    # pylint: disable=protected-access
    exception = raised_error._excinfo[1]
    assert str(exception) != MOCK_ERROR_MESSAGE


def test_tests_mock_exception_value_error():
    """
    Mock raising ValueError without specifying any arguments
    """
    mock_error = MockException(exception=ValueError)
    with pytest.raises(ValueError) as raised_error:
        mock_error()
    assert mock_error.call_count == 1
    assert mock_error.args == [()]
    assert mock_error.kwargs == [{}]
    # pylint: disable=protected-access
    exception = raised_error._excinfo[1]
    assert isinstance(exception, ValueError)
    assert str(exception) == MOCK_ERROR_MESSAGE


def test_tests_mock_exception_custom_error_args():
    """
    Mock raising custom exception with specific arguments
    """
    mock_error = MockException(
        exception=MockError,
        exception_kwargs=MOCK_KWARGS,
    )
    arg = 'argumentative'
    kwargs = {
        'errors': 'yes we like errors'
    }
    with pytest.raises(MockError) as raised_error:
        mock_error(arg, **kwargs)
    assert mock_error.call_count == 1
    assert mock_error.args == [(arg,)]
    assert mock_error.kwargs == [kwargs]
    # pylint: disable=protected-access
    exception = raised_error._excinfo[1]
    assert isinstance(exception, MockError)
    assert str(exception) == ''
