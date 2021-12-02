"""
Iolanta facet management.

This module contains a few functions which later will be refactored into
Iolanta - the generic metaverse/cyberspace browser.
"""
import operator
import pydoc
from dataclasses import dataclass
from typing import Optional, Callable, Union, cast, List

from more_itertools import first
from rdflib import RDFS
from rdflib.term import Node, URIRef, Literal

from iolanta.facet import Facet
from ldflex import LDFlex
from octadocs.iolanta.errors import FacetNotCallable, FacetNotFound
from octadocs.octiron import Octiron

HTML = URIRef('https://html.spec.whatwg.org/')


def find_default_facet_iri_for_environment(ldflex: LDFlex, environment: URIRef):
    rows = ldflex.query(
        '''
        SELECT * WHERE {
            ?environment iolanta:hasDefaultFacet ?facet .
        }
        ''',
        environment=environment,
    )

    facets = map(operator.itemgetter('facet'), rows)

    return first(facets, None)


def find_explicit_facet(
    node: Node,
    ldflex: LDFlex,
    environment: URIRef,
):
    """Find a facet that is explicitly bound to the node."""
    rows = ldflex.query(
        '''
        SELECT ?facet ?environment WHERE {
            ?node iolanta:facet ?facet .
            ?facet iolanta:supports ?environment .
        }
        ''',
        node=node,
        environment=environment,
    )

    facets = map(operator.itemgetter('facet'), rows)

    if facet := first(facets, None):
        return facet


def find_inferred_facet(
    node: Node,
    ldflex: LDFlex,
    environment: URIRef,
):
    """Find facet based on skos:broader relation between environments."""
    facet = find_explicit_facet(
        node=node,
        ldflex=ldflex,
        environment=environment,
    )

    if facet is not None:
        return facet

    broader_environments = map(
        operator.itemgetter('broader_environment'),
        ldflex.query(
            '''
            SELECT ?broader_environment WHERE {
                ?environment skos:broader ?broader_environment .
            }
            ''',
            environment=environment,
        ),
    )

    for environment in broader_environments:
        facet = find_explicit_facet(
            node=node,
            ldflex=ldflex,
            environment=environment,
        )

        if facet is not None:
            return facet


def resolve_literal_type(literal: Literal) -> URIRef:
    """Resolve literal data type."""
    if literal.datatype is not None:
        return literal.datatype

    return RDFS.Literal


def find_facet_iri(
    ldflex: LDFlex,
    environment: URIRef,
    node: Node,
) -> Optional[URIRef]:
    if isinstance(node, Literal):
        node = resolve_literal_type(node)

    facet = find_inferred_facet(
        node=node,
        ldflex=ldflex,
        environment=environment,
    )

    if facet is not None:
        return facet

    facet = find_default_facet_iri_for_environment(
        ldflex=ldflex,
        environment=environment,
    )

    if facet is None:
        raise FacetNotFound(
            node=node,
            environment=environment,
        )

    return facet


def resolve_facet(iri: URIRef) -> Callable[[Octiron, Node], str]:
    """Resolve a path to a Python object to that object."""
    url = str(iri)

    if not url.startswith('python://'):
        raise Exception(
            'Octadocs only supports facets which are importable Python '
            'callables. The URLs of such facets must start with `python://`, '
            'which {url} does not comply to.'.format(
                url=url,
            )
        )

    # It is impossible to use `urlpath` for this operation because it (or,
    # rather, one of upper classes from `urllib` that `urlpath` depends upon)
    # will lowercase the URL when parsing it - which means, irreversibly. We
    # have to resort to plain string manipulation.
    import_path = url.replace('python://', '').strip('/')

    facet = pydoc.locate(import_path)

    if not callable(facet):
        raise FacetNotCallable(
            path=import_path,
            facet=facet,
        )

    return facet


def render(
    node: Union[str, Node],
    octiron: Octiron,
    environment: URIRef = HTML,
) -> str:
    """Find an Iolanta facet for a node and render it."""
    facet_iri = Render(
        ldflex=octiron.ldflex,
    ).find_facet_iri(
        node=node,
        environment=environment,
    )

    if facet_iri is None:
        raise ValueError([facet_iri, node, environment])

    facet = resolve_facet(iri=facet_iri)

    facet = facet(
        octiron=octiron,
        iri=node,
    )

    if isinstance(facet, Facet):
        return facet.render()

    return str(facet)


@dataclass
class Render:
    """Facet renderer."""

    ldflex: LDFlex

    def find_facet_iri(
        self,
        node: Node,
        environment: URIRef,
    ) -> URIRef:
        """Find facet IRI for given node in given env."""
        if isinstance(node, Literal):
            return self.find_facet_iri_for_literal(
                literal=node,
                environment=environment,
            )

        if facet := self.find_facet_iri_by_instance(
            node=node,
            environment=environment,
        ):
            return facet

        instance_types = self.find_instance_types(node)
        for instance_type in instance_types:
            if facet := self.find_facet_iri_by_instance_type(
                instance_type=instance_type,
                environment=environment,
            ):
                return facet

        if facet := self.find_default_facet_iri_by_environment(
            environment=environment,
        ):
            return facet

        raise FacetNotFound(
            node=node,
            environment=environment,
            node_types=instance_types,
        )

    def __call__(
        self,
        node: Node,
        environment: URIRef,
    ) -> str:
        ...

    def find_facet_iri_for_literal(self, literal: Literal, environment: URIRef):
        """Find facet IRI for a literal."""
        if (
            literal.datatype is not None
            and (facet := self.find_facet_iri_by_datatype(
                datatype=literal.datatype,
                environment=environment,
            ))
        ):
            return facet

        if facet := self.find_facet_iri_by_instance_type(
            instance_type=RDFS.Literal,
            environment=environment,
        ):
            return facet

        if facet := self.find_default_facet_iri_by_environment(
            environment=environment,
        ):
            return facet

        raise FacetNotFound(
            node=literal,
            environment=environment,
        )

    def find_facet_iri_by_datatype(
        self,
        datatype: URIRef,
        environment: URIRef,
    ) -> Optional[URIRef]:
        """Find facet by datatype of a literal value."""
        rows = self.ldflex.query(
            '''
            SELECT ?facet WHERE {
                $datatype iolanta:datatypeFacet ?facet .
                ?facet iolanta:supports $env .
            }
            ''',
            datatype=datatype,
            env=environment,
        )

        try:
            return cast(URIRef, first(rows)['facet'])
        except ValueError:
            return None

    def find_facet_iri_by_instance_type(
        self,
        instance_type: URIRef,
        environment: URIRef,
    ):
        """Find facet for a node by its type."""
        rows = self.ldflex.query(
            '''
            SELECT ?facet WHERE {
                $instance_type iolanta:instanceFacet ?facet .
                ?facet iolanta:supports $env .
            }
            ''',
            instance_type=instance_type,
            env=environment,
        )

        try:
            return cast(URIRef, first(rows)['facet'])
        except (ValueError, TypeError):
            return None

    def find_default_facet_iri_by_environment(
        self,
        environment: URIRef,
    ) -> Optional[URIRef]:
        """Find default facet IRI by environment."""
        rows = self.ldflex.query(
            '''
            SELECT ?facet WHERE {
                $env iolanta:hasDefaultFacet ?facet .
            }
            ''',
            env=environment,
        )

        try:
            return cast(URIRef, first(rows)['facet'])
        except (ValueError, TypeError):
            return None

    def find_instance_types(self, node: URIRef) -> List[URIRef]:
        """Find types for particular node."""
        rows = self.ldflex.query(
            '''
            SELECT ?type WHERE {
                $node rdf:type ?type .
            }
            ''',
            node=node,
        )

        return list(
            map(
                operator.itemgetter('type'),
                rows,
            ),
        )

    def find_facet_iri_by_instance(
        self,
        node: Node,
        environment: URIRef,
    ):
        """Find facet IRI by instance."""
        rows = self.ldflex.query(
            '''
            SELECT ?facet WHERE {
                $node iolanta:facet ?facet .
                ?facet iolanta:supports $env .
            }
            ''',
            node=node,
            env=environment,
        )

        try:
            return cast(URIRef, first(rows)['facet'])
        except (ValueError, TypeError):
            return None
