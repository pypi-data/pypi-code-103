# RUNES AND MASTERIES
from pydantic import BaseModel


class Perk(BaseModel):
    perk: int
    var1: int
    var2: int
    var3: int


class Style(BaseModel):
    description: str
    selections: list[Perk]
    style: int


class StatPerks(BaseModel):
    defense: int
    flex: int
    offense: int


class Perks(BaseModel):
    stat_perks: StatPerks
    styles: list[Style]
