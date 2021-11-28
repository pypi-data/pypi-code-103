'''pipe file to connect core files and application files'''
import os
from typing import Dict, List, Optional, Tuple, Union

import codefast as cf
import joblib

from .authorization import Authorization


class AccountLoader:
    __db = os.path.join(cf.io.dirname(), 'memory.joblib')
    __keys = ['host', 'port', 'password', 'fernet_key']
    __init_file = '/tmp/redis.json'

    @classmethod
    def query_secrets(cls) -> Tuple[str]:
        if cf.io.exists(cls.__db):
            list_ = joblib.load(cls.__db)
            list_[-1] = bytes(list_[-1], 'utf-8')
            return tuple(list_)
        else:
            return None

    @classmethod
    def set_secrets(cls, secrets: Dict[str, str]) -> None:
        values = [secrets[k] for k in cls.__keys]
        joblib.dump(values, cls.__db)

    @classmethod
    def init_auth(cls) -> Authorization:
        secrets = cls.query_secrets()
        if secrets:
            return Authorization(secrets[0], secrets[1], secrets[2],
                                 secrets[3])

        if not cf.io.exists(cls.__init_file):
            raise Exception('init file not found')

        accounts = cf.json(cls.__init_file)
        cls.set_secrets(accounts)
        host, port, password, fernet_key = cls.query_secrets()
        cf.io.rm(cls.__init_file)
        return Authorization(host, port, password, fernet_key)


author = AccountLoader.init_auth()
