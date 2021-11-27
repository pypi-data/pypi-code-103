from . import utils
from . import soup
from .. import errors
from ..topic import Topic
from ..project import Project
from ..errors import OpenTrainingError

from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import set_source_info
from sphinx.util import logging
from docutils import nodes


_logger = logging.getLogger(__name__)


def setup(app):
    app.add_directive('ot-project', _ProjectDirective)
    app.connect('doctree-read', _ev_doctree_read__extract_projectnodes)

def _ev_doctree_read__extract_projectnodes(app, doctree):
    try:
        docname = app.env.docname

        for n in doctree.traverse(_ProjectNode):
            soup.sphinx_add_element(app, Project(
                docname = docname, 
                title = utils.get_document_title(docname, doctree), 
                path = n.path,
                userdata = n,
                persons = n.persons,
                tasks = n.tasks,
            ))
            n.replace_self([])
    except Exception:
        _logger.exception(f'{docname}: cannot extract project nodes')
        raise

class _ProjectNode(nodes.Element):
    def __init__(self, path, persons, tasks):
        super().__init__(self)
        self.path = path
        self.persons = persons
        self.tasks = tasks

class _ProjectDirective(SphinxDirective):
    required_arguments = 1   # path
    option_spec = {
        'persons': utils.list_of_elementpath,
        'tasks': utils.list_of_elementpath,
    }

    def run(self):
        path = utils.element_path(self.arguments[0].strip())
        persons = self.options.get('persons')
        tasks = self.options.get('tasks')

        project = _ProjectNode(
            path = path,
            persons = persons,
            tasks = tasks,
        )

        project.document = self.state.document
        set_source_info(self, project)

        return [project]
