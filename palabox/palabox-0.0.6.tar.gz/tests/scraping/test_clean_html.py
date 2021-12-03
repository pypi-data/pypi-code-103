"""Test the cleaning of html."""

import pytest

from palabox.scraping.clean_html import clean_html_to_text

TEST_CASES = [
    ("<p>ABC</p>", "ABC"),
    ("<p>ABC</p><p>ABC</p>", "ABC\nABC"),
    ("<h1>ABC</h1><p>ABC</p>", "ABC\nABC"),
    ("<p>ABC</p><h1>ABC</h1>", "ABC\n\n\nABC"),
]


@pytest.mark.parametrize("test_input,expected", TEST_CASES)
def test_clean_html_to_text(test_input: str, expected: str) -> None:
    """Test clean_html_to_text."""
    result = clean_html_to_text(f"<html><body>{test_input}</body></html>")
    assert isinstance(result, str)
    assert result == expected
