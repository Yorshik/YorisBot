import argparse
import datetime
from enum import FlagBoundary
import re
import shlex

import aiogram
from aiogram.types import ChatPermissions, MessageEntity, chat
from core.bot import bot
from factories.triggers.base import TriggerBase
from factories.triggers.handlers import trigger_checker
from utils import database_manager, parse_message


class TextTrigger(TriggerBase):
    def __init__(self):
        self.chat = None
        self.answer = None
        self.text = None
        self.type = "text"
        self.id = None

    async def matches(self, msg: aiogram.types.Message) -> bool:
        text = msg.text.strip()

        await trigger_checker.trigger(msg)

        print("trigger check")
        text = msg.text
        pattern = r'^trigger\s+-(a|r)\s+-type\s+"text"'

        not_found = re.search(pattern, text) is None

        if not_found:
            print("Не нашелся команда триггер")
            return False
        print("нашел")
        args = text[len("trigger") :].strip()
        parser = argparse.ArgumentParser(prog="trigger", add_help=False)

        group = parser.add_mutually_exclusive_group()
        group.add_argument("-a", action="store_true")
        group.add_argument("-r", action="store_true")
        parser.add_argument("-type", type=str, required=True)
        parser.add_argument("-outcome", type=str)
        parser.add_argument("-text", type=str)
        parser.add_argument("-id", type=int)
        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False

        self.chat = await database_manager.get_chat(msg.chat.id)
        self.text = parsed.text
        self.answer = parsed.outcome
        self.id = parsed.id if parsed.id else None

        extracted_user = await parse_message.extract_user(msg)

        if parsed.a:
            if self.answer is None:
                await msg.reply("даун на чё мне отвечать?")
                return False
            return True
        elif parsed.r and (
            await database_manager.check_trigger_id(self.chat, self.id)
            or await database_manager.check_trigger_bytext(self.chat, self.answer)
        ):

            await database_manager.delete_trigger(
                chat=self.chat, id=self.id, answer=self.answer
            )

            await msg.reply("команда удалена")
            return False

        return True

    async def execute(self, msg: aiogram.types.Message):
        await database_manager.text_trigger(
            chat=self.chat, text=self.text, answer=self.answer
        )

        await msg.reply("триггер был создан")
