from typing import Callable
from unittest.mock import sentinel

import pytest
from baby_steps import given, then, when
from district42 import schema
from multidict import CIMultiDict, CIMultiDictProxy
from pytest import raises
from revolt import substitute
from revolt.errors import SubstitutionError

from district42_exp_types.ci_multi_dict import schema_ci_multi_dict


@pytest.mark.parametrize("factory", [
    lambda: list(),
    lambda: CIMultiDict(),
    lambda: CIMultiDictProxy(CIMultiDict())
])
def test_ci_multi_dict_multidict_substitution(factory: Callable):
    with given:
        sch = schema_ci_multi_dict

    with when:
        res = substitute(sch, factory())

    with then:
        assert res == schema_ci_multi_dict(factory())
        assert res != sch


@pytest.mark.parametrize("factory", [
    lambda x: list(x),
    lambda x: CIMultiDict(x),
    lambda x: CIMultiDictProxy(CIMultiDict(x))
])
def test_ci_multi_dict_multidict_keys_substitution(factory: Callable):
    with given:
        sch = schema_ci_multi_dict

    with when:
        res = substitute(sch, factory([
            ("id", 1),
            ("name", "Bob"),
        ]))

    with then:
        assert res == schema_ci_multi_dict([
            ("id", schema.int(1)),
            ("name", schema.str("Bob")),
        ])
        assert res != sch


@pytest.mark.parametrize("factory", [
    lambda x: list(x),
    lambda x: CIMultiDict(x),
    lambda x: CIMultiDictProxy(CIMultiDict(x))
])
def test_ci_multi_dict_multidict_value_substitution_error(factory: Callable):
    with given:
        sch = schema_ci_multi_dict

    with when, raises(Exception) as exception:
        substitute(sch, factory([
            ("val", sentinel)
        ]))

    with then:
        assert exception.type is SubstitutionError


@pytest.mark.parametrize("factory", [
    lambda x: list(x),
    lambda x: CIMultiDict(x),
    lambda x: CIMultiDictProxy(CIMultiDict(x))
])
def test_ci_multi_dict_multidict_incorrect_value_substitution_error(factory: Callable):
    with given:
        sch = schema_ci_multi_dict([
            ("id", schema.int),
        ])

    with when, raises(Exception) as exception:
        substitute(sch, factory([
            ("id", "1")
        ]))

    with then:
        assert exception.type is SubstitutionError


@pytest.mark.parametrize("factory", [
    lambda x: list(x),
    lambda x: CIMultiDict(x),
    lambda x: CIMultiDictProxy(CIMultiDict(x))
])
def test_ci_multi_dict_multidict_more_keys_substitution_error(factory: Callable):
    with given:
        sch = schema_ci_multi_dict([
            ("id", schema.int),
        ])

    with when, raises(Exception) as exception:
        substitute(sch, factory([
            ("id", 1),
            ("name", "Bob"),
        ]))

    with then:
        assert exception.type is SubstitutionError


@pytest.mark.parametrize("factory", [
    lambda x: list(x),
    lambda x: CIMultiDict(x),
    lambda x: CIMultiDictProxy(CIMultiDict(x))
])
def test_ci_multi_dict_multidict_less_keys_substitution(factory: Callable):
    with given:
        sch = schema_ci_multi_dict([
            ("id", schema.int),
            ("name", schema.str),
        ])

    with when:
        res = substitute(sch, factory([
            ("ID", 1),
        ]))

    with then:
        assert res == schema_ci_multi_dict([
            ("id", schema.int(1)),
            ("name", schema.str),
        ])
        assert res != sch


@pytest.mark.parametrize("factory", [
    lambda x: list(x),
    lambda x: CIMultiDict(x),
    lambda x: CIMultiDictProxy(CIMultiDict(x))
])
def test_ci_multi_dict_multidict_multi_key_substitution(factory: Callable):
    with given:
        sch = schema_ci_multi_dict([
            ("id", schema.int),
            ("ID", schema.int),
            ("name", schema.str),
        ])

    with when:
        res = substitute(sch, factory([
            ("id", 1),
        ]))

    with then:
        assert res == schema_ci_multi_dict([
            ("id", schema.int(1)),
            ("id", schema.int(1)),
            ("name", schema.str),
        ])
        assert res != sch


@pytest.mark.parametrize("factory", [
    lambda x: list(x),
    lambda x: CIMultiDict(x),
    lambda x: CIMultiDictProxy(CIMultiDict(x))
])
def test_ci_multi_dict_multidict_multi_key_type_substitution_error(factory: Callable):
    with given:
        sch = schema_ci_multi_dict([
            ("id", schema.int),
            ("id", schema.str),
            ("name", schema.str),
        ])

    with when, raises(Exception) as exception:
        substitute(sch, factory([
            ("id", 1),
        ]))

    with then:
        assert exception.type is SubstitutionError


@pytest.mark.parametrize("factory", [
    lambda x: list(x),
    lambda x: CIMultiDict(x),
    lambda x: CIMultiDictProxy(CIMultiDict(x))
])
def test_ci_multi_dict_multidict_multi_key_same_values_substitution(factory: Callable):
    with given:
        sch = schema_ci_multi_dict([
            ("ID", schema.int),
            ("id", schema.int),
            ("name", schema.str),
        ])

    with when:
        res = substitute(sch, factory([
            ("id", 1),
            ("ID", 1),
        ]))

    with then:
        assert res == schema_ci_multi_dict([
            ("id", schema.int(1)),
            ("id", schema.int(1)),
            ("name", schema.str),
        ])
        assert res != sch


@pytest.mark.parametrize("factory", [
    lambda x: list(x),
    lambda x: CIMultiDict(x),
    lambda x: CIMultiDictProxy(CIMultiDict(x))
])
def test_ci_multi_dict_multidict_multi_key_diff_values_substitution(factory: Callable):
    with given:
        sch = schema_ci_multi_dict([
            ("id", schema.int),
            ("ID", schema.str),
            ("name", schema.str),
        ])

    with when:
        res = substitute(sch, factory([
            ("ID", 1),
            ("id", "1"),
        ]))

    with then:
        assert res == schema_ci_multi_dict([
            ("id", schema.int(1)),
            ("id", schema.str("1")),
            ("name", schema.str),
        ])
        assert res != sch


@pytest.mark.parametrize("factory", [
    lambda x: list(x),
    lambda x: CIMultiDict(x),
    lambda x: CIMultiDictProxy(CIMultiDict(x))
])
def test_ci_multi_dict_multidict_multi_key_substitution_error(factory: Callable):
    with given:
        sch = schema_ci_multi_dict([
            ("id", schema.int),
            ("name", schema.str),
        ])

    with when, raises(Exception) as exception:
        substitute(sch, factory([
            ("id", 1),
            ("id", 1),
        ]))

    with then:
        assert exception.type is SubstitutionError
