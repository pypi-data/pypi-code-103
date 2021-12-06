# coding=utf-8
import logging
from enum import Enum
from typing import List
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


__author__ = 'ThucNC'

from ucode.models.question import Question

_logger = logging.getLogger(__name__)


class LessonType(Enum):
    VIDEO = 'video'
    QUIZ = 'quiz'
    LECTURE = 'lecture'
    FILE = 'file'


class QuizType(Enum):
    SUBMIT_SINGLE_QUESTION = 'submit_single_question'
    SUBMIT_ALL = 'submit_all'


@dataclass_json
@dataclass
class Lesson:
    name: str = ""
    description: str = ""
    content: str = ""
    video: str = ""
    file: str = ""
    is_free: bool = False
    xp: int = 100
    src_id: str = ""
    src_url: str = ""
    type: LessonType = LessonType.QUIZ
    tags: List[str] = field(default_factory=list)
    questions: List[Question] = field(default_factory=list)
