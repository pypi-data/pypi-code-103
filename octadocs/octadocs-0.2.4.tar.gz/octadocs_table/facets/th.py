from dominate.tags import a
from more_itertools import first
from rdflib import URIRef

from octadocs.octiron import Octiron


def render_th(octiron: Octiron, iri: str):
    """Render a table column header."""
    iri = URIRef(iri)
    rows = octiron.query(
        '''
        SELECT * WHERE {
            OPTIONAL {
                $iri rdfs:label ?label .
            }

            OPTIONAL {
                $iri rdfs:comment ?comment .
            }

            OPTIONAL {
                $iri octa:symbol ?symbol .
            }

            OPTIONAL {
                $iri octa:url ?url .
            }
        } ORDER BY DESC(?label) DESC(?comment) DESC(?symbol) DESC(?url)
        ''',
        iri=iri,
    )

    try:
        row = first(rows)
    except ValueError:
        return str(iri)

    label = row.get('label', str(iri))
    if symbol := row.get('symbol'):
        label = f'{symbol} {label}'

    if url := row.get('url'):
        return a(label, href=url)

    return label
