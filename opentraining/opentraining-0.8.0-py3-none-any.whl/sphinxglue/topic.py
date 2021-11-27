from . import utils
from . import soup
from .. import errors
from ..topic import Topic

from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import set_source_info
from sphinx.util import logging
from docutils import nodes

logger = logging.getLogger(__name__)


def setup(app):
    app.add_directive('ot-topic', _TopicDirective)
    app.connect('doctree-read', _ev_doctree_read__extract_topicnodes)

def _ev_doctree_read__extract_topicnodes(app, doctree):
    try:
        docname = app.env.docname
        topic_nodes = list(doctree.traverse(_TopicNode))
        if len(topic_nodes) > 1:
            raise errors.OpenTrainingError(f'{docname} contains multiple topics')

        for n in topic_nodes:
            soup.sphinx_add_element(app, Topic(
                title=utils.get_document_title(docname, doctree),
                path=n.path, 
                docname=docname,
                userdata=n,
                dependencies=n.dependencies,
            ))
            n.replace_self([])
    except Exception:
        logger.exception(f'{docname}: cannot extract topic nodes')
        raise
        
class _TopicNode(nodes.Element):
    def __init__(self, path, dependencies):
        super().__init__(self)
        self.title = None
        self.path = path
        self.dependencies = dependencies

class _TopicDirective(SphinxDirective):
    required_arguments = 1   # path

    option_spec = {
        'dependencies': utils.list_of_elementpath,
    }

    def run(self):
        path = utils.element_path(self.arguments[0].strip())
        dependencies = self.options.get('dependencies', [])

        topic = _TopicNode(path=path, dependencies=dependencies)
        topic.document = self.state.document
        set_source_info(self, topic)

        return [topic]

