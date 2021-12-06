"""NanamiLang Date Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import datetime

from .base import Base


class Date(Base):
    """NanamiLang Date Data Type Class"""

    name: str = 'Date'
    _expected_type = datetime.datetime
    _python_reference: datetime.datetime
    purpose = 'Encapsulate Python 3 datetime.datetime'

    def __init__(self, reference: datetime.datetime) -> None:
        """NanamiLang Date, initialize new instance"""

        self._hashed = hash(reference)

        super(Date, self).__init__(reference=reference)

    def format(self) -> str:
        """NanamiLang Date, format() method implementation"""

        return f'#{self._python_reference.year}-{self._python_reference.month}-{self._python_reference.day}'
