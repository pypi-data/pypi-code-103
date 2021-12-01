from dataclasses import dataclass


@dataclass(init=True, frozen=True)
class GetTranscription:
    pk: int
    name: str
