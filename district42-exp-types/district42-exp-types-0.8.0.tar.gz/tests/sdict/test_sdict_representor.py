from baby_steps import given, then, when
from district42 import represent, schema

from district42_exp_types.sdict import schema_sdict


def test_sdict_representation():
    with given:
        sch = schema_sdict

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.sdict"


def test_sdict_keys_representation():
    with given:
        sch = schema_sdict({
            "id": schema.int,
            "name": schema.str,
        })

    with when:
        res = represent(sch)

    with then:
        assert res == "\n".join([
                            "schema.sdict({",
                            "    'id': schema.int,",
                            "    'name': schema.str",
                            "})"
                        ])


def test_sdict_relaxed_keys_representation():
    with given:
        sch = schema_sdict({
            "id": schema.int,
            "name": schema.str,
            ...: ...
        })

    with when:
        res = represent(sch)

    with then:
        assert res == "\n".join([
                            "schema.sdict({",
                            "    'id': schema.int,",
                            "    'name': schema.str,",
                            "    ...: ...",
                            "})"
                        ])
