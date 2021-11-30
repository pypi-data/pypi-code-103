import os
from typing import Any, List


def make_name_importable(name: str) -> str:
    """
    Converts a system path to importable name
    """
    if os.path.isfile(name) and name.lower().endswith(".py"):
        name = name[:-3].replace("./", "").replace("\\", ".").replace("/", ".")
        while name.startswith("."):
            name = name[1:]
        return name
    return name


def flatten(deep_list: List[Any]) -> List[Any]:
    """
    Recursively flatten the list into 1D list containing all nested elements
    """
    if len(deep_list) == 0:
        return deep_list
    if isinstance(deep_list[0], list):
        return flatten(deep_list[0]) + flatten(deep_list[1:])
    return deep_list[:1] + flatten(deep_list[1:])
