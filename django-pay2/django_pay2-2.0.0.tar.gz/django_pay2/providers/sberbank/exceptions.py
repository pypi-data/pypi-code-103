import requests


class SberbankApiError(Exception):
    def __init__(self, response: requests.Response):
        self.response = response
