from dataclasses import dataclass


@dataclass(init=True, frozen=True)
class GetLineType:
    pk: int
    name: str
