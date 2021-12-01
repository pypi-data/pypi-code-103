# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

from datetime import datetime
from collections import defaultdict

from slugify import slugify

from stag.signals import signals
from stag.ecs import Page, Taxonomy, Term, Metadata, Content
from stag.utils import chdir, date_sorting_key
from stag.exceptions import StagPluginError

_TAXONOMIES = []
_RAW_TAXO = defaultdict(lambda: defaultdict(set))


def copy_output_type(pages, default="html"):
    for page in pages:
        if page.output and page.output.type:
            return page.output.type
    return default


def update_metadata(page, **kw):
    if not page.metadata:
        page.metadata = Metadata()
    kw.update(page.metadata.data)
    page.metadata.data = kw


def init_taxonomies(site):
    if not site.config.taxonomies:
        return

    global _TAXONOMIES
    _TAXONOMIES = [
        Taxonomy(
            name=ttab.key,
            singular=ttab.singular,
            plural=ttab.plural,
            possible_terms=ttab.possible_terms,
        )
        for ttab in site.config.taxonomies
    ]


def add_pages(site):
    for page in site.pages:
        if not page.metadata:
            continue

        for taxonomy in _TAXONOMIES:
            terms = page.metadata.get(taxonomy.name)

            if not terms:
                continue
            if not isinstance(terms, list):
                terms = [terms]

            for term in terms:
                if taxonomy.possible_terms is not None:
                    if term not in taxonomy.possible_terms:
                        msg = f"invalid term: '{term}' is not a possible term for {taxonomy.plural}"
                        raise StagPluginError(msg)

                _RAW_TAXO[taxonomy.name][term].add(page)


def finalize(site):
    # Pages can be created by users for taxonomies and terms. In this situation
    # stag will override some members (page.list), update others with unset
    # values (metadata) and leave the rest untouched (e.g. content).
    #
    # This is to give users possibility to hardcode custom metadata for specific
    # taxonomies.
    now = datetime.now()
    for taxonomy in _TAXONOMIES:
        baseslug = slugify(taxonomy.name)
        taxo_page = site.get_or_make_page(baseslug)
        taxo_page.taxonomy = taxonomy
        update_metadata(taxo_page, title=taxonomy.plural, date=now)

        for term, pages in _RAW_TAXO[taxonomy.name].items():
            termslug = slugify(str(term))
            term_page = site.get_or_make_page(f"{baseslug}/{termslug}")
            term_page.term = Term(termslug, sorted(pages, key=date_sorting_key()))
            term_page.output = Content(type=copy_output_type(pages))
            update_metadata(term_page, title=term, date=now, taxonomy=taxonomy.name)

            taxo_page.taxonomy.terms.append(term_page)

        taxo_page.taxonomy.terms.sort()
        taxo_page.output = Content(type=copy_output_type(taxo_page.taxonomy.terms))


def register_plugin(site):
    global _TAXONOMIES
    global _RAW_TAXO
    _TAXONOMIES = []
    _RAW_TAXO = defaultdict(lambda: defaultdict(set))

    site.signals.readers_finished.connect(add_pages)
    site.signals.processors_init.connect(finalize)
    init_taxonomies(site)
