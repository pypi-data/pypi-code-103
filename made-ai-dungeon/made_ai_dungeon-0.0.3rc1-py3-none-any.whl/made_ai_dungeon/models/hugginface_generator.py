from typing import Optional, Tuple

import requests
from loguru import logger


class HugginfaceGenerator:
    def __init__(self, api_url: str, headers: str, context_length: int = 2000, min_generated_length: int = 500) -> None:
        self.api_url = api_url
        self.headers = headers
        self.context_length = context_length
        self.min_generated_length = min_generated_length

    def generate_text(self, input_text: str, context: Optional[str]) -> Tuple[str, str]:
        if context is None:
            context = ""
        elif len(context) > self.context_length:
            context = context[-self.context_length:]
        query_text = context + input_text
        query_output = self.query_hugginface(query_text)
        if query_output is None:
            new_context = context
            generated_text = "Проблемы с сервером попробуйте позже"
        else:
            new_context = query_output
            generated_text = query_output[len(query_text):]

        logger.info("Generated text: {gt}, Context: {ct}", gt=generated_text, ct=new_context)
        return generated_text, new_context

    def query_hugginface(self, text: str) -> Optional[str]:
        input_text = text
        while len(input_text) - len(text) < self.min_generated_length:
            response = requests.post(self.api_url, headers=self.headers, json=input_text).json()
            logger.debug("Response {r}", r=response)
            if not isinstance(response, list):
                return None
            else:
                input_text = response[0].get('generated_text')
        return input_text
