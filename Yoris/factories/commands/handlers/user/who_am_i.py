import contexts
from utils import database_manager, graphics, stats
from aiogram.types import BufferedInputFile
import datetime
from factories.commands.base import BaseCommand


class WhoAmICommand(BaseCommand):
    def __init__(self):
        self.user = None
        self.chat = None

    async def execute(self, ctx: contexts.MessageContext):
        buf = await graphics.get_chat_member_stats(self.user, self.chat, days=(datetime.date.today() - self.user.created_at.date()).days)
        buf.seek(0)
        photo = BufferedInputFile(buf.getvalue(), "image.png")
        text = await stats.get_user_info(self.user, self.chat)
        await ctx.reply_photo(photo, text)


class TerminalFriendlyWhoAmICommand(WhoAmICommand):
    factory_type = "command"
    prefix = ["who-am-i", "кто я", "профиль", "хто я"]

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        prefix = self.prefix_used(ctx)
        if not prefix:
            return False
        self.user = await database_manager.get_user(ctx.from_user.id)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True