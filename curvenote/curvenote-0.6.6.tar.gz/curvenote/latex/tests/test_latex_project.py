from unittest.mock import MagicMock, Mock, patch

import pytest

from curvenote.client import Session
from curvenote.latex import LatexProject
from curvenote.models import BlockFormat


@patch.object(LatexProject, "create_folders")
def test_create_project(create_folders):
    LatexProject(Mock(), "some/folder", {})

    assert create_folders.called


@patch.object(LatexProject, "add_article")
@patch.object(LatexProject, "reconcile")
@patch.object(LatexProject, "create_folders")
def test_build_single_article_by_name(add_article, reconcile, create_folders):
    LatexProject.build_single_article_by_name(
        "some/folder",
        Session("fake-token"),
        "some-project-id",
        "some-article-id",
        1,
        BlockFormat.tex,
        {},
    )

    assert create_folders.called
    assert add_article.called
    assert reconcile.called
