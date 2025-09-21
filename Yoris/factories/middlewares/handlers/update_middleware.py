import aiogram

from factories.middlewares.base import MiddlewareBase
from utils import database_manager


class UpdateMiddleware(MiddlewareBase):
    async def process(self, msg: aiogram.types.Message):
        await database_manager.update_user(msg)
        await database_manager.update_chat(msg)
        await database_manager.update_chat_member(msg, await msg.bot.get_chat_member(msg.chat.id, msg.from_user.id))
