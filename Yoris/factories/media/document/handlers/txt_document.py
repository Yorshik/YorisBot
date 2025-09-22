import io

import database_manager
from factories.media.document.base import DocumentBase
import contexts
import decouple
from utils.i18n import translate as _

ADMIN_ID = decouple.config("ADMIN_ID", cast=int, default=5123114598)


class TxtDocument(DocumentBase):
    factory_type = "media/document"

    def __init__(self):
        self.author = None
        self.chat = None
        self.file = None
        self.caption = None

    async def matches(self, ctx: contexts.FileContext):
        if not (ctx.mime_type == "text/plain" or ctx.file_name.endswith(".txt")):
            return False
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.caption = ctx.caption
        if not((self.author.id == ADMIN_ID and self.caption != "not to execute") or (self.author.id != ADMIN_ID and self.caption == "to execute")):
            return False
        self.chat = await database_manager.get_chat(ctx.chat.id)
        self.file = await ctx.bot.download(ctx.file_id, destination=io.BytesIO())
        self.file.seek(0)
        return True

    async def execute(self, ctx: contexts.FileContext):
        from main import factory_dispatcher
        with io.TextIOWrapper(self.file, encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                from_user = contexts.base_context.User(
                    id=self.author.id,
                    username=self.author.username,
                    first_name=self.author.first_name,
                    last_name=self.author.last_name,
                    is_bot=False,
                )
                context = contexts.MessageContext(
                    text=line,
                    from_user=from_user,
                    chat=self.chat,
                    type=ctx.type,
                    bot=ctx.bot,
                    is_via_bot=False,
                )
                await factory_dispatcher.command_factory.handle(context)
                await factory_dispatcher.trigger_creator_factory.handle(context)
        await ctx.reply(_("All commands were executed.", ctx=ctx))
        self.file = io.BytesIO()
