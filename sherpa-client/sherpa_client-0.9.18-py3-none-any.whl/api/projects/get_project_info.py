from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.project_bean import ProjectBean
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_name: str,
    *,
    client: Client,
    compute_metrics: Union[Unset, None, bool] = False,
    compute_owner: Union[Unset, None, bool] = True,
    compute_engines: Union[Unset, None, bool] = True,
) -> Dict[str, Any]:
    url = "{}/projects/{projectName}/_info".format(client.base_url, projectName=project_name)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "computeMetrics": compute_metrics,
        "computeOwner": compute_owner,
        "computeEngines": compute_engines,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[ProjectBean]:
    if response.status_code == 200:
        response_200 = ProjectBean.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[ProjectBean]:
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
    compute_metrics: Union[Unset, None, bool] = False,
    compute_owner: Union[Unset, None, bool] = True,
    compute_engines: Union[Unset, None, bool] = True,
) -> Response[ProjectBean]:
    kwargs = _get_kwargs(
        project_name=project_name,
        client=client,
        compute_metrics=compute_metrics,
        compute_owner=compute_owner,
        compute_engines=compute_engines,
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
    compute_metrics: Union[Unset, None, bool] = False,
    compute_owner: Union[Unset, None, bool] = True,
    compute_engines: Union[Unset, None, bool] = True,
) -> Optional[ProjectBean]:
    """ """

    return sync_detailed(
        project_name=project_name,
        client=client,
        compute_metrics=compute_metrics,
        compute_owner=compute_owner,
        compute_engines=compute_engines,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    *,
    client: Client,
    compute_metrics: Union[Unset, None, bool] = False,
    compute_owner: Union[Unset, None, bool] = True,
    compute_engines: Union[Unset, None, bool] = True,
) -> Response[ProjectBean]:
    kwargs = _get_kwargs(
        project_name=project_name,
        client=client,
        compute_metrics=compute_metrics,
        compute_owner=compute_owner,
        compute_engines=compute_engines,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    project_name: str,
    *,
    client: Client,
    compute_metrics: Union[Unset, None, bool] = False,
    compute_owner: Union[Unset, None, bool] = True,
    compute_engines: Union[Unset, None, bool] = True,
) -> Optional[ProjectBean]:
    """ """

    return (
        await asyncio_detailed(
            project_name=project_name,
            client=client,
            compute_metrics=compute_metrics,
            compute_owner=compute_owner,
            compute_engines=compute_engines,
        )
    ).parsed
