from baby_steps import given, then, when
from district42 import represent, schema

from district42_exp_types.ci_multi_dict import schema_ci_multi_dict


def test_ci_multi_dict_representation():
    with given:
        sch = schema_ci_multi_dict

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.ci_multi_dict"


def test_ci_multi_dict_empty_representation():
    with given:
        sch = schema_ci_multi_dict({})

    with when:
        res = represent(sch)

    with then:
        assert res == "schema.ci_multi_dict([])"


def test_ci_multi_dict_one_key_representation():
    with given:
        sch = schema_ci_multi_dict({"id": schema.int})

    with when:
        res = represent(sch)

    with then:
        assert res == "\n".join([
            "schema.ci_multi_dict([",
            "    ('id', schema.int)",
            "])"
        ])


def test_ci_multi_dict_many_keys_representation():
    with given:
        sch = schema_ci_multi_dict([
            ("Id", schema.int),
            ("id", schema.str),
            ("name", schema.str("banana")),
        ])

    with when:
        res = represent(sch)

    with then:
        assert res == "\n".join([
            "schema.ci_multi_dict([",
            "    ('Id', schema.int),",
            "    ('id', schema.str),",
            "    ('name', schema.str('banana'))",
            "])",
        ])


def test_ci_multi_dict_nested_keys_representation():
    with given:
        sch = schema_ci_multi_dict({
            "id": schema.int,
            "user": schema_ci_multi_dict({
                "id": schema.int,
                "name": schema.str("banana")
            }),
            "is_deleted": schema.bool
        })

    with when:
        res = represent(sch)

    with then:
        assert res == "\n".join([
            "schema.ci_multi_dict([",
            "    ('id', schema.int),",
            "    ('user', schema.ci_multi_dict([",
            "        ('id', schema.int),",
            "        ('name', schema.str('banana'))",
            "    ])),",
            "    ('is_deleted', schema.bool)",
            "])",
        ])
