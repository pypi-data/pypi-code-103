import random

from discord import CategoryChannel


async def _sort(self, *, key=None, reverse=False):
    payload = [
        {"id": channel.id, "position": index}
        for index, channel in enumerate(sorted(self.channels, key=key, reverse=reverse))
    ]

    await self._state.http.bulk_channel_update(self.guild.id, payload)


async def _alphabetize(self, *, reverse=False):
    await self.sort(key=lambda c: c.name, reverse=reverse)


async def _shuffle(self):
    await self.sort(key=lambda _: random.random())


CategoryChannel.sort = _sort
CategoryChannel.alphabetise = _alphabetize
CategoryChannel.alphabetize = _alphabetize
CategoryChannel.shuffle = _shuffle