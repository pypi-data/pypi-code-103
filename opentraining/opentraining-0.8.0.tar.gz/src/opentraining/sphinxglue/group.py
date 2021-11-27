from . import utils
from . import soup
from .. import errors
from ..topic import Topic
from ..group import Group
from ..errors import OpenTrainingError

from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import set_source_info
from sphinx.util import logging
from docutils import nodes

from networkx.algorithms.dag import topological_sort

_logger = logging.getLogger(__name__)


def setup(app):
    app.add_directive('ot-group', _GroupDirective)
    app.connect('doctree-read', _ev_doctree_read__extract_groupnodes)

def _ev_doctree_read__extract_groupnodes(app, doctree):
    '''Add group metadata to soup. Leave group node intact; it is expanded
    later when all metadata has been collected.'''

    try:
        docname = app.env.docname
        group_nodes = list(doctree.traverse(_GroupNode))
        if len(group_nodes) > 1:
            raise OpenTrainingError(f'{docname} contains multiple groups')

        for n in group_nodes:
            soup.sphinx_add_element(app, Group(
                docname=docname, 
                title=utils.get_document_title(docname, doctree), 
                path=n.path,
                userdata=n,
            ))
            n.replace_self([])
    except Exception:
        _logger.exception(f'{docname}: cannot extract group nodes')
        raise

class _GroupNode(nodes.Element):
    def __init__(self, path):
        super().__init__(self)
        self.path = path

class _GroupDirective(SphinxDirective):
    required_arguments = 1   # path

    def run(self):
        path = utils.element_path(self.arguments[0].strip())

        group = _GroupNode(path=path)
        group.document = self.state.document
        set_source_info(self, group)

        return [group]

