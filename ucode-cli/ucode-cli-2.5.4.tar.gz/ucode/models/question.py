# coding=utf-8
import logging
from enum import Enum
from typing import List
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


__author__ = 'ThucNC'
_logger = logging.getLogger(__name__)


class QuestionType(Enum):
    SINGLE_CHOICE = 'single_choice'
    MULTI_CHOICE = 'multiple_choice'
    SHORT_ANSWER = 'short_answer'
    LONG_ANSWER = 'long_answer'
    FILL_IN = 'fill_in'
    CODE = 'code'
    TURTLE = 'turtle'
    SPORT = 'sport'
    DRAG_DROP = 'drag_drop'
    FIND_DIFF = 'find_diff'
    THEORY = 'theory'
    SORTING = 'sorting'
    PUZZLE = 'puzzle'
    CLASSIFY = 'classify'
    MATCHING = 'matching'
    MEMORY = 'memory'


@dataclass_json
@dataclass
class QuestionContent:
    text: str = ""
    text_type: str = "html"
    image: str = ""  # url / svg
    image_type: str = ""
    video: str = ""
    video_type: str = ""
    sound: str = ""
    sound_text: str = ""


@dataclass_json
@dataclass
class QuestionOption:
    id: str = ""
    content: str = ""
    # contents: QuestionContent = None
    # index: str = ""
    # question_id: str = ""
    # option_id: str = ""
    is_correct: bool = False
    value: object = None
    settings: str = ""  # json

    text: str = ""
    text_type: str = "html"
    image: str = ""  # url / svg
    image_type: str = ""
    video: str = ""
    video_type: str = ""
    sound: str = ""
    sound_text: str = ""


@dataclass_json
@dataclass
class Question:
    base_question: bool = False
    sub_question: bool = False
    source: object = "" # json
    src_name: str = ""
    src_id: str = ""
    src_index: int = 0
    score: int = 0
    src_ans_id: str = ""
    src_url: str = ""
    answer: str = ""
    type: QuestionType = QuestionType.SHORT_ANSWER
    src_ans_tag: str = ""
    statement: str = ""
    statement_format: str = "html"  # html | markdown
    statement_language: str = 'en'  # en \ vi
    statement_media: QuestionContent = None
    options: List[QuestionOption] = field(default_factory=list) # for multiple choice question
    option_display: str = "" # json
    solution: str = ""
    solutions: QuestionContent = None
    hint: QuestionContent = None
    tags: List[str] = field(default_factory=list)

    # translations: List[Question] = field(default_factory=list)
