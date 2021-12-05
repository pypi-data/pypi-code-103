from uuid import UUID, uuid4

from baby_steps import given, then, when
from blahblah import fake

from district42_exp_types.uuid import schema_uuid


def test_uuid_generation():
    with given:
        sch = schema_uuid

    with when:
        res = fake(sch)

    with then:
        assert isinstance(res, UUID)


def test_uuid_value_generation():
    with given:
        val = uuid4()
        sch = schema_uuid(val)

    with when:
        res = fake(sch)

    with then:
        assert res == val
