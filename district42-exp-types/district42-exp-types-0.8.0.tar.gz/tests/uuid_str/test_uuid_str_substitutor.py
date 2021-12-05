from uuid import uuid4

from baby_steps import given, then, when
from pytest import raises
from revolt import substitute
from revolt.errors import SubstitutionError

from district42_exp_types.uuid_str import schema_uuid_str


def test_uuid_str_substitution():
    with given:
        value = str(uuid4())
        sch = schema_uuid_str

    with when:
        res = substitute(sch, value)

    with then:
        assert res == schema_uuid_str(value)
        assert res != sch


def test_uuid_str_value_substitution():
    with given:
        value = str(uuid4())
        sch = schema_uuid_str(value)

    with when:
        res = substitute(sch, value)

    with then:
        assert res == schema_uuid_str(value)
        assert id(res) != id(sch)


def test_uuid_str_substitution_invalid_value_error():
    with given:
        value = str(uuid4())
        sch = schema_uuid_str(value)

    with when, raises(Exception) as exception:
        substitute(sch, uuid4())

    with then:
        assert exception.type is SubstitutionError


def test_uuid_str_substitution_incorrect_value_error():
    with given:
        value = str(uuid4())
        sch = schema_uuid_str(value)

    with when, raises(Exception) as exception:
        substitute(sch, str(uuid4()))

    with then:
        assert exception.type is SubstitutionError


def test_uuid_str_lowercase_substitution():
    with given:
        value = str(uuid4()).lower()
        sch = schema_uuid_str.lowercase()

    with when:
        res = substitute(sch, value)

    with then:
        assert res == schema_uuid_str(value).lowercase()
        assert res != sch


def test_uuid_str_lowercase_substitution_error():
    with given:
        value = str(uuid4()).upper()
        sch = schema_uuid_str.lowercase()

    with when, raises(Exception) as exception:
        substitute(sch, value)

    with then:
        assert exception.type is SubstitutionError


def test_uuid_str_uppercase_substitution():
    with given:
        value = str(uuid4()).upper()
        sch = schema_uuid_str.uppercase()

    with when:
        res = substitute(sch, value)

    with then:
        assert res == schema_uuid_str(value).uppercase()
        assert res != sch


def test_uuid_str_uppercase_substitution_error():
    with given:
        value = str(uuid4()).lower()
        sch = schema_uuid_str.uppercase()

    with when, raises(Exception) as exception:
        substitute(sch, value)

    with then:
        assert exception.type is SubstitutionError
