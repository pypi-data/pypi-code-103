from unittest.mock import MagicMock, Mock, patch

import pytest

from curvenote.latex import LatexArticle
from jtex import Tag

@patch.object(LatexArticle, "authors")
def test_author_names_lookup(mock_authors):
    a1 = Mock()
    a1.plain = None
    a1.user = "1"
    a2 = Mock()
    a2.plain = "Jane Doe"
    a2.user = None
    mock_authors.__get__ = Mock(return_value=[a1, a2])
    article = LatexArticle(None, "", "")
    article._block = MagicMock()
    u1 = Mock()
    u1.id = "1"
    u1.display_name = "User One"
    u2 = Mock()
    u2.id = "2"
    u2.display_name = "User Two"
    article._users = [u1, u2]
    authors = article.authors
    assert len(authors) == 2

    author_names = article.author_names
    assert len(author_names) == 2
    assert author_names[0] == "User One"
    assert author_names[1] == "Jane Doe"


def test_oxalink():
    a = LatexArticle(Mock(), "", "")

    a._version = Mock()

    a._version.id = Mock()
    a._version.id.project = "qwerty"
    a._version.id.block = "asdfgh"
    a._version.id.version = 3

    assert a.oxalink("https://cn.com") == "https://cn.com/oxa:qwerty/asdfgh.3"


@pytest.mark.parametrize(
    "tags1, tags2, content, keys, cases",
    [
        ([], [], "block1\n\nblock2\n", [], []),
        (["random"], [], "block1\n\nblock2\n", [], []),
        (["no-export"], [], "block2\n", [], []),
        (["abstract"], [], "block2\n", ["abstract"], [("abstract", "block1\n")]),
        (
            ["abstract"],
            ["abstract"],
            "",
            ["abstract"],
            [("abstract", "block1\n\nblock2\n")],
        ),
        (["abstract"], ["no-export"], "", ["abstract"], [("abstract", "block1\n")]),
    ],
)
def test_dump_article(tags1, tags2, content, keys, cases):
    allowed_tags = set([Tag("abstract", False), Tag("another", False)])

    article = LatexArticle(Mock(), "", "")

    block1 = Mock()
    block1.tags = tags1
    block1.content = "block1"

    block2 = Mock()
    block2.tags = tags2
    block2.content = "block2"

    article._latex_block_versions = [block1, block2]

    content, tagged_content = article.dump(allowed_tags)

    assert content == content
    assert list(tagged_content.keys()) == keys
    for tag, case in cases:
        assert tagged_content[tag]
        assert tagged_content[tag] == case


def test_dump_article_with_plain_text_tag():
    allowed_tags = set([Tag("abstract", True)])

    session = Mock()
    article = LatexArticle(session, "", "")

    block1 = Mock()
    block1.tags = ["abstract"]
    block1.content = "block1"
    block1.fetch_content.return_value = "plain text"

    article._latex_block_versions = [block1]

    content, tagged_content = article.dump(allowed_tags)

    assert content == content
    assert list(tagged_content.keys()) == ["abstract"]
    assert tagged_content["abstract"] == "plain text"