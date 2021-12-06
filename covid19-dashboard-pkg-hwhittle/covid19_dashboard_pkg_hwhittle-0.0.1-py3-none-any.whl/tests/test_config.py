"""test_config module

This module exports functions for testing the config.py module
"""

import covid19dashboard.config as config

def reset_test_environment():
    """
    This function clears the configuration cache
    """
    config.config_cache = None

def test_fetch_config_simple():
    """
    This test ensures that the fetch_config function correctly loads the configuration file
    """
    reset_test_environment()

    config_obj = config.fetch_config("./test-data/test-config.json")
    assert 'foo' in config_obj
    assert 'object' in config_obj

    assert config_obj['foo'] == 'bar'
    assert config_obj['object'] == {
        'a': 1,
        'b': 2
    }

def test_fetch_config_cache():
    """
    This test ensures that the fetch_config function caches the file and doesn't re-read it
    """
    reset_test_environment()

    config_obj      = config.fetch_config("./test-data/test-config.json")
    config_obj_two  = config.fetch_config("./test-data/test-config.json")

    assert config_obj is config_obj_two

def test_fetch_config_error():
    """
    This test ensures the fetch_config function throws a FileNotFoundError if the file
    does not exist.
    """
    reset_test_environment()

    file_not_found_error = False

    try:
        config.fetch_config("this_file_does_not_exist")
    except FileNotFoundError:
        file_not_found_error = True

    assert file_not_found_error is True

def test_get_config_simple():
    """
    This test ensures the get_config function correctly returns the given index
    """
    reset_test_environment()

    filename = "./test-data/test-config.json"

    assert config.get_config("foo", filename) == 'bar'
    assert config.get_config("object", filename) == {
        'a': 1,
        'b': 2
    }

def test_get_config_no_index():
    """
    This test ensures the get_config function correctly returns the whole
    configuration object if the index is None.
    """
    reset_test_environment()

    config_obj = config.get_config(None, "./test-data/test-config.json")

    assert config_obj is not None

def test_get_config_missing_index():
    """
    This test ensures the get_config function returns None if the index is not
    in the configuration object
    """
    reset_test_environment()

    config_obj = config.get_config("missing_index", "./test-data/test-config.json")

    assert config_obj is None
