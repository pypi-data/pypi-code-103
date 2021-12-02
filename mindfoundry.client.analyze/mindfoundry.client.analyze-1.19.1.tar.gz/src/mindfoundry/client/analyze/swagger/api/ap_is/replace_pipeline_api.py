from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.future import Future
from ...models.update_deployed_pipeline_api_request import (
    UpdateDeployedPipelineApiRequest,
)
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    pipeline_api_id: int,
    json_body: UpdateDeployedPipelineApiRequest,

) -> Dict[str, Any]:
    url = "{}/v1/pipelineApis/{pipelineApiId}/replace".format(
        client.base_url,pipelineApiId=pipeline_api_id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    

    

    

    json_json_body = json_body.to_dict()



    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[
    Future,
    None,
    None,
    None
]]:
    if response.status_code == 201:
        response_201 = Future.from_dict(response.json())



        return response_201
    if response.status_code == 401:
        response_401 = None

        return response_401
    if response.status_code == 403:
        response_403 = None

        return response_403
    if response.status_code == 404:
        response_404 = None

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[
    Future,
    None,
    None,
    None
]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    pipeline_api_id: int,
    json_body: UpdateDeployedPipelineApiRequest,

) -> Response[Union[
    Future,
    None,
    None,
    None
]]:
    kwargs = _get_kwargs(
        client=client,
pipeline_api_id=pipeline_api_id,
json_body=json_body,

    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)

def sync(
    *,
    client: Client,
    pipeline_api_id: int,
    json_body: UpdateDeployedPipelineApiRequest,

) -> Optional[Union[
    Future,
    None,
    None,
    None
]]:
    """ Updates the pipeline for the specified published pipeline """

    return sync_detailed(
        client=client,
pipeline_api_id=pipeline_api_id,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    pipeline_api_id: int,
    json_body: UpdateDeployedPipelineApiRequest,

) -> Response[Union[
    Future,
    None,
    None,
    None
]]:
    kwargs = _get_kwargs(
        client=client,
pipeline_api_id=pipeline_api_id,
json_body=json_body,

    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(
            **kwargs
        )

    return _build_response(response=response)

async def asyncio(
    *,
    client: Client,
    pipeline_api_id: int,
    json_body: UpdateDeployedPipelineApiRequest,

) -> Optional[Union[
    Future,
    None,
    None,
    None
]]:
    """ Updates the pipeline for the specified published pipeline """

    return (await asyncio_detailed(
        client=client,
pipeline_api_id=pipeline_api_id,
json_body=json_body,

    )).parsed
