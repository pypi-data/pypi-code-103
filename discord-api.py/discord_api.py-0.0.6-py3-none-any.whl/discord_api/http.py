from aiohttp import ClientSession
from .gateway import DiscordGateway
from .command import Command
from .errors import *
from .role import Role
from .member import Member
from ujson import dumps

class Route:
    def __init__(self, method, route):
        self.method = method
        self.route = route

class DiscordRequest:
    def __init__(self, client):
        self.session = ClientSession(loop = client.loop, json_serialize = dumps)
        self.baseurl = "https://discord.com/api/v9"
        self.token = None
        self.client = client

    async def connect(self):
        uri = await self.get_ws_url()
        self.ws = await self.session.ws_connect(uri + "?v=9&encoding=json")
        await DiscordGateway.start_gateway(self.client, self.ws, self.token)

    def _token(self, token):
        self.token = token

    async def json_or_text(self, r):
        if r.headers["Content-Type"] == "application/json":
            return await r.json()

    async def get_ws_url(self):
        data = await self.request(Route("GET", "/gateway"))
        return data["url"]

    async def request(self, route:Route, *args, **kwargs):
        headers = {
            "Authorization": f"Bot {self.token}"
        }
        if kwargs.get("json"):
            headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers
        async with self.session.request(route.method, f"{self.baseurl}{route.route}", *args, **kwargs) as r:
            if r.status == 429:
                raise ApiError("Now api is limit. Wait a minute please.")
            return await self.json_or_text(r)

    async def static_login(self):
        data = await self.request(Route("GET", "/users/@me"))
        return data

    async def send_message(self, channelid, payload):
        await self.request(Route("POST", f"/channels/{channelid}/messages"), json = payload)

    async def slash_callback(self, interaction, payload):
        json = {
            "type": 4,
            "data": payload
        }
        return await self.request(Route("POST", f"/interactions/{interaction.id}/{interaction.token}/callback"), json = json)

    async def fetch_commands(self):
        return await self.request(Route("GET", f"/applications/{self.client.user.id}/commands"))

    async def add_command(self, command:Command):
        await self.request(Route("POST", f"/applications/{self.client.user.id}/commands"), json = command.to_dict())
        
    async def add_role(self, member:Member, role:Role):
        await self.request(Route("PUT", f"/guilds/{member.guild.id}/members/{member.id}/roles/{role.id}"))
