"""NanamiLang String Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from .base import Base


class String(Base):
    """NanamiLang String Data Type Class"""

    name: str = 'String'
    _expected_type = str
    _python_reference: str

    def __init__(self, reference: str) -> None:
        """NanamiLang String, initialize new instance"""

        super(String, self).__init__(reference=reference)

    def format(self) -> str:
        """NanamiLang String, format() method implementation"""

        return f'"{self.reference()}"'
