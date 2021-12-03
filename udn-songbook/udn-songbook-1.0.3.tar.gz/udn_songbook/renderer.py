# vim: set ft=python ts=4 sts=2 sw=4 et ci nu:
# wrapper around jinja2 so we can call it
# from both song and book, and potentially
# override or replace it

import os
import sys

import jinja2

from .filters import custom_filters


class Renderer(object):
    """
    Generic class, will call out to jinja2 or any other rendering
    engine we choose to use

    All SOng objects contain HTML markup, these classes are intended to
    use that to output HTML documents
    """

    def __init__(self, templatedirs=[], stylesheets=[]):
        """
        creates  a jinja2 environment, loading templates from the specified
        directory, falling back on templates defined in this package

        Same applies to css. Should probably move over to scss but there you go.
        """
        self.env = jinja2.Environment(
            loader=jinja2.ChoiceLoader(
                [
                    jinja2.FileSystemLoader(templatedirs),
                    jinja2.PackageLoader("udn_songbook", "templates"),
                ]
            )
        )
        # update the filter list
        self.env.filters.update(custom_filters)

    def render(self, template, context, **kwargs):
        """
        Render the chose templated  with the provided context
        The template will be searched for in the given paths, in order, stopping at
        first match - if no template directories are provided, uses the templates
        from this package.
        """
        tpl = self.env.get_template(template)
        return tpl.render(context, **kwargs)


class HTMLRenderer(Renderer):
    """
    The HTML Renderer uses Jinja2 templates to generate HTML pages and an index if appropriate
    Each song will have HTML markup automatically generated via ukedown
    """

    pass


class PDFRenderer(Renderer):
    """
    The PDF Renderer processes one or more songsheets and returns them as rendered PDF docs
    """

    pass
