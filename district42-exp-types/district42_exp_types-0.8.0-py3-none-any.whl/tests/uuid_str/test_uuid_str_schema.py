from uuid import uuid4

from baby_steps import given, then, when
from district42.errors import DeclarationError
from pytest import raises

from district42_exp_types.uuid_str import UUIDStrSchema, schema_uuid_str


def test_uuid_str_declaration():
    with when:
        sch = schema_uuid_str

    with then:
        assert isinstance(sch, UUIDStrSchema)


def test_uuid_str_value_declaration():
    with given:
        value = str(uuid4())

    with when:
        sch = schema_uuid_str(value)

    with then:
        assert sch.props.value == value


def test_uuid_str_invalid_value_type_declaration_error():
    with given:
        value = uuid4()

    with when, raises(Exception) as exception:
        schema_uuid_str(value)

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == ("`schema.uuid_str` value must be an instance of 'str', "
                                        f"instance of 'UUID' {value!r} given")


def test_uuid_str_invalid_value_declaration_error():
    with when, raises(Exception) as exception:
        schema_uuid_str("")

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == "badly formed hexadecimal UUID string"


def test_uuid_str_already_declared_declaration_error():
    with given:
        value = str(uuid4())
        another_value = str(uuid4())

    with when, raises(Exception) as exception:
        schema_uuid_str(value)(another_value)

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == f"`schema.uuid_str({value!r})` is already declared"


def test_uuid_str_lowercase_declaration():
    with when:
        sch = schema_uuid_str.lowercase()

    with then:
        assert sch.props.is_lowercase is True


def test_uuid_str_lowercase_already_declared_declaration_error():
    with given:
        value = str(uuid4()).upper()

    with when, raises(Exception) as exception:
        schema_uuid_str(value).lowercase()

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == (f"`schema.uuid_str({value!r})` "
                                        "is already declared")


def test_uuid_str_lowercase_already_declared_lowercase_declaration_error():
    with when, raises(Exception) as exception:
        schema_uuid_str.lowercase().lowercase()

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == "`schema.uuid_str.lowercase()` is already declared"


def test_uuid_str_lowercase_already_declared_uppercase_declaration_error():
    with when, raises(Exception) as exception:
        schema_uuid_str.uppercase().lowercase()

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == "`schema.uuid_str.uppercase()` is already declared"


def test_uuid_str_uppercase_declaration():
    with when:
        sch = schema_uuid_str.uppercase()

    with then:
        assert sch.props.is_uppercase is True


def test_uuid_str_uppercase_already_declared_declaration_error():
    with given:
        value = str(uuid4()).lower()

    with when, raises(Exception) as exception:
        schema_uuid_str(value).uppercase()

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == (f"`schema.uuid_str({value!r})` "
                                        "is already declared")


def test_uuid_str_uppercase_already_declared_uppercase_declaration_error():
    with when, raises(Exception) as exception:
        schema_uuid_str.uppercase().uppercase()

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == "`schema.uuid_str.uppercase()` is already declared"


def test_uuid_str_uppercase_already_declared_lowercase_declaration_error():
    with when, raises(Exception) as exception:
        schema_uuid_str.lowercase().uppercase()

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == "`schema.uuid_str.lowercase()` is already declared"
