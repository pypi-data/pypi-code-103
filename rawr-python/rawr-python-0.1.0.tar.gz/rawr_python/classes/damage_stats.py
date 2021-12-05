from pydantic import BaseModel


class DamageStats(BaseModel):
    magic_damage_done: int
    magic_damage_done_to_champions: int
    magic_damage_taken: int
    physical_damage_done: int
    physical_damage_done_to_champions: int
    physical_damage_taken: int
    total_damage_done: int
    total_damage_done_to_champions: int
    total_damage_taken: int
    true_damage_done: int
    true_damage_done_to_champions: int
    true_damage_taken: int
