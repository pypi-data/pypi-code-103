from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict, Union

AnyDict = Dict[Any, Any]

StageKey = str

BranchingKey = Union[List[str], str]


class PathDict(TypedDict):
    response: List[str]
    then: List[Dict[str, Any]]


# References = Dict[Any, Any]
Responses = Dict[str, Any]
StageType = List[Dict[str, Any]]


@dataclass
class Asked:
    responses: Responses
    stop_reason: Any


ScriptDict = Dict[str, StageType]
