from factories.commands.base import BaseCommand
import contexts
from utils import parse_message, database_manager
from aiogram.types import MessageEntity
from utils.i18n import translate as _
import datetime
import argparse
import shlex


class MuteCheckCommand(BaseCommand):
    def __init__(self):
        self.user = None
        self.chat = None

    async def execute(self, ctx: contexts.MessageContext):
        mute = await database_manager.get_mute(chat=self.chat, user=self.user)
        if not mute:
            text = _("{name} is not muted", ctx=ctx, name=self.user.name)
            entities = [
                MessageEntity(
                    type="text_link",
                    offset=0,
                    length=len(self.user.name),
                    url=self.user.link
                )
            ]
            await ctx.reply(text, entities=entities)
            return
        text = _(
            "{user_name} is muted\n"
            "Expires in {} minutes\n"
            "Muted by {author_name}",
            ctx=ctx,
            user_name=mute.user.name,
            author_name=mute.author.name,
            time=int((mute.until_date - datetime.datetime.now()).total_seconds() / 60),
        )
        await ctx.reply(text)


class TerminalMuteCheckCommand(BaseCommand):
    factory_type = "command"
    prefix = "mute-check"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        prefix = self.prefix_used(ctx)
        if not prefix:
            return False
        text = ctx.text
        if not text.startswith("mute-check"):
            return False
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
        user = await database_manager.get_user(extracted_user)
        chat = await database_manager.get_chat(ctx.chat.id)
        self.user = user
        self.chat = chat
        return True