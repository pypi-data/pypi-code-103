from pydantic import BaseModel


class ChampionDamage(BaseModel):
    basic: bool
    magic_damage: int
    name: str
    participant_id: int
    physical_damage: int
    spell_name: str
    spell_slot: int
    true_damage: int
    type: str
