from typing import Any, List

import pytest
from baby_steps import given, then, when
from district42 import schema
from th import PathHolder
from valera import validate
from valera.errors import ExtraElementValidationError

from district42_exp_types.unordered import UnorderedContainsValidationError, unordered_schema


@pytest.mark.parametrize("value", [
    [],
    [1],
    [1, 2],
])
def test_unordered_contains_validation(value: List[Any]):
    with given:
        sch = unordered_schema([...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == []


@pytest.mark.parametrize("value", [
    [1, 2],
    [1, 2, 3],
    [1, 2, 3, 4],
])
def test_unordered_contains_head_validation(value: List[Any]):
    with given:
        sch = unordered_schema([schema.int(1), schema.int(2), ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == []


def test_unordered_contains_head_validation_incorrect_element_error():
    with given:
        value = []
        sch = unordered_schema([schema.int(1), schema.int(2), ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            UnorderedContainsValidationError(PathHolder(), schema.int(1)),
            UnorderedContainsValidationError(PathHolder(), schema.int(2)),
        ]


def test_unordered_contains_head_validation_missing_element_error():
    with given:
        value = [1]
        sch = unordered_schema([schema.int(1), schema.int(2), ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            UnorderedContainsValidationError(PathHolder(), schema.int(2))
        ]


def test_unordered_contains_head_validation_error_extra_element():
    with given:
        value = [0, 1, 2]
        sch = unordered_schema([schema.int(1), schema.int(2), ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            ExtraElementValidationError(PathHolder(), actual_value=value[0], index=0)
        ]


@pytest.mark.parametrize("value", [
    [1, 2],
    [0, 1, 2],
    [-1, 0, 1, 2],
])
def test_unordered_contains_tail_validation(value: List[Any]):
    with given:
        sch = unordered_schema([..., schema.int(1), schema.int(2)])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == []


def test_unordered_contains_tail_validation_incorrect_element_error():
    with given:
        value = [2]
        sch = unordered_schema([..., schema.int(1), schema.int(2)])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            UnorderedContainsValidationError(PathHolder(), schema.int(1))
        ]


def test_unordered_contains_tail_validation_missing_element_error():
    with given:
        value = [1]
        sch = unordered_schema([..., schema.int(1), schema.int(2)])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            UnorderedContainsValidationError(PathHolder(), schema.int(2))
        ]


@pytest.mark.only
def test_unordered_contains_tail_validation_extra_element_error():
    with given:
        value = [1, 2, 3]
        sch = unordered_schema([..., schema.int(1), schema.int(2)])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            ExtraElementValidationError(PathHolder(), actual_value=value[2], index=2)
        ]


def test_unordered_contains_validation_incorrect_tail_element_error():
    with given:
        value = [1, 3]
        sch = unordered_schema([..., schema.int(1), schema.int(2), ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            UnorderedContainsValidationError(PathHolder(), schema.int(2))
        ]


@pytest.mark.parametrize("value", [
    [1, 2],
    [1, 2, 3],
    [0, 1, 2],
    [0, 1, 2, 3],
])
def test_unordered_contains_body_validation(value: List[Any]):
    with given:
        sch = unordered_schema([..., schema.int(1), schema.int(2), ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == []


def test_unordered_contains_validation_incorrect_head_element_error():
    with given:
        value = [3, 2]
        sch = unordered_schema([..., schema.int(1), schema.int(2), ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            UnorderedContainsValidationError(PathHolder(), schema.int(1))
        ]


def test_unordered_contains_validation_extra_head_element_error():
    with given:
        value = [0, 1]
        sch = unordered_schema([..., schema.int(1), schema.int(2), ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            UnorderedContainsValidationError(PathHolder(), schema.int(2))
        ]


def test_unordered_contains_validation_extra_tail_element_error():
    with given:
        value = [2, 3]
        sch = unordered_schema([..., schema.int(1), schema.int(2), ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            UnorderedContainsValidationError(PathHolder(), schema.int(1))
        ]


def test_unordered_contains_validation_extra_body_element():
    with given:
        value = [1, 0, 2]
        sch = unordered_schema([..., schema.int(1), schema.int(2), ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == []


def test_unordered_contains_validation_missing_tail_element_error():
    with given:
        value = [1]
        sch = unordered_schema([..., schema.int(1), schema.int(2), ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            UnorderedContainsValidationError(PathHolder(), schema.int(2))
        ]


def test_unordered_contains_validation_missing_head_element_error():
    with given:
        value = [2]
        sch = unordered_schema([..., schema.int(1), schema.int(2), ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            UnorderedContainsValidationError(PathHolder(), schema.int(1))
        ]


def test_unordered_contains_validation_incorrect_order():
    with given:
        value = [2, 1]
        sch = unordered_schema([..., schema.int(1), schema.int(2), ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == []


def test_unordered_contains_validation_no_elements_error():
    with given:
        value = []
        sch = unordered_schema([..., schema.int, ...])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            UnorderedContainsValidationError(PathHolder(), schema.int)
        ]
