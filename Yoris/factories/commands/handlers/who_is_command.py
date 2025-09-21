from utils import parse_message, database_manager, graphics, stats
from factories.commands.base import BaseCommand
import contexts
import datetime
from aiogram.types import BufferedInputFile


class WhoIsCommand(BaseCommand):
    def __init__(self):
        self.user = None
        self.chat = None

    async def execute(self, ctx: contexts.MessageContext):
        buf = await graphics.get_chat_member_stats(self.user, self.chat, days=(datetime.date.today() - self.user.created_at.date()).days)
        buf.seek(0)
        photo = BufferedInputFile(buf.getvalue(), "image.png")
        text = await stats.get_user_info(self.user, self.chat)
        await ctx.reply_photo(photo, text)


class TerminalFriendlyWhoAmICommand(WhoIsCommand):
    factory_type = "command"
    prefix = ["who-is", "кто ты", "твой профиль", "хто ты"]

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        prefix = self.prefix_used(ctx)
        if not prefix:
            return False
        extracted_user = await parse_message.extract_user(ctx)
        if not extracted_user:
            return False
        self.user = await database_manager.get_user(extracted_user)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True
