from typing import Any, Dict, Union

import httpx

from ...client import Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    *,
    client: Client,
    test_size: Union[Unset, None, float] = 0.2,
    incremental: Union[Unset, None, bool] = False,
) -> Dict[str, Any]:
    url = "{}/projects/{projectName}/_split_corpus".format(client.base_url, projectName=project_name)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "testSize": test_size,
        "incremental": incremental,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _build_response(*, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=None,
    )


def sync_detailed(
    project_name: str,
    *,
    client: Client,
    test_size: Union[Unset, None, float] = 0.2,
    incremental: Union[Unset, None, bool] = False,
) -> Response[Any]:
    kwargs = _get_kwargs(
        project_name=project_name,
        client=client,
        test_size=test_size,
        incremental=incremental,
    )

    response = httpx.post(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    project_name: str,
    *,
    client: Client,
    test_size: Union[Unset, None, float] = 0.2,
    incremental: Union[Unset, None, bool] = False,
) -> Response[Any]:
    kwargs = _get_kwargs(
        project_name=project_name,
        client=client,
        test_size=test_size,
        incremental=incremental,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)
