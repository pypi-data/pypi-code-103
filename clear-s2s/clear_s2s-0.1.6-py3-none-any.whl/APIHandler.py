from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.util.retry import Retry
import logging.config
import requests_pkcs12
import requests
import xmltodict


class APIHandler:
    token_url = "https://api.thomsonreuters.com/tr-oauth/v1/token"

    retry_strategy = Retry(
        total=5,
        backoff_factor=10,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
    )

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        client_id: str,
        client_secret: str,
        s2s_scopes: str,
        cert_path: str = None,
        cert_key: str = None,
        headers: dict = {},
        logging: bool = False,
    ):
        self._host = host
        self._username = username
        self.__password = password
        self.__client_id = client_id
        self.__client_secret = client_secret
        self._scopes = s2s_scopes
        self.__cert_path = cert_path
        self.__cert_key = cert_key
        self._headers = headers
        self.__logging = logging
        self.http = requests.Session()
        self._authenticate()

    @property
    def host(self):
        return self._host

    @property
    def username(self):
        return self._username
    
    @property
    def get_headers(self):
        return self._headers
    
    def _authenticate(self):
        if not self.__cert_path:
            _headers = {
                "Content-Type": "application/x-www-form-urlencoded", 
                "Accept": "application/json"
            }
            data = {
                'client_id': self.__client_id,
                'client_secret': self.__client_secret,
                'scopes': self._scopes, 
                'grant_type': 'client_credentials'
            }
            res = requests.post(self.token_url, data=data, headers=_headers)
            token = res.json()['access_token']
            self.headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/xml'}
            self._cert = None
        else:
            self.headers = {'Content-Type': 'application/xml'}
            self._cert = (self.__cert_path, self.__cert_key)

    def send_request(self, url, payload=None):
        params = {'data': payload, 'headers': self.headers}

        # First request to get data from URL
        if self._cert != None:
            response = requests_pkcs12.post(
                self.host + url,
                auth=HTTPBasicAuth(self.username, self.__password),
                pkcs12_filename=self.__cert_path,
                pkcs12_password=self.__cert_key,
                **params
            )
        else:
            response = self.http.post(self._host + url, **params)

        res = xmltodict.parse(response.content)

        # Second request to get data from Uri from first request
        if 'Uri' in res[list(res.keys())[0]]:
            result_url = res[list(res.keys())[0]]['Uri']
            if self.__cert_path and self.__cert_key:
                obj = requests_pkcs12.get(
                    result_url,
                    params={
                        'startGroup': 0,
                        'direction': 'dsc',
                        'sortBy':'relevance',
                        'maxGroups': 1
                    },
                    auth=HTTPBasicAuth(self.username, self.__password),
                    pkcs12_filename=self.__cert_path,
                    pkcs12_password=self.__cert_key,
                )
            else:
                obj = self.http.get(
                    result_url,
                    params={
                        'startGroup': 0,
                        'direction': 'dsc',
                        'sortBy': 'relevance',
                        'maxGroups': 1
                    }, 
                    headers=self.headers
                )
            return xmltodict.parse(obj.content)
        else:
            return {'NoMatch': 'No match found'}