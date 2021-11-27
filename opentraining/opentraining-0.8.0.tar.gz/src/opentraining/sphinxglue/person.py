from . import utils
from . import soup
from .. import errors
from ..person import Person

from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import set_source_info
from sphinx.util import logging
from docutils import nodes

logger = logging.getLogger(__name__)


def setup(app):
    app.add_directive('ot-person', _PersonDirective)
    app.connect('doctree-read', _ev_doctree_read__extract_personnodes)

def _ev_doctree_read__extract_personnodes(app, doctree):
    try:
        docname = app.env.docname
        person_nodes = list(doctree.traverse(_PersonNode))
        if len(person_nodes) > 1:
            raise errors.OpenTrainingError(f'{docname} contains multiple persons')

        for n in person_nodes:
            soup.sphinx_add_element(app, Person(
                docname=docname,
                title=utils.get_document_title(docname, doctree),
                path=n.path, 
                userdata=n,
                firstname=n.firstname,
                lastname=n.lastname,
            ))
            n.replace_self([])
    except Exception:
        logger.exception(f'{docname}: cannot extract person nodes')
        raise
        
class _PersonNode(nodes.Element):
    def __init__(self, path, firstname, lastname):
        super().__init__(self)
        self.title = None
        self.path = path
        self.firstname = firstname
        self.lastname = lastname

class _PersonDirective(SphinxDirective):
    required_arguments = 1   # path

    option_spec = {
        'firstname': str,
        'lastname': str,
    }

    def run(self):
        path = utils.element_path(self.arguments[0].strip())
        firstname = self.options.get('firstname')
        lastname = self.options.get('lastname')

        person = _PersonNode(path=path, 
                             firstname=firstname,
                             lastname=lastname)
        person.document = self.state.document
        set_source_info(self, person)

        return [person]
