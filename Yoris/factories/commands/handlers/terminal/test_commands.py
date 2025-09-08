import aiogram

from factories.commands.base import CommandBase


# class TestCommand(CommandBase):
#     async def matches(self, msg: aiogram.types.Message) -> bool:
#         return True
#
#     async def execute(self, msg: aiogram.types.Message):
#         print(msg.entities)