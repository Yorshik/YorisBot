import contexts
from factories.commands.base import CommandBase


class PingCommand(CommandBase):
    async def matches(self, ctx: contexts.MessageContext) -> bool:
        return ctx.text.lower() == "ping"

    async def execute(self, ctx: contexts.MessageContext):
        await ctx.reply("ПОНГ")


class PewCommand(CommandBase):
    async def matches(self, ctx: contexts.MessageContext) -> bool:
        return ctx.text.lower() == "pew"

    async def execute(self, ctx: contexts.MessageContext):
        await ctx.reply("Пау")


class KingCommand(CommandBase):
    async def matches(self, ctx: contexts.MessageContext) -> bool:
        return ctx.text.lower() == "king"

    async def execute(self, ctx: contexts.MessageContext):
        await ctx.reply("КОНГ")


class BotCommand(CommandBase):
    async def matches(self, ctx: contexts.MessageContext) -> bool:
        return ctx.text.lower() == "bot"

    async def execute(self, ctx: contexts.MessageContext):
        await ctx.reply("На месте")
