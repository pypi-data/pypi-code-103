"""NanamiLang Vector Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


import nanamilang.shortcuts as shortcuts
from .base import Base
from .nil import Nil
from .integernumber import IntegerNumber


class Vector(Base):
    """NanamiLang Vector Data Type Class"""

    name: str = 'Vector'
    _expected_type = list
    _python_reference: list
    purpose = 'Encapsulate Python 3 list of NanamiLang Base data types'

    def get(self, index: IntegerNumber) -> Base:
        """NanamiLang Vector, get() implementation"""

        shortcuts.ASSERT_IS_INSTANCE_OF(
            index,
            IntegerNumber,
            message='Vector.get() index must be an IntegerNumber'
        )

        # In Python
        # We could get an IndexError
        # But in other languages, we could get just NULL value
        return shortcuts.get(self.reference(), index.reference(), Nil('nil'))

    def count(self):
        """NanamiLang Set, count() implementation"""

        return IntegerNumber(len(self.reference()))

    def __init__(self, reference: list) -> None:
        """NanamiLang Vector, initialize new instance"""

        self.init_assert_only_base(reference)

        super(Vector, self).__init__(reference=reference)

    def format(self) -> str:
        """NanamiLang Vector, format() method implementation"""

        return '[' + f'{" ".join([i.format() for i in self.reference()])}' + ']'

    def reference_as_list(self) -> list:
        """NanamiLang Vector, reference_as_list() implementation"""

        return list(self.reference())
