from typing import List, Optional, Type

from asking.prompts.prompt import MultipleChoicePromptBuilder, PromptBuilder
from asking.prompts.recall_prompt import RecallPromptBuilder
from asking.protocols import AskActionProtocol

all_prompt_builders: List[Type[PromptBuilder]] = [
    RecallPromptBuilder,
    MultipleChoicePromptBuilder,
]


def get_prompt_parts(ask: AskActionProtocol) -> Optional[str]:
    for builder_cls in all_prompt_builders:
        builder = builder_cls(ask=ask)
        if parts := builder.prompt:
            return parts
    return None


def get_prompt(ask: AskActionProtocol) -> str:
    if parts := get_prompt_parts(ask=ask):
        return f"({parts})"
    return ""
