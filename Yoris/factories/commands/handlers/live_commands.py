import contexts
from factories.commands.base import BaseCommand
from utils.i18n import translate as _

class LiveCommand(BaseCommand):
    command_text = None
    reply_text = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        if self.command_text is None:
            return False
        return ctx.text.lower() == self.command_text.lower()

    async def execute(self, ctx: contexts.MessageContext):
        if self.reply_text is None:
            raise NotImplementedError()
        await ctx.reply(_(self.reply_text))


class TerminalPingCommand(LiveCommand):
    command_text = 'ping'
    reply_text = 'PONG'
    factory_type = "command"


class FriendlyPingCommand(LiveCommand):
    command_text = 'пинг'
    reply_text = 'ПОНГ'
    factory_type = "command"


class TerminalKingCommand(LiveCommand):
    command_text = 'king'
    reply_text = 'KONG'
    factory_type = "command"


class FriendlyKingCommand(LiveCommand):
    command_text = 'кинг'
    reply_text = 'КОНГ'
    factory_type = "command"


class TerminalPewCommand(LiveCommand):
    command_text = 'pew'
    reply_text = 'POW'
    factory_type = "command"


class FriendlyPewCommand(LiveCommand):
    command_text = 'пиу'
    reply_text = 'ПАУ'
    factory_type = "command"


class TerminalBotCommand(LiveCommand):
    command_text = 'bot'
    reply_text = 'Present✅'
    factory_type = "command"


class FriendlyBotCommand(LiveCommand):
    command_text = 'бот'
    reply_text = 'На месте✅'
    factory_type = "command"
