from os import getenv
import hvac
from .logger import get_logger


def _get_client(
    vault_url=None, vault_username=None, vault_password=None, vault_skip_verify=True
):
    logger = get_logger(__name__)
    vault_url = getenv("VAULT_URL", vault_url)
    vault_username = getenv("VAULT_USERNAME", vault_username)
    vault_password = getenv("VAULT_PASSWORD", vault_password)
    vault_skip_verify = getenv("VAULT_SKIP_VERIFY", vault_skip_verify)
    if not vault_url:
        logger.error(
            "vault_url argument is not provided and VAULT_URL is not present in the environment"
        )
        return None
    if not vault_username:
        logger.error(
            "vault_username argument is not provided and VAULT_USERNAME is not present in the environment"
        )
        return None
    if not vault_password:
        logger.error(
            "vault_password argument is not provided and VAULT_PASSWORD is not present in the environment"
        )
        return None
    client = hvac.Client(url=vault_url, verify=vault_skip_verify)
    login_response = client.auth_userpass(
        username=vault_username,
        password=vault_password,
    )
    if client.is_authenticated():
        return client
    return None


def get_vault_secrets(
    path="",
    vault_url=None,
    vault_username=None,
    vault_password=None,
    vault_skip_verify=True,
):
    """get vault secrets for the path

    :param path: vault secrets path
    :type path: str
    :param vault_url: vault server url. If vault_url is none, VAULT_URL environment value will be assigned.
    :type vault_url: str
    :param vault_username: vault username. If vault_username is none, VAULT_USERNAME environment value will be assigned.
    :type vault_username: str
    :param vault_password: vault password. If vault_password is none, VAULT_PASSWORD environment value will be assigned.
    :type vault_password: str
    :param vault_skip_verify: vault skip verification. If VAULT_SKIP_VERIFY is none, VAULT_PASSWORD environment value will be assigned.
    :type vault_skip_verify: bool
    :return: List(Dict[str, Any]) if successful, `None` otherwise
    """
    logger = get_logger(__name__)
    client = _get_client(
        vault_url=vault_url,
        vault_username=vault_username,
        vault_password=vault_password,
        vault_skip_verify=vault_skip_verify,
    )
    if client is None:
        return None
    try:
        secrets = client.read(path)
        client.revoke_self_token()
        if "data" in secrets:
            return secrets["data"]
    except Exception as e:
        logger.error(f"Got an error: {e.message}")
        return None
    return None
