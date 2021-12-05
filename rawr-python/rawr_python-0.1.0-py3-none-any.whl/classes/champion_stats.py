from pydantic import BaseModel


class ChampionStats(BaseModel):
    ability_haste: int
    ability_power: int
    armor: int
    armor_pen: int
    armor_pen_percent: int
    attack_damage: int
    attack_speed: int
    bonus_armor_pen_percent: int
    bonus_magic_pen_percent: int
    cc_reduction: int
    cooldown_reduction: int
    health: int
    health_max: int
    health_regen: int
    lifesteal: int
    magic_pen: int
    magic_pen_percent: int
    magic_resist: int
    movement_speed: int
    omnivamp: int
    physical_vamp: int
    power: int
    power_max: int
    power_regen: int
    spell_vamp: int
