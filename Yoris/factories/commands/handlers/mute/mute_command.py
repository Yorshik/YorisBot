import aiogram.exceptions

from factories.commands.base import BaseCommand
import contexts
from utils import database_manager, parse_message
import datetime
from aiogram.types import ChatPermissions
import argparse
import shlex
from utils.i18n import translate as _


class MuteCommand(BaseCommand):
    def __init__(self):
        self.author = None
        self.user = None
        self.chat = None
        self.period = None
        self.reason = None
        self.was_admin = None
        self.tg_admin_title = None
        
    async def execute(self, ctx: contexts.MessageContext):
        answer_text = _("{name} is muted for {period} minutes\n{reason_part}\nModerator: {moderator}", ctx=ctx, period=self.period, name=self.user.name, reason_part=f"Reason: {self.reason}" if self.reason else "", moderator=self.author.name)
        until_date = datetime.datetime.now() + datetime.timedelta(minutes=self.period)
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False
        )
        try:
            await ctx.bot.restrict_chat_member(self.chat.id, self.user.id, permissions=permissions, until_date=until_date)
        except aiogram.exceptions.TelegramBadRequest:
            await ctx.reply(_("I can't mute {name} because they are admin.", ctx, name=self.user.name))
        else:
            await ctx.reply(answer_text)
            await database_manager.create_mute(
                chat=self.chat,
                user=self.user,
                until_date=until_date,
                reason=self.reason,
                was_admin=self.was_admin,
                tg_admin_title=self.tg_admin_title
            )
        

class TerminalMuteCommand(MuteCommand):
    factory_type = "command"
    prefix = "mute"
    
    async def matches(self, ctx: contexts.MessageContext) -> bool:
        prefix = self.prefix_used(ctx)
        if not prefix:
            return False
        text = ctx.text
        args = text[len(prefix):].strip()
        parser = argparse.ArgumentParser(prog=prefix, add_help=False)
        parser.add_argument('-minutes', type=int)
        parser.add_argument('-hours', type=int)
        parser.add_argument('-days', type=int)
        parser.add_argument('-weeks', type=int)
        parser.add_argument('-months', type=int)
        parser.add_argument('-reason', type=str)
        parser.add_argument('-user')
        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        self.chat = await database_manager.get_chat(ctx.chat.id)
        if not any([parsed.minutes, parsed.hours, parsed.days, parsed.weeks, parsed.months]):
            period = await database_manager.get_mute_period(self.chat)
        else:
            period = 0
            if parsed.minutes:
                period = parsed.minutes
            if parsed.hours:
                period = parsed.hours * 60
            if parsed.days:
                period = parsed.days * 60 * 24
            if parsed.weeks:
                period = parsed.weeks * 60 * 24 * 7
            if parsed.months:
                period = parsed.months * 60 * 24 * 7 * 30
        extracted_user = await parse_message.extract_user(ctx)
        if not extracted_user:
            return False
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.user = await database_manager.get_user(extracted_user)
        self.reason = parsed.reason
        self.period = period
        member = await ctx.bot.get_chat_member(ctx.chat.id, ctx.from_user.id)
        self.was_admin = member.status in ("administrator", "creator")
        self.tg_admin_title = member.custom_title or ""
        return True
    