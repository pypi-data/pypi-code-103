from abc import ABC, abstractmethod, abstractproperty
from io import StringIO
from typing import IO

from dinject import Parser, ParserOptions, inject

from edition.metadata import Metadata


class Press(ABC):
    def __init__(self, markdown_body: str, metadata: Metadata) -> None:
        self._markdown_body = markdown_body
        self._metadata = metadata

    def _post_injection(self) -> None:
        """override"""
        pass

    def _inject_blocks(self) -> None:
        reader = StringIO(self._markdown_body)
        writer = StringIO()
        inject(
            parser=Parser(
                keyword="edition-exec",
                options=self.injection_options,
            ),
            reader=reader,
            writer=writer,
        )
        self._markdown_body = writer.getvalue()
        self._post_injection()

    @abstractproperty
    def injection_options(self) -> ParserOptions:
        """options"""

    def press(self, writer: IO[str]) -> None:
        """Perform the press."""
        self._inject_blocks()
        self._press(writer)

    @abstractmethod
    def _press(self, writer: IO[str]) -> None:
        """Perform the press."""
