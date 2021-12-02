from pathlib import Path
from typing import Dict

from mkdocs.plugins import BasePlugin
from rdflib import URIRef, PROV
from urlpath import URL

from iolanta import as_document
from iolanta.models import LDContext
from octadocs.mixins import OctadocsMixin
from octadocs.types import OCTA


class ProvenancePlugin(OctadocsMixin, BasePlugin):
    """Render an HTML table from data presented in the graph."""

    namespaces = {'prov': PROV}
    plugin_data_dir = Path(__file__).parent / 'data'

    def named_contexts(self) -> Dict[str, LDContext]:
        """Reusable named contexts."""
        return {
            'provenance': as_document(
                URL('file://', self.plugin_data_dir / 'named-context.yaml'),
            ),
        }

    def vocabularies(self) -> Dict[URIRef, Path]:
        """Load PROV-O ontology."""
        return {
            URIRef(PROV): self.plugin_data_dir / 'prov.json',
            URIRef(OCTA.term('provenance')): (
                self.plugin_data_dir / 'inference.yaml'
            ),
        }
