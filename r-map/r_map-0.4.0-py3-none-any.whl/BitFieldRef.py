from .Node import Node
from r_map import BitField
from .ValueNodeMixins import UnsignedValueNodeMixin
from .ValidationError import ValidationError

class BitFieldRef(UnsignedValueNodeMixin, Node):
    _nb_attrs = frozenset(['reg_offset', 'slice_width', 'field_offset'])
    """Class to represent a reference to a bitfield. This is useful
    as a register may only have access to a portion of bitfield. The "portion"
    is modelled with this class"""

    def __init__(self, *, reg_offset, slice_width=0, field_offset=0, **kwargs):
        """Initializer for BitFieldRef class
        Definition here merely to define default arguments
        :param reg_offset: The offset within the parent register where this
                           BitFieldRef resides.
        :param slice_width: The width of this bitfield_ref. If this is left at
                            the default 0, use the full width of the child's
                            bitfield ref.
        :param field_offset: The offset within the BitField from where this
                             BitFieldRef applies.
        """
        super().__init__(slice_width=slice_width, reg_offset=reg_offset,
                field_offset=field_offset, **kwargs)

        if slice_width < 0:
            raise ValueError("Slice width needs to be greater than 0")
        if field_offset < 0:
            raise ValueError("field_offsett needs to be greater than 0")

        self.__slice_width_setup(slice_width)

    def __slice_width_setup(self, slice_width):
        self.slice_width = slice_width
        self.mask = (1 << slice_width) - 1


    @property
    def bf(self):
        return self._bf

    def _add(self, bf):
        if isinstance(bf, BitField):
            if bf in self:
                return #already added
            self._children[bf.name] = bf
        else:
            raise ValueError("Expected argument to be of type BitField or one "
                             "of its descendents")
        if self.slice_width == 0:
            self.__slice_width_setup(bf.width)

        self._bf = bf
        if bf.parent == None:
            bf._parent = self
        if not hasattr(bf, '_references'):
            bf._references = set()
        bf._references.add(self)
        ref_count = len(bf._references)
        if ref_count > 1:
            # this line is a bit confusing an ambiguous. It doesn't intend to
            # indicate that mulitple references from a bitfield means that some
            # of the bitfieldrefs are aliases. The _alias boolean is used here
            # when deserializing the bitfield to not make a copy and instead to
            # use an already created instance
            self._alias = True
            if not self._ref:
                self._ref = next(iter(bf._references - set([self])))

    @property
    def reset_val(self):
        return ((self._bf.reset_val >> self.field_offset) & self.mask) << self.reg_offset

    @property
    def value(self):
        return ((self._bf.value >> self.field_offset) & self.mask) << self.reg_offset

    @value.setter
    def value(self, new_value):
        bf = self._bf

        old_bf_value = bf.value & ~(self.mask << self.field_offset)
        new_value = (new_value >> self.reg_offset) & self.mask

        bf.value = old_bf_value | (new_value << self.field_offset)

    def _copy(self, *, new_instance:bool=False, new_alias:bool=False,
              _deep_copy=True, _context=None, **kwargs):
        """Create a deep copy of this object

        Implementation within this class is almost the same as that from Node.
        The difference is that if this object is an alias, do not instantiate
        copies of children. Merely add existing bitfield as this object's
        bitfield and inject self as a reference

        """

        if _context is None:
            _context = {}

        deep_copy = not (new_alias or self._alias)
        new_obj = super()._copy(new_alias=new_alias, new_instance=new_instance,
                                _context=_context, _deep_copy=deep_copy, **kwargs)

        if not deep_copy:
            if new_obj._ref:
                new_obj._add(new_obj._ref.bf)
            else:
                new_obj._add(self.bf)

        return new_obj

    def validate(self):
        yield from super().validate()
        if self._bf is None:
            yield ValidationError( self, 'No child bitfield present')
        else:
            bf = self._bf
            if self.slice_width > bf.width:
                yield ValidationError(
                        self,
                        "Slice width is larger than bitfield's width")

