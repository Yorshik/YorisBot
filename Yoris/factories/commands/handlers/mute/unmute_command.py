from factories.commands.base import BaseCommand
import contexts
from aiogram.types import ChatPermissions
from utils.i18n import translate as _
from utils import database_manager, parse_message
import shlex
import argparse


class UnMuteCommand(BaseCommand):
    def __init__(self):
        self.author = None
        self.user = None
        self.chat = None

    async def execute(self, ctx: contexts.MessageContext):
        await ctx.reply(_("{user_name} unmuted.\nModerator: {author_name}", ctx=ctx, author_name=self.author.name, user_name=self.user.name))
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
        await ctx.bot.restrict_chat_member(self.chat.id, self.user.id, permissions=permissions)
        await database_manager.delete_mute(self.chat, self.user)


class TerminalUnMuteCommand(UnMuteCommand):
    factory_type = "command"
    prefix = "unmute"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        prefix = self.prefix_used(ctx)
        if not prefix:
            return False
        text = ctx.text
        args = text[len(prefix):].strip()
        parser = argparse.ArgumentParser(prog=prefix, add_help=False)
        parser.add_argument('-user')
        try:
             parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        extracted_user = await parse_message.extract_user(ctx)
        if not extracted_user:
            return False
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.user = await database_manager.get_user(extracted_user)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True
