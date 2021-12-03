from typing import Sequence
from .seeker import CodeSeeker


__all__ = 'CodeSeekerRegistry',


class CodeSeekerRegistry(dict):
    def __init__(self, items: Sequence[CodeSeeker]) -> None:
        super().__init__()

        for item in items:
            self.register(item)

    def register(self, element: CodeSeeker) -> None:
        assert isinstance(element, CodeSeeker), 'Must be a `CodeSeeker` type.'
        assert element not in self and element.name not in self, (
            'Such a seeker already registered. \rn'
            'Remove previous manually to add new one.'
        )

        self[element.name] = element
