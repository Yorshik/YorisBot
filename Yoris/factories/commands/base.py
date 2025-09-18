import contexts

class CommandBase:
    async def matches(self, ctx: contexts.MessageContext) -> bool:
        raise NotImplementedError

    async def execute(self, ctx: contexts.MessageContext):
        raise NotImplementedError
