import pytest
from jsonmanager import JsonObject, flatjson
from tests.example_complex_dicts import (
    _example_1,
    _example_2,
    _object_example_1,
    _object_example_2,
    _object_example_3,
    _return_flat,
)

"""
    Test object json
"""


def test_has_keys():
    data = JsonObject(_object_example_1)

    print(data.keys())

    keys = data.keys()
    assert list(keys) == [
        "to_objects",
    ]


def test_keyword_handling():
    data = JsonObject(_object_example_2)
    assert data.problems is not None


def test_raises_exception():
    data = JsonObject(_object_example_3)
    with pytest.raises(AttributeError):
        value = data.randomkey
        assert value is None


def test_contains_functionality():
    data = JsonObject(_example_1)
    assert "id" in data


def test_retrieve_correct_json_property():
    data = JsonObject(_example_2)
    assert "image" in data.json
    assert "thumbnail" in data.json


def test_flat_example():
    data = flatjson(_example_2)

    assert data == _return_flat
