from . import utils
from . import soup
from .. import errors
from ..topic import Topic
from ..exercise import Exercise
from ..task import Task
from ..person import Person
from ..node import Node
from ..group import Group
from ..errors import OpenTrainingError

from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import set_source_info
from sphinx.util import logging
from docutils import nodes

import subprocess
import re

_logger = logging.getLogger(__name__)


def setup(app):
    app.add_directive('ot-graph', _GraphDirective)
    app.connect('doctree-resolved', _ev_doctree_resolved__expand_topicgraph_nodes)

def _ev_doctree_resolved__expand_topicgraph_nodes(app, doctree, docname):
    '''"doctree-resolved" event handler to expand topic graph nodes'''
    try:
        soup.sphinx_create_soup(app)
        expander = _GraphExpander(app=app, docname=docname)
        for n in doctree.traverse(_GraphNode):
            expander.expand(n)
    except OpenTrainingError as err:
        _logger.warning(f'{docname}: cannot expand topic graph, errors follow ...\n{err}', location=err.userdata)

class _GraphNode(nodes.Element):
    def __init__(self, entries):
        super().__init__(self)
        self.entries = entries

class _GraphDirective(SphinxDirective):
    option_spec = {
        'entries': utils.list_of_elementpath,
    }
    def run(self):
        node = _GraphNode(entries=self.options.get('entries', []))
        node.document = self.state.document
        set_source_info(self, node)
        return [node]

class _GraphExpander:
    def __init__(self, app, docname):
        self._app = app
        self._docname = docname

    def expand(self, node):
        try:
            graph, hilit_nodes = self._graphnode_to_graph(node)
            dot = self._graph_to_dot(graph=graph, hilit_nodes=hilit_nodes, node=node)
            svg = self._dot_to_svg(dot=dot, node=node)
            node.replace_self(nodes.raw(svg, svg, format='html'))
        except errors.OpenTrainingError as e:
            node.replace_self([])
            raise

    def _graphnode_to_graph(self, node):
        assert isinstance(node, _GraphNode)

        worldgraph = self._app.ot_soup.worldgraph()
        if len(node.entries) == 0:
            return worldgraph, set()

        # highlight node-type entries. expand group-type entries as
        # their contained nodes.
        node_entries = set()
        hilit_nodes = set()

        for entry_path in node.entries:
            entry = self._app.ot_soup.element_by_path(entry_path, userdata=node)
            if isinstance(entry, Node):
                node_entries.add(entry)
                hilit_nodes.add(entry)
            elif isinstance(entry, Group):
                for elem in entry.iter_recursive(cls=Node):
                    if isinstance(elem, Node):
                        node_entries.add(elem)
            else:
                assert False, entry_path

        return self._app.ot_soup.subgraph(node_entries, userdata=node), hilit_nodes

    def _graph_to_dot(self, graph, hilit_nodes, node):
        lines = [
            'digraph {',
        ]

        root_cluster = self._dot_group_clusters(graph, node=node)
        lines.extend(self._dot_cluster_lines(root_cluster, hilit_nodes=hilit_nodes, node=node))

        for src, dst in graph.edges:
            lines.extend(self._dot_edge_lines(src, dst))

        lines.append('}')

        return '\n'.join(lines)
    
    class Cluster:
        def __init__(self, group):
            self.group = group
            self.clusters = []
            self.nodes = []  # leaf topics

    def _dot_group_clusters(self, graph, node):
        root_cluster = self.Cluster(self._app.ot_soup.root)

        have_clusters = { self._app.ot_soup.root: root_cluster }
        # walk topics and create cluster hierarchy from their
        # containing groups
        for n in graph.nodes:
            assert isinstance(n, Node), n
            cluster = self._dot_make_cluster(n.parent, have_clusters, node=node)
            cluster.nodes.append(n)

        return root_cluster

    def _dot_make_cluster(self, group, have_clusters, node):
        assert type(group) is Group

        cluster = have_clusters.get(group)
        if not cluster:
            cluster = self.Cluster(group)
            have_clusters[group] = cluster
            parent_cluster = self._dot_make_cluster(group.parent, have_clusters, node=node)
            parent_cluster.clusters.append(cluster)

        return cluster

    def _dot_cluster_lines(self, cluster, hilit_nodes, node):
        lines = []
        if cluster.group is not self._app.ot_soup.root:
            lines.append('subgraph cluster_' + self._dot_id_from_path(cluster.group.path) + '{')
            lines.append(f'label = "{cluster.group.title}";')
            lines.append('style = rounded;')  # rounded corners

        for n in cluster.nodes:
            lines.extend(self._dot_node_lines(n, hilit=(n in hilit_nodes)))
        for subcluster in cluster.clusters:
            lines.extend(self._dot_cluster_lines(subcluster, hilit_nodes, node=node))

        if cluster.group is not self._app.ot_soup.root:
            lines.append('}')
        return lines

    @staticmethod
    def _percent_to_rgb(percent):
        # colors taken from
        # https://www.w3schools.com/colors/colors_picker.asp,
        # "Lightness"
        if percent == 0:
            return "#ffffff"
        elif 0 < percent <= 10:
            return "#e6ffe6"
        elif 10 < percent <= 20:
            return "#ccffcc"
        elif 20 < percent <= 30:
            return "#b3ffb3"
        elif 30 < percent <= 40:
            return "#99ff99"
        elif 40 < percent <= 50:
            return "#80ff80"
        elif 50 < percent <= 60:
            return "#66ff66"
        elif 60 < percent <= 70:
            return "#4dff4d"
        elif 70 < percent <= 80:
            return "#33ff33"
        elif 80 < percent <= 90:
            return "#1aff1a"
        elif 90 < percent <= 100:
            return "#00ff00"

        assert False, f'invalid percentage: {percent}'

    def _dot_node_lines(self, node, hilit):
        uri = self._app.builder.get_relative_uri(from_=self._docname, to=node.docname)
        node_id = '_'.join(node.path)

        border = 1
        if hilit:
            border *= 3

        if isinstance(node, Topic):
            return [
                f'{node_id} [',
                f'    label="{node.title}";',
                f'    href="{uri}";',
                '    style=filled;',
                f'    penwidth="{border}";',
                '    fillcolor="#DCDCDC";'
                '];',
            ]
        elif isinstance(node, Exercise):
            return [
                f'{node_id} [',
                f'    label="{node.title}";',
                f'    href="{uri}";',
                '    style=filled;',
                f'    penwidth="{border}";',
                '    fillcolor="red";'
                '];',
            ]
        elif isinstance(node, Task):
            return [
                f'{node_id} [',
                f'    label=<{node.title}>;',
                f'    href="{uri}";',
                '    shape=box;',
                '    style=filled;',
                f'    penwidth="{border}"',
#                f'    fillcolor="{self._percent_to_rgb(node.percent_done)}";'
                '];',
            ]

        elif isinstance(node, Person):
            return [
                f'{node_id} [',
                f'    label="{node.title}";',
                f'    href="{uri}";',
                '    shape=box;',
                '    style=filled;',
                f'    penwidth="{border}";'
                '];',
            ]

    def _dot_edge_lines(self, src, dst):
        src_id = '_'.join(src.path)
        dst_id = '_'.join(dst.path)
        return [f'{src_id} -> {dst_id};']

    _re_width = re.compile(r'width\s*=\s*".*"')
    def _dot_to_svg(self, dot, node):
        try:
            completed = subprocess.run(
                ['dot', '-v', '-T', 'svg'],
                input=dot, check=True, text=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise errors.OpenTrainingError(f'dot exited with status {e.returncode}:\n[dot]\n{dot}\n[stderr]\n{e.stderr}', userdata=node)
        except FileNotFoundError as e:
            raise errors.OpenTrainingError('dot not installed; please install the "graphviz" package (Debianish: "sudo apt install graphviz", Fedorish: "dnf install graphviz")', userdata=node)
    
        svg = completed.stdout
        # strip XML declaration (we are embedding it)
        svg = svg[svg.index('<svg'):]

        if True:
            # patch "width" out (we want it scaled to fit the page)
            width = self._re_width.search(svg)
             # hm. if not there, dot has changed, apparently. fix that.
            assert width is not None
            svg = svg[:width.start()] + svg[width.end():]

        return svg

    def _dot_id_from_path(self,  path):
        return '_'.join(path)
