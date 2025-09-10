import argparse
import datetime
import shlex

import aiogram
from aiogram.types import ChatPermissions
from aiogram.types import MessageEntity
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
        except SystemExit:
            return False
        self.chat = await database_manager.get_chat(msg.chat.id)
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
        extracted_user = await parse_message.extract_user(msg)
        self.author = await database_manager.get_user(msg.from_user.id)
        self.user = await database_manager.get_user(extracted_user)
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
        await database_manager.create_mute(self.chat, self.user, self.author, until_date)


class UnMuteCommand(CommandBase):
    def __init__(self):
        self.author = None
        self.user = None
        self.chat = None

    async def matches(self, msg: aiogram.types.Message) -> bool:
        text = msg.text
        if not text.startswith('unmute'):
            return False
        args = text[len("unmute"):].strip()
        parser = argparse.ArgumentParser(prog='unmute', add_help=False)
        parser.add_argument('-user', required=True)
        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        extracted_user = await parse_message.extract_user(msg)
        self.author = await database_manager.get_user(msg.from_user.id)
        self.user = await database_manager.get_user(extracted_user)
        self.chat = await database_manager.get_chat(msg.chat.id)
        return True

    async def execute(self, msg: aiogram.types.Message):
        await msg.reply(f"{self.user.name} unmuted.\nModerator: {self.author.name}")
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True
        )
        await bot.restrict_chat_member(self.chat.id, self.user.id, permissions=permissions)
        await database_manager.delete_mute(self.chat, self.user)


class MutePeriodCommand(CommandBase):
    def __init__(self):
        self.period = None
        self.chat = None

    async def matches(self, msg: aiogram.types.Message) -> bool:
        text = msg.text
        if not text.startswith('mute-period'):
            return False
        args = text[len("mute-period"):].strip()
        parser = argparse.ArgumentParser(prog='mute-period', add_help=False)
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
        self.chat = await database_manager.get_chat(msg.chat.id)
        return True

    async def execute(self, msg: aiogram.types.Message):
        await database_manager.set_mute_period(self.chat, self.period)
        await msg.reply("New default mute period: {} minutes".format(self.period))


class MutesCommand(CommandBase):
    async def matches(self, msg: aiogram.types.Message) -> bool:
        text = msg.text
        return text.startswith('mutes')

    async def execute(self, msg: aiogram.types.Message):
        chat = await database_manager.get_chat(msg.chat.id)
        mutes = await database_manager.get_mutes(chat)
        if not mutes:
            await msg.reply("No one is muted")
            return
        text = "Mutes of this chat:\n\n"
        for mute in mutes:
            text += f"{mute.user.name} is muted\n"
            text += f"Expires in {int((mute.until_date - datetime.datetime.now()).total_seconds() / 60)} minutes\n"
            text += f"Muted by {mute.author.name}\n"
            text += f"\n"
        await msg.reply(text)


class MuteCheckCommand(CommandBase):
    def __init__(self):
        self.user = None
        self.chat = None

    async def matches(self, msg: aiogram.types.Message) -> bool:
        text = msg.text
        if not text.startswith("mute-check"):
            return False
        args = text[len("mute-check"):].strip()
        parser = argparse.ArgumentParser(prog='mute-check', add_help=False)
        parser.add_argument('-user')
        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        if not parsed.user:
            return False
        extracted_user = await parse_message.extract_user(msg)
        user = await database_manager.get_user(extracted_user)
        chat = await database_manager.get_chat(extracted_user)
        self.user = user
        self.chat = chat
        return True

    async def execute(self, msg: aiogram.types.Message):
        mute = await database_manager.get_mute(chat=self.chat, user=self.user)
        if not mute:
            text = f"{self.user.name} is not muted"
            entities = [
                MessageEntity(
                    type="text_link",
                    offset=0,
                    length=len(self.user.name),
                    url=self.user.link,
                    disable_web_page_preview=True
                )
            ]
            await msg.reply(text, entities=entities)
            return
        text = ""
        text += f"{mute.user.name} is muted\n"
        text += f"Expires in {int((mute.until_date - datetime.datetime.now()).total_seconds() / 60)} minutes\n"
        text += f"Muted by {mute.author.name}"
        await msg.reply(text)