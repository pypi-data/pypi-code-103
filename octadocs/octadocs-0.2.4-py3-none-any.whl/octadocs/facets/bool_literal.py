from typing import cast

from rdflib import Literal

from iolanta.facet import Facet


class BoolLiteral(Facet):
    """Render bool values."""

    def render(self):
        """Render as icon."""
        literal = cast(Literal, self.iri)
        return '✔️' if literal.value else '❌'
