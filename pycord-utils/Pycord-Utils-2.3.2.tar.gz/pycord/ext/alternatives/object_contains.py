import discord
from discord.channel import CategoryChannel, DMChannel, TextChannel

if discord.version_info < (2, 0, 0):
    from discord.channel import VoiceChannel as VocalGuildChannel

else:
    from discord.channel import VocalGuildChannel

from discord.guild import Guild
from discord.member import Member
from discord.message import Message
from discord.role import Role
from discord.user import User, BaseUser


def _Guild__contains__(self, item):
    if hasattr(item, "guild"):
        return item.guild == self

    if isinstance(item, BaseUser):
        return item.id in self._members

    return False


Guild.__contains__ = _Guild__contains__


def _Role__contains__(self, item):
    if isinstance(item, User):
        item = self.guild._members.get(item.id)

    if isinstance(item, Member):
        return item._roles.has(self.id)

    return False


Role.__contains__ = _Role__contains__


def _TextChannel__contains__(self, item):
    if hasattr(item, "channel"):
        return item.channel == self

    if isinstance(item, User):
        item = self.guild._members.get(item.id)

    if isinstance(item, Member):
        return self.permissions_for(item).read_messages

    return False


TextChannel.__contains__ = _TextChannel__contains__


def _VocalGuildChannel__contains__(self, item):
    if isinstance(item, BaseUser) and item.id in self.voice_states:
        return True

    return False


VocalGuildChannel.__contains__ = _VocalGuildChannel__contains__


def _CategoryChannel__contains__(self, item):
    if hasattr(item, "category"):
        return item.category == self

    return False


CategoryChannel.__contains__ = _CategoryChannel__contains__


def _DMChannel__contains__(self, item):
    if hasattr(item, "channel"):
        return item.channel == self

    if isinstance(item, BaseUser):
        return item in (self.me, self.recipient)

    return False


DMChannel.__contains__ = _DMChannel__contains__