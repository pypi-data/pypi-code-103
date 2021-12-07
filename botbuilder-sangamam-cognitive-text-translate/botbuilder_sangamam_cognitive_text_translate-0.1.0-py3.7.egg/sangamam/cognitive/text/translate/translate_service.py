from .translate_settings import TranslateSettings
from .translate_response import TranslateResponse, Translate
import requests
import uuid


class TranslateService:
    def __init__(self, request: TranslateSettings):
        self.params = None
        self.headers = None
        self.request_url = None
        if not request.validate_settings():
            raise Exception('invalid settings')

        self.translate_request = request
        self.prepare_request()

    def prepare_request(self):
        end_point_url = self.translate_request.url
        path = '/translate?api-version=3.0'
        self.request_url = end_point_url + path

        self.params = {
            'api-version': '3.0',
            'from': self.translate_request.from_lang,
            'to': ','.join(self.translate_request.to_lang),
        }

        self.headers = {
            'Ocp-Apim-Subscription-Key': self.translate_request.subscription_key,
            'Ocp-Apim-Subscription-Region': self.translate_request.subscription_region,
            'Content-Type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

    def translate_text(self, text: str) -> TranslateResponse:
        text = str(text)
        body = [
            {'text': text}
        ]
        response = TranslateResponse()
        requests_output = requests.post(self.request_url, params=self.params, headers=self.headers, json=body)
        response.status_code = requests_output.status_code
        response.status_message = requests_output.json()

        response.from_lang.lang = self.translate_request.from_lang
        response.from_lang.text = text

        if response.status_code == 200:
            response.output = []
            for item in requests_output.json()[0]['translations']:
                translate = Translate()
                translate.lang = item['to']
                translate.text = item['text']
                response.output.append(translate)

        return response
