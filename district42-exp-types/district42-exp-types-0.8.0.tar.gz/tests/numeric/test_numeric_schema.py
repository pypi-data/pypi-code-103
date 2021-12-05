from baby_steps import given, then, when
from district42.errors import DeclarationError
from pytest import raises

from district42_exp_types.numeric import NumericSchema, schema_numeric


def test_numeric_declaration():
    with when:
        sch = schema_numeric

    with then:
        assert isinstance(sch, NumericSchema)


def test_numeric_value_declaration():
    with given:
        value = "42"

    with when:
        sch = schema_numeric(value)

    with then:
        assert sch.props.value == value


def test_numeric_invalid_value_type_declaration_error():
    with when, raises(Exception) as exception:
        schema_numeric(42)

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == ("`schema.numeric` value must be an instance of 'str', "
                                        "instance of 'int' 42 given")


def test_numeric_invalid_value_declaration_error():
    with when, raises(Exception) as exception:
        schema_numeric("a")

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == "invalid literal for int() with base 10: 'a'"


def test_numeric_already_declared_declaration_error():
    with when, raises(Exception) as exception:
        schema_numeric("42")("42")

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == "`schema.numeric('42')` is already declared"


def test_numeric_min_value_declaration():
    with given:
        min_value = 1

    with when:
        sch = schema_numeric.min(min_value)

    with then:
        assert sch.props.min == min_value


def test_numeric_invalid_min_value_type_declaration_error():
    with when, raises(Exception) as exception:
        schema_numeric.min("42")

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == ("`schema.numeric` value must be an instance of 'int', "
                                        "instance of 'str' '42' given")


def test_numeric_value_already_declared_min_declaration_error():
    with when, raises(Exception) as exception:
        schema_numeric.min(1)("42")

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == "`schema.numeric.min(1)` is already declared"


def test_numeric_min_value_already_declared_less_value_declaration_error():
    with given:
        sch = schema_numeric("42")

    with when, raises(Exception) as exception:
        sch.min(43)

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == (
            f"`{sch!r}` min value must be less than or equal to 42, 43 given"
        )


def test_numeric_min_value_already_declared_min_declaration_error():
    with when, raises(Exception) as exception:
        schema_numeric.min(1).min(2)

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == "`schema.numeric.min(1)` is already declared"


def test_numeric_max_value_declaration():
    with given:
        max_value = 2

    with when:
        sch = schema_numeric.max(max_value)

    with then:
        assert sch.props.max == max_value


def test_numeric_invalid_max_value_type_declaration_error():
    with when, raises(Exception) as exception:
        schema_numeric.max("42")

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == ("`schema.numeric` value must be an instance of 'int', "
                                        "instance of 'str' '42' given")


def test_numeric_value_already_declared_max_declaration_error():
    with when, raises(Exception) as exception:
        schema_numeric.max(100)("42")

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == "`schema.numeric.max(100)` is already declared"


def test_numeric_max_value_already_declared_greater_value_declaration_error():
    with given:
        sch = schema_numeric("42")

    with when, raises(Exception) as exception:
        sch.max(41)

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == (
            f"`{sch!r}` max value must be greater than or equal to 42, 41 given"
        )


def test_numeric_max_value_already_declared_max_declaration_error():
    with when, raises(Exception) as exception:
        schema_numeric.max(2).max(1)

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == "`schema.numeric.max(2)` is already declared"


def test_numeric_min_max_value_declaration():
    with given:
        min_value, max_value = 1, 2

    with when:
        sch = schema_numeric.min(min_value).max(max_value)

    with then:
        assert sch.props.min == min_value
        assert sch.props.max == max_value


def test_numeric_min_max_with_value_declaration():
    with given:
        value = "2"
        min_value, max_value = 1, 3

    with when:
        sch = schema_numeric(value).min(min_value).max(max_value)

    with then:
        assert sch.props.value == value
        assert sch.props.min == min_value
        assert sch.props.max == max_value
