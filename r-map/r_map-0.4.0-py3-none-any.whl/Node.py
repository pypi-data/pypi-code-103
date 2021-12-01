from __future__ import annotations
from collections import OrderedDict as OD
from uuid import uuid4
from itertools import chain
from operator import itemgetter
import logging
logger = logging.getLogger(__name__)

class NodeMeta(type):
    '''used to magically update the nb_attrs'''
    def __new__(mcs, name, bases, attrs):
        _nb_attrs = attrs.get('_nb_attrs', frozenset())
        for b in bases:
            if hasattr(b, '_nb_attrs'):
                _nb_attrs |= b._nb_attrs
        attrs['_nb_attrs'] = _nb_attrs

        new_class = super().__new__(mcs, name, bases, attrs)
        return new_class

class GetIoFunc:
    """Non data descriptor to get a user supplied IO function from a parent node
    if necessary
    """
    def __set_name__(self, owner, name):
        self.name = name
    def __get__(self, instance, owner):
        """As this is a non data descriptor, the instance won't ever have a
        reference to the supplied function. Need to query the parent
        """
        if not instance:
            raise AttributeError("Descriptor only to be used on instances")
        if instance.parent:
            func = getattr(instance.parent, self.name)
            setattr(instance, self.name, func)
            return func
        else:
            raise AttributeError(f"No {self.name} function provided!")

class Node(metaclass=NodeMeta):
    '''A node in the tree data structure representing the register map'''
    #these names are not to be looked for in children
    #when pickling, only be concerned with these
    _nb_attrs = frozenset(['name', 'descr', 'doc', 'uuid', '_ref', '_alias'])

    _reg_read_func = GetIoFunc()
    _reg_write_func = GetIoFunc()
    _block_read_func = GetIoFunc()
    _block_write_func = GetIoFunc()

    def __init__(self, **kwargs):
        '''
        Args:
            name(str)      : A the name of the Node
            descr(str)     : A description for the node (usually shorter than doc)
            doc(str)       : A documentation string for the node
            uuid(str)      : A Universal Identifier
            _ref(Node): If not None, the reference to the Node that this
                              node is an instance of
            _alias(bool): If True, this node is an alias for the reference node
        '''
        for key in self._nb_attrs:
            setattr(self, key, kwargs.get(key, None))
        self._parent = None

        if self.name is None:
            raise ValueError("Passed None for name parameter. name is a required parameter")
        #if not self.name.isidentifier():
        #    raise ValueError("supplied name is not a valid identifier: {}".format(self.name))
        self._children = {}
        self.__doc__ = next((i for i in (self.descr, self.doc) if i), 'No description')
        self.uuid = kwargs.get('uuid', uuid4().hex)

        unexpecteds = kwargs.keys() - self._nb_attrs
        if unexpecteds:
            raise ValueError("Got unexpected keyword arguments: {}".format('\n'.join(unexpecteds)))

    @property
    def parent(self):
        return self._parent

    def _add(self, item):
        """Add node to self._children. Called from `parent` property
        """
        if isinstance(item, Node):
            if item in self:
                return #already added
            elif item.name in self:
                if item.parent:
                    #maintain consistency as we're replacing an existing item
                    item.parent._remove(item)
            self._children[item.name] = item
            item._parent = self
        else:
            raise ValueError("Expected argument to be of type Node or one of "
                             "its descendents")
    def _remove(self, item):
        if isinstance(item, Node) and item in self:
            self._children.pop(item.name)
            item._parent = None
        else:
            raise ValueError("Expected argument to be of type Node or one of "
                             "its descendents")

    def __contains__(self, item):
        if isinstance(item, Node):
            return item.name in self._children
        elif isinstance(item, str):
            return item in self._children
        else:
            return NotImplemented

    def __dir__(self):
        local_items = {f for f in vars(self) if f[0] != '_'}
        children    = {c for c in self._children}
        class_objs  = {s for s in dir(type(self)) if s[0] != '_'}
        return list(local_items | children | class_objs)

    def __getattr__(self, name):
        if name in self._nb_attrs or name[:2] == '__':
            raise AttributeError(f"{name} not found")
        try:
            return self._children[name]
        except (KeyError, AttributeError) as e:
            raise AttributeError(f"{name} not found")

    def __getitem__(self, item):
        return self._children[item]

    def __iter__(self):
        return (child for child in self._children.values())

    def _walk(self, levels=2, top_down=True):
        'return up to <levels> worth of nodes'
        if levels == 0: #i am a leaf node
            yield self
            return
        if top_down:
            yield self
        for node in self:
            #if a negative number is supplied, all elements below will be traversed
            if levels >= 0:
                new_levels = levels -1
            else:
                new_levels = levels
            yield from node._walk(levels=new_levels, top_down=top_down)
        if not top_down:
            yield self

    def __bool__(self):
        return True #don't call __len__

    def __len__(self):
        return len(self._children)

    def __str__(self):
        return f'{type(self).__name__}: {self.name}'

    def __repr__(self):
        items = ((k,getattr(self, k)) for k in self._nb_attrs)
        #don't want these to be in the repr
        me = {k:v for (k,v) in items if v is not None}
        if '_ref' in me:
            me['_ref'] = me['_ref'].uuid

        arg_strings = (f'{k}={v!r}' for (k,v) in sorted(me.items(), key=itemgetter(0)))
        return f"{type(self).__name__}({','.join(arg_strings)})"

    def _copy(self, *, new_instance:bool=False, new_alias:bool=False,
              _context:dict=None, _deep_copy:bool=True, **kwargs):
        """Create a deep copy of this object

        :param new_instance: Indicate if the copy should be considered an
            instance of this node. When a node is an instance of another, it
            will have a `_ref` attribute pointing to it.
        :param new_alias: Indicate if the copy should be an alias of this node.
              If True, the copy will have an `_alias` boolean set to True.
        :param _context: A dictionary holding mapping of original objects to
             newly created copies. This is essential for ensuring that when the
             same child bitfield is being copied from multiple parent bitfield
             references, only a single newly created copy will be used
        :param _deep_copy: If True, copy children too. Mainly used in
                           BitFieldRef override.
        :returns: The newly created copy
        """
        if _context is None:
            _context = {}
        elif self in _context:
            return _context[self] # I've already been copied


        existing_items = {k:getattr(self, k) for k in self._nb_attrs}
        #It's a copy so shouldn't have the same uuid
        existing_items.pop('uuid', None)
        existing_items.update(kwargs)

        if new_instance:
            existing_items['_ref'] = self
        elif not ('_ref' in kwargs and kwargs['_ref']) and self._ref:
            existing_items['_ref'] = self._ref._copy(_context=_context)

        if new_alias:
            existing_items['_alias'] = True

        new_obj = type(self)(**existing_items)

        _context[self] = new_obj

        if _deep_copy:
            for obj in self:
                new_obj._add(obj._copy(new_alias=new_alias, _context=_context))

        return new_obj

    def validate(self):
        """Do some validation checks on the parameters set on this instance and
        that of the child bitfield

        :returns: Iterable of errors found
        """
        for child in self:
            yield from child.validate()

