"""Datatypes."""
# pylint: disable=invalid-name,too-many-instance-attributes

from dataclasses import dataclass
from typing import List


@dataclass
class FormValues:
    """FormValues."""

    city: str
    school: str


@dataclass
class CodinGamer:
    """CodinGamer."""

    userId: int
    pseudo: str
    countryId: str
    publicHandle: str
    schoolId: int
    rank: int
    onlineSince: int
    formValues: FormValues
    city: str
    level: int
    xp: int
    category: str


@dataclass
class RankHistorics:
    """RankHistorics."""

    ranks: List[int]
    totals: List[int]
    points: List[int]
    contestPoints: List[int]
    optimPoints: List[int]
    codegolfPoints: List[int]
    multiTrainingPoints: List[int]
    clashPoints: List[int]
    dates: List[int]


@dataclass
class CodingamePointsRankingDto:
    """CodingamePointsRankingDto."""

    codingamePointsTotal: int
    codingamePointsRank: int
    codingamePointsContests: int
    codingamePointsAchievements: int
    codingamePointsXp: int
    codingamePointsOptim: int
    codingamePointsCodegolf: int
    codingamePointsMultiTraining: int
    codingamePointsClash: int
    numberCodingamers: int
    numberCodingamersGlobal: int
    rankHistorics: RankHistorics


@dataclass
class CodinGameStats:
    """CodinGameStats."""

    codingamerPoints: int
    achievementCount: int
    codingamer: CodinGamer
    codingamePointsRankingDto: CodingamePointsRankingDto
