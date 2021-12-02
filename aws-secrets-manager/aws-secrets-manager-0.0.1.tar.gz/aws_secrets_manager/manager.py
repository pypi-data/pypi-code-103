import json
from typing import Sequence, Union, Dict

import boto3.session
import botocore


class CredentialsNotExists(Exception):
    def __str__(self):
        return 'AWS Credentials Not Exists'


class AWSSecretsManager:
    """
    AWS SecretsManager
    """

    def __init__(self):
        self._secrets = {}

    @staticmethod
    def get_client():
        botocore_session = botocore.session.get_session({  # noqa
            'config_file': (None, 'AWS_SECRETS_CONFIG_FILE', None, None)
        })
        session = boto3.session.Session(botocore_session=botocore_session)
        if session.get_credentials() is None:
            raise CredentialsNotExists()
        return session.client('secretsmanager')  # noqa

    def _get_secrets(self, key: str) -> Union[Sequence, Dict]:
        if key not in self._secrets:
            client = self.get_client()
            self._secrets[key] = json.loads(client.get_secret_value(SecretId=key)['SecretString'])
        return self._secrets

    def get(self, key, default=None):
        _secrets = self._get_secrets(key)
        return _secrets.get(key, default)

    def __getitem__(self, item):
        _secrets = self._get_secrets(item)
        return _secrets[item]


secrets = AWSSecretsManager()
