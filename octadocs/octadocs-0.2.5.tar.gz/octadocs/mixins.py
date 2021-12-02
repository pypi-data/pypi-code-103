import operator
from functools import cached_property
from pathlib import Path
from typing import Dict, Optional, Union

from mkdocs.plugins import BasePlugin
from rdflib import Namespace, URIRef
from rdflib.term import Node
from typer import Typer

from iolanta.loaders.base import term_for_python_class
from iolanta.models import LDContext, Triple
from octadocs.octiron import Octiron
from octadocs.plugin import cached_octiron


class OctadocsMixin(BasePlugin):
    """MkDocs plugin that aims to extend Octadocs functionality."""

    octiron: Octiron
    namespaces: Optional[Dict[str, Namespace]] = None
    plugin_data_dir: Path

    def typer(self) -> Optional[Typer]:
        """Return a CLI command for octadocs app."""

    @cached_property
    def templates_path(self) -> Optional[Path]:
        """Templates associated with the plugin."""
        path = Path(__file__).parent / 'templates'
        if path.exists():
            return path

    def named_contexts(self) -> Dict[str, LDContext]:
        """Named contexts."""
        return {}

    def vocabularies(self) -> Dict[URIRef, Path]:
        """Pieces of structured data to load into graph."""
        return {}

    def on_config(self, config, **kwargs):
        """Adjust system configuration to suit this plugin."""
        # Make plugin's templates available to MkDocs
        if self.templates_path:
            config['theme'].dirs.append(str(self.templates_path))

        docs_dir = Path(config['docs_dir'])
        self.octiron = cached_octiron(
            docs_dir=docs_dir,
        )
        self.bind_namespaces()

        # Publish named contexts to make them reusable for the whole system
        config['extra']['named_contexts'].update(self.named_contexts())

        # Load vocabularies and data into graph
        for url, path in self.vocabularies().items():
            self.octiron.update_from_file(
                path=path,
                local_iri=url,
                global_url=url,
                named_contexts=config['extra']['named_contexts'],
                skip_file_if_not_importable=False,
            )

    def on_files(self, *args, **kwargs):
        """Extract metadata from files and compose the site graph."""
        self.inference()

    def inference(self):
        """Apply inference, if any."""

    def update(self, sparql_query: str):
        """Apply the given SPARQL INSERT query."""
        self.octiron.graph.update(sparql_query)

    def query(self, sparql_query: str, **kwargs: Union[str, int, Node]):
        """Query and return results."""
        return self.octiron.query(sparql_query, **kwargs)

    def insert(self, *triples: Triple):
        """Insert triples into graph."""
        graph = term_for_python_class(self.__class__)
        quads = map(
            operator.methodcaller('as_quad', graph),
            triples,
        )
        self.octiron.graph.addN(quads)

    def bind_namespaces(self):
        if not self.namespaces:
            return

        for prefix, namespace in self.namespaces.items():
            self.octiron.graph.bind(prefix, namespace)
