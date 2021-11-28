from typing import Any, Dict, List, Tuple

from docutils import nodes

from sphinx import addnodes
from sphinx.builders import html as builders
from sphinx.domains.index import IndexRole
from sphinx.util import logging
from sphinx.util.nodes import process_index_entry

logger = logging.getLogger(__name__)

# ------------------------------------------------------------


class TextElement(nodes.Element):

    child_text_separator = ''
    """Separator for child nodes, used by `astext()` method."""

    textclass = nodes.Text

    def __init__(self, rawsource='', text='', *children, **attributes):
        if text != '':
            textnode = self.textclass(text)
            super().__init__(rawsource, textnode, *children, **attributes)
        else:
            super().__init__(rawsource, *children, **attributes)


class term(nodes.Part, TextElement): pass


# ------------------------------------------------------------




# ------------------------------------------------------------

class XRefIndex(IndexRole):
    """
    based on
    https://github.com/sphinx-doc/sphinx/blob/4.x/sphinx/domains/index.py
    """

    textclass = nodes.Text

    def run(self) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
        target_id = 'index-%s' % self.env.new_serialno('index')
        if self.has_explicit_title:
            # if an explicit target is given, process it as a full entry
            title = self.title
            entries = process_index_entry(self.target, target_id)
        else:
            # otherwise we just create a single entry
            if self.target.startswith('!'):
                title = self.title[1:]
                entries = [('single', self.target[1:], target_id, 'main', None)]
            else:
                title = self.title
                entries = [('single', self.target, target_id, '', None)]

        index = addnodes.index(entries=entries)
        target = nodes.target('', '', ids=[target_id])
        text = self.textclass(title, title)
        self.set_source_info(index)
        return [index, target, text], []


# ------------------------------------------------------------


class BaseHTMLBuilder(builders.StandaloneHTMLBuilder):
    """
    based on
    https://github.com/sphinx-doc/sphinx/blob/4.x/sphinx/builders/html/__init__.py
    """

    def index_adapter(self) -> None:
        raise NotImplementedError

    def write_genindex(self) -> None:
        genindex = self.index_adapter()

        indexcounts = []
        for _k, entries in genindex:
            indexcounts.append(sum(1 + len(subitems)
                                   for _, (_, subitems, _) in entries))

        genindexcontext = {
            'genindexentries': genindex,
            'genindexcounts': indexcounts,
            'split_index': self.config.html_split_index,
        }
        logger.info('genindex ', nonl=True)

        if self.config.html_split_index:
            self.handle_page('genindex', genindexcontext,
                             'genindex-split.html')
            self.handle_page('genindex-all', genindexcontext,
                             'genindex.html')
            for (key, entries), count in zip(genindex, indexcounts):
                ctx = {'key': key, 'entries': entries, 'count': count,
                       'genindexentries': genindex}
                self.handle_page('genindex-' + key, ctx,
                                 'genindex-single.html')
        else:
            self.handle_page('genindex', genindexcontext, 'genindex.html')


# ------------------------------------------------------------
