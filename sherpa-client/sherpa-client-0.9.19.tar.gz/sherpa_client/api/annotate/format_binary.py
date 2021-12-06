from io import BytesIO
from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.format_binary_form import FormatBinaryForm
from ...types import UNSET, File, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    multipart_data: FormatBinaryForm,
    inline_labels: Union[Unset, None, bool] = True,
    inline_label_ids: Union[Unset, None, bool] = True,
    inline_text: Union[Unset, None, bool] = True,
) -> Dict[str, Any]:
    url = "{}/annotate/_format_binary".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "inlineLabels": inline_labels,
        "inlineLabelIds": inline_label_ids,
        "inlineText": inline_text,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    multipart_multipart_data = multipart_data.to_multipart()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "files": multipart_multipart_data,
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[File]:
    if response.status_code == 200:
        response_200 = File(payload=BytesIO(response.content))

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[File]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    multipart_data: FormatBinaryForm,
    inline_labels: Union[Unset, None, bool] = True,
    inline_label_ids: Union[Unset, None, bool] = True,
    inline_text: Union[Unset, None, bool] = True,
) -> Response[File]:
    kwargs = _get_kwargs(
        client=client,
        multipart_data=multipart_data,
        inline_labels=inline_labels,
        inline_label_ids=inline_label_ids,
        inline_text=inline_text,
    )

    response = httpx.post(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    multipart_data: FormatBinaryForm,
    inline_labels: Union[Unset, None, bool] = True,
    inline_label_ids: Union[Unset, None, bool] = True,
    inline_text: Union[Unset, None, bool] = True,
) -> Optional[File]:
    """ """

    return sync_detailed(
        client=client,
        multipart_data=multipart_data,
        inline_labels=inline_labels,
        inline_label_ids=inline_label_ids,
        inline_text=inline_text,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    multipart_data: FormatBinaryForm,
    inline_labels: Union[Unset, None, bool] = True,
    inline_label_ids: Union[Unset, None, bool] = True,
    inline_text: Union[Unset, None, bool] = True,
) -> Response[File]:
    kwargs = _get_kwargs(
        client=client,
        multipart_data=multipart_data,
        inline_labels=inline_labels,
        inline_label_ids=inline_label_ids,
        inline_text=inline_text,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    multipart_data: FormatBinaryForm,
    inline_labels: Union[Unset, None, bool] = True,
    inline_label_ids: Union[Unset, None, bool] = True,
    inline_text: Union[Unset, None, bool] = True,
) -> Optional[File]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            multipart_data=multipart_data,
            inline_labels=inline_labels,
            inline_label_ids=inline_label_ids,
            inline_text=inline_text,
        )
    ).parsed
