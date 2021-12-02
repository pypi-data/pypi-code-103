import json
from functools import partial
from itertools import starmap
from typing import TextIO, Optional, Iterable

from rdflib import URIRef, Graph

from iolanta.models import LDDocument, LDContext, Quad, Triple
from iolanta.parsers.base import Parser
from iolanta.reformat_blank_nodes import reformat_blank_nodes


class JSON(Parser):
    """Load JSON data."""

    def as_jsonld_document(self, raw_data: TextIO) -> LDDocument:
        """Read JSON content as a JSON-LD document."""
        return json.load(raw_data)

    def as_quad_stream(
        self,
        raw_data: TextIO,
        iri: Optional[URIRef],
        context: LDContext,
    ) -> Iterable[Quad]:
        """Read JSON-LD data into a quad stream."""
        graph = Graph()
        graph.parse(
            data=raw_data.read(),
            format='json-ld',
            context=context,
        )

        triples = map(
            partial(
                reformat_blank_nodes,
                f'{iri}/{self.blank_node_prefix}',
            ),
            starmap(
                Triple,
                iter(graph),
            ),
        )

        return list(
            triple.as_quad(iri)
            for triple in triples
        )
