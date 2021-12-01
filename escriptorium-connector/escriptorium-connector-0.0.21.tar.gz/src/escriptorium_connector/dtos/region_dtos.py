from dataclasses import dataclass


@dataclass(init=True, frozen=True)
class GetRegionType:
    pk: int
    name: str
