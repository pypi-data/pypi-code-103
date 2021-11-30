from enum import Enum, unique


@unique
class Content(Enum):
    MARKDOWN = 0
    HTML = 1
