from dataclasses import dataclass
from typing import Dict, List, Union, Optional

from rdflib import Graph
from rdflib.plugins.sparql.processor import SPARQLResult
from rdflib.term import Node, Variable, Identifier

SelectRow = Dict[str, Node]


class SelectResult(List[SelectRow]):
    """Result of a SPARQL SELECT."""

    @property
    def first(self) -> Optional[SelectRow]:
        """Return first element of the list."""
        return self[0] if self else None


SPARQLQueryArgument = Optional[Union[Node, str, int, float]]


QueryResult = Union[
    SelectResult,   # SELECT
    Graph,          # CONSTRUCT
    bool,           # ASK
]


def _format_query_bindings(
    bindings: List[Dict[Variable, Identifier]],
) -> SelectResult:
    """
    Format bindings before returning them.

    Converts Variable to str for ease of addressing.
    """
    return SelectResult([
        {
            str(variable_name): rdf_value
            for variable_name, rdf_value
            in row.items()
        }
        for row in bindings
    ])


@dataclass
class LDFlex:
    """Fluent interface to a semantic graph."""

    graph: Graph

    def query(
        self,
        query_text: str,
        **kwargs: SPARQLQueryArgument,
    ) -> QueryResult:
        """
        Run a SPARQL `SELECT`, `CONSTRUCT`, or `ASK` query.

        Args:
            query_text: The SPARQL text;
            **kwargs: bind variables in the query to values if necessary. For
                example:

                ```python
                ldflex.query(
                    'SELECT ?title WHERE { ?page octa:title ?title }',
                    ?page=page_iri,
                )
                ```

        Returns:
            Results of the query:

            - a graph for `CONSTRUCT`,
            - a list of dicts for `SELECT`,
            - or a boolean for `ASK`.
        """
        sparql_result: SPARQLResult = self.graph.query(
            query_text,
            initBindings=kwargs,
        )

        if sparql_result.askAnswer is not None:
            return sparql_result.askAnswer

        if sparql_result.graph is not None:
            graph: Graph = sparql_result.graph
            for prefix, namespace in self.graph.namespaces():
                graph.bind(prefix, namespace)

            return graph

        return _format_query_bindings(sparql_result.bindings)
