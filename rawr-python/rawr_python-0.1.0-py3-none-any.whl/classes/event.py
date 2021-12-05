from typing import Optional
from pydantic import BaseModel
from .champion_damage import ChampionDamage
from .champion_position import ChampionPosition


class Event(BaseModel):
    type: str
    timestamp: str
    after_id: Optional[int]
    assisting_participant_ids: Optional[list[int]]
    before_id: Optional[int]
    bounty: Optional[int]
    creator_id: Optional[int]
    gold_gain: Optional[int]
    item_id: Optional[int]
    kill_streak_length: Optional[int]
    kill_type: Optional[str]
    killer_id: Optional[int]
    killer_team_id: Optional[int]
    level: Optional[int]
    level_up_type: Optional[str]
    lane_type: Optional[str]
    monster_type: Optional[str]
    multi_kill_length: Optional[int]
    participant_id: Optional[int]
    position: Optional[ChampionPosition]
    real_timestamp: Optional[int]
    skill_slot: Optional[int]
    victim_damage_dealt: Optional[list[ChampionDamage]]
    victim_damage_received: Optional[list[ChampionDamage]]
    victim_id: Optional[int]
    ward_type: Optional[str]
