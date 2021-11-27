from .element import Element
from .group import Group
from .node import Node
from .topic import Topic
from .exercise import Exercise
from .task import Task
from . import errors
from . import element

from networkx.algorithms.dag import descendants
from networkx import DiGraph
from networkx.exception import NetworkXError


class Soup:
    def __init__(self, elements):
        self._root_group = Group(
            title='Root', 
            path=(), 
            docname='', 
            userdata=None,
        )

        # build group hierarchy, and throw in remaining elements.
        my_elements = set(elements)
        self._make_hierarchy(self._root_group, my_elements)
        self._add_nodes_to_groups(self._root_group, my_elements)
        assert len(my_elements) == 0, my_elements

        # once the elements have paths in their final hierarchy, we
        # can let them resolve their own stuff. for example, a task
        # initially refers to a person's *path* - final situation
        # should be that a task refers to the Person object directly.
        errs = []
        for element in self._root_group.iter_recursive():
            try:
                element.resolve(self)
            except errors.OpenTrainingError as e:
                errs.append(e)

        if len(errs):
            raise errors.CompoundError(
                'there were errors resolving paths of some elements', errors=errs, 
                # don't know which thing I could refer to when doing a
                # global resolve.
                userdata=None,
            )

        # finally, create graph
        self._worldgraph = self._make_worldgraph(self._root_group)


    @property
    def resolved(self):
        return self._root_group is not None

    @property
    def root(self):
        return self._root_group

    def element_by_path(self, path, userdata):
        return self._root_group.element_by_path(path, userdata=userdata)

    def __iter__(self):
        return self._root_group.iter_recursive()

    def worldgraph(self):
        return self._worldgraph

    def subgraph(self, entrypoints, userdata):
        '''Given entrypoints, compute a subgraph of the world graph that
        contains the entrypoints and all their descendants.

        entrypoints is an iterable of element paths or elements (can
        be mixed)
        '''

        # paranoia
        for e in entrypoints:
            assert isinstance(e, Element)

        topics = set()
        for topic in entrypoints:
            topics.add(topic)
            topics.update(descendants(self._worldgraph, topic))
        return self._worldgraph.subgraph(topics)

    @classmethod
    def _make_hierarchy(cls, root, elements):
        level = 1
        while True:
            all_groups = [g for g in elements if isinstance(g, Group)]
            if not all_groups:   # no more groups
                break
            level_groups = [g for g in all_groups if len(g._requested_path) == level]
            for g in level_groups:
                root.add_element(g, userdata=None)
                elements.remove(g)
            level += 1

    @classmethod
    def _add_nodes_to_groups(cls, root, elements):
        nodes = [n for n in elements if isinstance(n, Element)]
        for n in nodes:
            root.add_element(n, userdata=None)
            elements.remove(n)

    @classmethod
    def _make_worldgraph(cls, root):
        worldgraph = DiGraph()
        collected_errors = []

        for elem in root.iter_recursive(cls=Node):
            if not isinstance(elem, Node):
                continue
            worldgraph.add_node(elem)
            for target_path in elem.dependencies:
                try:
                    target_topic = root.element_by_path(target_path, userdata=elem.userdata)
                    worldgraph.add_edge(elem, target_topic)
                except errors.PathNotFound as e:
                    collected_errors.append(
                        errors.DependencyError(
                            f'{elem.docname} ({elem}): dependency {target_path} not found', 
                            userdata=elem))

        if len(collected_errors) != 0:
            raise errors.CompoundError('cannot build world graph', errors=collected_errors, 
                                       # don't know which thing I could refer to when doing a
                                       # global resolve.
                                       userdata=None,
                                       )
        return worldgraph

            
    def _assert_resolved(self):
        if not self.resolved:
            raise errors.NotCommitted('soup not resolved')

    def _assert_unresolved(self):
        if self.resolved:
            raise errors.AlreadyCommitted('soup already resolved')
