# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

import os
import logging

import attr
from jinja2 import Template, Environment, FileSystemLoader, FunctionLoader, ChoiceLoader
from jinja2.exceptions import TemplateSyntaxError

from .template_functions import update_env
from stag.site import SiteTemplateProxy
from stag.exceptions import StagError

try:
    from stag._version import version
except ImportError:
    version = "unknown version"


log = logging.getLogger(__name__)


_DEFAULT_TEMPLATE = "{{ content }}"
_DEFAULT_HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="{{{{ site.config.get('lang', 'en') }}}}">
  <head>
    <meta name="generator" content="stag ({version})" />
    <meta charset="UTF-8">
    <title>{{{{ page.metadata.title }}}} - {{{{ site.config.title }}}}</title>
  </head>
  <body>
  {{{{ content }}}}
  </body>
</html>
"""


def load_default_template(name):
    log.error(f"Template not found: {name}. Using built-in basic template.")
    _, ext = os.path.splitext(name)
    template = _DEFAULT_HTML_TEMPLATE if ext == ".html" else _DEFAULT_TEMPLATE
    return template


def get_env(theme, config):
    env = Environment(
        loader=ChoiceLoader(
            [
                FileSystemLoader(theme),
                FunctionLoader(load_default_template),
            ]
        ),
        extensions=["jinja2.ext.debug", "jinja2.ext.do"],
        trim_blocks=True,
        lstrip_blocks=True,
    )
    update_env(env, config)
    return env


def is_term(page):
    return bool(page.term)


def is_taxonomy(page):
    return bool(page.taxonomy)


def get_default_type(page, templates):
    if is_taxonomy(page):
        return templates["taxonomy"]
    if is_term(page):
        return templates["list"]
    return templates["page"]


def file_in_url(url):
    bn = os.path.basename(url)
    _, ext = os.path.splitext(bn)
    return bool(ext)


def render_page(page, site, env):
    config = site.config
    myconfig = config.template

    type_ = page.metadata.get("type")
    if not type_:
        type_ = get_default_type(page, myconfig.templates)

    try:
        template = env.get_template(f"{type_}.{page.output.type}")
    except TemplateSyntaxError as e:
        raise StagError(f"{e.filename}:{e.lineno}: {e.message}")
    url = page.relurl.strip("/")

    # TODO: test this behavior (mgoral, 2021-09-21)
    if file_in_url(url):
        outpath = os.path.join(config.output, url)
    else:
        index = f"index.{page.output.type}"
        outpath = os.path.join(config.output, url, index)

    if os.path.exists(outpath):
        log.error(f"page already exists, skipping: {outpath}")
        return

    outdir = os.path.dirname(outpath)
    if outdir:
        os.makedirs(outdir, exist_ok=True)
    with open(outpath, "w") as fd:
        sp = SiteTemplateProxy(site)
        try:
            fd.write(template.render(content=page.output.content, site=sp, page=page))
        except Exception as e:
            path = page.source.path if page.source else page.relurl
            raise StagError(f"Rendering of {path} failed: {str(e)}")
