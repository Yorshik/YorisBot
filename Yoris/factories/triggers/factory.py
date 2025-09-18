from typing import Type

import aiogram
from factories.factory_base import Factory
from factories.triggers.base import TriggerBase


class TriggerFactory(Factory):
    def __init__(self):
        self._triggers = []
        
        print("----------auto-register")
        self._auto_register("factories.triggers.handlers.terminal", TriggerBase)
        print("-----------registred")

    def register(self, command: Type[TriggerBase]):
        self._triggers.append(command())

    async def handle(self, msg: aiogram.types.Message):
        for trigger in self._triggers:
            if await trigger.matches(msg):
                await trigger.execute(msg)
