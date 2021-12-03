import boto3
import json


class GetSecretFailed(Exception):
    pass


class SecretsConnectionFailed(Exception):
    pass


class Secrets:
    def __init__(self, *args, **kwargs):
        try:
            self.secrets = boto3.client('secretsmanager')
        except Exception as e:
            raise SecretsConnectionFailed(str(e))

    def get_secret(self, secret_name):
        try:
            get_secret_value_response = self.secrets.get_secret_value(
                SecretId=secret_name
            )
        except Exception as e:
            raise GetSecretFailed(str(e))
        return json.loads(get_secret_value_response['SecretString'])
