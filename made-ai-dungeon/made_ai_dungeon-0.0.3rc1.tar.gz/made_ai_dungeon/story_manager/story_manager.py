from typing import Dict, Any
from .text_generator import TextGenerator


class StoryManager:

    def __init__(self, generator: TextGenerator) -> None:
        self.generator = generator
        self.story_context_cache: Dict[int, Any] = {}

    def generate_story(self, chat_id: int, input_text: str) -> str:
        context = self.story_context_cache.get(chat_id)
        generated_text, new_context = self.generator.generate_text(input_text, context)
        self.story_context_cache[chat_id] = new_context
        return generated_text
