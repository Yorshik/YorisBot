import aiogram.types
from aiogram.enums import ContentType
from factories.commands.factory import CommandFactory
from factories.middlewares.factory import MiddlewareFactory
import contexts
from factories.triggers.factory import TriggerCreatorFactory, TriggerExecutorFactory


class Dispatcher:
    def __init__(self):

        self.command_factory = CommandFactory()
        self.middleware_factory = MiddlewareFactory()
        self.trigger_creator_factory = TriggerCreatorFactory()
        self.trigger_executor_factory = TriggerExecutorFactory()

    async def dispatch(self, message: aiogram.types.Message):
        context = self.message_convert_to_context(message)
        await self.middleware_factory.process(message)
        if context.type == ContentType.TEXT:
            await self.command_factory.handle(context)
            await self.trigger_creator_factory.handle(context)
            await self.trigger_executor_factory.handle(context)

    def message_convert_to_context(self, message: aiogram.types.Message):
        if message.content_type == ContentType.TEXT:
            return contexts.MessageContext.from_message(message)
        if message.content_type == ContentType.PHOTO or message.content_type == ContentType.AUDIO or message.content_type == ContentType.VIDEO or message.content_type == ContentType.DOCUMENT or message.content_type == ContentType.ANIMATION:
            return contexts.FileContext(message)
        if message.content_type == ContentType.STICKER:
            return contexts.StickerContext(message)
        if message.content_type == ContentType.LEFT_CHAT_MEMBER:
            return contexts.ChatMemberLeftContext(message)
        if message.content_type == ContentType.NEW_CHAT_MEMBERS:
            return contexts.NewChatMembersContext(message)
        if message.content_type == ContentType.PINNED_MESSAGE:
            return contexts.PinnedMessageContext(message)
        if message.content_type == ContentType.DICE:
            return contexts.DiceContext(message)

