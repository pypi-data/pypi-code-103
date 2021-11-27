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
    app.add_directive('ot-project-taskstats', _ProjectTaskStatsDirective)
    app.connect('doctree-resolved', _ev_doctree_resolved__expand_project_taskstats_nodes)

def _ev_doctree_resolved__expand_project_taskstats_nodes(app, doctree, docname):
    for n in doctree.traverse(_ProjectTaskStatsNode):
        try:
            project = app.ot_soup.element_by_path(n.project, userdata=n)
        except OpenTrainingError as e:
            _logger.warning(e, location=e.userdata)
            n.replace_self([])
            continue

        table = nodes.table()
        tgroup = nodes.tgroup(cols=8)
        table += tgroup
        tgroup += nodes.colspec(colwidth=8)
        tgroup += nodes.colspec(colwidth=4)
        tgroup += nodes.colspec(colwidth=1)
        tgroup += nodes.colspec(colwidth=4)
        tgroup += nodes.colspec(colwidth=1)
        tgroup += nodes.colspec(colwidth=4)
        tgroup += nodes.colspec(colwidth=1)
        tgroup += nodes.colspec(colwidth=2)

        if 'thead':
            thead = nodes.thead()
            tgroup += thead
            row = nodes.row()
            thead += row

            entry = nodes.entry()
            row += entry
            entry += nodes.Text('Task')

            entry = nodes.entry()
            row += entry
            entry += nodes.Text('Implementation Points')

            entry = nodes.entry()
            row += entry
            entry += nodes.Text('%')

            entry = nodes.entry()
            row += entry
            entry += nodes.Text('Documentation Points')

            entry = nodes.entry()
            row += entry
            entry += nodes.Text('%')

            entry = nodes.entry()
            row += entry
            entry += nodes.Text('Integration Points')

            entry = nodes.entry()
            row += entry
            entry += nodes.Text('%')

            entry = nodes.entry()
            row += entry
            entry += nodes.Text('% Total')

        if 'tbody':
            tbody = nodes.tbody()
            tgroup += tbody

            if n.sort_by == 'title': 
                key=lambda s: s[0].title
            elif n.sort_by == 'percent-total':
                key=lambda s: s[4]
            else:
                assert False, 'unknown sort_by: '+sort_by

            if n.sort_order == 'ascending':
                reverse = False
            elif n.sort_order == 'descending':
                reverse = True
            else:
                assert False, 'unknown sort_order: '+sort_order

            stats = project.taskstats()
            for task, implementation_percent, documentation_percent, integration_percent, total_percent in sorted(stats, key=key, reverse=reverse):
                row = nodes.row()
                tbody += row

                # link to task
                entry = nodes.entry()
                row += entry
                p = nodes.paragraph()
                entry += p
                p += [utils.make_reference(text=task.title,
                                           from_docname=docname, to_docname=task.docname,
                                           app=app)]

                # implementation
                entry = nodes.entry()
                row += entry
                entry += nodes.Text(str(task.implementation_points))

                entry = nodes.entry()
                row += entry
                entry += nodes.Text(str(round(implementation_percent, 2)))

                # documentation
                entry = nodes.entry()
                row += entry
                entry += nodes.Text(str(task.documentation_points))

                entry = nodes.entry()
                row += entry
                entry += nodes.Text(str(round(documentation_percent, 2)))

                # integration
                entry = nodes.entry()
                row += entry
                entry += nodes.Text(str(task.integration_points))

                entry = nodes.entry()
                row += entry
                entry += nodes.Text(str(round(integration_percent, 2)))

                # total
                entry = nodes.entry()
                row += entry
                entry += nodes.Text(str(round(total_percent, 2)))

        n.replace_self([table])

class _ProjectTaskStatsNode(nodes.Element):
    def __init__(self, project, sort_by, sort_order):
        super().__init__(self)
        self.project = project
        self.sort_by = sort_by
        self.sort_order = sort_order

class _ProjectTaskStatsDirective(SphinxDirective):
    required_arguments = 1   # path
    option_spec = {
        'sort-by': lambda argument: directives.choice(argument, ('title', 'percent-total')),
        'sort-order': lambda argument: directives.choice(argument, ('ascending', 'descending')),
    }

    def run(self):
        project = utils.element_path(self.arguments[0].strip())

        sort_by = self.options.get('sort-by', 'title')
        sort_order = self.options.get('sort-order', 'ascending')

        tasks = _ProjectTaskStatsNode(
            project = project, 
            sort_by = sort_by, 
            sort_order = sort_order)
        tasks.document = self.state.document
        set_source_info(self, tasks)

        return [tasks]
