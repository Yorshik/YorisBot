import argparse
import shlex
import datetime

import contexts
from utils import database_manager
from utils import parse_message
from factories.commands.base import CommandBase


class WarnCommand(CommandBase):
    def __init__(self):
        self.user = None
        self.author = None
        self.reason = None
        self.period = None
        self.chat = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text
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
        until_date = datetime.datetime.now() + datetime.timedelta(minutes=self.period)
        await database_manager.create_warn(
            chat=self.chat,
            author=self.author,
            user=self.user,
            until_date=until_date,
            reason=self.reason
        )
        answer_text = f"{self.user.name} gets a warn ({await database_manager.get_user_warn_count(self.user)}/{self.chat.warn_limit})\n"
        answer_text += f"Will be removed in {self.period} minutes\n"
        answer_text += f"Moderator: {self.author.name}\n"
        if self.reason:
            answer_text += f"Reason: {self.reason}"
        await ctx.reply(answer_text)


class UnWarnCommand(CommandBase):
    def __init__(self):
        self.user = None
        self.chat = None
        self.author = None
        self.numbers = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text
        if not text.startswith('unwarn'):
            return False
        args_str = text[len('unwarn'):].strip()
        parser = argparse.ArgumentParser(prog='unwarn', add_help=False)
        parser.add_argument('-user', required=True)
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-number', type=int)
        group.add_argument('--all', action='store_true')
        group.add_argument('-amount', type=int)
        try:
            parsed = parser.parse_args(shlex.split(args_str))
        except SystemExit:
            return False
        extracted_user = await parse_message.extract_user(ctx)
        self.user = await database_manager.get_user(extracted_user)
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        if parsed.number:
            self.numbers = [parsed.number]
        elif parsed.all:
            self.numbers = []
        elif parsed.amount:
            self.numbers = list(range(1, parsed.amount + 1))
        else:
            self.numbers = [-1]
        return True

    async def execute(self, ctx: contexts.MessageContext):
        deleted_warns = await database_manager.delete_warns(chat=self.chat, user=self.user, numbers=self.numbers)
        await ctx.reply(f"Deleted warns: {deleted_warns}.\nModerator: {self.author.name}")


class WarnPeriodCommand(CommandBase):
    def __init__(self):
        self.period = None
        self.chat = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text
        if not text.startswith('warn-period'):
            return False
        args = text[len("warn-period"):].strip()
        parser = argparse.ArgumentParser(prog='warn-period', add_help=False)
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

    async def execute(self, ctx: contexts.MessageContext):
        await database_manager.set_warn_period(self.chat, self.period)
        await ctx.reply("New default warn period: {} minutes".format(self.period))


class WarnLimitCommand(CommandBase):
    def __init__(self):
        self.limit = None
        self.chat = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text
        if not text.startswith('warn-limit'):
            return False
        args = text[len("warn-limit"):].strip()
        parser = argparse.ArgumentParser(prog='warn-limit', add_help=False)
        parser.add_argument("-limit", type=int, required=True)
        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        self.limit = parsed.limit
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True

    async def execute(self, ctx: contexts.MessageContext):
        await database_manager.set_warn_limit(self.chat, self.limit)


class WarnListCommand(CommandBase):
    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text
        return text.startswith("warn-list")

    async def execute(self, ctx: contexts.MessageContext):
        chat = await database_manager.get_chat(ctx.chat.id)
        warns = await database_manager.get_warns(chat)
        if not warns:
            await ctx.reply("No one is warned")
            return
        text = "Warns of this chat:\n\n"
        for warn in warns:
            text += f"{warn.warn_id}. {warn.user.name} is warned\n"
            text += f"Expires in {int((warn.until_date - datetime.datetime.now()).total_seconds() / 60)} minutes.\n"
            text += f"Warned by {warn.author.name}\n"
            if warn.reason:
                text += f"Reason: {warn.reason}\n"
            text += f"\n"
        await ctx.reply(text)


class WarnsCheckCommand(CommandBase):
    def __init__(self):
        self.user = None
        self.chat = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text
        if not text.startswith('warns-check'):
            return False
        args = text[len("warns-check"):].strip()
        parser = argparse.ArgumentParser(prog='warns-check', add_help=False)
        parser.add_argument("-user")
        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        if not parsed.user:
            print("I AM NOT PARSED")
            return False
        extracted_user = await parse_message.extract_user(ctx)
        user = await database_manager.get_user(extracted_user)
        chat = await database_manager.get_chat(ctx.chat.id)
        self.user = user
        self.chat = chat
        return True

    async def execute(self, ctx: contexts.MessageContext):
        warns = await database_manager.get_user_warns(self.chat, self.user)
        if not warns:
            await ctx.reply(f"{self.user.name} is not warned")
            return
        text = f"Warns of {self.user.name}:\n\n"
        for warn in warns:
            text += f"{warn.warn_id}. {warn.user.name}\n"
            text += f"Expires in {int((warn.until_date - datetime.datetime.now()).total_seconds() / 60)} minutes\n"
            text += f"Warned by {warn.author.name}\n"
            text += "\n"
        await ctx.reply(text)

