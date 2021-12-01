import os
from typing import Dict, Any, Optional, NamedTuple, Union
from pydantic import SecretStr
from pydantic import BaseSettings as PydanticBaseSettings
from async_hvac import AsyncClient
import logging
from contextlib import suppress
import asyncio


logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s:%(asctime)s:%(message)s")


class Kubernetes(NamedTuple):
    role: str
    jwt_token: SecretStr


def _get_config(config: str, settings: PydanticBaseSettings) -> Optional[str]:
    _config_value: Optional[str] = None
    if config.upper() in os.environ:
        _config_value = os.environ.get(config.upper())
        logging.debug(f"CONFIG: Found {config} in Environment")
    if getattr(settings.__config__, config.lower(), None) is not None:
        _config_value = getattr(settings.__config__, config.lower())
        logging.debug(f"CONFIG: Found {config} in Config")
    if _config_value is None:
        logging.debug(f"CONFIG: Could not Find {config}")
        raise Exception

    return _config_value


def _extract_kubernetes(settings: PydanticBaseSettings) -> Optional[Kubernetes]:
    """Extract Kubernetes token from default file, and role from environment or from BaseSettings.Config"""
    _kubernetes_jwt: SecretStr
    with suppress(FileNotFoundError):
        with open("/var/run/secrets/kubernetes.io/serviceaccount/token") as token_file:
            _kubernetes_jwt = SecretStr(token_file.read().strip())
            logging.debug(
                "Found Kubernetes JWT Token in file '/var/run/secrets/kubernetes.io/serviceaccount/token'"
            )

        # Kubernetes role
        kubernetes_role = _get_config(
            config="VAULT_KUBERNETES_ROLE", settings=settings)
        if kubernetes_role is not None:
            return Kubernetes(role=kubernetes_role, jwt_token=_kubernetes_jwt)

    return None


async def _get_authenticated_vault_client(
    settings: PydanticBaseSettings,
) -> Optional[AsyncClient]:

    client = None
    token = None
    try:
        # HOST
        _vault_host = _get_config(config="VAULT_HOST", settings=settings)

        # PORT
        _vault_port = _get_config(config="VAULT_PORT", settings=settings)

        # URL
        _vault_url = f"http://{_vault_host}:{_vault_port}"

        _vault_kubernetes = _extract_kubernetes(settings)

        if _vault_kubernetes is not None:
            hvac_client_token = AsyncClient(url=_vault_url)
            token = await hvac_client_token.auth_kubernetes(
                role=_vault_kubernetes.role,
                jwt=_vault_kubernetes.jwt_token.get_secret_value(),
            )

            try:
                client = AsyncClient(
                    url=_vault_url, token=token["auth"]["client_token"])
                await hvac_client_token.close()
                return client
            except Exception as err:
                logging.debug(
                    "Could not get Authenticated VAULT Client. Try Again")
                logging.debug(err)
                await hvac_client_token.close()
                raise err
        else:
            return None
    except Exception as err:
        logging.debug(err)
        return None


async def _get_credentials(
    settings: PydanticBaseSettings, vault_client: AsyncClient, _vault_service: str
) -> Dict[str, Any]:
    d: Dict[str, Any] = {}
    if vault_client is None:
        logging.warning(
            "VAULT CLIENT: Could not find a suitable authentication method for Vault. Will read from ENV"
        )
        return {}

    for field_name, field in settings.__fields__.items():
        vault_val: Union[str, Dict[str, Any]]

        vault_secret_path: Optional[str] = field.field_info.extra.get(
            "vault_secret_path", None
        )
        vault_secret_key: Optional[str] = field.field_info.extra.get(
            "vault_secret_key", None
        )
        if vault_secret_path is not None and vault_secret_key is not None:
            try:
                path = vault_secret_path + _vault_service
                vault_api_response = (await vault_client.read(path))["data"]
                logging.debug(vault_api_response.keys())
                vault_val = vault_api_response[vault_secret_key.upper()]
                if vault_secret_key.lower() == "mongo_url":
                    vault_val = vault_val.replace("ssl=false", "ssl=true")
                    vault_val += "&ssl_cert_reqs=CERT_NONE"
                # vault_val = vault_val.replace("ssl=true", "ssl=false")
                logging.debug(f"Found {vault_secret_key.upper()}")
            except Exception:
                logging.debug(
                    f'VAULT SECRET: Could not get key "{vault_secret_key}" in secret "{vault_secret_path}". Will try from ENV'
                )
                continue

            d[field.alias] = vault_val
        else:
            logging.debug(
                f"VAULT SECRET: Field {field_name} will be obtained from ENV")
    await vault_client.close()
    return d


def vault_config_settings_source(settings: PydanticBaseSettings) -> Dict[str, Any]:
    _vault_service = _get_config(config="SERVICE", settings=settings)

    loop = asyncio.get_event_loop()
    task = asyncio.create_task(_get_authenticated_vault_client(settings))
    vault_client = loop.run_until_complete(task)

    task = asyncio.create_task(_get_credentials(
        settings, vault_client, _vault_service))
    credentials = loop.run_until_complete(task)

    return credentials
