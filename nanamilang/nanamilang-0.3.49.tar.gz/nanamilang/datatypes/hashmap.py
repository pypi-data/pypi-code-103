"""NanamiLang HashMap Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


from functools import reduce
import nanamilang.shortcuts as shortcuts
from .base import Base
from .nil import Nil
from .integernumber import IntegerNumber


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

        # We're filtering all the triplets by hashed() comparison
        possible = shortcuts.get(
            tuple(filter(lambda _: _[0] == key.hashed(), self.reference())), 0, None)
        return possible[2] if possible else Nil('nil')  # third item of triplet is actually a value

    def count(self):
        """NanamiLang Set, count() implementation"""

        return IntegerNumber(len(self.reference()))

    def __init__(self, reference: tuple) -> None:
        """NanamiLang HashMap, initialize new instance"""

        self.init_assert_only_base(reduce(lambda _, __: _ + __, map(lambda _: (_[1], _[2]), reference)))

        # TODO: FIX THIS, THIS SHIT DOES NOT WORK FOR COMPLEX STRUCTURES
        self._hashed = hash(reference)

        super(HashMap, self).__init__(reference=reference)

    def format(self) -> str:
        """NanamiLang HashMap, format() method implementation"""

        return '{' + f'{" ".join([f"{k.format()} {v.format()}" for _, k, v in self.reference()])}' + '}'

    def reference_as_tuple(self) -> tuple:
        """NanamiLang HashMap, reference_as_tuple() method implementation"""

        return self.reference()
