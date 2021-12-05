from pydantic import BaseModel
from .participant import Participant
from .metadata import Metadata


class Ban(BaseModel):
    champion_id: int
    pick_turn: int


class ObjectiveInfo(BaseModel):
    first: bool
    kills: int


class Objectives(BaseModel):
    baron: ObjectiveInfo
    champion: ObjectiveInfo
    dragon: ObjectiveInfo
    inhibitor: ObjectiveInfo
    rift_herald: ObjectiveInfo
    tower: ObjectiveInfo


class MatchTeam(BaseModel):
    bans: list[Ban]
    objectives: Objectives
    team_id: int
    win: bool


class MatchInfo(BaseModel):
    game_creation: int
    game_duration: int
    game_end_timestamp: int
    game_id: int
    game_mode: str
    game_name: str
    game_start_timestamp: int
    game_type: str
    game_version: str
    map_id: int
    participants: list[Participant]
    platform_id: str
    queue_id: int
    teams: list[MatchTeam]
    tournament_code: str


class Match(BaseModel):
    metadata: Metadata
    info: MatchInfo
