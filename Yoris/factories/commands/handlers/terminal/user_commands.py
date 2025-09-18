import argparse
import datetime
import contexts
from aiogram.types import BufferedInputFile
import shlex
from utils import database_manager
from utils import graphics
from factories.commands.base import CommandBase


class MyStats(CommandBase):
    def __init__(self):
        self.user = None
        self.chat = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text
        if not text.startswith('my-stats'):
            return False
        args_str = text[len("my-stats"):].strip()
        parser = argparse.ArgumentParser()
        parser.add_argument('-days', type=int)
        parser.add_argument('-weeks', type=int)
        parser.add_argument('-months', type=int)
        parser.add_argument("--all", action="store_true")
        try:
            parsed_args = parser.parse_args(shlex.split(args_str))
        except SystemExit:
            return False
        self.user = await database_manager.get_user(ctx.from_user.id)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        if parsed_args.all:
            days = (datetime.date.today() - self.user.created_at.date()).days
        else:
            days = 0
            if parsed_args.days:
                days += parsed_args.days
            if parsed_args.weeks:
                days += parsed_args.weeks * 7
            if parsed_args.months:
                days += parsed_args.months * 30
        if not days:
            days = 7
        self.days = days
        return True

    async def execute(self, ctx: contexts.MessageContext):
        buf = await graphics.get_chat_member_stats(self.user, self.chat, days=self.days)
        buf.seek(0)
        photo = BufferedInputFile(buf.getvalue(), "image.png")
        await ctx.reply_photo(photo)
