from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union, Any
from ..node import DrbNode
from ..utils.url_node import UrlNode


class DrbFactory(ABC):
    """
    The Factory class defines the abstract class to be implemented in order to
    build drb nodes according to their physical form.
    The factory shall be aware of the implementations available to build nodes
    and build a relation between the physical data and its virtual node
    representation.
    """

    @abstractmethod
    def _create(self, node: DrbNode) -> DrbNode:
        """ Build a DrbNode thanks to this factory implementation.
        :param : The DrbNode of the physical data.
        :type node: DrbNode
        :return: a drb node representing the passed node
        :rtype: DrbNode
        :raises:
            DrbFactoryException: if the factory cannot build the node
        """
        raise NotImplementedError("Call impl method")

    def create(self, source: Union[DrbNode, str]) -> DrbNode:
        """ Build a DrbNode thanks to this factory implementation.
        :param source: the URI or the DrbNode of the physical data.
        :type source: str, DrbNode
        :return: a drb node representing the passed source
        :rtype: DrbNode
        :raises:
            DrbFactoryException: if the given source is not valid
        """
        if isinstance(source, DrbNode):
            return self._create(source)
        else:
            return self._create(UrlNode(source))
