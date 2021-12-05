from uuid import uuid4

from baby_steps import given, then, when
from pytest import raises
from revolt import substitute
from revolt.errors import SubstitutionError

from district42_exp_types.uuid import schema_uuid


def test_uuid_substitution():
    with given:
        value = uuid4()
        sch = schema_uuid

    with when:
        res = substitute(sch, value)

    with then:
        assert res == schema_uuid(value)
        assert res != sch


def test_uuid_value_substitution():
    with given:
        value = uuid4()
        sch = schema_uuid(value)

    with when:
        res = substitute(sch, value)

    with then:
        assert res == schema_uuid(value)
        assert id(res) != id(sch)


def test_uuid_substitution_invalid_value_error():
    with given:
        sch = schema_uuid(uuid4())

    with when, raises(Exception) as exception:
        substitute(sch, str(uuid4()))

    with then:
        assert exception.type is SubstitutionError


def test_uuid_substitution_incorrect_value_error():
    with given:
        sch = schema_uuid(uuid4())

    with when, raises(Exception) as exception:
        substitute(sch, uuid4())

    with then:
        assert exception.type is SubstitutionError
