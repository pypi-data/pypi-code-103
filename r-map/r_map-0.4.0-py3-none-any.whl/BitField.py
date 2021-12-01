from math import ceil
from .Node import Node
from .ValueNodeMixins import UnsignedValueNodeMixin
from collections import defaultdict
import r_map.Enumeration #get around circular dependancy
from .ValidationError import ValidationError
class BitField(UnsignedValueNodeMixin, Node):
    _nb_attrs = frozenset(['width', 'reset_val', 'access'])
    def __init__(self, *, width=1, reset_val=0, access='XX', **kwargs):
        """Initialization function for BitField type"""
        if width < 1:
            raise ValueError("Width needs to be >= 1")
        if reset_val < 0:
            raise ValueError("reset_val needs to be >= 0")

        super().__init__(width=width,
                         reset_val=reset_val,
                         access=access,
                         **kwargs)

        mask = (1 << width) - 1
        reset_val &= mask
        self.mask = mask
        self._value = self.reset_val

    def __str__(self):
        return super().__str__() + \
            ' width: {}, reset_val: {:#0{width}x}, value: {:#0{width}x}'.format(
                self.width,
                self.reset_val,
                self.value,
                width=ceil(self.width/4+2)) #+2 to account for the "0x"

    def reset(self):
        self.value = self.reset_val

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, x):
        if isinstance(x, str):
            for enumeration in self:
                if enumeration.name == x:
                    self._value = enumeration.value
                    break
            else:
                raise ValueError(f"{x} doesn't match any enumeration pertaining"
                                 f" to bitfield: {self.name}")
        elif isinstance(x, r_map.Enumeration):
            self._value = x.value
        elif isinstance(x, int):
            self._value = x & self.mask
        else:
            raise NotImplementedError("Enumerations only support ints and Enumerations")

    @property
    def annotation(self):
        return next((a.name for a in self if a.value == self.value), hex(self.value))

    def validate(self):
        yield from super().validate()
        used_vals = defaultdict(list)

        for c in self:
            used_vals[c.value].append(c)

        val_template =  "The following enumerations have the same value: {}"
        for key, vals in used_vals.items():
            if len(vals) > 1:
                yield ValidationError(
                        self, val_template.format(', '.join(map(str, vals))))

    def _get_parent_regs(self):
        if not hasattr(self, '_references'):
            raise ValueError("BitField doesn't have any parents so cannot "
                             "perform an IO")
        return [bf_ref.parent for bf_ref in self._references]


    def write(self, val=None, always_write:bool=True):
        """Perform a bitfield write using containing registers's IO.
        :param val: The value to update the bitfield with
        :param always_write: If True, even if the new value matches the just
                             read back value (as part of read-modify-write),
                             write the value anyway
        """
        #first attempt to update the bitfield's value
        if val is not None:
            self.value = val
        val = self.value
        #do a read-modify-write of all of the parent registers
        parent_regs = self._get_parent_regs()
        for r in parent_regs:
            r.read()
        same_value = self.value == val
        self.value = val #in case they're different
        if always_write or not same_value:
            for r in parent_regs:
                r.write()

    def read(self) -> int:
        for r in self._get_parent_regs():
            r.read()
        return self.value
