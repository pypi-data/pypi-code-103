from typing import Any, List
from unittest.mock import sentinel

import pytest
from baby_steps import given, then, when
from district42 import schema
from pytest import raises
from revolt import substitute
from revolt.errors import SubstitutionError

from district42_exp_types.unordered import unordered_schema


@pytest.mark.parametrize("value", [
    [],
    [1],
    [1, 2],
])
def test_unordered_elements_substitution(value: List[Any]):
    with given:
        sch = unordered_schema

    with when:
        res = substitute(sch, value)

    with then:
        assert res == unordered_schema([substitute(schema.int, x) for x in value])
        assert res != sch


def test_unordered_elements_substitution_error():
    with given:
        sch = unordered_schema

    with when, raises(Exception) as exception:
        substitute(sch, [sentinel])

    with then:
        assert exception.type is SubstitutionError


def test_unordered_len_substitution():
    with given:
        sch = unordered_schema.len(2)

    with when:
        res = substitute(sch, [1, 2])

    with then:
        assert res == unordered_schema([schema.int(1), schema.int(2)]).len(2)
        assert res != sch


@pytest.mark.parametrize("value", [
    [1],
    [1, 2, 3],
])
def test_unordered_len_substitution_error(value: List[Any]):
    with given:
        sch = unordered_schema.len(2)

    with when, raises(Exception) as exception:
        substitute(sch, value)

    with then:
        assert exception.type is SubstitutionError


@pytest.mark.parametrize("value", [
    [1, 2],
    [1, 2, 3],
])
def test_unordered_min_len_substitution(value: Any):
    with given:
        sch = unordered_schema.len(2, ...)

    with when:
        res = substitute(sch, value)

    with then:
        assert res == unordered_schema([substitute(schema.int, x) for x in value]).len(2, ...)
        assert res != sch


def test_unordered_min_len_substitution_error():
    with given:
        sch = unordered_schema.len(2, ...)

    with when, raises(Exception) as exception:
        substitute(sch, [1])

    with then:
        assert exception.type is SubstitutionError


@pytest.mark.parametrize("value", [
    [],
    [1],
    [1, 2],
])
def test_unordered_max_len_substitution(value: List[Any]):
    with given:
        sch = unordered_schema.len(..., 2)

    with when:
        res = substitute(sch, value)

    with then:
        assert res == unordered_schema([substitute(schema.int, x) for x in value]).len(..., 2)
        assert res != sch


def test_unordered_max_len_substitution_error():
    with given:
        sch = unordered_schema.len(..., 2)

    with when, raises(Exception) as exception:
        substitute(sch, [1, 2, 3])

    with then:
        assert exception.type is SubstitutionError


@pytest.mark.parametrize("value", [
    [1],
    [1, 2],
    [1, 2, 3],
])
def test_unordered_min_max_len_substitution(value: List[Any]):
    with given:
        sch = unordered_schema.len(1, 3)

    with when:
        res = substitute(sch, value)

    with then:
        assert res == unordered_schema([substitute(schema.int, x) for x in value]).len(1, 3)
        assert res != sch


@pytest.mark.parametrize("value", [
    [],
    [1, 2, 3, 4],
])
def test_unordered_min_max_len_substitution_error(value: List[Any]):
    with given:
        sch = unordered_schema.len(1, 3)

    with when, raises(Exception) as exception:
        substitute(sch, value)

    with then:
        assert exception.type is SubstitutionError
