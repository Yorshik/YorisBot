import aiogram

from factories.commands.base import CommandBase


class PingCommand(CommandBase):
    async def matches(self, msg: aiogram.types.Message) -> bool:
        return msg.text.lower() == "ping"

    async def execute(self, msg: aiogram.types.Message):
        await msg.reply("ПОНГ")


class PewCommand(CommandBase):
    async def matches(self, msg: aiogram.types.Message) -> bool:
        return msg.text.lower() == "pew"

    async def execute(self, msg: aiogram.types.Message):
        await msg.reply("Пау")


class KingCommand(CommandBase):
    async def matches(self, msg: aiogram.types.Message) -> bool:
        return msg.text.lower() == "king"

    async def execute(self, msg: aiogram.types.Message):
        await msg.reply("КОНГ")


class BotCommand(CommandBase):
    async def matches(self, msg: aiogram.types.Message) -> bool:
        return msg.text.lower() == "bot"

    async def execute(self, msg: aiogram.types.Message):
        await msg.reply("На месте")
