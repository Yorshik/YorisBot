from factories.commands.base import BaseCommand
import contexts
from utils import database_manager
from utils.i18n import translate as _
import argparse
import shlex


class MutePeriodCommand(BaseCommand):
    def __init__(self):
        self.period = None
        self.chat = None

    async def execute(self, ctx: contexts.MessageContext):
        await database_manager.set_mute_period(self.chat, self.period)
        await ctx.reply(_("New default mute period: {period} minutes", ctx=ctx, period=self.period))


class TerminalMutePeriodCommand(MutePeriodCommand):
    factory_type = "command"
    prefix = "mute-period"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        prefix = self.prefix_used(ctx)
        if not prefix:
            return False
        text = ctx.text
        args = text[prefix:].strip()
        parser = argparse.ArgumentParser(prog=prefix, add_help=False)
        parser.add_argument('-minutes', type=int)
        parser.add_argument('-hours', type=int)
        parser.add_argument('-days', type=int)
        parser.add_argument('-weeks', type=int)
        parser.add_argument('-months', type=int)
        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        self.period = 0
        if parsed.minutes:
            self.period += parsed.minutes
        if parsed.hours:
            self.period += parsed.hours * 60
        if parsed.days:
            self.period += parsed.days * 60 * 24
        if parsed.weeks:
            self.period += parsed.weeks * 60 * 24 * 7
        if parsed.months:
            self.period += parsed.months * 60 * 24 * 7 * 30
        if not self.period:
            return False
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True
