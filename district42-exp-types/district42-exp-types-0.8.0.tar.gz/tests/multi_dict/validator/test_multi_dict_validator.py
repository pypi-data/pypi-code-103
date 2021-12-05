from typing import Any, Dict, Mapping

import pytest
from baby_steps import given, then, when
from th import PathHolder
from valera import validate
from valera.errors import TypeValidationError

from district42_exp_types.multi_dict import schema_multi_dict


@pytest.mark.parametrize("value", [
    {},
    {"id": 1},
    {"id": 1, "name": "Bob"},
])
def test_multi_dict_type_validation(value: Dict[Any, Any]):
    with given:
        sch = schema_multi_dict

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == []


def test_multi_dict_type_validation_error():
    with given:
        sch = schema_multi_dict
        value = []

    with when:
        result = validate(sch, value)

    with then:
        assert result.get_errors() == [
            TypeValidationError(PathHolder(), value, Mapping)
        ]
