from pathlib import Path
from typing import Dict, Any

from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page
from rdflib import URIRef

from octadocs.octiron.context_loaders import context_from_yaml
from octadocs.plugin import cached_octiron
from octadocs_table.models import TABLE


class TablePlugin(BasePlugin):
    """Render an HTML table from data presented in the graph."""

    @property
    def templates_path(self) -> Path:
        """Templates associated with the plugin."""
        return Path(__file__).parent / 'templates'

    def context_url(self) -> str:
        path = Path(__file__).parent / 'yaml/ctx.yaml'
        return f'file://{path}'

    def load_context(self):
        """Load YAML-LD context."""
        return context_from_yaml(Path(__file__).parent / 'yaml/ctx.yaml')

    def on_config(self, config, **kwargs):
        """Adjust configuration."""
        # Make plugin's templates available to MkDocs
        config['theme'].dirs.append(str(self.templates_path))

        named_context = self.load_context()

        try:
            contexts = config['extra']['named_contexts']
        except KeyError:
            contexts = config['extra']['named_contexts'] = {}

        contexts['table'] = named_context

        docs_dir = Path(config['docs_dir'])

        self.octiron = cached_octiron(
            docs_dir=docs_dir,
        )

        # Prefix
        self.octiron.graph.bind('table', TABLE)

        # Load the triples
        self.octiron.update_from_file(
            path=Path(__file__).parent / 'yaml/octadocs-table.yaml',
            local_iri=URIRef(TABLE),
            global_url='/octadocs-table.yaml',
            named_contexts=config['extra']['named_contexts'],
        )

    def on_page_context(
        self,
        context: Dict[str, Any],
        page: Page,
        **kwargs,
    ):
        """Make custom functions available to the template."""
        context.update({
            'table': TABLE,
        })

        return context
