"""NanamiLang Base Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from nanamilang.shortcuts import \
    ASSERT_IS_INSTANCE_OF, \
    ASSERT_COLLECTION_IS_NOT_EMPTY, \
    ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF


class Base:
    """NanamiLang Base Data Type Class"""

    _hashed: int
    name: str = 'Base'
    _expected_type = None
    _python_reference = None

    def __init__(self, reference) -> None:
        """NanamiLang Base Data Type, initialize new instance"""

        ASSERT_IS_INSTANCE_OF(
            reference,
            self._expected_type,
            message=f'{self.name}: {self._expected_type} expected'
        )

        self._python_reference = reference

    def hashed(self) -> int:
        """NanamiLang Base Data Type, hashed() prototype"""

        return self._hashed

    def init_assert_ref_is_not_empty(self, reference) -> None:
        """NanamiLang Base Data Type, assert reference not empty"""

        ASSERT_COLLECTION_IS_NOT_EMPTY(
            reference, f'{self.name}: "ref" could not be empty')

    def init_assert_only_base(self, reference) -> None:
        """NanamiLang Base Data Type, assert that only base types"""

        ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF(
            reference,
            Base,
            f'{self.name}: can only host/contain Nanamilang types')

    def reference(self):
        """NanamiLang Base Data Type, self._python_reference getter"""

        return self._python_reference

    def origin(self) -> str:
        """NanamiLang Base Data Type, children may have this method"""

    def format(self) -> str:
        """NanamiLang Base Data Type, format() default implementation"""

        return f'{self._python_reference}'

    def __str__(self) -> str:
        """NanamiLang Base Data Type, __str__() method implementation"""

        return f'<{self.name}>: {self.format()}'

    def __repr__(self) -> str:
        """NanamiLang Base Data Type, __repr__() method implementation"""

        return self.__str__()
