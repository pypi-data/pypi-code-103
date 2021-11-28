# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional

# Pip
from jsoncodable import JSONCodable
from noraise import noraise

# Local
from .chat import Chat
from .user import User

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- class: Message -------------------------------------------------------- #

class Message(JSONCodable):

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        id: str,
        from_: Optional[User],
        chat: Chat,
        date: int,
        extra: Optional[dict]
    ):
        self.id = id
        self.from_ = from_
        self.chat = chat
        self.date = date
        self.extra = extra


    @classmethod
    @noraise()
    def from_dict(cls, j: dict):
        message_id = j['message_id']
        del j['message_id']

        from_ = None

        if 'from' in j:
            from_ = User.from_dict(j['from'])
            del j['from']

        chat = Chat.from_dict(j['chat'])
        del j['chat']

        date = j['date']
        del j['date']

        return cls(
            id=message_id,
            from_=from_,
            chat=chat,
            date=date,
            extra=j
        )


# -------------------------------------------------------------------------------------------------------------------------------- #