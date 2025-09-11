import aiogram
from typing import Type
from factories.middlewares.base import MiddlewareBase
from factory_base import Factory
from handlers.stats_middleware import StatsMiddleware
from handlers.update_middleware import UpdateMiddleware


class MiddlewareFactory(Factory):
    def __init__(self):
        self._middlewares = [UpdateMiddleware(), StatsMiddleware()]

        # self._auto_register("factories.middlewares.handlers", MiddlewareBase)

    def register(self, middleware: Type[MiddlewareBase]):
        self._middlewares.append(middleware())

    async def process(self, msg: aiogram.types.Message):
        for middleware in self._middlewares:
            await middleware.process(msg)
