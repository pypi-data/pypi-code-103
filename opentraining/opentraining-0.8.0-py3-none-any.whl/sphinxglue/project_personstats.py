from . import utils
from . import soup
from ..project import Project
from ..person import Person
from ..task import Task
from ..group import Group
from ..errors import OpenTrainingError

from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import set_source_info
from docutils import nodes
from docutils.parsers.rst import directives 


from sphinx.util import logging
_logger = logging.getLogger(__name__)


def setup(app):
    app.add_directive('ot-project-personstats', _ProjectPersonStatsDirective)
    app.connect('doctree-resolved', _ev_doctree_resolved__expand_project_personstats_nodes)

def _ev_doctree_resolved__expand_project_personstats_nodes(app, doctree, docname):
    for n in doctree.traverse(_ProjectPersonStatsNode):
        try:
            project = app.ot_soup.element_by_path(n.project, userdata=n)
        except OpenTrainingError as e:
            _logger.warning(e, location=e.userdata)
            n.replace_self([])
            continue

        table = nodes.table()
        tgroup = nodes.tgroup(cols=5)
        table += tgroup
        tgroup += nodes.colspec(colwidth=8)
        tgroup += nodes.colspec(colwidth=4)
        tgroup += nodes.colspec(colwidth=4)
        tgroup += nodes.colspec(colwidth=4)
        tgroup += nodes.colspec(colwidth=4)

        if 'thead':
            thead = nodes.thead()
            tgroup += thead
            row = nodes.row()
            thead += row

            entry = nodes.entry()
            row += entry
            entry += nodes.Text('Person')

            entry = nodes.entry()
            row += entry
            entry += nodes.Text('Implementation')

            entry = nodes.entry()
            row += entry
            entry += nodes.Text('Documentation')

            entry = nodes.entry()
            row += entry
            entry += nodes.Text('Integration')

            entry = nodes.entry()
            row += entry
            entry += nodes.Text('Total')

        if 'tbody':
            tbody = nodes.tbody()
            tgroup += tbody

            if n.sort_by == 'name': 
                key=lambda s: (s[0].lastname, s[0].firstname)
            elif n.sort_by == 'points-total':
                key=lambda s: s[4]
            else:
                assert False, 'unknown sort_by: '+sort_by

            if n.sort_order == 'ascending':
                reverse = False
            elif n.sort_order == 'descending':
                reverse = True
            else:
                assert False, 'unknown sort_order: '+sort_order

            stats = project.personstats()
            for person, implementation_points, documentation_points, integration_points, total_points in sorted(stats, key=key, reverse=reverse):
                row = nodes.row()
                tbody += row

                # link to person
                entry = nodes.entry()
                row += entry
                p = nodes.paragraph()
                entry += p
                if person.firstname and person.lastname:
                    text = f' {person.lastname} {person.firstname}'
                else:
                    text = person.title
                p += [utils.make_reference(text=text,
                                           from_docname=docname, to_docname=person.docname,
                                           app=app)]

                entry = nodes.entry()
                row += entry
                entry += nodes.Text(str(implementation_points))

                entry = nodes.entry()
                row += entry
                entry += nodes.Text(str(documentation_points))

                entry = nodes.entry()
                row += entry
                entry += nodes.Text(str(integration_points))

                entry = nodes.entry()
                row += entry
                entry += nodes.Text(str(total_points))

        n.replace_self([table])

class _ProjectPersonStatsNode(nodes.Element):
    def __init__(self, project, sort_by, sort_order):
        super().__init__(self)
        self.project = project
        self.sort_by = sort_by
        self.sort_order = sort_order
        
class _ProjectPersonStatsDirective(SphinxDirective):
    required_arguments = 1   # project
    option_spec = {
        'sort-by': lambda argument: directives.choice(argument, ('name', 'points-total')),
        'sort-order': lambda argument: directives.choice(argument, ('ascending', 'descending')),
    }

    def run(self):
        project = utils.element_path(self.arguments[0].strip())

        sort_by = self.options.get('sort-by', 'name')
        sort_order = self.options.get('sort-order', 'ascending')

        persons = _ProjectPersonStatsNode(
            project = project, 
            sort_by = sort_by, 
            sort_order = sort_order)
        persons.document = self.state.document
        set_source_info(self, persons)

        return [persons]
