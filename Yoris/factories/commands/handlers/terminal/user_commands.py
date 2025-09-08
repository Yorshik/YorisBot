import argparse

import aiogram
from aiogram.types import InputFile, FSInputFile, BufferedInputFile
import shlex
import database_manager
import graphics
from factories.commands.base import CommandBase


class MyStats(CommandBase):
    def __init__(self):
        self.user = None
        self.chat = None

    async def matches(self, msg: aiogram.types.Message) -> bool:
        text = msg.text
        if not text.startswith('my-stats'):
            return False
        args_str = text[len("my-stats"):].strip()
        parser = argparse.ArgumentParser()
        parser.add_argument('days', type=int)
        try:
            parsed_args = parser.parse_args(shlex.split(args_str))
        except SystemExit:
            return False
        days = 7
        if parsed_args.days:
            days = parsed_args.days
        self.days = days
        self.user = await database_manager.get_user(msg.from_user.id)
        self.chat = await database_manager.get_chat(msg.chat.id)
        return True

    async def execute(self, msg: aiogram.types.Message):
        buf = await graphics.get_chat_member_stats(self.user, self.chat, days=self.days)
        buf.seek(0)
        photo = BufferedInputFile(buf.getvalue(), "image.png")
        await msg.reply_photo(photo)
