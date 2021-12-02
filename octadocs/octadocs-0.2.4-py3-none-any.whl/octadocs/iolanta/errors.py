from dataclasses import dataclass, field
from typing import List

from documented import DocumentedError
from rdflib import URIRef
from rdflib.term import Node, Literal


@dataclass
class FacetNotCallable(DocumentedError):
    """
    Python facet not callable.

    !!! error "Cannot import an object or cannot call it."

          - Import path: `{self.path}`
          - Object imported: `{self.facet}`

        The imported Python object is not a callable and thus cannot be used as a
        facet.
    """

    path: str
    facet: object


@dataclass
class FacetNotFound(DocumentedError):
    """
    Facet not found.

    !!! error "No way to render the node you asked for"
        - **Node:** `{self.node}` *({self.node_type})*
        - **Environment:** [{self.environment}]({self.environment})

        We tried desperately but could not find a facet to display this node 😟

        - Looked for a facet assigned to this node directly:
            - `{self.node}` `iolanta:facet` `?facet` .
            - where `?facet` `iolanta:supports` `{self.environment}` .

        - Looked for a facet assigned to the classes this node belongs:
            - `{self.node}` `rdf:type` `?type` .
            - `?cls` `iolanta:instanceFacet` `?facet` .
          where `?type` is one of these: `{self.render_node_types}`.

        - Looked for a facet assigned to the environment:
            - `{self.environment}` `iolanta:hasDefaultFacet` `?facet` .

        None of these were found, so we fail and suffer miserably.
    """

    node: Node
    environment: URIRef
    node_types: List[URIRef] = field(default_factory=list)

    @property
    def node_type(self) -> str:
        """Node type."""
        node_type = type(self.node).__name__
        if isinstance(self.node, Literal):
            node_type = f'{node_type}, datatype={self.node.datatype}'

        return node_type

    @property
    def render_node_types(self) -> str:
        """Render node types."""
        return ', '.join(map(str, self.node_types)) if (
            self.node_types
        ) else '(bad luck, no types found)'
