import operator
from dataclasses import dataclass
from typing import Iterable, List, Dict, Any

from dominate.tags import table, thead, tr, tbody, th, td
from rdflib import URIRef

from iolanta.facet import Facet
from octadocs.iolanta import render
from octadocs.octiron import Octiron
from octadocs_table.models import TABLE

Row = Dict[URIRef, Any]   # type: ignore


def list_columns(
    iri: URIRef,
    octiron: Octiron,
) -> List[URIRef]:
    """List of column IRIs for a table."""
    # Idea: http://www.snee.com/bobdc.blog/2014/04/rdf-lists-and-sparql.html
    return list(
        map(
            operator.itemgetter('column'),
            octiron.query(
                '''
                SELECT ?column WHERE {
                    ?iri table:columns/rdf:rest*/rdf:first ?column .
                }
                ''',
                iri=URIRef(iri),
            ),
        ),
    )


def construct_headers(
    octiron: Octiron,
    iri: URIRef,
    columns: List[URIRef],
) -> Iterable[th]:
    """Construct table headers."""
    for column in columns:
        yield th(render(
            node=column,
            octiron=octiron,
            environment=TABLE.th,
        ))


def construct_row(
    instance: URIRef,
    octiron: Octiron,
    columns: List[URIRef],
) -> Row:
    """Construct a table row."""
    formatted_columns = '({})'.format(
        ', '.join([
            f'<{column}>' for column in columns
        ]),
    )
    cells = octiron.query(
        '''
        SELECT * WHERE {
            $instance ?column ?value .
            FILTER(?column IN %s) .
        }
        ''' % formatted_columns,
        instance=instance,
    )

    return {
        cell['column']: cell['value']
        for cell in cells
    }


def select_instances(
    iri: URIRef,
    octiron: Octiron,
) -> Iterable[URIRef]:
    """Select instances, or rows, for the table."""
    return map(
        operator.itemgetter('instance'),
        octiron.query(
            '''
            SELECT ?instance WHERE {
                $iri table:class ?class .
                ?instance a ?class .
            }
            ''',
            iri=iri,
        ),
    )


def render_row(
    row: Row,
    columns: List[URIRef],
    octiron: Octiron,
) -> Iterable[td]:
    for column in columns:
        cell_value = row.get(column)

        if cell_value:
            cell_content = render(
                node=cell_value,
                octiron=octiron,
                environment=TABLE.td,
            )
            yield td(cell_content)

        else:
            yield td()


def get_ordering(iri: URIRef, octiron: Octiron) -> List[URIRef]:
    """List of columns that we are ordering by."""
    # Idea: http://www.snee.com/bobdc.blog/2014/04/rdf-lists-and-sparql.html
    return list(
        map(
            operator.itemgetter('column'),
            octiron.query(
                '''
                SELECT ?column WHERE {
                    ?iri table:ordering/rdf:rest*/rdf:first ?column .
                }
                ''',
                iri=URIRef(iri),
            ),
        ),
    )


def construct_sorter(ordering: List[URIRef]):
    """Construct a sorting procedure for rows in a table."""
    def sorter(row: Row):
        return [
            row.get(order_field, None)
            for order_field in ordering
        ]

    return sorter


def order_rows(
    rows: List[Row],
    ordering: List[URIRef],
):
    """Order rows by particular properties."""
    return sorted(
        rows,
        key=construct_sorter(ordering),
    )


@dataclass
class Table(Facet):
    """Octadocs Table."""

    def render(self) -> table:
        """Render the table."""
        columns = list_columns(
            iri=self.uriref,
            octiron=self.octiron,
        )

        ordering = get_ordering(
            iri=self.uriref,
            octiron=self.octiron,
        )

        headers = construct_headers(
            octiron=self.octiron,
            iri=self.uriref,
            columns=columns,
        )

        instances = select_instances(
            iri=self.uriref,
            octiron=self.octiron,
        )

        rows = [
            construct_row(
                instance=instance,
                columns=columns,
                octiron=self.octiron,
            )
            for instance in instances
        ]

        rows = order_rows(
            rows=rows,
            ordering=ordering,
        )

        rows = [
            tr(
                *render_row(
                    row=row,
                    columns=columns,
                    octiron=self.octiron,
                ),
            )
            for row in rows
        ]

        return table(
            thead(
                tr(*headers),
            ),
            tbody(*rows),
        )
