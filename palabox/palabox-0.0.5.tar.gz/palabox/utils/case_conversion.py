"""Case conversion."""

import re


def normal_to_snake_case(text: str) -> str:
    """Convert from normal to snake_case."""
    return text.lower().replace(" ", "_")


def normal_to_camelcase(text: str) -> str:
    """Convert from normal to camelCase."""
    texts = text.lower().split(" ")
    texts = [texts[0]] + list(map(lambda x: x.capitalize(), texts[1:]))
    return "".join(texts)


def camelcase_to_snake_case(text: str) -> str:
    """Convert from camelCase to snake_case."""
    return re.sub(r"([A-Z])", r"_\g<1>", text).lower()


def snake_case_to_camelcase(text: str) -> str:
    """Convert from snake_case to camelCase."""
    return normal_to_camelcase(text.replace("_", " "))
