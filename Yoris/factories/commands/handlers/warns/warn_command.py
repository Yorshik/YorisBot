from factories.commands.base import BaseCommand
from utils.i18n import translate as _
import contexts
import argparse
import shlex
from utils import parse_message, database_manager
import datetime


class WarnCommand(BaseCommand):
    def __init__(self):
        self.user = None
        self.author = None
        self.reason = None
        self.period = None
        self.chat = None

    async def execute(self, ctx: contexts.MessageContext):
        answer_text = _(
            "{user_name} gets a warn ({warn_count}/{warn_to_ban})\nWill be removed in {period} minutes\nModerator: {author_name}\n{reason_part}",
            ctx=ctx,
            user_name=self.user.name,
            warn_count=await database_manager.get_user_warn_count(self.user),
            warn_to_ban=self.chat.warn_to_ban,
            period=self.period,
            author_name=self.author.name,
            reason_part=f"Reason: {self.reason}" if self.reason else "",
        )
        await ctx.reply(answer_text)
        until_date = datetime.datetime.now() + datetime.timedelta(minutes=self.period)
        await database_manager.create_warn(
            chat=self.chat,
            author=self.author,
            user=self.user,
            until_date=until_date,
            reason=self.reason
        )


class TerminalWarnCommand(BaseCommand):
    factory_type = "command"
    prefix = "warn"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        prefix = self.prefix_used(ctx)
        if not prefix:
            return False
        text = ctx.text
        args_str = text[len(prefix):].strip()
        parser = argparse.ArgumentParser(prog=prefix, add_help=False)
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
        if not extracted_user:
            return False
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
