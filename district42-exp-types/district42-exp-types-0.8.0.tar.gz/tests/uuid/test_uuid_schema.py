from uuid import uuid4

from baby_steps import given, then, when
from district42.errors import DeclarationError
from pytest import raises

from district42_exp_types.uuid import UUIDSchema, schema_uuid


def test_uuid_declaration():
    with when:
        sch = schema_uuid

    with then:
        assert isinstance(sch, UUIDSchema)


def test_uuid_value_declaration():
    with given:
        value = uuid4()

    with when:
        sch = schema_uuid(value)

    with then:
        assert sch.props.value == value


def test_uuid_invalid_value_type_declaration_error():
    with given:
        value = str(uuid4())

    with when, raises(Exception) as exception:
        schema_uuid(value)

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == ("`schema.uuid` value must be an instance of 'UUID', "
                                        f"instance of 'str' {value!r} given")


def test_uuid_already_declared_declaration_error():
    with given:
        value = uuid4()
        another_value = uuid4()

    with when, raises(Exception) as exception:
        schema_uuid(value)(another_value)

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == f"`schema.uuid({value!r})` is already declared"
