import aiogram
from aiogram.enums import ContentType

from factories.commands.factory import CommandFactory
from factory import MiddlewareFactory


class Dispatcher:
    def __init__(self):
        self.command_factory = CommandFactory()
        self.middleware_factory = MiddlewareFactory()

    async def dispatch(self, message: aiogram.types.Message, bot: aiogram.Bot):
        await self.middleware_factory.process(message, bot)

        if message.content_type == ContentType.TEXT:
            await self.command_factory.handle(message)
