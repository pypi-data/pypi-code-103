"""Datatypes."""
# pylint: disable=invalid-name,too-many-instance-attributes

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class QuestionCount:
    """QuestionCount."""

    difficulty: str
    count: int


@dataclass
class Contributions:
    """Contributions."""

    points: int
    questionCount: int
    testcaseCount: int


@dataclass
class Profile:
    """Profile."""

    realName: str
    websites: List[str]
    countryName: str
    skillTags: List[str]
    company: Optional[str]
    school: Optional[str]
    starRating: float
    aboutMe: str
    userAvatar: str
    reputation: int
    ranking: int


@dataclass
class SubmissionCount:
    """SubmissionCount."""

    difficulty: str
    count: int
    submissions: int


@dataclass
class SubmitStats:
    """SubmitStats."""

    acSubmissionNum: List[SubmissionCount]
    totalSubmissionNum: List[SubmissionCount]


@dataclass
class MatchedUser:
    """MatchedUser."""

    username: str
    githubUrl: str
    contributions: Contributions
    profile: Profile
    submitStats: SubmitStats


@dataclass
class LeetCodeData:
    """Data from LeetCode about one user."""

    allQuestionsCount: List[QuestionCount]
    matchedUser: MatchedUser
