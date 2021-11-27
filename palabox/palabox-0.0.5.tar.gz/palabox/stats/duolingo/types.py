"""Datatypes."""
# pylint: disable=invalid-name,too-many-instance-attributes

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TrackingProperties:
    streak: int
    username: str
    creation_age: int
    is_age_restricted: bool
    creation_date: str
    num_followers: int
    gems: int
    user_id: int
    goal: int
    direction: str
    learning_reason: str
    num_sections_unlocked: int
    num_classrooms: int
    num_skills_unlocked: int
    num_observees: int
    achievements: List[str]
    lingots: int
    trial_account: bool
    prior_proficiency_onboarding: int
    level: int
    learning_language: str
    num_sessions_completed: int
    num_following: int
    ui_language: str


@dataclass
class XPGain:
    eventType: Optional[str]
    xp: int
    time: int


@dataclass
class progressQuizHistory:
    endTime: int
    startTime: int
    score: float
    maxRowReachedDuringMigration: int


@dataclass
class Skill:
    lessons: int
    name: str
    finishedLessons: int
    finishedLevels: int
    levels: int
    shortName: str
    accessible: bool = False
    strength: float = 0.0


@dataclass
class Course:
    authorId: str
    title: str
    learningLanguage: str
    xp: int
    healthEnabled: bool
    fromLanguage: str
    crowns: int
    id: str


@dataclass
class CurrentCourse:
    status: str
    learningLanguage: str
    crowns: int
    xp: int
    wordsLearned: int
    id: str
    title: str
    numberOfWords: Optional[int]
    skills: List[List[Skill]]
    progressQuizHistory: List[progressQuizHistory]


@dataclass
class DuolingoStats:
    """FormValues."""

    bio: str
    trackingProperties: TrackingProperties
    totalXp: int
    timezoneOffset: str
    inviteURL: str
    xpGains: List[XPGain]
    courses: List[Course]
    weeklyXp: int
    monthlyXp: int
    lingots: int
    streak: int
    name: str
    xpGoal: int
    email: str
    username: str
    currentCourse: CurrentCourse
