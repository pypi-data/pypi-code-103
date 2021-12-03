__all__ = ('Client',)

from typing import Optional
from .aiorequests import *
from .guild import Guild

URL = r'https://api.sgroup.qq.com'


class Client:
    def __init__(self, app_id: str, token: str):
        self.token = token
        self.app_id = app_id
        self.auth = {'Authorization': f'Bot {self.app_id}.{self.token}'}

    async def get_guild(self, guild_id: str) -> Optional[Guild]:
        r = await get(URL + f'/guilds/{guild_id}', headers=self.auth)
        return Guild(await r.json())

    async def get_all_guid(self) -> list[Guild]:
        r = await get(URL + '/users/@me/guilds', headers=self.auth)
        return [Guild(i) for i in await r.json()]
