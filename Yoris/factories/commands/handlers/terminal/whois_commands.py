import argparse
import shlex

import aiogram

import parse_message
from factories.commands.base import  CommandBase
from utils import database_manager


class WhoIsCommand(CommandBase):
    def __init__(self):
        self.user = None

    async def matches(self, msg: aiogram.types.Message):
        text = msg.text
        if not text.startswith("who-is"):
            return False

        args_str = text[len("who-is"):].strip()

        parser = argparse.ArgumentParser(prog="who-is", add_help=False)
        parser.add_argument("-user")
        parser.add_argument("--me", action="store_true")
        try:
            parsed = parser.parse_args(shlex.split(args_str))
        except SystemExit:
            return False
        print(parsed)
        if not any([parsed.me, parsed.user]) or all([parsed.me, parsed.user]):
            return False
        if parsed.user:
            extracted_user = await parse_message.extract_user(msg)
            print(f"{extracted_user=}")
            user = await database_manager.get_chat_member(extracted_user)
        else:
            user = await database_manager.get_chat_member(msg.from_user.id)
        self.user = user
        return True

    async def execute(self, msg: aiogram.types.Message):
        await msg.reply(f"Йоу, это упрощенное 'кто ты'. Посмотрим...\nid - {self.user.user.id}\nusername - {self.user.user.username}\n first name - {self.user.user.first_name}\nlast name - {self.user.user.last_name}")
