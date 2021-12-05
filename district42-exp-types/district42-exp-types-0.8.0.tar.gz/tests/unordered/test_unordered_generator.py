from typing import Any, Callable
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from blahblah import Generator, Random, RegexGenerator
from blahblah._consts import LIST_LEN_MAX, LIST_LEN_MIN
from district42.types import Schema

from district42_exp_types.unordered import unordered_schema


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


def test_unordered_generation(*, generate, random_):
    with given:
        sch = unordered_schema

    with when:
        res = generate(sch)

    with then:
        assert isinstance(res, list)
        assert random_.mock_calls == [
            call.random_int(LIST_LEN_MIN, LIST_LEN_MAX),
            call.shuffle_list([])
        ]
