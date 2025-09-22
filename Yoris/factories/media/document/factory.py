from typing import Type
import contexts
from factories.factory_base import Factory
from factories.media.document.base import DocumentBase


class DocumentFactory(Factory):
    def __init__(self):
        self._documents = []

        self._auto_register("factories.media.document.handlers", DocumentBase, factory_type="media/document")

    def register(self, command: Type[DocumentBase]):
        self._documents.append(command())

    async def handle(self, ctx: contexts.MessageContext):
        for document in self._documents:
            if await document.matches(ctx):
                await document.execute(ctx)
