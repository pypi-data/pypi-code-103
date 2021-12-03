"""Case conversion."""

from typing import Any, Dict

from .case_conversion import camelcase_to_snake_case


def convert_dict_keys_to_snake_case(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a dict to keys."""
    return {
        camelcase_to_snake_case(key): convert_dict_keys_to_snake_case(value)
        if isinstance(value, dict)
        else value
        for key, value in dictionary.items()
    }
