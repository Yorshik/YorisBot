from factories.triggers.base import TriggerBase
from utils import database_manager
from utils.i18n import translate as _
import contexts
import argparse
import shlex


class AppendTextTrigger(TriggerBase):
    def __init__(self):
        self.author = None
        self.chat = None
        self.outcome = None
        self.income = None

    async def execute(self, ctx: contexts.MessageContext):
        trigger = await database_manager.add_trigger(chat=self.chat, author=self.author, type="text",
                                                          mode="dynamic", is_enabled=None, text_income=self.income,
                                                          text_outcome=self.outcome)
        await ctx.reply(_("Trigger was created by {author_name}\nTrigger id: {id}", ctx=ctx, author_name=self.author.name, id=trigger.id))


class TerminalAppendTextTrigger(AppendTextTrigger):
    factory_type = "trigger"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        text = ctx.text.strip()
        if not text.startswith("append-trigger"):
            return False
        args = text[len("append-trigger"):].strip()
        parser = argparse.ArgumentParser(prog="append-trigger", add_help=False)
        parser.add_argument("-type", type=str, required=True)
        parser.add_argument("-outcome", type=str, required=True)
        parser.add_argument("-income", type=str, required=True)
        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        if parsed.type != "text":
            return False
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        self.income = parsed.income
        self.outcome = parsed.outcome
        return True


class RemoveTextTrigger(TriggerBase):
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


class TerminalRemoveTextTrigger(RemoveTextTrigger):
    factory_type = "trigger"

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


class ExecutorTextTrigger(TriggerBase):
    factory_type = "executor"

    def __init__(self, chat=None):
        self.chat = chat
        self.triggers = []
        self.trigger_to_execute = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        self.chat = await database_manager.get_chat(ctx.chat.id)
        self.triggers = await database_manager.get_triggers(chat=self.chat, type="text")
        text = ctx.text.strip().lower()
        for trigger in self.triggers:
            if trigger.text_income.lower() == text:
                self.trigger_to_execute = trigger
                return True
        self.trigger_to_execute = None
        return False

    async def execute(self, ctx: contexts.MessageContext):
        await ctx.reply(self.trigger_to_execute.text_outcome)
