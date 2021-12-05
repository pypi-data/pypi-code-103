from _pytest.python_api import raises
from baby_steps import given, then, when
from district42 import schema
from revolt import substitute
from revolt.errors import SubstitutionError

from district42_exp_types.sdict import schema_sdict


def test_sdict_substitution():
    with given:
        sch = schema_sdict

    with when:
        res = substitute(sch, {})

    with then:
        assert res == schema_sdict({})
        assert res != sch


def test_sdict_nested_substitution():
    with given:
        sch = schema_sdict({
            "result": schema_sdict({
                "id": schema.int,
                "name": schema.str,
                "friend": schema_sdict({
                    "id": schema.int,
                    "name": schema.str
                })
            })
        })

    with when:
        res = substitute(sch, {
            "result.id": 1,
            "result.name": "Bob",
            "result.friend.id": 2,
            "result.friend.name": "Alice",
        })

    with then:
        assert res == schema_sdict({
            "result": schema_sdict({
                "id": schema.int(1),
                "name": schema.str("Bob"),
                "friend": schema_sdict({
                    "id": schema.int(2),
                    "name": schema.str("Alice")
                })
            })
        })
        assert res != sch


def test_sdict_relaxed_substitution():
    with given:
        sch = schema_sdict({
            "result": schema_sdict({
                "id": schema.int,
                "name": schema.str,
                ...: ...
            })
        })

    with when:
        res = substitute(sch, {
            "result.id": 1,
        })

    with then:
        assert res == schema_sdict({
            "result": schema_sdict({
                "id": schema.int(1),
                "name": schema.str,
                ...: ...
            })
        })
        assert res != sch


def test_sdict_relaxed_extra_key_substitution_error():
    with given:
        sch = schema_sdict({
            "result": schema_sdict({
                "id": schema.int,
                "name": schema.str,
                ...: ...
            })
        })

    with when, raises(Exception) as exception:
        substitute(sch, {
            "result.id": 1,
            "result.deleted_at": None
        })

    with then:
        assert exception.type is SubstitutionError


def test_sdict_relaxed_ellipsis_substitution_error():
    with given:
        sch = schema_sdict({
            "result": schema_sdict({
                "id": schema.int,
                "name": schema.str,
                ...: ...
            })
        })

    with when, raises(Exception) as exception:
        substitute(sch, {
            "result.id": 1,
            ...: ...
        })

    with then:
        assert exception.type is SubstitutionError
