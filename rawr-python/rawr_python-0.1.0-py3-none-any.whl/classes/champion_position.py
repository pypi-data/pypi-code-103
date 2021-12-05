from pydantic import BaseModel


class ChampionPosition(BaseModel):
    x: int
    y: int
