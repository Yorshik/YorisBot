import argparse
import datetime
import shlex

import aiogram
from aiogram.types import ChatPermissions

import parse_message
from factories.commands.base import CommandBase
from utils import database_manager
from core.bot import bot


class MuteCommand(CommandBase):
    def __init__(self):
        self.author = None
        self.user = None
        self.chat = None
        self.period = None
        self.force = None
        self.reason = None

    async def matches(self, msg: aiogram.types.Message) -> bool:
        text = msg.text
        if not text.startswith('mute'):
            return False
        args = text[len("mute"):].strip()
        parser = argparse.ArgumentParser(prog='mute', add_help=False)
        parser.add_argument('-minutes', type=int)
        parser.add_argument('-hours', type=int)
        parser.add_argument('-days', type=int)
        parser.add_argument('-weeks', type=int)
        parser.add_argument('-months', type=int)
        parser.add_argument('-reason', type=str)
        parser.add_argument('--force', action='store_true')
        parser.add_argument('-user', required=True)
        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit as e:
            return False
        if not any([parsed.minutes, parsed.hours, parsed.days, parsed.weeks, parsed.months]):
            period = await database_manager.get_default_mute_period(msg.chat.id)
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
        extracted_user = await parse_message.extract_user(msg)
        self.author = await database_manager.get_user(msg.from_user.id)
        self.user = await database_manager.get_user(extracted_user)
        self.chat = await database_manager.get_chat(msg.chat.id)
        self.force = parsed.force
        self.reason = parsed.reason
        self.period = period
        return True

    async def execute(self, msg: aiogram.types.Message):
        answer_text = f"{self.user.name} is muted for {self.period} minutes\n"
        if self.reason:
            answer_text += f"Reason: {self.reason}\n"
        if self.force:
            answer_text += f"If this user is an admin - all his messages wil be deleted\n"
        answer_text += f"Moderator: {self.author.name}"
        await msg.reply(answer_text)
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
        await bot.restrict_chat_member(self.chat.id, self.user.id, permissions=permissions, until_date=until_date)
