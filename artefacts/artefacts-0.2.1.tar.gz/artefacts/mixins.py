from artefacts import config
from artefacts.context import Context


context = Context(config=config)


class ContextReader:
    @property
    def context(self):
        return context

    @property
    def manifest(self):
        return self.context.manifest

    @property
    def catalog(self):
        return self.context.catalog

    @property
    def run_results(self):
        return self.context.run_results

    @property
    def sources(self):
        return self.context.sources


class NodeContextReader(ContextReader):
    @property
    def manifest_node(self):
        return self.manifest.nodes[self]

    @property
    def catalog_node(self):
        return self.catalog.nodes[self]

    @property
    def run_result_items(self):
        return [rr for rr in self.run_results.results if rr.unique_id == self.unique_id]

    @property
    def source_freshness_checks(self):
        return [fc for fc in self.sources.results if fc.unique_id == self.unique_id]


class Artifact:
    @property
    def schema_version(self):
        return self.metadata.schema_version

    def __str__(self):
        return f"<{self.__class__.__name__} {self.schema_version}>"

    def __repr__(self):
        return str(self)
