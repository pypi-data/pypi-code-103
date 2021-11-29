from urllib.parse import urljoin
import requests
import os

from . import exceptions


# set defaults for MLP API adapter
MLP_HOST = os.getenv("TEXTA_TAGGER_MLP_URL", "http://mlp-dev.texta.ee:5000")
MLP_MAJOR_VERSION = int(os.getenv("TEXTA_TAGGER_MLP_MAJOR_VERSION", "2"))


def check_mlp_connection(func):
    """
    Wrapper function for checking MLP connection prior to requests.
    """
    def func_wrapper(*args, **kwargs):
        MLP_URL = args[0].mlp_host
        try:
            response = requests.get(MLP_URL, timeout=3)
            if not response.ok: raise exceptions.MLPNotAvailableError()
            return func(*args, **kwargs)
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
            raise exceptions.MLPNotAvailableError()
    return func_wrapper


class MLP2Analyzer:

    def __init__(self, MLP_HOST=MLP_HOST):
        self.mlp_host = MLP_HOST
        self.mlp_url = urljoin(MLP_HOST, "mlp")

    @check_mlp_connection
    def process(self, text):
        if not text or len(text) < 2:
            return {"text": {"text": text}, "texta_facts": []}
        response = requests.post(self.mlp_url, data=text.encode())
        if response.status_code != 200:
            raise exceptions.MLPFailedError("MLP service sent non-200 response. Please check MLP url and input.")
        response_json = response.json()
        return response_json

    @check_mlp_connection
    def lemmatize(self, text):
        if not text or len(text) < 2:
            return text
        response = requests.post(self.mlp_url, data=text.encode())
        if response.status_code != 200:
            raise exceptions.MLPFailedError(f"MLP service sent non-200 response: {response.text}")
        response_json = response.json()
        lemmas = response_json["text"]["lemmas"]
        return lemmas


class MLP3Analyzer:

    def __init__(self, MLP_HOST=MLP_HOST):
        self.mlp_host = MLP_HOST
        self.mlp_url = urljoin(MLP_HOST, "mlp/text")

    @check_mlp_connection
    def process(self, text):
        if not text:
            return {"text": {"text": text}, "texta_facts": []}
        payload = {"text": text.encode(), "analyzers": []}
        response = requests.post(self.mlp_url, data=payload)
        if response.status_code != 200:
            raise exceptions.MLPFailedError("MLP service sent non-200 response. Please check MLP url and input.")
        processed_text = response.json()
        return processed_text

    @check_mlp_connection
    def lemmatize(self, text):
        if not text:
            return text
        payload = {"text": text.encode(), "analyzers": ["lemmas"]}
        response = requests.post(self.mlp_url, data=payload)
        if response.status_code != 200:
            raise exceptions.MLPFailedError("MLP service sent non-200 response. Please check MLP url and input.")
        lemmas = response.json()["text"]["lemmas"]
        return lemmas


def get_mlp_analyzer(mlp_host=None, mlp_major_version=2):
    """
    Function for retrieving an MLP object based on MLP hostname and major version (2/3).
    Also possible to use MLP from package.
    :param: str mlp_host: Hostname for the MLP service.
    :param: int mlp_major_version: Major version number (2.x.x vs 3.x.x) of MLP.
    :param: bool use_api: 
    :return: analyzer object.
    """
    if mlp_host:
        # get analyzer over api
        if mlp_major_version == 2:
            analyzer = MLP2Analyzer(MLP_HOST=mlp_host)
        else:
            analyzer = MLP3Analyzer(MLP_HOST=mlp_host)
    else:
        # get analyzer from package
        # import MLP package here so it won't throw importerror if API used and package not installed
        from texta_mlp.mlp import MLP
        analyzer = MLP()
    return analyzer
