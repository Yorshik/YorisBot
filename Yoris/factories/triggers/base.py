import contexts


class TriggerBase:
    factory_type = None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        raise NotImplementedError

    async def execute(self, ctx: contexts.MessageContext):
        raise NotImplementedError
