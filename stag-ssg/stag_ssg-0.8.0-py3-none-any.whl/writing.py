# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

import logging

from typing import Optional, Callable, List

from stag.ecs import Path
from stag.writers.jinja import render_page, get_env
from stag.writers.copy import copy_page


log = logging.getLogger(__name__)


def is_static(page):
    return page.source and not page.input


def outputable(page):
    return page.output and page.metadata


def render(site):
    env = get_env(site.config.template.name, site.config)
    site.signals.jinja_environment_prepared.emit(env, site)
    for page in site.pages:
        if outputable(page):
            render_page(page, site, env)
        elif is_static(page):
            copy_page(page, site)
        else:
            log.error(f"Couldn't deduce how to render page: {page.relurl}")
