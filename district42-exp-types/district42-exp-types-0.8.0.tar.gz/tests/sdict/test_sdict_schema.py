from baby_steps import then, when
from district42 import optional, schema

from district42_exp_types.sdict import SDictSchema, schema_sdict


def test_sdict_declaration():
    with when:
        sch = schema_sdict

    with then:
        assert isinstance(sch, SDictSchema)


def test_sdict_nested_declaration():
    with when:
        sch = schema_sdict({
            "result.id": schema.int(1),
            "result.name": schema.str("Bob"),
            "result.friend.id": schema.int(2),
            "result.friend.name": schema.str("Alice"),
        })

    with then:
        assert sch == schema.sdict({
            "result": schema.sdict({
                "id": schema.int(1),
                "name": schema.str("Bob"),
                "friend": schema.sdict({
                    "id": schema.int(2),
                    "name": schema.str("Alice")
                })
            })
        })


def test_sdict_nested_optional_declaration():
    with when:
        sch = schema_sdict({
            "result.id": schema.int(1),
            optional("result.name"): schema.str("Bob"),
        })

    with then:
        assert sch == schema.sdict({
            "result": schema.sdict({
                "id": schema.int(1),
                optional("name"): schema.str("Bob"),
            })
        })


def test_sdict_relaxed_declaration():
    with when:
        sch = schema_sdict({
            "result.id": schema.int(1),
            "result.name": schema.str("Bob"),
            ...: ...
        })

    with then:
        assert sch == schema.sdict({
            "result": schema.sdict({
                "id": schema.int(1),
                "name": schema.str("Bob")
            }),
            ...: ...
        })


def test_sdict_relaxed_nested_declaration():
    with when:
        sch = schema_sdict({
            "result": {...: ...},
            "result.id": schema.int(1),
            "result.name": schema.str("Bob"),
        })

    with then:
        assert sch == schema.sdict({
            "result": schema.sdict({
                ...: ...,
                "id": schema.int(1),
                "name": schema.str("Bob")
            })
        })


def test_sdict_relaxed_deep_nested_declaration():
    with when:
        sch = schema_sdict({
            "result.id": schema.int(1),
            "result.name": schema.str("Bob"),
            "result.friend": {
                "id": schema.int(2),
                "name": schema.str("Alice"),
                ...: ...
            }
        })

    with then:
        assert sch == schema.sdict({
            "result": schema.sdict({
                "id": schema.int(1),
                "name": schema.str("Bob"),
                "friend": schema.sdict({
                    "id": schema.int(2),
                    "name": schema.str("Alice"),
                    ...: ...
                })
            })
        })
