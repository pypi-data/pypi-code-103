from typing import Dict

from vatis.asr_commons.config import Language
from vatis.asr_commons.constants.custom_models import MODEL
from vatis.asr_commons.custom_models import Model

from vatis.live_asr.config_variables import API_KEY, AUTHENTICATION_PROVIDER_URL
import requests
from requests import Response


class ClientAuthorization:
    def __init__(self, auth_token: str, service_host: str):
        self._auth_token = auth_token
        self._service_host = service_host

    @property
    def auth_token(self) -> str:
        return self._auth_token

    @property
    def service_host(self) -> str:
        return self._service_host


def get_auth_token(model: Model = None, language: Language = None) -> ClientAuthorization:
    assert model is not None or language is not None

    query_params: Dict[str, str] = {'service': 'LIVE_ASR'}

    if model is not None:
        query_params[MODEL] = str(model.uid)

    if language is not None:
        query_params['language'] = language.value

    response: Response = requests.get(
        AUTHENTICATION_PROVIDER_URL,
        params=query_params,
        headers={'Authorization': 'Bearer ' + API_KEY}
    )

    if response.status_code != 200:
        raise ConnectionAbortedError(f'Bad status code {response.status_code}')

    parsed = response.json()

    return ClientAuthorization(**parsed)

