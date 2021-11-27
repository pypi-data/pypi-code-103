from ..soup import Soup
from ..element import Element
from ..topic import Topic
from ..exercise import Exercise
from ..task import Task
from ..group import Group
from .. import errors

from sphinx.util import logging
_logger = logging.getLogger(__name__)


def _prepare_app(app):
    if hasattr(app, 'ot_soup'):
        raise OpenTrainingError('Soup already created, cannot add one more element')
    if not hasattr(app.env, 'ot_elements'):
        app.env.ot_elements = set()

def sphinx_add_element(app, element):
    _prepare_app(app)
    assert isinstance(element, Element)
    app.env.ot_elements.add(element)    

def sphinx_purge_doc(app, env, docname):
    if hasattr(env, 'ot_elements'):
        env.ot_elements -= {e for e in env.ot_elements if e.docname == docname}

def sphinx_create_soup(app):
    if hasattr(app, 'ot_soup'):
        return

    try:
        app.ot_soup = Soup(app.env.ot_elements)
    except errors.CompoundError as e:
        for err in e:
            _logger.warning(str(err), location=err.userdata)
