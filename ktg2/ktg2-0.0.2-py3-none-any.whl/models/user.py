# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional

# Pip
from jsoncodable import JSONCodable
from noraise import noraise

# -------------------------------------------------------------------------------------------------------------------------------- #



# ---------------------------------------------------------- class: User --------------------------------------------------------- #

class User(JSONCodable):

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        id: int,
        is_bot: bool,
        first_name: str,
        username: str
    ):
        self.id = id
        self.is_bot = is_bot
        self.first_name = first_name
        self.username = username


    @classmethod
    @noraise()
    def from_dict(cls, j: dict):
        return cls(
            id=j.get('id'),
            is_bot=j.get('is_bot'),
            first_name=j.get('first_name'),
            username=j.get('username')
        )


# -------------------------------------------------------------------------------------------------------------------------------- #