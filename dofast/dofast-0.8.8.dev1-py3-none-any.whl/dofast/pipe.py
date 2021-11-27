'''pipe file to connect core files and application files'''
from typing import Dict, List, Optional, Tuple, Union

import codefast as cf
import keyring

from .authorization import Authorization


class AccountLoader:
    SERVICE_NAME = 'dofast'
    KEYRING_KEYS = ['host', 'port', 'password', 'fernet_key']

    @classmethod
    def query_secrets(cls) -> Tuple[str]:
        secrets = [
            keyring.get_password(cls.SERVICE_NAME, k) for k in cls.KEYRING_KEYS
        ]
        if all(secrets):
            secrets[-1] = bytes(secrets[-1], 'utf-8')
            return tuple(secrets)
        return None

    @classmethod
    def set_secrets(cls, secrets: Dict[str, str]) -> None:
        for k, v in secrets.items():
            keyring.set_password(cls.SERVICE_NAME, k, v)


def init_auth():
    secrets = AccountLoader.query_secrets()
    if secrets:
        return Authorization(secrets[0], secrets[1], secrets[2], secrets[3])

    try:
        accounts = cf.json('/tmp/redis_account.json')
        AccountLoader.set_secrets(accounts)
        host, port, password, fernet_key = AccountLoader.query_secrets()
        return Authorization(host, port, password, fernet_key)
    except ModuleNotFoundError as e:
        cf.warning('Module not found', str(e))
        return None


author = init_auth()
