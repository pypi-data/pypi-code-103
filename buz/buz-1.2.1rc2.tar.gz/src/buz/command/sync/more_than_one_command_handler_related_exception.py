from typing import Collection

from buz.command import Command, CommandHandler


class MoreThanOneCommandHandlerRelatedException(Exception):
    def __init__(self, command: Command, command_handlers: Collection[CommandHandler]):
        self.command = command
        self.command_handlers = command_handlers
        super().__init__(f"There is more than one handler registered for {command.fqn()}.")
