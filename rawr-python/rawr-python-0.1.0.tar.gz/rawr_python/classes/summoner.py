from pydantic import BaseModel


class Summoner(BaseModel):
    id: str
    account_id: str
    puuid: str
    name: str
    profile_icon_id: str
    summoner_level: int
