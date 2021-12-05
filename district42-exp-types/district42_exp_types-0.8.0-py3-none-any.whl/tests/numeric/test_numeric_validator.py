import pytest
from baby_steps import given, then, when
from th import PathHolder
from valera import validate
from valera.errors import (
    MaxValueValidationError,
    MinValueValidationError,
    TypeValidationError,
    ValueValidationError,
)

from district42_exp_types.numeric import schema_numeric


def test_numeric_type_validation():
    with when:
        result = validate(schema_numeric, "42")

    with then:
        assert result.get_errors() == []


def test_numeric_type_validation_error():
    with given:
        value = 42

    with when:
        result = validate(schema_numeric, value)

    with then:
        assert result.get_errors() == [TypeValidationError(PathHolder(), value, str)]


def test_numeric_value_validation():
    with given:
        value = "42"

    with when:
        result = validate(schema_numeric(value), value)

    with then:
        assert result.get_errors() == []


def test_numeric_value_validation_error():
    with given:
        expected_value = "42"
        actual_value = "43"

    with when:
        result = validate(schema_numeric(expected_value), actual_value)

    with then:
        assert result.get_errors() == [
            ValueValidationError(PathHolder(), actual_value, expected_value)
        ]


@pytest.mark.parametrize("value", ["1", "2"])
def test_numeric_min_value_validation(value: str):
    with when:
        result = validate(schema_numeric.min(1), value)

    with then:
        assert result.get_errors() == []


def test_numeric_min_value_validation_error():
    with given:
        min_value = 1
        actual_value = "0"

    with when:
        result = validate(schema_numeric.min(min_value), actual_value)

    with then:
        assert result.get_errors() == [
            MinValueValidationError(PathHolder(), actual_value, min_value)
        ]


@pytest.mark.parametrize("value", ["1", "2"])
def test_numeric_max_value_validation(value: str):
    with when:
        result = validate(schema_numeric.max(2), value)

    with then:
        assert result.get_errors() == []


def test_numeric_max_value_validation_error():
    with given:
        max_value = 1
        actual_value = "2"

    with when:
        result = validate(schema_numeric.max(max_value), actual_value)

    with then:
        assert result.get_errors() == [
            MaxValueValidationError(PathHolder(), actual_value, max_value)
        ]


@pytest.mark.parametrize("value", ["1", "2", "3"])
def test_numeric_min_max_value_validation(value: int):
    with when:
        result = validate(schema_numeric.min(1).max(3), value)

    with then:
        assert result.get_errors() == []


def test_numeric_min_max_greater_value_validation_error():
    with given:
        min_value = 1
        max_value = 3
        actual_value = "4"

    with when:
        result = validate(schema_numeric.min(min_value).max(max_value), actual_value)

    with then:
        assert result.get_errors() == [
            MaxValueValidationError(PathHolder(), actual_value, max_value)
        ]


def test_numeric_min_max_less_value_validation_error():
    with given:
        min_value = 1
        max_value = 3
        actual_value = "0"

    with when:
        result = validate(schema_numeric.min(min_value).max(max_value), actual_value)

    with then:
        assert result.get_errors() == [
            MinValueValidationError(PathHolder(), actual_value, min_value)
        ]
