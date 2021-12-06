"""NanamiLang Set Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


from functools import reduce

import nanamilang.shortcuts as shortcuts
from .base import Base
from .integernumber import IntegerNumber
from .nil import Nil


class Set(Base):
    """NanamiLang Set Data Type Class"""

    name: str = 'Set'
    _expected_type = set
    _python_reference: set
    purpose = 'Encapsulate Python 3 set of NanamiLang Base data types'

    def get(self, element: Base) -> Base:
        """NanamiLang Set, get() implementation"""

        shortcuts.ASSERT_IS_CHILD_OF(
            element,
            Base,
            message='Set.get() element must be a child of Base'
        )

        return shortcuts.find(
            self.reference(), Nil('nil'),
            function=lambda e: e.hashed() == element.hashed()
        )

    def count(self):
        """NanamiLang Set, count() implementation"""

        return IntegerNumber(len(self.reference()))

    def __init__(self, reference: set) -> None:
        """NanamiLang Set, initialize new instance"""

        self.init_assert_only_base(reference)

        self._hashed = reduce(
            lambda e, n: e + n,
            map(lambda e: e.hashed(), reference or (Nil('nil'),))
        )

        super(Set, self).__init__(reference=reference)

    def format(self) -> str:
        """NanamiLang Set, format() method implementation"""

        return '#{' + f'{" ".join([i.format() for i in self.reference()])}' + '}'

    def reference_as_tuple(self) -> tuple:
        """NanamiLang Set, reference_as_tuple() implementation"""

        return tuple(self.reference())
