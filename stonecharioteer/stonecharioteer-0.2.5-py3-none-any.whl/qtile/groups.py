"""This module defines the groups in Qtile"""

from enum import Enum
from libqtile.config import Group


class GroupName(Enum):
    """Enumerated group names"""

    WEB = "web"
    CHAT = "chat"
    TERM = "term"
    PERSONAL = "personal"
    DEV = "dev"
    TMP = "tmp"
    CALL = "call"


groups = [Group(f"{ix+1}: {group.value}") for ix, group in enumerate(list(GroupName))]
