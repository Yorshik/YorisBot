import aiogram


class CommandBase:
    async def matches(self, msg: aiogram.types.Message) -> bool:
        raise NotImplementedError

    async def execute(self, msg: aiogram.types.Message):
        raise NotImplementedError
