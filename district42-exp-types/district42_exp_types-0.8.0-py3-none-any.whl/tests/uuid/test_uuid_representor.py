from uuid import uuid4

from baby_steps import given, then, when
from district42 import represent

from district42_exp_types.uuid import schema_uuid


def test_uuid_representation():
    with given:
        sch = schema_uuid

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.uuid"


def test_uuid_value_representation():
    with given:
        value = uuid4()
        sch = schema_uuid(value)

    with when:
        res = represent(sch)

    with then:
        assert res == f"schema.uuid({value!r})"
