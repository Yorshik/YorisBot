import argparse
import shlex

import contexts
from utils import parse_message
from factories.commands.base import  CommandBase
from utils import database_manager


class WhoIsCommand(CommandBase):
    def __init__(self):
        self.user = None

    async def matches(self, ctx: contexts.MessageContext):
        text = ctx.text
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
            extracted_user = await parse_message.extract_user(ctx)
            print(f"{extracted_user=}")
            user = await database_manager.get_chat_member(extracted_user)
        else:
            user = await database_manager.get_chat_member(ctx.from_user.id)
        self.user = user
        return True

    async def execute(self, ctx: contexts.MessageContext):
        await ctx.reply(f"Йоу, это упрощенное 'кто ты'. Посмотрим...\nid - {self.user.user.id}\nusername - {self.user.user.username}\n first name - {self.user.user.first_name}\nlast name - {self.user.user.last_name}")


class WhatIsCommand(CommandBase):
    def __init__(self):
        self.chat = None

    async def matches(self, ctx: contexts.MessageContext):
        text = ctx.text
        if not text.startswith("what-is"):
            return False
        args_str = text[len("what-is"):].strip()
        parser = argparse.ArgumentParser(prog="what-is", add_help=False)
        parser.add_argument("-chat")
        parser.add_argument("--this", action="store_true")
        try:
            parsed = parser.parse_args(shlex.split(args_str))
        except SystemExit:
            return False
        if not any([parsed.chat, parsed.this]) or all([parsed.chat, parsed.this]):
            return False
        if parsed.chat:
            extracted_chat = await parse_message.extract_chat(ctx)
            chat = await database_manager.get_chat(extracted_chat)
        else:
            chat = await database_manager.get_chat(ctx.chat.id)
        self.chat = chat
        return True

    async def execute(self, ctx: contexts.MessageContext):
        await ctx.reply(f"Йоу, это упрощенное 'чат инфо'. Посмотрим...\nid - {self.chat.id}\nusername - {self.chat.username}\nname - {self.chat.chat_name}")