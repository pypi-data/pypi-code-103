"""NanamiLang FloatNumber Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


from .base import Base


class FloatNumber(Base):
    """NanamiLang FloatNumber Data Type Class"""

    name: str = 'FloatNumber'
    _expected_type = float
    _python_reference: float
    purpose = 'Encapsulate Python 3 float'

    def hashed(self) -> int:
        """NanamiLang Date, hashed() implementation"""

        return hash(self._python_reference)

    def __init__(self, reference: float) -> None:
        """NanamiLang FloatNumber, initialize new instance"""

        super(FloatNumber, self).__init__(reference=reference)
