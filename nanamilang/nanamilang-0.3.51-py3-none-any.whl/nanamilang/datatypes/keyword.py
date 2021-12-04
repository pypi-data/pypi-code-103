"""NanamiLang Keyword Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


from .base import Base


class Keyword(Base):
    """NanamiLang Keyword Data Type Class"""

    name: str = 'Keyword'
    _expected_type = str
    _python_reference: str
    purpose = 'Many LISPs have this data type, so we also do'

    def __init__(self, reference: str) -> None:
        """NanamiLang Keyword, initialize new instance"""

        self.init_assert_ref_is_not_empty(reference)

        self._hashed = hash(reference)

        super(Keyword, self).__init__(reference=reference)

    def format(self) -> str:
        """NanamiLang Keyword, format() method implementation"""

        return f':{self._python_reference}'
