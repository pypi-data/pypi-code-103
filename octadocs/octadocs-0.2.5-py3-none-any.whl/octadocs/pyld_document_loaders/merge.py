from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Any

from iolanta.models import LDContext
from iolanta.context import merge
from octadocs.pyld_document_loaders.base import DocumentLoader
from octadocs.pyld_document_loaders.models import JsonLDDocument


@dataclass
class MergeLoader(DocumentLoader):
    """
    Merge context retrieved from another source with a pre-generated context.

    For example, load context from a remote URL and then merge with context
    of current directory.
    """

    base_context: LDContext
    loader: DocumentLoader

    def __call__(self, url: str, options: Dict[str, Any]) -> JsonLDDocument:
        child_document = self.loader(url=url, options=options)
        base_context = deepcopy(self.base_context)

        if '@import' in base_context:
            base_context.pop('@import')

        base_context = {
            '@context': base_context,
        }

        child_document['document'] = merge(
            first=base_context,
            second=child_document['document'],
        )

        # raise ValueError(child_document)

        return child_document
