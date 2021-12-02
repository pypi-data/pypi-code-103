import logging
from unittest.mock import call, patch

import pytest

from curvenote.latex.utils import just_log_errors, log_and_raise_errors


@patch.object(logging, "info", wraps=logging.info)
def test_just_log_value_errors_factory(mock_logging):
    @just_log_errors(lambda *args: f"message {args[0]}")
    def under_test(*args):
        raise ValueError("boom")

    under_test(1)
    mock_logging.assert_called_with("message 1")


@patch.object(logging, "error", wraps=logging.error)
def test_just_log_value_errors(mock_logging):
    @log_and_raise_errors(lambda *args: f"message {args[0]}")
    def under_test(*args):
        raise ValueError("boom")

    with pytest.raises(ValueError):
        under_test(1)
    mock_logging.assert_has_calls([call("message 1"), call("Error: %s", "boom")])
