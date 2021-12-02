from dominate.tags import a
from more_itertools import first

from iolanta.facets.errors import PageNotFound
from octadocs.octiron import Octiron
from rdflib.term import Node, Literal


def default(octiron: Octiron, iri: Node) -> str:
    """Default facet to draw a link to something in HTML environment."""
    if isinstance(iri, Literal):
        return str(iri.value)

    descriptions = octiron.query(
        '''
        SELECT * WHERE {
            OPTIONAL {
                ?page rdfs:label ?label .
            }

            OPTIONAL {
                ?page octa:symbol ?symbol .
            }

            OPTIONAL {
                ?page octa:url ?url .
            }

            OPTIONAL {
                ?page a octa:Page .
                BIND(true AS ?is_page)
            }
        } ORDER BY ?label LIMIT 1
        ''',
        page=iri,
    )

    try:
        description = first(descriptions)
    except ValueError:
        return str(iri)

    label = description.get('label', str(iri))
    url = description.get('url')

    symbol = description.get('symbol')
    if not symbol:
        if description.get('is_page'):
            symbol = '📃'

        elif url:
            symbol = '🔗'

        else:
            symbol = '[?]'

    if url:
        return a(
            symbol,
            label,
            href=url,
        )

    return label
