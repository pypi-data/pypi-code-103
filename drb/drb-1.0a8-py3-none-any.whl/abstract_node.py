from __future__ import annotations

import abc
from typing import List, Union

from .node import DrbNode
from .predicat import Predicate
from .factory.factory_resolver import DrbFactoryResolver, DrbNodeList
from .exceptions import DrbException, DrbNotImplementationException


class AbstractNode(DrbNode, abc.ABC):
    """
    This class regroup default implementation of DrbNode about the browsing
    using bracket and slash and also implementation of some utils functions.
    """
    def __len__(self):
        if not self.children:
            return 0
        return len(self.children)

    def __getitem__(self, item):
        if isinstance(item, DrbNode):
            children = self._get_named_child(name=item.name,
                                             namespace_uri=item.namespace_uri)
        elif isinstance(item, str):
            try:
                children = self._get_named_child(name=item)
            except DrbException as ex:
                raise KeyError(f'Invalid key: {item}') from ex
        elif isinstance(item, int):
            children = self.children[item]
        elif isinstance(item, tuple):
            try:
                if len(item) == 1:
                    children = self[item[0]]
                elif len(item) == 2:
                    if isinstance(item[1], str):
                        children = self._get_named_child(name=item[0],
                                                         namespace_uri=item[1])
                    elif isinstance(item[1], int):
                        children = self._get_named_child(name=item[0],
                                                         occurrence=item[1])
                    else:
                        raise KeyError(f"Invalid key {item}.")
                elif len(item) == 3:
                    children = self._get_named_child(name=item[0],
                                                     namespace_uri=item[1],
                                                     occurrence=item[2])
                else:
                    raise KeyError(f'Invalid key {item}')
            except DrbException as ex:
                raise KeyError(f'Invalid key {item}') from ex
        elif isinstance(item, Predicate):
            children = []
            for c in self.children:
                if item.matches(c):
                    children.append(c)
        else:
            raise TypeError(f"{type(item)} type not supported.")

        if isinstance(children, list):
            return DrbNodeList(children)
        try:
            return DrbFactoryResolver().create(children)
        except DrbException:
            return children

    def __truediv__(self, child):
        if isinstance(child, DrbNode):
            children = self._get_named_child(name=child.name,
                                             namespace_uri=child.namespace_uri)
        elif isinstance(child, str):
            children = self._get_named_child(name=child)
        elif isinstance(child, Predicate):
            children = []
            for c in self.children:
                if child.matches(c):
                    children.append(c)
        else:
            raise DrbNotImplementationException(
                f"{type(child)} type not managed.")
        return DrbNodeList(children)

    def _get_named_child(self, name: str, namespace_uri: str = None,
                         occurrence: int = None) -> Union[DrbNode,
                                                          List[DrbNode]]:
        """
        Retrieves a child with the given name, namespace and occurrence. Can
        also retrieves a list of child if the occurrence is not specified.

        :param name: child name
        :type name: str
        :param namespace_uri: child namespace URI (default: None)
        :type namespace_uri: str
        :param occurrence: child occurrence (default: None)
        :type occurrence: int
        :returns: the requested DrbNode if the occurrence is defined, otherwise
         a list of requested DrbNode children
        :rtype: DrbNode | List[DrbNode]
        """
        if occurrence is not None and (not isinstance(occurrence, int)
                                       or occurrence <= 0):
            raise DrbException(f'Invalid occurrence: {occurrence}')
        try:
            named_children = [x for x in self.children if x.name == name
                              and x.namespace_uri == namespace_uri]
            if len(named_children) <= 0:
                raise DrbException(f'No child found having name: {name} and'
                                   f' namespace: {namespace_uri}')
            if occurrence is None:
                return named_children
            else:
                return named_children[occurrence - 1]
        except (IndexError, TypeError) as error:
            raise DrbException(f'Child ({name},{occurrence}) not found') \
                from error
