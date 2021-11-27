from . import errors
from .element import Element, verify_is_path
from .node import Node


class Group(Element):
    def __init__(self, title, path, docname, userdata):
        super().__init__(
            title=title, 
            path=path, 
            docname=docname, 
            userdata=userdata)
        self._children = {}    # {name: element}

    def __len__(self):
        return len(self._children)

    def add_element(self, element, userdata):
        child_name = element._requested_path[0]
        if len(element._requested_path) == 1: # leaf; add to children
            child = self._children.get(child_name)
            if child:
                raise errors.OpenTrainingError(f'{self}: cannot add "{child_name}"; already exists: {child}', 
                                               userdata=userdata)
            self._children[child_name] = element
            del element._requested_path
            element.parent = self
        else:
            parent = self._children.get(child_name)
            if parent is None:
                raise errors.OpenTrainingError(f'{self}: cannot add "{element._requested_path}": '
                                        f'intermediate "{child_name}" does not exist')
            element._requested_path = element._requested_path[1:]
            parent.add_element(element, userdata=self.userdata)

    def element_by_path(self, path, userdata):
        '''Get element by path. path is relative to this group.'''
        
        verify_is_path(path, userdata)

        element = self._children.get(path[0])
        if element is None:
            raise errors.PathNotFound(f'{self}: no element with name "{path[0]}"', userdata=userdata)
        if len(path) == 1:
            return element

        return element.element_by_path(path[1:], userdata)

    def child_by_name(self, name):
        '''Get direct child element by name.'''
        child = self._children.get(name)
        if child is None:
            raise errors.OpenTrainingError(f'{self}: no child with name {name}')
        return child

    def element_name(self, element):
        '''Get name of element under which it is know to his group.

        Raises OpenTrainingError if element not there.

        '''
        for name, elem in self._children.items():
            if elem is element:
                return name
        else:
            raise errors.OpenTrainingError(f'{element} is not a child of {self}')

    def has_element(self, element):
        '''Does this group have the element?'''
        for name, elem in self._children.items():
            if elem is element:
                return True
        return False

    def iter_recursive(self, cls=None):
        '''Iterator (name, element) over descendants, recursively'''
        if cls:
            assert issubclass(cls, Element)
        else:
            cls = Element

        if issubclass(Group, cls):
            yield self

        for name, elem in self._children.items():
            if isinstance(elem, Group):
                yield from elem.iter_recursive(cls)
            elif isinstance(elem, cls):
                yield elem
