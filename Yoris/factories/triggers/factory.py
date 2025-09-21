from typing import Type
import contexts
from factories.factory_base import Factory
from factories.triggers.base import TriggerBase


class TriggerCreatorFactory(Factory):
    def __init__(self):
        self._triggers = []
        
        self._auto_register("factories.triggers.handlers.dynamic", TriggerBase, factory_type="trigger")
        self._auto_register("factories.triggers.handlers.static", TriggerBase, factory_type="trigger")

    def register(self, command: Type[TriggerBase]):
        self._triggers.append(command())

    async def handle(self, ctx: contexts.MessageContext):
        for trigger in self._triggers:
            if await trigger.matches(ctx):
                await trigger.execute(ctx)


class TriggerExecutorFactory(Factory):
    def __init__(self):
        self._triggers = []
        self._auto_register("factories.triggers.handlers.dynamic", TriggerBase, factory_type="executor")
        self._auto_register("factories.triggers.handlers.static", TriggerBase, factory_type="executor")

    def register(self, trigger: Type[TriggerBase]):
        self._triggers.append(trigger())

    async def handle(self, ctx: contexts.MessageContext):
        for trigger in self._triggers:
            if await trigger.matches(ctx):
                await trigger.execute(ctx)