from utils.i18n import translate as _
from factories.triggers.base import TriggerBase
import contexts
import argparse
import shlex
from utils import database_manager


class TerminalRemoveTrigger(TriggerBase):
    factory_type = "trigger"
    def __init__(self):
        self.key = None
        self.chat = None

        # self.author = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text.strip()
        if not text.startswith("remove-trigger"):
            return False
        args = text[len("remove-trigger"):].strip()
        parser = argparse.ArgumentParser(prog="remove-trigger", add_help=False)
        parser.add_argument("-key", type=int, required=True)
        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        self.key = parsed.key
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True

    async def execute(self, ctx: contexts.MessageContext):
        result = await database_manager.delete_trigger(chat=self.chat, key=self.key)
        if result:
            await ctx.reply(_("Trigger successfully was deleted"))
        else:
            await ctx.reply(_("Trigger was not deleted"))
