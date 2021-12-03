from typing import List, Optional

from buz.command import CommandBus, Command, CommandHandler
from buz.command.middleware import HandleMiddleware, HandleMiddlewareChainResolver
from buz.command.sync import MoreThanOneCommandHandlerRelatedException
from buz.locator import Locator


class SyncCommandBus(CommandBus):
    def __init__(
        self,
        locator: Locator[Command, CommandHandler],
        middlewares: Optional[List[HandleMiddleware]] = None,
    ):
        self.__locator = locator
        self.__handle_middleware_chain_resolver = HandleMiddlewareChainResolver(middlewares or [])

    def handle(self, command: Command) -> None:
        command_handlers = self.__locator.get(command)

        if len(command_handlers) > 1:
            raise MoreThanOneCommandHandlerRelatedException(command, command_handlers)

        command_handler = command_handlers[0]
        self.__handle_middleware_chain_resolver.resolve(command, command_handler, self.__perform_handle)

    def __perform_handle(self, command: Command, command_handler: CommandHandler) -> None:
        command_handler.handle(command)
