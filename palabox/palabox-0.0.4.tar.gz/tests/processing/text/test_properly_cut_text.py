"""Test properly_cut_text."""

import pytest

from palabox.processing.text.properly_cut_text import properly_cut_text

TEST_CASES = [
    ("My name is Marco.", 0, 17, "My name is Marco."),
    ("My name is Marco.", -1, 17, "My name is Marco."),
    ("My name is Marco.", 0, 20, "My name is Marco."),
]

TEXT_CASES_2 = [
    ("123456789", 2, 5, 1, 2, "123456789"),
    ("123456 789", 2, 5, 1, 2, "123456 789"),
    ("This is a 3.5 dollars bread", 1, 2, 0, 0, "This is a 3.5 dollars bread"),
    ("This is a 3. and 5", 1, 2, 0, 0, "This is a 3."),
    ("This is a 3. and 5", 1, 2, 0, 10, "This is a 3. and 5"),
    ("This is a 3. and 5", 15, 16, 0, 0, "and 5"),
]


@pytest.mark.parametrize("test_input,start_idx,end_idx,expected", TEST_CASES)
def test_properly_cut_text(test_input: str, start_idx: int, end_idx: int, expected: str) -> None:
    """Test properly_cut_text."""
    result = properly_cut_text(test_input, start_idx, end_idx)
    assert result == expected


@pytest.mark.parametrize("test_input,start_idx,end_idx,nbr_before,nbr_after,expected", TEXT_CASES_2)
def test_properly_cut_text_2(
    test_input: str,
    start_idx: int,
    end_idx: int,
    expected: str,
    nbr_before: int,
    nbr_after: int,
) -> None:
    """Test properly_cut_text."""
    result = properly_cut_text(test_input, start_idx, end_idx, nbr_before, nbr_after)
    assert result == expected
