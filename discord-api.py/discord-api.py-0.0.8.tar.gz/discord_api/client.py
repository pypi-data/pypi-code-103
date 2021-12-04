from .http import DiscordRequest
from uvloop import install
import asyncio
from .command import Command
from .clientuser import ClientUser
from typing import Optional, List
from .guild import Guild

class Client:
    def __init__(self, loop:asyncio.AbstractEventLoop = None, log:bool = True) -> None:
        """
        This can setup a discordbot.

        Args:
            loop (asyncio.AbstractEventLoop)
            log (bool)

        Returns:
            Client (class)

        Examples:
            from discord_api import Client
            client = Client()
        """
        install()
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.http = DiscordRequest(self)
        self.guilds = []
        self.commands = []
        self.log = log

    def dispatch(self, eventname, *args, **kwargs):
        name = "on_" + eventname
        if hasattr(self, name):
            coro = getattr(self, name)
            try:
                self.loop.create_task(coro(*args, **kwargs))
            except:
                pass

    def print(self, name, content):
        """
        This is print a like sanic log
        
        Examples:
            client.print("test", "this is test")
        """
        if self.log is True:
            print(f"[{name}]:{content}")

    async def connect(self) -> None:
        """
        This can connect to discord gateway.
        But if you want to use this, you need to use `await client.login()`
        """
        await self.http.connect()

    async def login(self) -> None:
        """
        This can login to discord api.
        """
        self.user = ClientUser.from_dict(await self.http.static_login())

    async def start(self, token):
        """
        This can run a discord client.
        """
        self.print("START", "Now starting...")
        self.http._token(token)
        await self.login()
        await self.setup_command()
        await self.connect()
    
    def run(self, token):
        """
        This can run a discord client.

        Examples:
            client = Client()
            client.run("ToKeN")
        """
        self.loop.run_until_complete(self.start(token))

    def event(self, coro):
        """
        This is send gateway event.

        Examples:
            client = Client()
        
            @client.event
            async def on_ready():
                print("ready")

            client.run("ToKeN")
        """
        setattr(self, coro.__name__, coro)
        return coro

    def get_guild(self, _id:int) -> Optional[Guild]:
        guild = None
        for guild in self.guilds:
            if _id == guild.id:
                break
        return guild

    async def fetch_commands(self) -> List[Command]:
        """
        This can fetch discord application commands from discord api.
        """
        datas = await self.http.fetch_commands()
        return [Command.from_dict(data) for data in datas]

    def get_channel(self, _id:int):
        channel = None
        for guild in self.guilds:
            for channel in guild.text_channels:
                if _id == channel.id:
                    break
        return channel

    async def setup_command(self):
        """
        set up a application command.
        """
        apis = await self.fetch_commands()
        for command in self.commands:
            update = False
            for api in apis:
               if api.name == command.name:
                   break
            else:
                update = True
            if update:
                data = await self.http.add_command(command)

    def add_command(self, command:Command) -> None:
        """
        This can add discord application commannd.

        Examples:
            from discord_api import Client, Command

            client = Client()
            client.add_command(Command(name = "ping", description = "pong"))
        
            client.run("ToKeN")
        """
        self.commands.append(command)
