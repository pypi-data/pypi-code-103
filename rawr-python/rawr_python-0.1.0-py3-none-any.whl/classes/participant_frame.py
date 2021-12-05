from pydantic import BaseModel
from .champion_stats import ChampionStats
from .damage_stats import DamageStats
from .champion_position import ChampionPosition


class ParticipantFrame(BaseModel):
    participant_id: int
    current_gold: int
    gold_per_second: int
    jungle_minions_killed: int
    level: int
    minions_killed: int
    time_enemy_spent_controlled: int
    total_gold: int
    xp: int
    champion_stats: ChampionStats
    damage_stats: DamageStats
    position: ChampionPosition
