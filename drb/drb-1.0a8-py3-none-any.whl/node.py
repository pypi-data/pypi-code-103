from __future__ import annotations

import abc
from typing import List, Dict, Optional, Tuple, Any
from .item import DrbItem
from .node_impl import NodeImpl
from .path import ParsedPath

"""
    Generic node interface. This interface represents a single node of a tree
    of data. Any node can have no, one or several children. This interface
    provides the primarily operations to browse an entire data structure. All
    implementations of the "Data Request Broker" shall be able to produce such
    nodes.
"""


class DrbNode(DrbItem, NodeImpl, abc.ABC):
    @property
    @abc.abstractmethod
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        """ Returns attributes of the current node.
        This operation all attributes owned by the current node.
        Attributes are represented by a dict with as key the tuple
        (name, namespace_uri) of the attribute and as value the value of this
        attribute.
        :return: The a dict attributes of the current node.
        :rtype: dict
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        """
        Returns the value of the corresponding attribute, following it's name
        and it's namespace URI for the matching.
        :param name: attribute name to match.
        :type name: str
        :param namespace_uri: attribute namespace URI to match.
        :type namespace_uri: str
        :return: the associated value of the matched attribute.
        :rtype: Any
        :raises:
            DrbException: if the given name and namespace URI not math any
                          attribute of the current node.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def parent(self) -> Optional[DrbNode]:
        """
        The parent of this node. Returns a reference to the parent node of the
        current node according to the current implementation. Most of the
        nodes have a parent except root nodes or if they have just been
        removed, etc. If the node has no parent the operation returns None.
        :return: The parent of this node or None.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def path(self) -> ParsedPath:
        """ The full path of this node.
        The path it the complete location of this node. The supported format
        is URI and apache common VFS. Examples of path (

        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def children(self) -> List[DrbNode]:
        """
        The list of children of the current node. Returns a list of
        references to the children of the current node. The current node may
        have no child and the operation returns therefore a null reference.
        :return: The list of children if any null otherwise.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def has_child(self) -> bool:
        """
        Checks if current node is parent of at least one child.
        :return: true if current node has at least one child, false otherwise
        """
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        """
        Releases all resources attached to the current node.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __len__(self):
        """len operator return the number of children.
        This len operator returns the children count.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, item):
        """Implements the item in brace operator to access this node children.
        The brace operator is used to access the children node, according to
        the following rules:

        - If item is a DrbNode, this node retrieved from this nodes children is
        returned. In case of multiple occurrence of the node, a list of nodes
        is returned.

        - If item is a single string, the children nodes with the item as name
        is retrieved from its children.

        - If item is a integer (int), the item-th children node will be
         returned.

         - If item is a tuple (name: str, namespace: str, occurrence: int)
              * item[0] shall be the children node name,
              * item[1] could be the namespace
              * item[2] could be the occurrence of the node.
            Namespace and occurrence are optional, node name is mandatory.
         The tuple retrieved the node occurrence.

         - If Item is subclass of Predicate, children nodes matching this
            predicate are returned.

        Except when using integer index, a list is always returned.
        When the item does not match any result, DrbNodeException is raised,
        except for predicate which is able to return empty child list.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __truediv__(self, child):
        """Div operator setup to manage access to children list.
        The truediv operator is redefined here to manage path navigation as
        posix style representation. It allows access to the children by their
        names.
        The navigation behaviour depends on the right element of the div
        operator:
        - If the right operator is a string, operator results a list of
           children nodes matching this name string.
        - If the right operator is a DrbNode, operator results a list of
           children nodes matching this node name and namespace.
        - If the the right operator is subclass of class Predicate, operator
           results a list of children nodes matching the predicate
        """
        raise NotImplementedError
