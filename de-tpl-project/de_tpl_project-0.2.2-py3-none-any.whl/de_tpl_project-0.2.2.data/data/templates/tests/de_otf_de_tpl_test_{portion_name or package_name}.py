""" default integration and unit tests for new app/namespace-root/de-template/... projects.

remove the outsourced marker in the first line of this test module if you want to add more specialized tests.
"""
import importlib
import os

from ae.base import TESTS_FOLDER
from ae.inspector import module_attr

conf_test_mod = importlib.import_module("conftest")
# noinspection PyUnresolvedReferences
skip_gitlab_ci = conf_test_mod.skip_gitlab_ci


@skip_gitlab_ci
def test_version():
    main_module = importlib.import_module("{'main' if os.path.isfile('main' + PY_EXT) else import_name}")
    # noinspection PyUnresolvedReferences
    pkg_version = main_module.__version__
    assert pkg_version
    assert isinstance(pkg_version, str)
    assert pkg_version.count(".") == 2
    assert pkg_version == module_attr("{import_name}", '__version__')


@skip_gitlab_ci
def test_docstring():
    main_module = importlib.import_module("{'main' if os.path.isfile('main' + PY_EXT) else import_name}")
    pkg_docstring = main_module.__doc__
    assert pkg_docstring
    assert isinstance(pkg_docstring, str)
    assert pkg_docstring == module_attr("{import_name}", '__doc__')


def test_tests_folder_exists():
    assert os.path.isdir(TESTS_FOLDER)
