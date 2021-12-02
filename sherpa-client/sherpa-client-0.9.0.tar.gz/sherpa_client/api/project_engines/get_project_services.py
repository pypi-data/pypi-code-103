from typing import Any, Dict, List, Optional, Union

import httpx

from ...client import Client
from ...models.http_service_record import HttpServiceRecord
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    *,
    client: Client,
    name: Union[Unset, None, str] = "",
    engine: Union[Unset, None, str] = "",
    function: Union[Unset, None, str] = "",
    type: Union[Unset, None, str] = "",
    version: Union[Unset, None, str] = "",
) -> Dict[str, Any]:
    url = "{}/projects/{projectName}/services".format(client.base_url, projectName=project_name)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "name": name,
        "engine": engine,
        "function": function,
        "type": type,
        "version": version,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[List[HttpServiceRecord]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_http_service_record_array_item_data in _response_200:
            componentsschemas_http_service_record_array_item = HttpServiceRecord.from_dict(
                componentsschemas_http_service_record_array_item_data
            )

            response_200.append(componentsschemas_http_service_record_array_item)

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[List[HttpServiceRecord]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    project_name: str,
    *,
    client: Client,
    name: Union[Unset, None, str] = "",
    engine: Union[Unset, None, str] = "",
    function: Union[Unset, None, str] = "",
    type: Union[Unset, None, str] = "",
    version: Union[Unset, None, str] = "",
) -> Response[List[HttpServiceRecord]]:
    kwargs = _get_kwargs(
        project_name=project_name,
        client=client,
        name=name,
        engine=engine,
        function=function,
        type=type,
        version=version,
    )

    response = httpx.get(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    project_name: str,
    *,
    client: Client,
    name: Union[Unset, None, str] = "",
    engine: Union[Unset, None, str] = "",
    function: Union[Unset, None, str] = "",
    type: Union[Unset, None, str] = "",
    version: Union[Unset, None, str] = "",
) -> Optional[List[HttpServiceRecord]]:
    """ """

    return sync_detailed(
        project_name=project_name,
        client=client,
        name=name,
        engine=engine,
        function=function,
        type=type,
        version=version,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    *,
    client: Client,
    name: Union[Unset, None, str] = "",
    engine: Union[Unset, None, str] = "",
    function: Union[Unset, None, str] = "",
    type: Union[Unset, None, str] = "",
    version: Union[Unset, None, str] = "",
) -> Response[List[HttpServiceRecord]]:
    kwargs = _get_kwargs(
        project_name=project_name,
        client=client,
        name=name,
        engine=engine,
        function=function,
        type=type,
        version=version,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    project_name: str,
    *,
    client: Client,
    name: Union[Unset, None, str] = "",
    engine: Union[Unset, None, str] = "",
    function: Union[Unset, None, str] = "",
    type: Union[Unset, None, str] = "",
    version: Union[Unset, None, str] = "",
) -> Optional[List[HttpServiceRecord]]:
    """ """

    return (
        await asyncio_detailed(
            project_name=project_name,
            client=client,
            name=name,
            engine=engine,
            function=function,
            type=type,
            version=version,
        )
    ).parsed
