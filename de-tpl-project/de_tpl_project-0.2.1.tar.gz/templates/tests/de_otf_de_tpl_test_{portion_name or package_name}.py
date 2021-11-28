""" default integration and unit tests for new app/namespace-root/de-template/... projects.

remove the outsourced marker in the first line of this test module if you want to add more specialized tests.
"""
import importlib
import os

from ae.base import TESTS_FOLDER
from ae.inspector import module_attr

main_module = importlib.import_module("{'main' if os.path.isfile('main' + PY_EXT) else import_name}")


def test_version():
    # noinspection PyUnresolvedReferences
    pkg_version = main_module.__version__
    assert pkg_version
    assert isinstance(pkg_version, str)
    assert pkg_version.count(".") == 2
    assert pkg_version == module_attr("{import_name}", '__version__')


def test_docstring():
    pkg_docstring = main_module.__doc__
    assert pkg_docstring
    assert isinstance(pkg_docstring, str)
    assert pkg_docstring == module_attr("{import_name}", '__doc__')


def test_tests_folder_exists():
    assert os.path.isdir(TESTS_FOLDER)
