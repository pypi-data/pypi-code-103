# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional

# Pip
from jsoncodable import JSONCodable
from noraise import noraise

# Local
from .enums import ChatType

# -------------------------------------------------------------------------------------------------------------------------------- #



# ---------------------------------------------------------- class: Chat --------------------------------------------------------- #

class Chat(JSONCodable):

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        id: int,
        title: Optional[str],
        type: ChatType
    ):
        self.id = id
        self.title = title
        self.type = type


    @classmethod
    @noraise()
    def from_dict(cls, j: dict):
        return cls(
            id=j.get('id'),
            title=j.get('title'),
            type=ChatType(j.get('type'))
        )


# -------------------------------------------------------------------------------------------------------------------------------- #