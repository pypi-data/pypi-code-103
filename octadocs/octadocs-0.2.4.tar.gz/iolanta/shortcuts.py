from pathlib import Path
from typing import Type, Iterable

from rdflib import URIRef
from urlpath import URL

from iolanta.loaders.local_file import Loader, LocalFile
from iolanta.models import LDDocument, Quad, LDContext


def choose_loader_by_url(url: URL) -> Type[Loader]:
    """Find loader by URL scheme."""
    return LocalFile


def as_document(url: URL) -> LDDocument:
    """Retrieve the document presented by the specified URL."""
    loader_class = choose_loader_by_url(url)
    return loader_class().as_jsonld_document(url)


def as_quad_stream(
    url: URL,
    iri: URIRef,
    default_context: LDContext,
    root_directory: Path,
) -> Iterable[Quad]:
    """Retrieve the stream presented by the specified URL."""
    loader_class = choose_loader_by_url(url)
    return loader_class(
        root_directory=root_directory,
        default_context=default_context,
    ).as_quad_stream(
        url=url,
        iri=iri,
    )
