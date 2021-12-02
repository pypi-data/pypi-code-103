import json
from dataclasses import dataclass
from functools import partial
from itertools import starmap
from typing import Any, Dict, Iterator, List, Union

import rdflib
from documented import DocumentedError
from pyld.jsonld import JsonLdError

from iolanta.convert_dollar_signs import convert_dollar_signs
from iolanta.models import LDContext, LDDocument
from iolanta.reformat_blank_nodes import reformat_blank_nodes
from iolanta.context import merge
from octadocs.pyld_document_loaders.choice import ChoiceLoader
from octadocs.pyld_document_loaders.merge import MergeLoader
from octadocs.pyld_document_loaders.named import NamedLoader
from octadocs.types import LOCAL, Context, Triple
from pyld import jsonld
from pyld.documentloader.requests import requests_document_loader

try:  # noqa
    from yaml import CSafeDumper as SafeDumper  # noqa
    from yaml import CSafeLoader as SafeLoader  # noqa
except ImportError:
    from yaml import SafeDumper  # type: ignore   # noqa
    from yaml import SafeLoader  # type: ignore   # noqa

MetaData = Union[List[Dict[str, Any]], Dict[str, Any]]  # type: ignore  # noqa


@dataclass
class ExpandError(DocumentedError):
    """
    JSON-LD expand operation failed.

    Data: {self.formatted_data}
    Context: {self.formatted_context}
    IRI: {self.iri}

    {self.message}
    """

    message: str
    document: LDDocument
    context: LDContext
    iri: str

    @property
    def formatted_data(self) -> str:
        """Format document for printing."""
        return json.dumps(self.document, indent=2)

    @property
    def formatted_context(self):
        """Format context for printing."""
        return json.dumps(self.context, indent=2)


def as_triple_stream(
    raw_data: MetaData,
    context: Context,
    local_iri: str,
    named_contexts: Dict[str, Any],
    blank_node_prefix: str = '',
) -> Iterator[Triple]:
    """Convert YAML dict to a stream of triples."""
    if isinstance(raw_data, list):
        yield from _list_as_triple_stream(
            context=context,
            local_iri=local_iri,
            raw_data=raw_data,
            named_contexts=named_contexts,
            blank_node_prefix=blank_node_prefix,
        )

    elif isinstance(raw_data, dict):
        yield from _dict_as_triple_stream(
            context=context,
            local_iri=local_iri,
            raw_data=raw_data,
            named_contexts=named_contexts,
            blank_node_prefix=blank_node_prefix,
        )

    else:
        raise ValueError(f'Format of data not recognized: {raw_data}')


def jsonld_expand(data, context, local_iri, pyld_loader=None):
    """Expand the JSON_LD data with the help of particular loader."""
    options = {
        'base': str(LOCAL),
    }

    if context:
        options.update({'expandContext': context})

    if pyld_loader is not None:
        options.update({'documentLoader': pyld_loader})

    try:
        return jsonld.expand(
            data,
            options=options,
        )
    except (TypeError, JsonLdError) as err:
        raise ExpandError(
            message=str(err),
            document=data,
            context=context,
            iri=local_iri,
        ) from err


def _dict_as_triple_stream(  # type: ignore
    raw_data: LDDocument,
    context: LDContext,
    local_iri: str,
    named_contexts: Dict[str, LDContext],
    blank_node_prefix: str = '',
) -> Iterator[Triple]:
    """Convert dict into a triple stream."""
    meta_data = convert_dollar_signs(raw_data)

    local_context = meta_data.pop('@context', None)
    if isinstance(local_context, str):
        try:
            local_context = named_contexts[local_context]
        except KeyError as err:
            raise ValueError(
                f'Named context {local_context} is unknown.',
            ) from err

    if local_context is not None:
        context = merge(
            first=context,
            second=local_context,
        )

    if meta_data.get('@id') is None:
        # The document author did not tell us about what their document is.
        # In this case, we assume that the local_iri of the document file
        # is the subject of the document description.
        meta_data['@id'] = local_iri

    # The author specified an IRI the document tells us about. Let us
    # link this IRI to the local document IRI.
    meta_data['subjectOf'] = local_iri

    # Reason: https://github.com/RDFLib/rdflib-jsonld/issues/97
    # If we don't expand with an explicit @base, import will fail silently.
    meta_data = jsonld_expand(
        data=meta_data,
        local_iri=local_iri,
        context=context,
        pyld_loader=MergeLoader(
            base_context=context,
            loader=ChoiceLoader(loaders=[
                NamedLoader(documents=named_contexts),
                requests_document_loader(),
            ]),
        )
    )

    # Reason: https://github.com/RDFLib/rdflib-jsonld/issues/98
    # If we don't flatten, @included sections will not be imported.
    meta_data = jsonld.flatten(meta_data)
    serialized_meta_data = json.dumps(meta_data, indent=4)

    graph = rdflib.Graph()
    graph.parse(
        data=serialized_meta_data,
        format='json-ld',
    )
    yield from map(
        partial(
            reformat_blank_nodes,
            f'{local_iri}/{blank_node_prefix}',
        ),
        starmap(
            Triple,
            iter(graph),
        ),
    )


def _list_as_triple_stream(  # type: ignore
    raw_data: List[Dict[str, Any]],
    context: Context,
    local_iri: str,
    named_contexts: Dict[str, Any],
    blank_node_prefix: str = '',
) -> Iterator[Triple]:
    """Convert a list into a triple stream."""
    for sub_document_number, sub_document in enumerate(raw_data):
        yield from as_triple_stream(
            raw_data=sub_document,
            context=context,
            local_iri=local_iri,
            named_contexts=named_contexts,
            blank_node_prefix=f'{blank_node_prefix}_{sub_document_number}',
        )
