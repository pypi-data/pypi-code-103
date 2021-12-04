import pytest

from entries.forms import EntryForm

START_WITH_UPPER = lambda x: f"{x} should start with an uppercase letter"
NO_AMPERSAND = lambda x: f"{x} should use 'and' instead of '&'"
BAD_TAG = '<script type="text/javascript">'


@pytest.mark.parametrize(
    "field, formatter, value",
    [
        ("title", START_WITH_UPPER, "a lowercase title"),
        ("title", NO_AMPERSAND, "X & Y in title"),
        ("excerpt", START_WITH_UPPER, "a lowercase excerpt"),
        ("excerpt", NO_AMPERSAND, "X & Y in excerpt"),
    ],
)
def test_entry_field_invalid_input_found(field, formatter, value):
    form = EntryForm(data={field: value})
    assert form.errors[field] == [formatter(value)]


def test_title_all_errors():
    x = "a & Y."
    form = EntryForm(data={"title": x})
    assert form.errors["title"] == [START_WITH_UPPER(x), NO_AMPERSAND(x)]


def test_valid_content(sample_data):
    form = EntryForm(data=sample_data)
    assert BAD_TAG in sample_data["content"]
    assert form.is_valid()  # will call validation functions
    assert BAD_TAG not in form.cleaned_data["content"]
