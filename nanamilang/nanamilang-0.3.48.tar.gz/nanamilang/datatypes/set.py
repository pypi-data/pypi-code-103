"""NanamiLang Set Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


import nanamilang.shortcuts as shortcuts
from .base import Base
from .nil import Nil
from .integernumber import IntegerNumber


class Set(Base):
    """NanamiLang Set Data Type Class"""

    name: str = 'Set'
    _expected_type = set
    _python_reference: set
    purpose = 'Encapsulate Python 3 set of NanamiLang Base data types'

    def hashed(self) -> int:
        """NanamiLang Date, hashed() implementation"""

        return hash(self._python_reference)

    def get(self, element: Base) -> Base:
        """NanamiLang Set, get() implementation"""

        shortcuts.ASSERT_IS_CHILD_OF(
            element,
            Base,
            message='Set.get() index must be an IntegerNumber'
        )

        # In Python
        # There is no builtin function to find an element in a set
        # But in other Clojure, for instance, get function allows to do it
        return shortcuts.find(self.reference(), element.reference(), Nil('nil'))

    def count(self):
        """NanamiLang Set, count() implementation"""

        return IntegerNumber(len(self.reference()))

    def __init__(self, reference: set) -> None:
        """NanamiLang Set, initialize new instance"""

        self.init_assert_only_base(reference)

        super(Set, self).__init__(reference=reference)

    def format(self) -> str:
        """NanamiLang Set, format() method implementation"""

        return '#{' + f'{" ".join([i.format() for i in self.reference()])}' + '}'

    def reference_as_tuple(self) -> tuple:
        """NanamiLang Set, reference_as_tuple() implementation"""

        return tuple(self.reference())
