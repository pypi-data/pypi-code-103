from typing import Callable

import pytest
from baby_steps import given, then, when
from district42 import schema
from multidict import CIMultiDict, CIMultiDictProxy
from th import PathHolder
from valera import validate
from valera.errors import ExtraKeyValidationError, TypeValidationError

from district42_exp_types.ci_multi_dict import schema_ci_multi_dict


@pytest.mark.parametrize("multidict_factory", [
    lambda x: CIMultiDict(x),
    lambda x: CIMultiDictProxy(CIMultiDict(x))
])
def test_ci_multi_dict_multidict_validation(multidict_factory: Callable):
    with given:
        sch = schema_ci_multi_dict([
            ("id", schema.int(42)),
            ("ID", schema.str("42")),
            ("name", schema.str("Bob")),
        ])
        value = multidict_factory([
            ("ID", 42),
            ("id", "42"),
            ("name", "Bob"),
        ])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == []


@pytest.mark.parametrize("multidict_factory", [
    lambda x: CIMultiDict(x),
    lambda x: CIMultiDictProxy(CIMultiDict(x))
])
def test_ci_multi_dict_multidict_extra_value_validation_error(multidict_factory):
    with given:
        sch = schema_ci_multi_dict([
            ("id", schema.int(42)),
            ("name", schema.str("Bob")),
        ])
        value = multidict_factory([
            ("id", 42),
            ("id", "42"),
            ("name", "Bob"),
        ])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            ExtraKeyValidationError(PathHolder(), value, "id")
        ]


@pytest.mark.parametrize("multidict_factory", [
    lambda x: CIMultiDict(x),
    lambda x: CIMultiDictProxy(CIMultiDict(x))
])
def test_ci_multi_dict_multidict_missing_value_validation_error(multidict_factory):
    with given:
        sch = schema_ci_multi_dict([
            ("id", schema.int(42)),
            ("ID", schema.str("42")),
            ("name", schema.str("Bob")),
        ])
        value = multidict_factory([
            ("ID", 42),
            ("name", "Bob"),
        ])

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            TypeValidationError(PathHolder()["id"], 42, str)
        ]
