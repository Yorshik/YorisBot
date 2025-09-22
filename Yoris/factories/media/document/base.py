import contexts


class DocumentBase:
    async def matches(self, ctx: contexts.FileContext):
        raise NotImplementedError()

    async def execute(self, ctx: contexts.FileContext):
        raise NotImplementedError()
