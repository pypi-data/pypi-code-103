"""NanamiLang Function Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


from nanamilang.shortcuts import ASSERT_DICT_CONTAINS_KEY
from .base import Base


class Function(Base):
    """NanamiLang Function Data Type Class"""

    name: str = 'Function'
    _expected_type = dict
    _python_reference: dict
    purpose = 'Encapsulate function name and implementation'

    def __init__(self, reference: dict) -> None:
        """NanamiLang Function, initialize new instance"""

        ASSERT_DICT_CONTAINS_KEY('function_name', reference)
        ASSERT_DICT_CONTAINS_KEY('function_reference', reference)

        self._hashed = hash(reference.get('function_reference'))

        super(Function, self).__init__(reference=reference)

    def reference(self):
        """NanamiLang Function, reference() implementation"""

        return self._python_reference.get('function_reference')

    def format(self) -> str:
        """NanamiLang Function, format() method implementation"""

        return self._python_reference.get('function_name')

    def origin(self) -> str:
        """NanamiLang Function, origin() method implementation"""

        return self.format()
