import aiohttp
import asyncio
import json, sys
import importlib
from .utils import *
from .exception import ApiError
from threading import Thread

class Msg:
    def __init__(self, event):
        self.user_id = event['from_id']
        self.text = event['text']

class Ctx:
    def __init__(self, msg, bot):
        self.bot = bot
        self.message = msg

class Async_vk:
    def __init__(self, token, version = 5.131):
        # подключение к API
        self.token = token
        self.base_url = 'https://api.vk.com/method/'
        self.version = version

        # подключение к Longpool
        self.wait = 25
        self.key = None
        self.server = None
        self.ts = None

        # работа с командами
        self.events = []
        self.listeners = []
        self.commands = []
        self.__extensions = {}

    # методы для старта работы
    def run_bot(self, group_id):
        asyncio.run(self.update_bot_longpool(group_id))
        asyncio.run(self.start_loop())

    async def start_loop(self):
        self.loop = asyncio.get_event_loop()
        print('Ready')
        async for ctx in self.listen():
            self.dispatch(ctx)

    # базовые методы
    async def method(self, method_name, args = None):
        base_url = self.base_url + method_name
        params = {'access_token': self.token, 'v': self.version}
        if args:
            params = {**params, **args}

        async with aiohttp.ClientSession() as session:
            async with session.post(base_url, data = params) as resp:
                response = await resp.json()

                if 'error' in response.keys():
                    error = ApiError(method_name, {'error_msg': response, 'error_code': response["error"]["error_code"]})
                    raise error

                return response['response']

    async def send(self, peer_id, msg, keyboard = None, attachment = None):
        base_url = self.base_url + 'messages.send'
        params = {'access_token': self.token,
                    'v': self.version,
                    'user_id': peer_id,
                    'message': msg,
                    'random_id': get_random_id(),}
        if keyboard:
            params['keyboard'] = keyboard

        if attachment:
            params['attachment'] = attachment

        async with aiohttp.ClientSession() as session:
            async with session.post(base_url, data=params) as resp:
                print(await resp.json())

    # методы подключения и настройки сервера
    async def update_bot_longpool(self, group_id, update_ts=True):
        longpool = await self.method('groups.getLongPollServer', {'group_id': group_id})
        self.key = longpool['key']
        self.server = longpool['server']

        if update_ts:
            self.ts = longpool['ts']

        self.group_id = group_id

    async def check(self):
        """ Получить события от сервера один раз """

        values = {
            'act': 'a_check',
            'key': self.key,
            'ts': self.ts,
            'wait': self.wait,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.server, params = values, timeout=self.wait + 10) as resp:
                response = await resp.json()
                if 'failed' not in response:
                    self.ts = response['ts']
                    #{'user1' : ['event1', 'event2']}
                    new_events = [raw_event for raw_event in response['updates']]
                    new_events = filter(lambda event: event['type'] == 'message_new', new_events)
                    for event in new_events:
                        new_msg = Msg(event['object']['message'])
                        yield Ctx(new_msg, self)


                elif response['failed'] == 1:
                    self.ts = response['ts']

                elif response['failed'] == 2:
                    await self.update_bot_longpool(self.group_id, update_ts=False)

                elif response['failed'] == 3:
                    await self.update_bot_longpool()

    async def listen(self):
        """ Слушать сервер """

        while True:
            async for ctx in self.check():
                yield ctx

    async def wait_for(self, check, timeout = 60):
        future = self.loop.create_future()
        self.listeners.append((future, check))
        return await asyncio.wait_for(future, timeout)

    def dispatch(self, ctx):
        # dispatch new event for listeners if has
        for listener in self.listeners:
            if not listener[0].cancelled():
                if listener[1](ctx):
                    listener[0].set_result(ctx)
                    self.listeners.remove(listener)
                    return

        # else if no listeners
        asyncio.create_task(self.on_message(ctx))

    # методы работы команд
    async def on_message(self, ctx):
        for command in self.commands:
            text_command = ctx.message.text.lower()
            if text_command.startswith(command['name']):
                await command['execute'](ctx)

    def command(self, name):
        def decorator(fn):
            new_command = {
                'execute': fn,
                'name': name
            }
            def wrapper(ctx):
                fn(ctx)

            self.commands.append(new_command)
            return wrapper
        return decorator

    def add_cog(self, cog):
        self.commands += cog.commands

    def get_command(self, name):
        for command in self.commands:
            if command['name'] == name:
                return command
        print(f'No command name {name}')
        return

    #работа с когами
    def load_extension(self, name, *, package = None):
        name = self._resolve_name(name, package)
        if name in self.__extensions:
            print(f'Error Extension Already Loaded {name}')
            return

        spec = importlib.util.find_spec(name)
        if spec is None:
            print(f'Error Extension Not Found {name}')
            return

        self._load_from_module_spec(spec, name)

    def _resolve_name(self, name, package):
        try:
            return importlib.util.resolve_name(name, package)
        except ImportError:
            print(f'Error Extension Not Found {name}')
            return

    def _load_from_module_spec(self, spec, key):
        # precondition: key not in self.__extensions
        lib = importlib.util.module_from_spec(spec)
        sys.modules[key] = lib
        try:
            spec.loader.exec_module(lib)
        except Exception as e:
            del sys.modules[key]
            print(f'ExtensionFailed {key}\n{e}')
            return

        try:
            setup = getattr(lib, 'setup')
        except AttributeError:
            del sys.modules[key]
            print(f'NoEntryPointError {key}')
            return

        try:
            setup(self)
        except Exception as e:
            del sys.modules[key]
            self._remove_module_references(lib.__name__)
            self._call_module_finalizers(lib, key)
            print(f'ExtensionFailed {key}\n{e}')
            return
        else:
            self.__extensions[key] = lib
