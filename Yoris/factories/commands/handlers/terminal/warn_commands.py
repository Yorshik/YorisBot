import argparse
import shlex
import datetime

import contexts
from utils import database_manager
from utils import parse_message
import aiogram
from factories.commands.base import CommandBase


class WarnCommand(CommandBase):
    def __init__(self):
        self.user = None
        self.author = None
        self.reason = None
        self.period = None
        self.chat = None

    async def matches(self, msg: aiogram.types.Message) -> bool:
        text = msg.text
        if not text.startswith('warn'):
            return False
        args_str = text[len('warn'):].strip()
        parser = argparse.ArgumentParser(prog='warn', add_help=False)
        parser.add_argument('-user', required=True)
        parser.add_argument('-reason')
        parser.add_argument('-minutes', type=int)
        parser.add_argument('-hours', type=int)
        parser.add_argument('-days', type=int)
        parser.add_argument('-weeks', type=int)
        parser.add_argument('-months', type=int)
        try:
            parsed = parser.parse_args(shlex.split(args_str))
        except SystemExit:
            return False
        extracted_user = await parse_message.extract_user(ctx)
        self.user = await database_manager.get_user(extracted_user)
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        period = 0
        if parsed.minutes:
            period += parsed.minutes
        if parsed.hours:
            period += parsed.hours * 60
        if parsed.days:
            period += parsed.days * 60 * 24
        if parsed.weeks:
            period += parsed.weeks * 60 * 24 * 7
        if parsed.months:
            period += parsed.months * 60 * 24 * 7 * 30
        if not period:
            period = await database_manager.get_warn_period(self.chat)
        self.period = period
        self.reason = parsed.reason
        return True

    async def execute(self, ctx: contexts.MessageContext):
        answer_text = (
            f"{self.user.name} gets a warn"
            f" ({await database_manager.get_user_warn_count(self.user)}/{self.chat.warn_to_ban})\n"
        )
        answer_text += f"Will be removed in {self.period} minutes\n"
        answer_text += f"Moderator: {self.author.name}\n"
        if self.reason:
            answer_text += f"Reason: {self.reason}"
        await msg.reply(answer_text)
        until_date = datetime.datetime.now() + datetime.timedelta(minutes=self.period)
        await database_manager.create_warn(
            chat=self.chat,
            author=self.author,
            user=self.user,
            until_date=until_date,
            reason=self.reason
        )