from uuid import UUID, uuid4

import pytest
from baby_steps import given, then, when
from blahblah import fake

from district42_exp_types.uuid_str import schema_uuid_str


def test_uuid_str_generation():
    with given:
        sch = schema_uuid_str

    with when:
        res = fake(sch)

    with then:
        assert isinstance(res, str)
        assert str(UUID(res)) in (res.lower(), res.upper())


@pytest.mark.parametrize("modifier", [str.lower, str.upper])
def test_uuid_str_value_generation(modifier):
    with given:
        val = modifier(str(uuid4()))
        sch = schema_uuid_str(val)

    with when:
        res = fake(sch)

    with then:
        assert res == val


def test_uuid_str_lowercase_generation():
    with given:
        sch = schema_uuid_str.lowercase()

    with when:
        res = fake(sch)

    with then:
        assert res.islower()


def test_uuid_str_uppercase_generation():
    with given:
        sch = schema_uuid_str.uppercase()

    with when:
        res = fake(sch)

    with then:
        assert res.isupper()
