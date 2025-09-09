import aiogram


class MiddlewareBase:
    async def process(self, msg: aiogram.types.Message):
        raise NotImplementedError
