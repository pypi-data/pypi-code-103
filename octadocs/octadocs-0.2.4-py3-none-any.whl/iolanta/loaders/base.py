from abc import ABC
from dataclasses import dataclass
from typing import Iterable, Optional, TextIO, Type

from rdflib import URIRef
from urlpath import URL

from iolanta.models import LDContext, Quad, LDDocument
from iolanta.namespaces import PYTHON
from iolanta.parsers.base import Parser


def term_for_python_class(cls: type) -> URIRef:
    """Construct term for Python class."""
    return PYTHON.term(f'{cls.__module__}.{cls.__qualname__}')


@dataclass(frozen=True)
class Loader(ABC):
    """
    Base class for loaders.

    Loader receives a URL (or a path) to certain location. It is responsible for
    reading data from that location and returning it as a stream of RDF quads.

    Usually, depending on the data format, Loader leverages Parsers for that
    purpose.
    """

    @classmethod
    def loader_class_iri(cls) -> URIRef:
        """Import path to the loader class."""
        return term_for_python_class(cls)

    def choose_parser_class(self, url: URL) -> Type[Parser]:
        """Find which parser class to use for this URL."""
        raise NotImplementedError()

    def as_jsonld_document(
        self,
        url: URL,
        iri: Optional[URIRef] = None,
    ) -> LDDocument:
        """Represent a file as a JSON-LD document."""
        raise NotImplementedError()

    def as_file(self, url: URL) -> TextIO:
        """Construct a file-like object."""
        raise NotImplementedError()

    def as_quad_stream(
        self,
        url: str,
        iri: Optional[URIRef],
    ) -> Iterable[Quad]:
        """Convert data into a stream of RDF quads."""
        raise NotImplementedError()

    def find_context(self, url: str) -> LDContext:
        """Find context for the file."""
        raise NotImplementedError()

    def __call__(self, url: str):
        raise NotImplementedError('This is for compatibility with PYLD.')
