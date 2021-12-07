import json
from os import getenv
import yaml
from .vault import get_vault_secrets
from .logger import get_logger
import re

_from_env = True
_vault_secrets = None
_json_configs = None
_yaml_configs = None


def init_config(from_env=True, json_file=None, yaml_file=None, vault_path=None):
    """initializes the config module

    :param from_env: should the config read from environment.
    :type from_env: bool
    :param json_file: json config file path.
    :type json_file: str
    :param yaml_file: yaml config file path.
    :type yaml_file: str
    :param vault_path: should the config read from valut server. If vault_path is set, The VAULT_URL & VAULT_TOKEN environments should be set.
    :type vault_path: str
    """

    global _from_env, _vault_secrets, _json_configs, _yaml_configs
    logger = get_logger(__name__)

    _from_env = from_env

    if not (json_file is None):
        try:
            with open(json_file, "r") as f:
                _json_configs = json.load(f)
        except Exception as e:
            logger.error(f"Got an error: {e.message}")

    if not (yaml_file is None):
        try:
            with open(yaml_file, "r") as f:
                _yaml_configs = yaml.load(f, yaml.SafeLoader)
        except Exception as e:
            logger.error(f"Got an error: {e.message}")
    if not (vault_path is None):
        _vault_secrets = get_vault_secrets(vault_path)


def get_config(key=True, default=None):
    """Get an config variable, return None if it doesn't exist.
    The optional second argument can specify an alternate default.

    :param key: configuration key parameter.
    :type key: str
    :param default: The default value if key doesn't exist.
    """
    global _from_env, _vault_secrets, _json_configs, _yaml_configs

    if _from_env:
        value = getenv(key=key, default=None)
        if not (value is None):
            return value
        else:
            value = getenv(key=re.sub(r"\s+", "_", key).upper(), default=None)
            if not (value is None):
                return value
    if not (_json_configs is None):
        if key in _json_configs:
            return _json_configs[key]
    if not (_yaml_configs is None):
        if key in _yaml_configs:
            return _yaml_configs[key]
    if not (_vault_secrets is None):
        if key in _vault_secrets:
            return _vault_secrets[key]
    return default
