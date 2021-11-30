from flask import request
from const import APPLICATION_CODE, DGAPI_SERVER
import requests


class DGAPI(object):
    """DGAPI connection"""

    server_address = DGAPI_SERVER

    @classmethod
    def send_request(self, type_method: str, endpoint: str, body: dict, headers: dict) -> requests.Response:
        nheaders = {**dict(request.headers), "application-code": APPLICATION_CODE}
        headers and nheaders.update(headers)
        return requests.request(type_method, r"http://%s/%s" % (self.server_address, endpoint), json=body, headers=nheaders)

    @classmethod
    def post(self, method: str, body: dict, headers: dict = {}) -> requests.Response:
        """
        Send POST request

        Parameters:
            method (str): Endponint request
            body (dict): Body
            headers (dict): Headers
        """
        return self.send_request('POST', method, body, headers)

    @classmethod
    def get(self, method: str, headers: dict = {}) -> requests.Response:
        """
        Send GET request

        Parameters:
            method (str): Endponint request
            headers (dict): Headers
        """
        return self.send_request('GET', method, None, headers)
