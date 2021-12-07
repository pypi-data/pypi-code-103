from http import HTTPStatus

import pytest
from django.urls import reverse
from markdownify import markdownify as md

from entries.utils import convert_md_to_html


def test_script_tag_allowed_in_entry(test_entry):
    assert '<script type="text/javascript">' not in test_entry.content


def test_script_tag_removed_by_function(sample_md_bad_tag):
    problem = '<script type="text/javascript">'
    assert problem in sample_md_bad_tag
    assert problem not in md(sample_md_bad_tag, strip=["script"])


def test_script_tag_stripped(test_entry):
    html = convert_md_to_html(test_entry.content)
    assert html == "<h1>This is a header script</h1>\n<p>test</p>"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "named_route, template_name",
    [
        ("entries:view_about", "about.html"),
        ("entries:list_entries", "entry_list.html"),
    ],
)
def test_ok_entry_views(client, named_route, template_name):
    url = reverse(named_route)
    response = client.get(url)
    assert HTTPStatus.OK == response.status_code
    assert template_name == response.template_name
