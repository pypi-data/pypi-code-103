"""Test the dict conversion."""

import pytest

from palabox.utils.case_conversion import (
    camelcase_to_snake_case,
    normal_to_camelcase,
    normal_to_snake_case,
    snake_case_to_camelcase,
)


@pytest.mark.parametrize(
    "test_input,expected",
    [("abc", "abc"), ("ABC", "abc"), ("abc def", "abc_def"), ("Abc Def", "abc_def")],
)
def test_normal_to_snake_case(test_input: str, expected: str) -> None:
    """normal_to_camelcase."""
    result = normal_to_snake_case(test_input)
    assert isinstance(result, str)
    assert result == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [("abc", "abc"), ("ABC", "abc"), ("abc def", "abcDef"), ("Abc Def", "abcDef")],
)
def test_normal_to_camelcase(test_input: str, expected: str) -> None:
    """normal_to_camelcase."""
    result = normal_to_camelcase(test_input)
    assert isinstance(result, str)
    assert result == expected


TESTS = [("abc", "abc"), ("abcDef", "abc_def")]


@pytest.mark.parametrize(
    "test_input,expected",
    TESTS,
)
def test_camelcase_to_snake_case(test_input: str, expected: str) -> None:
    """camelcase_to_snake_case."""
    result = camelcase_to_snake_case(test_input)
    assert isinstance(result, str)
    assert result == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [(y, x) for x, y in TESTS],
)
def test_snake_case_to_camelcase(test_input: str, expected: str) -> None:
    """snake_case_to_camelcase."""
    result = snake_case_to_camelcase(test_input)
    assert isinstance(result, str)
    assert result == expected
