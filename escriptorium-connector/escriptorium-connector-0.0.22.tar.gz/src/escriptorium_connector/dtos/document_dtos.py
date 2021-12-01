from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Union, List
from xmlrpc.client import DateTime

from .super_dtos import PagenatedResponse
from .transcription_dtos import GetTranscription
from .region_dtos import GetRegionType
from .line_dtos import GetLineType


class ReadDirection(str, Enum):
    LTR = "ltr"
    RTL = "rtl"


class LineOffset(int, Enum):
    BASELINE = 0
    TOPLINE = 1
    CENTERED = 2


@dataclass(init=True, frozen=True)
class PostDocument:
    name: str
    project: str
    main_script: str
    read_direction: ReadDirection
    line_offset: LineOffset
    tags: List[str] = field(default_factory=list)


@dataclass(init=True, frozen=True)
class PutDocument:
    name: str
    project: str
    main_script: str
    read_direction: ReadDirection
    line_offset: LineOffset
    tags: List[str] = field(default_factory=list)


@dataclass
class GetDocument:
    pk: int
    name: str
    project: str
    main_script: str
    read_direction: ReadDirection
    line_offset: LineOffset
    parts_count: int
    created_at: DateTime
    updated_at: DateTime
    transcriptions: List[GetTranscription] = field(default_factory=list)
    valid_block_types: List[GetRegionType] = field(default_factory=list)
    valid_line_types: List[GetLineType] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def __init__(
        self,
        pk: int,
        name: str,
        project: str,
        main_script: str,
        read_direction: str,
        line_offset: int,
        created_at: str,
        updated_at: str,
        parts_count: int = 0,
        transcriptions: List[Any] = [],
        valid_block_types: List[Any] = [],
        valid_line_types: List[Any] = [],
        tags: List[str] = [],
    ):
        self.pk = pk
        self.name = name
        self.project = project
        self.main_script = main_script
        self.read_direction = ReadDirection(read_direction)
        self.line_offset = LineOffset(line_offset)
        self.parts_count = parts_count
        self.created_at = DateTime(created_at)
        self.updated_at = DateTime(updated_at)
        self.transcriptions = [GetTranscription(**x) for x in transcriptions]
        self.valid_block_types = [GetRegionType(**x) for x in valid_block_types]
        self.valid_line_types = [GetLineType(**x) for x in valid_line_types]
        self.tags = tags


@dataclass
class GetDocuments(PagenatedResponse):
    results: List[GetDocument]

    def __init__(
        self,
        count: int,
        next: Union[str, None],
        previous: Union[str, None],
        results: List[Any] = [],
    ):
        super(GetDocuments, self).__init__(count, next, previous)
        self.results = [GetDocument(**x) for x in results]
