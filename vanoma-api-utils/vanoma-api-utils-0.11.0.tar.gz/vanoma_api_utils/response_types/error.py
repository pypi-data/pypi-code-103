from dataclasses import dataclass
from dataclasses_json import dataclass_json  # type: ignore
from dataclasses_json.api import LetterCase  # type: ignore

"""
TODO: Use DataClassJsonMixin to improve mypy. 
TODO: There's currently a bug in this class because it doesn't recognize letter_case.
"""


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Error:
    error_code: str
    error_message: str


def parse_error(json: str) -> Error:
    return Error.from_json(json)  # type: ignore
