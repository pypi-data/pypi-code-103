from typing import Any, Callable
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from blahblah import Generator, Random, RegexGenerator
from district42.types import Schema

from district42_exp_types.numeric import schema_numeric
from district42_exp_types.numeric._numeric_generator import INT_MAX, INT_MIN


@pytest.fixture()
def random_() -> Random:
    return Mock(Random, wraps=Random())


@pytest.fixture()
def generator(random_: Random) -> Generator:
    return Generator(random_, RegexGenerator(random_))


@pytest.fixture()
def generate(generator: Generator) -> Callable[[Schema], Any]:
    def _generate(sch: Schema) -> Any:
        return sch.__accept__(generator)
    return _generate


def test_numeric_generation(*, generate, random_):
    with given:
        sch = schema_numeric

    with when:
        res = generate(sch)

    with then:
        assert isinstance(res, str)
        assert INT_MIN <= int(res) <= INT_MAX
        assert random_.mock_calls == [
            call.random_int(INT_MIN, INT_MAX)
        ]


def test_numeric_value_generation(*, generate, random_):
    with given:
        val = "42"
        sch = schema_numeric(val)

    with when:
        res = generate(sch)

    with then:
        assert res == val
        assert random_.mock_calls == []


def test_numeric_min_generation(*, generate, random_):
    with given:
        min_val = 1
        sch = schema_numeric.min(min_val)

    with when:
        res = generate(sch)

    with then:
        assert isinstance(res, str)
        assert int(res) >= min_val
        assert random_.mock_calls == [
            call.random_int(min_val, INT_MAX)
        ]


def test_numeric_max_generation(*, generate, random_):
    with given:
        max_val = 2
        sch = schema_numeric.max(max_val)

    with when:
        res = generate(sch)

    with then:
        assert isinstance(res, str)
        assert int(res) <= max_val
        assert random_.mock_calls == [
            call.random_int(INT_MIN, max_val)
        ]


def test_numeric_min_max_generation(*, generate, random_):
    with given:
        min_val, max_val = 1, 2
        sch = schema_numeric.min(min_val).max(max_val)

    with when:
        res = generate(sch)

    with then:
        assert isinstance(res, str)
        assert min_val <= int(res) <= max_val
        assert random_.mock_calls == [
            call.random_int(min_val, max_val)
        ]
