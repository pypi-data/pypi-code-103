from uuid import uuid4

from baby_steps import given, then, when
from district42 import represent

from district42_exp_types.uuid_str import schema_uuid_str


def test_uuid_str_representation():
    with given:
        sch = schema_uuid_str

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.uuid_str"


def test_uuid_str_value_representation():
    with given:
        value = str(uuid4())
        sch = schema_uuid_str(value)

    with when:
        res = represent(sch)

    with then:
        assert res == f"schema.uuid_str({value!r})"


def test_uuid_str_lowercase_representation():
    with given:
        sch = schema_uuid_str.lowercase()

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.uuid_str.lowercase()"


def test_uuid_str_uppercase_representation():
    with given:
        sch = schema_uuid_str.uppercase()

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.uuid_str.uppercase()"
