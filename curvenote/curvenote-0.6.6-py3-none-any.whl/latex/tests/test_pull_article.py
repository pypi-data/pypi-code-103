import os
import subprocess
import tempfile
from typing import cast

import pytest
from jtex import LatexBuilder

from curvenote.client import Session
from curvenote.latex import LatexProject, OnlineTemplateLoader
from curvenote.utils import decode_oxa_link
from curvenote.models import BlockFormat


@pytest.mark.parametrize(
    "override_dir,url",
    [
        (
            None,
            "https://curvenote.com/oxa:nJ1zXZpgPHwAIvQtPCe4/efeOVBOpWerZdEqvVtEL.20",
        ),
        (None, "https://curvenote.com/oxa:nJ1zXZpgPHwAIvQtPCe4/OSifiOWbOKeE6SJTiWOr.1"),
    ],
)
def test_pull_article_builtin_template(override_dir, url):
    """
    Pull a full article using the python code - via url but using the baked in default template
    """

    if "CURVENOTE_TOKEN" in os.environ:
        token = os.environ["CURVENOTE_TOKEN"]
        session = Session(token)

        with tempfile.TemporaryDirectory() as tmp_dir:
            if override_dir is not None:
                tmp_dir = override_dir
            loader = OnlineTemplateLoader(tmp_dir)
            template_options, renderer = loader.initialise_with_builtin_template()

            assert decode_oxa_link(url) is not None
            latex_project = LatexProject.build_single_article_by_url(
                tmp_dir, session, url, cast(BlockFormat, template_options.tex_format)
            )
            builder = LatexBuilder(template_options, renderer, tmp_dir)
            builder.build(*latex_project.dump(template_options.get_allowed_tags()))


@pytest.fixture(params=["default", "plain_latex"], name="template_name")
def _template_name(request):
    return request.param


def test_pull_article_with_template(template_name):
    """
    Pull a full article using the python code - via url but pulling the basic template from the API
    """

    if "CURVENOTE_TOKEN" in os.environ:
        token = os.environ["CURVENOTE_TOKEN"]
        session = Session(token)

        with tempfile.TemporaryDirectory() as tmp_dir:
            loader = OnlineTemplateLoader(tmp_dir)
            template_options, renderer = loader.initialise_from_template_api(
                session, template_name
            )

            if (
                "CURVENOTE_ENV" in os.environ
                and os.environ["CURVENOTE_ENV"] == "development"
            ):
                url = "https://localhost:8083/oxa:9NOAIcplsbvUjvKy9PuA/p4uJR9W9gfbz3gfIPa96.27"
            else:
                url = "https://curvenote.com/oxa:nJ1zXZpgPHwAIvQtPCe4/efeOVBOpWerZdEqvVtEL.20"
            assert decode_oxa_link(url) is not None
            latex_project = LatexProject.build_single_article_by_url(
                tmp_dir, session, url, cast(BlockFormat, template_options.tex_format)
            )
            builder = LatexBuilder(template_options, renderer, tmp_dir)
            builder.build(*latex_project.dump(template_options.get_allowed_tags()))


@pytest.fixture(params=[None, "default", "plain_latex"], name="cli_template_name")
def _cli_template_name(request):
    return request.param


def test_cli_build_latex_with_template(cli_template_name):
    """
    Pull a full article using the cli and build it with the template
    """

    if "CURVENOTE_TOKEN" in os.environ:
        token = os.environ["CURVENOTE_TOKEN"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            if (
                "CURVENOTE_ENV" in os.environ
                and os.environ["CURVENOTE_ENV"] == "development"
            ):
                url = "https://localhost:8083/oxa:9NOAIcplsbvUjvKy9PuA/p4uJR9W9gfbz3gfIPa96.27"
            else:
                url = "https://curvenote.com/oxa:nJ1zXZpgPHwAIvQtPCe4/efeOVBOpWerZdEqvVtEL.17"
            assert decode_oxa_link(url) is not None

            CLI_CMD = f"python -m curvenote build-latex {tmp_dir} --url={url}"
            if cli_template_name is not None:
                CLI_CMD = CLI_CMD + f" --template={cli_template_name}"
            ret_val = subprocess.run(CLI_CMD, shell=True)
            assert ret_val.returncode == 0


def test_cli_pull_as_latex():
    """
    Pull a full article using the cli
    """

    if "CURVENOTE_TOKEN" in os.environ:
        token = os.environ["CURVENOTE_TOKEN"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            if (
                "CURVENOTE_ENV" in os.environ
                and os.environ["CURVENOTE_ENV"] == "development"
            ):
                url = "https://localhost:8083/oxa:9NOAIcplsbvUjvKy9PuA/p4uJR9W9gfbz3gfIPa96.27"
            else:
                url = "https://curvenote.com/oxa:nJ1zXZpgPHwAIvQtPCe4/efeOVBOpWerZdEqvVtEL.17"
            assert decode_oxa_link(url) is not None

            CLI_CMD = f"python -m curvenote pull-as-latex {tmp_dir} --url={url}"
            ret_val = subprocess.run(CLI_CMD, shell=True)
            assert ret_val.returncode == 0
