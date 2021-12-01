import json
from types import SimpleNamespace

import requests


class IkologikApiCredentials(object):

    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password
        self.jwt = None

    def get_url(self):
        return self.url

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_jwt(self):
        try:
            if self.jwt is None:
                # Prepare the headers
                headers = {
                    'Content-Type': 'application/json'
                }
                # Prepare the data
                data = json.dumps({
                    'username': self.username,
                    'password': self.password
                })
                # Execute
                response = requests.post(
                    f'{self.url}/api/v2/auth/login',
                    data=data,
                    headers=headers,
                    verify=False
                )
                result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                self.jwt = result.accessToken
                return self.jwt
            else:
                return self.jwt
        except requests.exceptions.HTTPError as error:
            print(error)
