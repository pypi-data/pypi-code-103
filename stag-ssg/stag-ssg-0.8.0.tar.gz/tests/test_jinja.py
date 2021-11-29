import os
import pytest

from stag.utils import chdir
from stag.config import TemplateTable
from stag.writers.jinja import render_page, get_env

from testutils import add_md_file, contents


@pytest.fixture(autouse=True)
def jinja_config(config):
    config.template = TemplateTable()
    config.template.name = "theme"
    return config


@pytest.fixture(autouse=True)
def default_templates(jinja_config, tmp_path):
    templates_dir = tmp_path / jinja_config.template.name
    templates_dir.mkdir()

    html_templ = templates_dir / "page.html"
    html_content = "<html><body>{{ content }}</body></html>"
    html_templ.write_text(html_content)
    print(html_templ)


def test_basic_gen(site, tmp_path):
    mdfile = add_md_file(site, "Content", parse=True)
    render_exp = f"<html><body>{mdfile.output.content}</body></html>"

    with chdir(tmp_path):
        env = get_env(site.config.template.name, site.config)
        render_page(mdfile, site, env)
        out = os.path.join(
            tmp_path, site.config.output, mdfile.relurl.strip("/"), "index.html"
        )
        assert contents(out) == render_exp
