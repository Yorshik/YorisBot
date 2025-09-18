from typing import Type
from factories.commands.base import CommandBase

from factories.factory_base import Factory


class CommandFactory(Factory):
    def __init__(self):
        self._commands = []

        self._auto_register("factories.commands.handlers.friendly", CommandBase)
        self._auto_register("factories.commands.handlers.terminal", CommandBase)

    def register(self, command: Type[CommandBase]):
        self._commands.append(command())

    async def handle(self, ctx):
        for command in self._commands:
            if await command.matches(ctx):
                await command.execute(ctx)
