# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
from shrike._core import experimental
import logging

log = logging.getLogger(__name__)


def test_experimental_with_custom_msg(caplog):
    @experimental(message="custom message")
    def foo():
        log.warn("This is foo.")

    with caplog.at_level("WARN"):
        foo()
    assert "custom message" in caplog.text
    assert "This is foo." in caplog.text


def test_experimental_with_default_msg(caplog):
    @experimental()
    def foo(a):
        return a

    with caplog.at_level("WARN"):
        x = foo(1)
    assert x == 1
    assert (
        "This is an experimental feature and could change at any time." in caplog.text
    )
