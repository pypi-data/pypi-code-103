from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    NamedTuple,
    Sequence,
    Set,
    Literal,
    Optional,
    TYPE_CHECKING,
    Tuple,
    Union,
    overload,
)


from .types.guild import Guild as GuildPayload
from .types.channel import VoiceChannel, TextChannel, CategoryChannel

VocalGuildChannel = Union[VoiceChannel]
GuildChannel = Union[VoiceChannel, TextChannel, CategoryChannel]


class Guild:
    __slots__ = (
        'id',
        'name',
        'icon',
        'owner_id',
        'owner',
        'member_count',
        'max_members',
        'description',
        'joined_at',
        '_channels'
    )

    def __init__(self, data: GuildPayload):
        self._channels: Dict[int, GuildChannel] = {}
        self._from_data(data)

    def _from_data(self, guild: GuildPayload) -> None:
        # according to Stan, this is always available even if the guild is unavailable
        # I don't have this guarantee when someone updates the guild.
        self.id = guild.get('id')
        self.name = guild.get('name')
        self.icon = guild.get('icon')
        self.owner_id = guild.get('owner_id')
        self.owner = guild.get('owner')
        self.member_count = guild.get('member_count')
        self.max_members = guild.get('max_members')
        self.description = guild.get('description')
        self.joined_at = guild.get('joined_at')
