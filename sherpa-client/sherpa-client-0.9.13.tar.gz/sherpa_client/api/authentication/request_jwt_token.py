from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bearer_token import BearerToken
from ...models.credentials import Credentials
from ...models.request_jwt_token_project_access_mode import RequestJwtTokenProjectAccessMode
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    json_body: Credentials,
    project_filter: Union[Unset, None, str] = UNSET,
    project_access_mode: Union[Unset, None, RequestJwtTokenProjectAccessMode] = UNSET,
    annotate_only: Union[Unset, None, bool] = False,
    login_only: Union[Unset, None, bool] = False,
) -> Dict[str, Any]:
    url = "{}/auth/login".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_project_access_mode: Union[Unset, None, str] = UNSET
    if not isinstance(project_access_mode, Unset):
        json_project_access_mode = project_access_mode.value if project_access_mode else None

    params: Dict[str, Any] = {
        "projectFilter": project_filter,
        "projectAccessMode": json_project_access_mode,
        "annotateOnly": annotate_only,
        "loginOnly": login_only,
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


def _parse_response(*, response: httpx.Response) -> Optional[BearerToken]:
    if response.status_code == 200:
        response_200 = BearerToken.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[BearerToken]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: Credentials,
    project_filter: Union[Unset, None, str] = UNSET,
    project_access_mode: Union[Unset, None, RequestJwtTokenProjectAccessMode] = UNSET,
    annotate_only: Union[Unset, None, bool] = False,
    login_only: Union[Unset, None, bool] = False,
) -> Response[BearerToken]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        project_filter=project_filter,
        project_access_mode=project_access_mode,
        annotate_only=annotate_only,
        login_only=login_only,
    )

    response = httpx.post(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    json_body: Credentials,
    project_filter: Union[Unset, None, str] = UNSET,
    project_access_mode: Union[Unset, None, RequestJwtTokenProjectAccessMode] = UNSET,
    annotate_only: Union[Unset, None, bool] = False,
    login_only: Union[Unset, None, bool] = False,
) -> Optional[BearerToken]:
    """ """

    return sync_detailed(
        client=client,
        json_body=json_body,
        project_filter=project_filter,
        project_access_mode=project_access_mode,
        annotate_only=annotate_only,
        login_only=login_only,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: Credentials,
    project_filter: Union[Unset, None, str] = UNSET,
    project_access_mode: Union[Unset, None, RequestJwtTokenProjectAccessMode] = UNSET,
    annotate_only: Union[Unset, None, bool] = False,
    login_only: Union[Unset, None, bool] = False,
) -> Response[BearerToken]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        project_filter=project_filter,
        project_access_mode=project_access_mode,
        annotate_only=annotate_only,
        login_only=login_only,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    json_body: Credentials,
    project_filter: Union[Unset, None, str] = UNSET,
    project_access_mode: Union[Unset, None, RequestJwtTokenProjectAccessMode] = UNSET,
    annotate_only: Union[Unset, None, bool] = False,
    login_only: Union[Unset, None, bool] = False,
) -> Optional[BearerToken]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
            project_filter=project_filter,
            project_access_mode=project_access_mode,
            annotate_only=annotate_only,
            login_only=login_only,
        )
    ).parsed
