""" wrapper for requests class and superwise token handling """
import jwt
import requests

from superwise import logger
from superwise.config import Config
from superwise.controller.exceptions import *


def token_retry(input_func):
    """
    A decorator for token retry handling (ie, refresh token if needed)
    :param input_func:
    :return:
    """

    def wrapper(*args, **kwargs):
        res = input_func(*args, **kwargs)
        if res.status_code == 403:
            args[0].refresh_token()
            res = input_func(*args, **kwargs)
        return res

    return wrapper


class Client:
    """ Client is a wrapper for requests for superwise pacakge """

    def __init__(self, client_id, secret, api_host, email=None, password=None):
        self.client_id = client_id
        self.secret = secret
        self.api_host = api_host
        self.email = email
        self.password = password
        self.token = self.get_token()
        self.tenant_id = self.get_tenant_id(self.token)
        self.logger = logger
        self.headers = self.build_headers()
        self.service_account = self.get_service_account()

    def get_tenant_id(self, token):
        try:
            jwt_payload = jwt.decode(token, "secret", options={"verify_signature": False})
        except:
            raise SuperwiseTokenException("error parsing jwt token: {}".format(token))
        if jwt_payload:
            return jwt_payload.get("tenantId")
        else:
            raise SuperwiseException("error decoding JWT")

    def build_headers(self):
        """
        return the headers to send in each API call
        :return: list of headers
        """
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.token,
        }

    def refresh_token(self):
        """
        refresh  bearer token

        :return: token string
        """
        return self.get_token()

    def get_token(self):
        """
        get bearer token to use in each API call

        :return: token string
        """

        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.email:
            url = "{}/identity/resources/auth/v1/user".format(Config.FRONTEGG_URL)
            params = {"email": self.email, "password": self.password}
        else:
            params = {"clientId": self.client_id, "secret": self.secret}
            url = "{}/identity/resources/auth/v1/api-token".format(Config.FRONTEGG_URL)
        res = self._post(url, params=params, headers=headers)

        error = False
        token = None
        try:
            token = res.json().get("accessToken")
        except:
            error = True
        if not token or error:
            raise SuperwiseAuthException("Error get or refresh token url={} params={} ".format(url, params))

        return token

    def _post(self, url, params, headers=None):
        """
        wrapper to requests.post(), with no refresh token handling
        :param url: url string
        :param params: json paramters to send
        :param headers: headers string
        :return: Response object (requests package)
        """
        headers = self.headers if not headers else headers
        logger.debug("POST:  {} params: {}".format(url, params))
        res = requests.post(url, json=params, headers=headers)
        return res

    @token_retry
    def post(self, url, params, headers=None):
        """
        wrapper for self._post() decoarted using token_retry.

        :param url: url string
        :param params: params: json paramters to send
        :param headers: headers: headers string

        :return: Response object (requests package)
        """
        return self._post(url, params, headers)

    @token_retry
    def get(self, url, query_params=None, headers=None):
        """
        wrapper for reuqests.get()

        :param url: url string
        :param query_params:  dictionary of paramters to add as query string
        :param headers: headers dictionary
        :return: Response object (requests package)
        """
        headers = self.headers if not headers else headers
        logger.debug("GET {} query params: {}".format(url, query_params))
        res = requests.get(url=url, headers=headers, params=query_params)
        return res

    @token_retry
    def delete(self, idx):
        """
        wrapper for reuqests.delete()

        :param idx: id int
        :return: Response object (requests package)
        """
        raise NotImplementedError()

    @token_retry
    def patch(self, url, params, headers=None):
        """
        wrapper for reuqests.delete()

        :return: Response object (requests package)
        """
        headers = self.headers if not headers else headers
        logger.debug("PATCH {}  params: {} ".format(url, params))
        res = requests.patch(url, json=params, headers=headers)
        return res

    def get_service_account(self):
        url = "https://{}/{}/{}".format(self.api_host, self.tenant_id, "admin/v1/settings/service-account")
        logger.debug("GET Service Account")
        try:
            res = requests.get(url, headers=self.headers)
            service_account = res.json().get("service_account")
        except Exception as e:
            logger.debug("Failed GET Service Account")
            raise SuperwiseServiceAccountException("Failed get service account with ext {}".format(e))
        return service_account
