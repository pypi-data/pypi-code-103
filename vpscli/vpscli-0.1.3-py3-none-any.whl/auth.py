#!/usr/bin/env python
import random
import re, os, sys, joblib
from collections import defaultdict
from functools import reduce
import codefast as cf
from getpass import getpass
from cryptography.fernet import Fernet
import base64
import json
from typing import List, Dict, Tuple, Union, Optional


class AccountLoader:
    __db = os.path.join(cf.io.dirname(), 'memory.joblib')
    __keys = ['REDIS_HOST', 'REDIS_PORT', 'REDIS_PASSWORD']

    @classmethod
    def decode_config_file(cls) -> dict:
        cf.info('decode config file and dump to memory')
        loc = os.path.join(cf.io.dirname(), 'data/redis.txt')
        text = cf.io.reads(loc).encode()
        passwd = getpass('Enter password: ').rstrip()
        passwd = base64.urlsafe_b64encode(passwd.encode() * 10)
        key = Fernet.generate_key()
        key = passwd.decode('utf-8')[:43] + key.decode('utf-8')[43:]
        f = Fernet(key.encode())
        return json.loads(f.decrypt(text).decode('utf-8'))

    @classmethod
    def query_secrets(cls) -> Tuple[str]:
        try:
            return joblib.load(cls.__db)
        except FileNotFoundError:
            cf.error('joblib load found no file')
            js = cls.decode_config_file()
            cls.set_secrets(js)
            return cls.query_secrets()
        except Exception as e:
            return None

    @classmethod
    def set_secrets(cls, secrets: Dict[str, str]) -> None:
        values = [secrets[k] for k in cls.__keys]
        joblib.dump(values, cls.__db)
