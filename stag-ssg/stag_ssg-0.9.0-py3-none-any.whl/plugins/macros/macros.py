# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

import os

from typing import Optional as _Optional

import attr
from jinja2 import Template, Environment, ChoiceLoader, FileSystemLoader, PackageLoader
from jinja2.exceptions import TemplateSyntaxError, TemplateNotFound

from stag.signals import signals
from stag.ecs import Page
from stag.site import SiteTemplateProxy


class MacroError(Exception):
    pass


def raise_macro_error(msg):
    raise MacroError(msg)


def import_module(*a, **kw):
    import importlib

    return importlib.import_module(*a, **kw)


@attr.s(auto_attribs=True)
class MacrosConfig:
    path: _Optional[str] = None


def is_viable(page):
    return page.source and page.input and page.input.content


def get_env(macros_dir, theme_dir):
    loaders = [FileSystemLoader(dir) for dir in [macros_dir, theme_dir] if dir]
    loaders.append(PackageLoader("stag.plugins", "macros"))  # builtin
    env = Environment(
        loader=ChoiceLoader(loaders),
        trim_blocks=True,
        lstrip_blocks=True,
        extensions=["jinja2.ext.debug", "jinja2.ext.do"],
    )
    env.globals["raise"] = raise_macro_error
    env.globals["import_module"] = import_module

    return env


def mutate(page, site, env):
    try:
        template = env.from_string(page.input.content)
        sp = SiteTemplateProxy(site)
        page.input.content = template.render(page=page, site=sp)
    except TemplateNotFound as e:
        raise MacroError(f"{page.source.relpath}: missing macro definitions file: {e}")
    except Exception as e:
        raise MacroError(f"{page.source.relpath}: {e}")


def resolve_macros(site):
    config = site.config
    myconfig = config.plugins.macros

    env = get_env(myconfig.path, config.template.name)
    env.globals["site"] = site
    env.globals["print"] = print

    for page in site.pages:
        if page.source and page.input:
            mutate(page, site, env)


def register_plugin(site):
    site.config.update_plugin_table("macros", MacrosConfig())
    site.signals.readers_finished.connect(resolve_macros)
