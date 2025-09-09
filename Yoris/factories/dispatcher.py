import aiogram
from aiogram.enums import ContentType

from factories.commands.factory import CommandFactory
from factories.middlewares.factory import MiddlewareFactory


class Dispatcher:
    def __init__(self):
        self.command_factory = CommandFactory()
        self.middleware_factory = MiddlewareFactory()

    async def dispatch(self, message: aiogram.types.Message):
        await self.middleware_factory.process(message)

        if message.content_type == ContentType.TEXT:
            await self.command_factory.handle(message)
