"""NanamiLang HashMap Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from functools import reduce
from nanamilang.shortcuts import ASSERT_IS_CHILD_OF
from .base import Base
from .nil import Nil


class HashMap(Base):
    """NanamiLang HashMap Data Type Class"""

    name: str = 'HashMap'
    _expected_type = dict
    _python_reference: dict

    def get(self, key: Base) -> Base:
        """NanamiLang HashMap, get() implementation"""

        ASSERT_IS_CHILD_OF(
            key,
            Base,
            message='HashMap.get() key must be a child of Base'
        )

        for k, v in self.reference().items():
            if k.name == key.name:
                if k.reference() == key.reference():
                    return v
        return Nil('nil')
        # Since, we can get None, we need to cast it to the NanamiLang Nil

    def __init__(self, reference: dict) -> None:
        """NanamiLang HashMap, initialize new instance"""

        # Since we using reduce() to represent plain list of keys and their values, we must ensure
        if reference.items():
            self.init_assert_only_base(
                list(reduce(lambda e, x: e + (x[0], x[1]), reference.items())))
        super(HashMap, self).__init__(reference=reference)

    def format(self) -> str:
        """NanamiLang HashMap, format() method implementation"""

        return '{' + f'{" ".join([f"{k.format()} {v.format()}" for k, v in self.reference().items()])}' + '}'

    def reference_as_list(self) -> list:
        """NanamiLang HashMap, reference_as_list() method implementation"""

        if not self.reference().items():
            return []
        else:
            return reduce(lambda existing, current: existing + (current[0], current[1]), self.reference().items())
