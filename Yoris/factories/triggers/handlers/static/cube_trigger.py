from factories.triggers.base import TriggerBase
from utils import database_manager, parse_command
from utils.i18n import translate as _
import contexts
import argparse
import shlex


class EnableCubeTrigger(TriggerBase):
    def __init__(self):
        self.author = None
        self.chat = None
        self.reaction = None

    async def execute(self, ctx: contexts.MessageContext):
        trigger = await database_manager.enable_or_create_trigger(
            chat=self.chat,
            type="cube",
            author=self.author,
            mode="static",
            is_enabled=True,
            cube_reaction=self.reaction
        )
        await ctx.reply(
            _("Cube trigger was enabled by {author_name}\nTrigger id: {id}",
              ctx=ctx, author_name=self.author.name, id=trigger.id)
        )


class TerminalEnableCubeTrigger(EnableCubeTrigger):
    factory_type = "trigger"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text.strip()
        if not text.startswith("enable-trigger"):
            return False
        args = text[len("enable-trigger"):].strip()
        parser = argparse.ArgumentParser(prog="enable-trigger", add_help=False)
        parser.add_argument("-reaction", type=str, nargs="?", required=True)
        parser.add_argument("-type", type=str, required=True)
        try:
            parsed = parser.parse_args(parse_command.split_enable_trigger_args(args))
        except SystemExit:
            return False
        if parsed.type != "cube":
            return False
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        self.reaction = parsed.reaction
        return True


class DisableCubeTrigger(TriggerBase):
    def __init__(self):
        self.key = None
        self.chat = None

    async def execute(self, ctx: contexts.MessageContext):
        result = await database_manager.disable_trigger(chat=self.chat, key=self.key)
        if result:
            await ctx.reply(_("Cube trigger was disabled"))
        else:
            await ctx.reply(_("Cube trigger was not found"))


class TerminalDisableCubeTrigger(DisableCubeTrigger):
    factory_type = "trigger"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text.strip()
        if not text.startswith("disable-trigger"):
            return False

        args = text[len("disable-trigger"):].strip()
        parser = argparse.ArgumentParser(prog="disable-trigger", add_help=False)
        parser.add_argument("-key", type=str)

        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False

        self.key = parsed.key or parsed.name
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True
