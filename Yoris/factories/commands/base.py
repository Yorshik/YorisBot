import contexts

class BaseCommand:
    factory_type = None
    prefix = None

    def prefix_used(self, ctx: contexts.MessageContext):
        if self.prefix is None:
            raise NotImplementedError
        if isinstance(self.prefix, str):
            if ctx.text.startswith(self.prefix):
                return self.prefix
        if isinstance(self.prefix, list):
            for prefix in self.prefix:
                if ctx.text.startswith(prefix):
                    return prefix
        return None

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        raise NotImplementedError

    async def execute(self, ctx: contexts.MessageContext):
        raise NotImplementedError
