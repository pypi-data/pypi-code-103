from typing import Optional, Tuple

from loguru import logger


def simple_generate(text1: str, text2: str) -> Tuple[str, str]:
    return text1, text2 + text1


class GeneratorStub:
    def __init__(self):
        self.model = simple_generate

    def generate_text(self, input_text: str, context: Optional[str]) -> Tuple[str, str]:
        if context is None:
            context = ""
        generated_text, new_context = self.model(input_text, context)
        logger.info("Generated text: {gt}, Context: {ct}", gt=generated_text, ct=context)
        return generated_text, new_context
