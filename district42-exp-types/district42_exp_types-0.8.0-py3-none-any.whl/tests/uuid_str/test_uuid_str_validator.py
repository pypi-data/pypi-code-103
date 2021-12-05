from typing import Callable
from uuid import UUID, uuid4

import pytest
from baby_steps import given, then, when
from th import PathHolder
from valera import validate
from valera.errors import TypeValidationError, ValueValidationError

from district42_exp_types.uuid_str import StrCaseValidationError, schema_uuid_str


@pytest.mark.parametrize("func", [str.lower, str.upper])
def test_uuid_str_type_validation(func: Callable[[str], str]):
    with given:
        value = func(str(uuid4()))

    with when:
        result = validate(schema_uuid_str, value)

    with then:
        assert result.get_errors() == []


def test_uuid_str_type_validation_error():
    with given:
        value = uuid4()

    with when:
        result = validate(schema_uuid_str, value)

    with then:
        assert result.get_errors() == [TypeValidationError(PathHolder(), value, str)]


def test_uuid_str_value_type_validation_error():
    with given:
        value = "<uuid>"

    with when:
        result = validate(schema_uuid_str, value)

    with then:
        assert result.get_errors() == [TypeValidationError(PathHolder(), value, UUID)]


@pytest.mark.parametrize(("actual_func", "expected_func"), [
    (str.lower, str.upper),
    (str.upper, str.lower),
])
def test_uuid_str_value_validation(actual_func: Callable[[str], str],
                                   expected_func: Callable[[str], str]):
    with given:
        value = str(uuid4())
        sch = schema_uuid_str(expected_func(value))

    with when:
        result = validate(sch, actual_func(value))

    with then:
        assert result.get_errors() == []


def test_uuid_str_value_validation_error():
    with given:
        expected_value = str(uuid4())
        actual_value = str(uuid4())

    with when:
        result = validate(schema_uuid_str(expected_value), actual_value)

    with then:
        assert result.get_errors() == [
            ValueValidationError(PathHolder(), actual_value, expected_value)
        ]


def test_uuid_str_invalid_value_validation_error():
    with given:
        expected_value = str(uuid4())
        actual_value = ""

    with when:
        result = validate(schema_uuid_str(expected_value), actual_value)

    with then:
        assert result.get_errors() == [
            ValueValidationError(PathHolder(), actual_value, expected_value)
        ]


def test_uuid_str_lowercase_validation():
    with given:
        value = str(uuid4()).lower()

    with when:
        result = validate(schema_uuid_str.lowercase(), value)

    with then:
        assert result.get_errors() == []


def test_uuid_str_lowercase_validation_error():
    with given:
        value = str(uuid4()).upper()

    with when:
        result = validate(schema_uuid_str.lowercase(), value)

    with then:
        assert result.get_errors() == [
            StrCaseValidationError(PathHolder(), value, "lower")
        ]


def test_uuid_str_uppercase_validation():
    with given:
        value = str(uuid4()).upper()

    with when:
        result = validate(schema_uuid_str.uppercase(), value)

    with then:
        assert result.get_errors() == []


def test_uuid_str_uppercase_validation_error():
    with given:
        value = str(uuid4()).lower()

    with when:
        result = validate(schema_uuid_str.uppercase(), value)

    with then:
        assert result.get_errors() == [
            StrCaseValidationError(PathHolder(), value, "upper")
        ]
