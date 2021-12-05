from uuid import UUID, uuid4

from baby_steps import given, then, when
from th import PathHolder
from valera import validate
from valera.errors import TypeValidationError, ValueValidationError

from district42_exp_types.uuid import schema_uuid


def test_uuid_type_validation():
    with when:
        result = validate(schema_uuid, uuid4())

    with then:
        assert result.get_errors() == []


def test_uuid_type_validation_error():
    with given:
        value = str(uuid4())

    with when:
        result = validate(schema_uuid, value)

    with then:
        assert result.get_errors() == [TypeValidationError(PathHolder(), value, UUID)]


def test_uuid_value_validation():
    with given:
        value = uuid4()

    with when:
        result = validate(schema_uuid(value), value)

    with then:
        assert result.get_errors() == []


def test_uuid_value_validation_error():
    with given:
        expected_value = uuid4()
        actual_value = uuid4()

    with when:
        result = validate(schema_uuid(expected_value), actual_value)

    with then:
        assert result.get_errors() == [
            ValueValidationError(PathHolder(), actual_value, expected_value)
        ]
