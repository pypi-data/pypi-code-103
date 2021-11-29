"""NanamiLang Vector Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from nanamilang.shortcuts import ASSERT_IS_INSTANCE_OF
from .base import Base
from .nil import Nil
from .integernumber import IntegerNumber


class Vector(Base):
    """NanamiLang Vector Data Type Class"""

    name: str = 'Vector'
    _expected_type = list
    _python_reference: list

    def get(self, index: IntegerNumber) -> Base:
        """NanamiLang Vector, get() implementation"""

        ASSERT_IS_INSTANCE_OF(
            index,
            IntegerNumber,
            message='Vector.get() index must be an IntegerNumber'
        )

        try:
            return self.reference()[index.reference()]
        except IndexError:
            return Nil('nil')
        # In Python, we could get IndexError,
        # but, for example, in Clojure, we just get a Nil result

    def __init__(self, reference: list) -> None:
        """NanamiLang Vector, initialize new instance"""

        self.init_assert_only_base(reference)

        super(Vector, self).__init__(reference=reference)

    def format(self) -> str:
        """NanamiLang Vector, format() method implementation"""

        return '[' + f'{" ".join([i.format() for i in self.reference()])}' + ']'

    def reference_as_list(self) -> list:
        """NanamiLang Vector, reference_as_list() method implementation"""

        return list(self.reference())
