from dominate.tags import span
from more_itertools import first

from iolanta.facet import Facet


class GithubLicense(Facet):
    """Render license information."""

    def render(self):
        """Render."""
        rows = self.query(
            '''
            SELECT * WHERE {
                $license
                    gh:spdx_id ?id ;
                    gh:name ?name .
            }
            ''',
            license=self.iri,
        )

        row = first(rows)

        title = row['name']
        text = str(row['id'])

        if text == 'NOASSERTION':
            text = title

        return span(text, title=title)
