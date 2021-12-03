from typing import Dict

import pytest

from palabox.utils.dict_conversion import convert_dict_keys_to_snake_case

TESTS = [
    ({"abc": 1}, {"abc": 1}),
    ({"abcDef": 1}, {"abc_def": 1}),
    ({"abcDef": {"efJi": "ef_ji"}, "x": 1}, {"abc_def": {"ef_ji": "ef_ji"}, "x": 1}),
]


@pytest.mark.parametrize(
    "test_input,expected",
    TESTS,
)
def test_convert_dict_keys_to_snake_case(test_input: Dict, expected: Dict) -> None:
    """normal_to_camelcase."""
    result = convert_dict_keys_to_snake_case(test_input)
    assert str(result) == str(expected)
