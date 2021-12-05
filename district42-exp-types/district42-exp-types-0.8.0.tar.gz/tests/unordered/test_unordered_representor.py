from baby_steps import given, then, when
from district42 import represent, schema

from district42_exp_types.unordered import unordered_schema


def test_unordered_representation():
    with given:
        sch = unordered_schema

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.unordered"


def test_unordered_elements_representation():
    with given:
        sch = unordered_schema([schema.int(1), schema.int(2)])

    with when:
        res = represent(sch)

    with then:
        assert res == "\n".join([
                          "schema.unordered([",
                          "    schema.int(1),",
                          "    schema.int(2)",
                          "])"
                      ])


def test_unordered_of_representation():
    with given:
        sch = unordered_schema(schema.int)

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.unordered(schema.int)"
