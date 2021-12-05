from typing import Any

import pytest
from baby_steps import given, then, when
from district42 import schema
from th import PathHolder

from valera import validate
from valera.errors import ValueValidationError


@pytest.mark.parametrize("value", [
    None,
    True,
    42,
    3.14,
    "banana",
])
def test_const_validation(value: Any):
    with when:
        result = validate(schema.const(value), value)

    with then:
        assert result.get_errors() == []


def test_const_validation_error():
    with given:
        expected_value = "banana"
        actual_value = "apple"

    with when:
        result = validate(schema.const(expected_value), actual_value)

    with then:
        assert result.get_errors() == [
            ValueValidationError(PathHolder(), actual_value, expected_value)
        ]


def test_const_type_validation_kwargs():
    with given:
        expected_value = "banana"
        actual_value = "apple"
        path = PathHolder().items[0]["key"]

    with when:
        result = validate(schema.const(expected_value), actual_value, path=path)

    with then:
        assert result.get_errors() == [
            ValueValidationError(path, actual_value, expected_value)
        ]
