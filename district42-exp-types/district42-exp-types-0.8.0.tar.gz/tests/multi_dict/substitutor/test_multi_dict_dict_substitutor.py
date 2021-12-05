from unittest.mock import sentinel

from baby_steps import given, then, when
from district42 import schema
from pytest import raises
from revolt import substitute
from revolt.errors import SubstitutionError

from district42_exp_types.multi_dict import schema_multi_dict


def test_multi_dict_dict_substitution():
    with given:
        sch = schema_multi_dict

    with when:
        res = substitute(sch, {})

    with then:
        assert res == schema_multi_dict({})
        assert res != sch


def test_multi_dict_dict_keys_substitution():
    with given:
        sch = schema_multi_dict
        value = {
            "id": 1,
            "name": "Bob"
        }

    with when:
        res = substitute(sch, value)

    with then:
        assert res == schema_multi_dict([
            ("id", schema.int(1)),
            ("name", schema.str("Bob")),
        ])
        assert res != sch


def test_multi_dict_dict_value_substitution_error():
    with given:
        sch = schema_multi_dict

    with when, raises(Exception) as exception:
        substitute(sch, {"val": sentinel})

    with then:
        assert exception.type is SubstitutionError


def test_multi_dict_dict_incorrect_value_substitution_error():
    with given:
        sch = schema_multi_dict({
            "id": schema.int,
        })

    with when, raises(Exception) as exception:
        substitute(sch, {"id": "1"})

    with then:
        assert exception.type is SubstitutionError


def test_multi_dict_dict_more_keys_substitution_error():
    with given:
        sch = schema_multi_dict({
            "id": schema.int,
        })

    with when, raises(Exception) as exception:
        substitute(sch, {
            "id": 1,
            "name": "Bob",
        })

    with then:
        assert exception.type is SubstitutionError


def test_multi_dict_dict_less_keys_substitution():
    with given:
        sch = schema_multi_dict({
            "id": schema.int,
            "name": schema.str,
        })

    with when:
        res = substitute(sch, {
            "id": 1,
        })

    with then:
        assert res == schema_multi_dict([
            ("id", schema.int(1)),
            ("name", schema.str),
        ])
        assert res != sch


def test_multi_dict_dict_multi_key_substitution():
    with given:
        sch = schema_multi_dict([
            ("id", schema.int),
            ("id", schema.int),
            ("name", schema.str),
        ])

    with when:
        res = substitute(sch, {
            "id": 1,
        })

    with then:
        assert res == schema_multi_dict([
            ("id", schema.int(1)),
            ("id", schema.int(1)),
            ("name", schema.str),
        ])
        assert res != sch


def test_multi_dict_dict_multi_key_substitution_error():
    with given:
        sch = schema_multi_dict([
            ("id", schema.int),
            ("id", schema.str),
            ("name", schema.str),
        ])

    with when, raises(Exception) as exception:
        substitute(sch, {
            "id": 1,
        })

    with then:
        assert exception.type is SubstitutionError
