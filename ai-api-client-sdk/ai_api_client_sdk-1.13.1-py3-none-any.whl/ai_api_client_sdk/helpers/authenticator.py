import requests

from ai_api_client_sdk.exception import AIAPIAuthenticatorException


class Authenticator:
    """Authenticator class is implemented to retrieve the authorization token from the xsuaa server

    :param auth_url: URL of the authorization endpoint. Should be the full URL (including /oauth/token)
    :type auth_url: str
    :param client_id: client id to be used for authorization
    :type client_id: str
    :param client_secret: client secret to be used for authorization
    :type client_secret: str
    """
    def __init__(self, auth_url: str, client_id: str, client_secret: str):
        self.url: str = auth_url
        self.client_id: str = client_id
        self.client_secret: str = client_secret

    def get_token(self) -> str:
        """Retrieves the token from the xsuaa server.

        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthenticatorException` if an unexpected exception occurs while
            trying to retrieve the token
        :return: The Bearer token
        :rtype: str
        """
        data = {'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}
        try:
            response = requests.post(url=self.url, data=data)
            access_token = response.json()['access_token']
        except Exception as e:  # TODO: handle 4XX cases explicitly
            raise AIAPIAuthenticatorException('Could not retrieve Authorization token') from e
        return f'Bearer {access_token}'
