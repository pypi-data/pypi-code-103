from typing import Any, Dict, List, Optional, Union

import httpx

from ...client import Client
from ...models.annotate_documents_with_many import AnnotateDocumentsWithMany
from ...models.annotated_document import AnnotatedDocument
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    json_body: AnnotateDocumentsWithMany,
    inline_labels: Union[Unset, None, bool] = True,
    inline_label_ids: Union[Unset, None, bool] = True,
    inline_text: Union[Unset, None, bool] = True,
    output_fields: Union[Unset, None, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/annotate/_annotate_documents".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "inlineLabels": inline_labels,
        "inlineLabelIds": inline_label_ids,
        "inlineText": inline_text,
        "outputFields": output_fields,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[List[AnnotatedDocument]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_annotated_document_array_item_data in _response_200:
            componentsschemas_annotated_document_array_item = AnnotatedDocument.from_dict(
                componentsschemas_annotated_document_array_item_data
            )

            response_200.append(componentsschemas_annotated_document_array_item)

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[List[AnnotatedDocument]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: AnnotateDocumentsWithMany,
    inline_labels: Union[Unset, None, bool] = True,
    inline_label_ids: Union[Unset, None, bool] = True,
    inline_text: Union[Unset, None, bool] = True,
    output_fields: Union[Unset, None, str] = UNSET,
) -> Response[List[AnnotatedDocument]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        inline_labels=inline_labels,
        inline_label_ids=inline_label_ids,
        inline_text=inline_text,
        output_fields=output_fields,
    )

    response = httpx.post(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    json_body: AnnotateDocumentsWithMany,
    inline_labels: Union[Unset, None, bool] = True,
    inline_label_ids: Union[Unset, None, bool] = True,
    inline_text: Union[Unset, None, bool] = True,
    output_fields: Union[Unset, None, str] = UNSET,
) -> Optional[List[AnnotatedDocument]]:
    """ """

    return sync_detailed(
        client=client,
        json_body=json_body,
        inline_labels=inline_labels,
        inline_label_ids=inline_label_ids,
        inline_text=inline_text,
        output_fields=output_fields,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: AnnotateDocumentsWithMany,
    inline_labels: Union[Unset, None, bool] = True,
    inline_label_ids: Union[Unset, None, bool] = True,
    inline_text: Union[Unset, None, bool] = True,
    output_fields: Union[Unset, None, str] = UNSET,
) -> Response[List[AnnotatedDocument]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        inline_labels=inline_labels,
        inline_label_ids=inline_label_ids,
        inline_text=inline_text,
        output_fields=output_fields,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    json_body: AnnotateDocumentsWithMany,
    inline_labels: Union[Unset, None, bool] = True,
    inline_label_ids: Union[Unset, None, bool] = True,
    inline_text: Union[Unset, None, bool] = True,
    output_fields: Union[Unset, None, str] = UNSET,
) -> Optional[List[AnnotatedDocument]]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
            inline_labels=inline_labels,
            inline_label_ids=inline_label_ids,
            inline_text=inline_text,
            output_fields=output_fields,
        )
    ).parsed
