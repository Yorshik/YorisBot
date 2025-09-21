from factories.commands.base import BaseCommand
import contexts
from utils import database_manager, graphics
from aiogram.types import BufferedInputFile
import argparse
import shlex
import datetime


class MyStatsCommand(BaseCommand):
    def __init__(self):
        self.user = None
        self.chat = None
        self.days = None

    async def execute(self, ctx: contexts.MessageContext):
        buf = await graphics.get_chat_member_stats(self.user, self.chat, days=self.days)
        buf.seek(0)
        photo = BufferedInputFile(buf.getvalue(), "image.png")
        await ctx.reply_photo(photo)


class TerminalMyStatsCommand(MyStatsCommand):
    factory_type = "command"
    prefix = "my-stats"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        prefix = self.prefix_used(ctx)
        if not prefix:
            return False
        text = ctx.text
        args_str = text[len(prefix):].strip()
        parser = argparse.ArgumentParser(prog=prefix, add_help=False)
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
