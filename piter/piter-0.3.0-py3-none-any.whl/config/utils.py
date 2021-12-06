from typing import List

import toml


def shrink_dependencies(dependencies: List[str]) -> List[str]:
    return list(map(lambda a: a.replace(" ", ""), dependencies))


def load_config():
    result = toml.load("pyproject.toml")
    result = result["tools"]
    result = result["piter"]
    # return toml.load("pyproject.toml")["tools"]["piter"]
    return result
