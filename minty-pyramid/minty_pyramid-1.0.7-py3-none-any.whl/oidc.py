# SPDX-FileCopyrightText: Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

"""Support code for handling of OIDC/OAuth 2 tokens"""

import jose.jwt
import json
import os
import redis
import requests
from typing import Set, TypedDict

OIDC_CACHE_SECONDS = int(os.environ.get("OIDC_CACHE_SECONDS", "60"))


class ParsedToken(TypedDict):
    """Class that represents a parsed JWT token"""

    user_uuid: str
    scope: Set[str]

    # Token also contains/can also contain:
    # - email
    # - name
    # - given_name ?
    # - family_name ?
    # But UserInfo does not contain those (yet), so they're not yet
    # passed along


def _retrieve_json_cached(url: str, cache: redis.Redis, cache_key: str):
    try:
        return json.loads(cache[cache_key])
    except (KeyError, json.decoder.JSONDecodeError):
        pass

    response = requests.get(url)
    response.raise_for_status()

    json_data = response.json()

    cache.set(cache_key, json.dumps(json_data), ex=OIDC_CACHE_SECONDS)

    return json_data


def parse_token(
    access_token: str,
    oidc_client_id: str,
    oidc_endpoint_config: str,
    instance_uuid: str,
    cache: redis.Redis,
) -> ParsedToken:
    cache_key = f"oidc_cache:{instance_uuid}"

    oidc_metadata = _retrieve_json_cached(
        oidc_endpoint_config, cache, f"{cache_key}:metadata"
    )
    jwks = _retrieve_json_cached(
        oidc_metadata["jwks_uri"], cache, f"{cache_key}:jwks"
    )

    decoded_token = jose.jwt.decode(
        token=access_token, key=jwks, audience=oidc_client_id
    )

    return ParsedToken(
        user_uuid=decoded_token["sub"],
        scope=set(decoded_token["scope"].split()),
    )
