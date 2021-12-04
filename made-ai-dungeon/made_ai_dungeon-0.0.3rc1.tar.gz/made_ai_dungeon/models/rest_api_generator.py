from typing import Optional, Tuple

import requests
from loguru import logger
from pydantic import BaseModel


class ResponseModel(BaseModel):
    generated_text: str


class RequestModel(BaseModel):
    text: str


class RestApiGenerator:
    def __init__(self, host_url: str, context_length: int) -> None:
        self.host_url = host_url
        self.context_length = context_length

    def generate_text(self, input_text: str, context: Optional[str]) -> Tuple[str, str]:
        if context is None:
            context = ""
        query_text = context + "\n" + input_text  # TODO: Check if special token should be here instead space
        query_text = query_text[-self.context_length:]  # TODO: context length limit by token not string length
        query_output = self.query(query_text)
        if query_output is None:
            generated_text = "Проблемы с сервером попробуйте позже"
            new_context = context
        else:
            generated_text = query_output.generated_text
            new_context = query_text + " " + generated_text  # TODO: Check if special token should be here instead space
        logger.info("Generated text: {gt}, Context: {ct}", gt=generated_text, ct=new_context)
        return generated_text, new_context

    def query(self, text: str) -> Optional[ResponseModel]:
        request_model = RequestModel(text=text)
        response = requests.get(
            f"{self.host_url}/generate/",
            json=request_model.dict(),
        )
        if response.ok:
            return ResponseModel(**response.json())
        return None
