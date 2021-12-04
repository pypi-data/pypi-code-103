import pytest
from markdownify import markdownify as md

from entries.models import Entry


@pytest.fixture
def sample_user(django_user_model):
    return django_user_model.objects.create(
        username="userjohn",
        first_name="john",
        last_name="doe",
        password="qwer1234qwer1234",
    )


@pytest.fixture
def modified_first_name():
    return "Juan"


@pytest.fixture
def modified_last_name():
    return "de la Cruz"


@pytest.fixture
def modified_name(modified_first_name, modified_last_name, sample_user):
    """Implies existence of `test_entry` which will be modified"""
    return {
        "first_name": modified_first_name,
        "last_name": modified_last_name,
    }


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create(
        username="userjames",
        first_name="james",
        last_name="delacruz",
        password="qwer1234qwer1234",
    )


@pytest.fixture
def sample_title():
    return "Sample valid title"


@pytest.fixture
def sample_slug():
    return "sample-valid-title"


@pytest.fixture
def sample_excerpt():
    return "Sample description."


@pytest.fixture
def sample_md_bad_tag():
    return """# This is a header script\r\n\r\n<script type="text/javascript">test</script>"""


@pytest.fixture
def sample_data(sample_title, sample_excerpt, sample_md_bad_tag):
    return {
        "title": sample_title,
        "excerpt": sample_excerpt,
        "content": sample_md_bad_tag,
    }


@pytest.fixture
def test_entry(sample_user, sample_data):
    return Entry.objects.create(
        title=sample_data["title"],
        excerpt=sample_data["excerpt"],
        content=md(sample_data["content"], strip=["script"]),
        author=sample_user,
    )


@pytest.fixture
def modified_data(test_entry, sample_excerpt, sample_md_bad_tag):
    """Implies existence of `test_entry` which will be modified"""
    return {
        "title": "Modified valid title",
        "excerpt": sample_excerpt,
        "content": sample_md_bad_tag,
    }
