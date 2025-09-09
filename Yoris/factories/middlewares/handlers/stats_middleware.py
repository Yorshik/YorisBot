import aiogram

from factories.middlewares.base import MiddlewareBase
from utils import database_manager


class StatsMiddleware(MiddlewareBase):
    async def process(self, msg: aiogram.types.Message):
        await database_manager.add_stats(msg)
