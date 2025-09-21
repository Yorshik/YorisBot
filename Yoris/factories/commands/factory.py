from typing import Type
from factories.commands.base import BaseCommand

from factories.factory_base import Factory


class CommandFactory(Factory):
    def __init__(self):
        self._commands = []

        self._auto_register("factories.commands.handlers", BaseCommand, factory_type="command")
        self._auto_register("factories.commands.handlers.cubes", BaseCommand, factory_type="command")
        self._auto_register("factories.commands.handlers.mute", BaseCommand, factory_type="command")
        self._auto_register("factories.commands.handlers.user", BaseCommand, factory_type="command")
        self._auto_register("factories.commands.handlers.warns", BaseCommand, factory_type="command")

    def register(self, command: Type[BaseCommand]):
        self._commands.append(command())

    async def handle(self, ctx):
        for command in self._commands:
            if await command.matches(ctx):
                print(ctx.text, command)
                await command.execute(ctx)
