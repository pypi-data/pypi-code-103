from typing import Any, List

import pytest
from baby_steps import given, then, when
from district42 import schema
from th import PathHolder
from valera import validate
from valera.errors import (
    ExtraElementValidationError,
    LengthValidationError,
    MaxLengthValidationError,
    MinLengthValidationError,
    TypeValidationError,
)

from district42_exp_types.unordered import UnorderedContainsValidationError, unordered_schema


@pytest.mark.parametrize("value", [
    [],
    [1],
    [1, 2],
    [42, 3.14, "banana"],
])
def test_unordered_type_validation(value: List[Any]):
    with when:
        result = validate(unordered_schema, value)

    with then:
        assert result.get_errors() == []


def test_unordered_type_validation_error():
    with given:
        value = {}

    with when:
        result = validate(unordered_schema, value)

    with then:
        assert result.get_errors() == [
            TypeValidationError(PathHolder(), value, list),
        ]


def test_unordered_no_elements_validation():
    with when:
        result = validate(unordered_schema([]), [])

    with then:
        assert result.get_errors() == []


def test_unordered_homogeneous_elements_validation():
    with given:
        value = [1, 2]

    with when:
        result = validate(unordered_schema([
            schema.int(1),
            schema.int(2),
        ]), value)

    with then:
        assert result.get_errors() == []


def test_unordered_heterogeneous_elements_validation():
    with given:
        value = [42, 3.14, "banana"]

    with when:
        result = validate(unordered_schema([
            schema.int(42),
            schema.float(3.14),
            schema.str("banana"),
        ]), value)

    with then:
        assert result.get_errors() == []


def test_unordered_more_element_validation_error():
    with given:
        value = [1]

    with when:
        result = validate(unordered_schema([]), value)

    with then:
        assert result.get_errors() == [
            ExtraElementValidationError(PathHolder(), actual_value=value[0], index=0),
        ]


def test_unordered_more_elements_validation_error():
    with given:
        value = [1, 2, 3]

    with when:
        result = validate(unordered_schema([schema.int]), value)

    with then:
        assert result.get_errors() == [
            ExtraElementValidationError(PathHolder(), actual_value=value[1], index=1),
            ExtraElementValidationError(PathHolder(), actual_value=value[2], index=2),
        ]


def test_unordered_less_elements_validation_error():
    with given:
        value = [1, 2]

    with when:
        result = validate(unordered_schema([schema.int, schema.int, schema.int]), value)

    with then:
        assert result.get_errors() == [
            UnorderedContainsValidationError(PathHolder(), schema.int)
        ]


def test_unordered_len_validation():
    with given:
        value = [1, 2]

    with when:
        result = validate(unordered_schema.len(2), value)

    with then:
        assert result.get_errors() == []


@pytest.mark.parametrize("value", [
    [1],
    [1, 2, 3],
])
def test_unordered_len_validation_error(value: List[Any]):
    with given:
        length = 2

    with when:
        result = validate(unordered_schema.len(length), value)

    with then:
        assert result.get_errors() == [
            LengthValidationError(PathHolder(), value, length)
        ]


@pytest.mark.parametrize("value", [
    [1, 2],
    [1, 2, 3],
])
def test_unordered_min_len_validation(value: List[Any]):
    with when:
        result = validate(unordered_schema.len(2, ...), value)

    with then:
        assert result.get_errors() == []


def test_unordered_min_len_validation_error():
    with given:
        value = [1]
        min_length = 2

    with when:
        result = validate(unordered_schema.len(min_length, ...), value)

    with then:
        assert result.get_errors() == [
            MinLengthValidationError(PathHolder(), value, min_length)
        ]


@pytest.mark.parametrize("value", [
    [1, 2],
    [1],
])
def test_unordered_max_len_validation(value: List[Any]):
    with when:
        result = validate(unordered_schema.len(..., 2), value)

    with then:
        assert result.get_errors() == []


def test_unordered_max_len_validation_error():
    with given:
        value = [1, 2, 3]
        max_length = 2

    with when:
        result = validate(unordered_schema.len(..., max_length), value)

    with then:
        assert result.get_errors() == [
            MaxLengthValidationError(PathHolder(), value, max_length)
        ]


@pytest.mark.parametrize(("min_length", "max_length"), [
    (2, 2),
    (1, 3),
])
def test_unordered_min_max_len_validation(min_length: int, max_length: int):
    with given:
        value = [1, 2]

    with when:
        result = validate(unordered_schema.len(min_length, max_length), value)

    with then:
        assert result.get_errors() == []


@pytest.mark.parametrize(("min_length", "max_length"), [
    (1, 1),
    (3, 3),
])
def test_unordered_min_max_len_validation_error(min_length: int, max_length: int):
    with given:
        value = [1, 2]

    with when:
        result = validate(unordered_schema.len(min_length, max_length), value)

    with then:
        assert len(result.get_errors()) == 1
