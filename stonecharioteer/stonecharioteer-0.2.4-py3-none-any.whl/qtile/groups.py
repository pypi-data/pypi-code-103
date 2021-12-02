"""This module defines the groups in Qtile"""

from enum import Enum
from libqtile.config import Group


class GroupName(Enum):
    """Enumerated group names"""

    MAIL = "mail"
    CHAT = "chat"
    TERM = "terminal"
    PERSONAL = "personal"
    TINKERING = "tinkering"
    DEV = "dev"
    CALL = "call"


groups = [Group(f"{ix+1}: {group.value}") for ix, group in enumerate(list(GroupName))]
