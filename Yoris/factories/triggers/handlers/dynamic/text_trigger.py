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
        self.name = None

    async def execute(self, ctx: contexts.MessageContext):
        trigger = await database_manager.add_trigger(chat=self.chat, author=self.author, type="text",
                                                          mode="dynamic", is_enabled=None, text_income=self.income,
                                                          text_outcome=self.outcome, name=self.name)
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
        parser.add_argument("-name", type=str)
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
        if parsed.name:
            self.name = parsed.name
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
