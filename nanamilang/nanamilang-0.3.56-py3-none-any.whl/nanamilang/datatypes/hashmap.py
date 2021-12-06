"""NanamiLang HashMap Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


from functools import reduce

import nanamilang.shortcuts as shortcuts
from .base import Base
from .integernumber import IntegerNumber
from .nil import Nil


class HashMap(Base):
    """NanamiLang HashMap Data Type Class"""

    name: str = 'HashMap'
    _expected_type = tuple
    _python_reference: tuple
    purpose = 'Encapsulate Python 3 tuple of NanamiLang Base data types'

    def get(self, key: Base) -> Base:
        """NanamiLang HashMap, get() implementation"""

        shortcuts.ASSERT_IS_CHILD_OF(
            key,
            Base,
            message='HashMap.get() key must be a child of Base'
        )

        return shortcuts.get(shortcuts.find(
            self.reference(), (),
            function=lambda e: e[0].hashed() == key.hashed()
        ), 1, Nil('nil'))

    def count(self):
        """NanamiLang Set, count() implementation"""

        return IntegerNumber(len(self.reference()))

    def __init__(self, reference: tuple) -> None:
        """NanamiLang HashMap, initialize new instance"""

        self.init_assert_only_base(shortcuts.depart(reference or ((Nil('nil'),),)))

        self._hashed = reduce(
            lambda e, n: e + n,
            map(lambda e: e.hashed(), shortcuts.depart(reference or ((Nil('nil'),),)))
        )

        super(HashMap, self).__init__(reference=reference)

    def format(self) -> str:
        """NanamiLang HashMap, format() method implementation"""

        return '{' + f'{" ".join([f"{k.format()} {v.format()}" for k, v in self.reference()])}' + '}'

    def reference_as_tuple(self) -> tuple:
        """NanamiLang HashMap, reference_as_tuple() method implementation"""

        return self.reference()
