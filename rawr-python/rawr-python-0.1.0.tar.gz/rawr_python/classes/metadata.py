from pydantic import BaseModel


class Metadata(BaseModel):
    data_version: str
    match_id: str
    participants: list[str]
