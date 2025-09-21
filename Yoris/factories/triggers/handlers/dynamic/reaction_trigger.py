from factories.triggers.base import TriggerBase
from utils import database_manager
from utils.i18n import translate as _
import contexts
import argparse
import shlex


class AppendReactionTrigger(TriggerBase):
    def __init__(self):
        self.author = None
        self.chat = None
        self.emoji = None
        self.reaction_name = None
        self.name = None

    async def execute(self, ctx: contexts.MessageContext):
        trigger = await database_manager.add_trigger(chat=self.chat, author=self.author, type="reaction",
                                                     mode="dynamic", is_enabled=None, reaction_name=self.reaction_name,
                                                     reaction_emoji=self.emoji, name=self.name)
        await ctx.reply(_("Trigger was created by {author_name}\nTrigger id: {id}", ctx=ctx, author_name=self.author.name, id=trigger.id))


class TerminalAppendReactionTrigger(AppendReactionTrigger):
    factory_type = "trigger"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text.strip()
        if not text.startswith("append-trigger"):
            return False
        args = text[len("append-trigger"):].strip()
        parser = argparse.ArgumentParser(prog="append-trigger", add_help=False)
        parser.add_argument("-type", type=str, required=True)
        parser.add_argument("-reaction-name", type=str, required=True)
        parser.add_argument("-emoji", type=str, required=True)
        parser.add_argument("-name", type=str)
        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        if parsed.type != "reaction":
            return False
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        self.reaction_name = parsed.reaction_name
        self.emoji = parsed.emoji
        return True


class RemoveReactionTrigger(TriggerBase):
    def __init__(self):
        self.key = None
        self.chat = None

        # self.author = None

    async def execute(self, ctx: contexts.MessageContext):
        result = await database_manager.delete_trigger(chat=self.chat, id=self.key)
        if result:
            await ctx.reply(_("Trigger successfully was deleted"))
        else:
            await ctx.reply(_("Trigger was not deleted"))


class TerminalRemoveReactionTrigger(RemoveReactionTrigger):
    factory_type = "trigger"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text.strip()
        if not text.startswith("remove-trigger"):
            return False
        args = text[len("remove-trigger"):].strip()
        parser = argparse.ArgumentParser(prog="remove-trigger", add_help=False)
        parser.add_argument("-key", required=True)
        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        self.key = parsed.key
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True


class ExecutorReactionTrigger(TriggerBase):
    factory_type = "executor"

    def __init__(self, chat=None):
        self.chat = chat
        self.triggers = []
        self.trigger_to_execute = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        self.chat = await database_manager.get_chat(ctx.chat.id)
        self.triggers = await database_manager.get_triggers(chat=self.chat, type="reaction")
        text = ctx.text.strip().lower()
        for trigger in self.triggers:
            if trigger.reaction_name.lower() == text:
                self.trigger_to_execute = trigger
                return True
        self.trigger_to_execute = None
        return False

    async def execute(self, ctx: contexts.MessageContext):
        await ctx.send_reaction(self.trigger_to_execute.reaction_emoji)
