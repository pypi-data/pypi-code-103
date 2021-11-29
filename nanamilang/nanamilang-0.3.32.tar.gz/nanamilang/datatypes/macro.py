"""NanamiLang Macro Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from nanamilang.shortcuts import ASSERT_DICT_CONTAINS_KEY
from .base import Base


class Macro(Base):
    """NanamiLang Macro Data Type Class"""

    name: str = 'Macro'
    _expected_type = dict
    _python_reference: dict

    def __init__(self, reference: dict) -> None:
        """NanamiLang Macro, initialize new instance"""

        ASSERT_DICT_CONTAINS_KEY('macro_name', reference)
        ASSERT_DICT_CONTAINS_KEY('macro_reference', reference)

        super(Macro, self).__init__(reference=reference)

    def reference(self):
        """NanamiLang Macro, reference() implementation"""

        return self._python_reference.get('macro_reference')

    def format(self) -> str:
        """NanamiLang Macro, format() method implementation"""

        return self._python_reference.get('macro_name')

    def origin(self) -> str:
        """NanamiLang Macro, origin() method implementation"""

        return self.format()
