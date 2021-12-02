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
    _expected_type = dict
    _python_reference: dict
    purpose = 'Encapsulate Python 3 dict of NanamiLang Base data types'

    def get(self, key: Base) -> Base:
        """NanamiLang HashMap, get() implementation"""

        shortcuts.ASSERT_IS_CHILD_OF(
            key,
            Base,
            message='HashMap.get() key must be a child of Base'
        )

        for k, v in self.reference().items():
            if k.name == key.name and k.reference() == key.reference():
                return v
        return Nil('nil')

    def count(self):
        """NanamiLang Set, count() implementation"""

        return IntegerNumber(len(self.reference()))

    def __init__(self, reference: dict) -> None:
        """NanamiLang HashMap, initialize new instance"""

        self.init_assert_only_base(
            list(reduce(lambda e, x: e + (x[0], x[1]), reference.items() or [[]])))
        super(HashMap, self).__init__(reference=reference)

    def format(self) -> str:
        """NanamiLang HashMap, format() method implementation"""

        return '{' + f'{" ".join([f"{k.format()} {v.format()}" for k, v in self.reference().items()])}' + '}'

    def reference_as_list(self) -> list:
        """NanamiLang HashMap, reference_as_list() method implementation"""

        return reduce(lambda existing, current: existing + (current[0], current[1]), self.reference().items() or [[]])
