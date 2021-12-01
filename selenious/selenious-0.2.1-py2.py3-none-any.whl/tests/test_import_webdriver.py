#!/usr/bin/env python
"""Tests for `selenious` decorators package."""


def test_import():
    """Simply imports webdriver to make coverage report happy"""
    from selenious import webdriver

    assert webdriver.Remote is not None


def skip_test_import_asserts():
    """This was an attempt to get 100% coverage, but I can't get it to work."""
    import sys
    import os

    sys.path.insert(0, os.path.join(os.getcwd(), "tests/mock_selenium"))
    from selenious import webdriver

    assert webdriver.Remote == "defined"
