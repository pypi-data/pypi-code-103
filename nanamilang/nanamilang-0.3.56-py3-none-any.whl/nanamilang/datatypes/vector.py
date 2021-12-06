"""NanamiLang Vector Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


from functools import reduce

import nanamilang.shortcuts as shortcuts
from .base import Base
from .integernumber import IntegerNumber
from .nil import Nil


class Vector(Base):
    """NanamiLang Vector Data Type Class"""

    name: str = 'Vector'
    _expected_type = tuple
    _python_reference: tuple
    purpose = 'Encapsulate Python 3 tuple of NanamiLang Base data types'

    def get(self, index: IntegerNumber) -> Base:
        """NanamiLang Vector, get() implementation"""

        shortcuts.ASSERT_IS_INSTANCE_OF(
            index,
            IntegerNumber,
            message='Vector.get() index must be an IntegerNumber'
        )

        return shortcuts.get(
            self.reference(),
            index.reference(), Nil('nil')
        )

    def count(self):
        """NanamiLang Set, count() implementation"""

        return IntegerNumber(len(self.reference()))

    def __init__(self, reference: tuple) -> None:
        """NanamiLang Vector, initialize new instance"""

        self.init_assert_only_base(reference)

        self._hashed = reduce(
            lambda e, n: e + n,
            map(lambda e: e.hashed(), reference or (Nil('nil'),))
        )

        super(Vector, self).__init__(reference=reference)

    def format(self) -> str:
        """NanamiLang Vector, format() method implementation"""

        return '[' + f'{" ".join([i.format() for i in self.reference()])}' + ']'

    def reference_as_tuple(self) -> tuple:
        """NanamiLang Vector, reference_as_tuple() implementation"""

        return self.reference()
