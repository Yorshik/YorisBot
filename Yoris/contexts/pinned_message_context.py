from aiogram.types import Message
from contexts.base_context import Context
from contexts.message_context import MessageContext


class PinnedMessageContext(Context):
    def __init__(self, message: Message):
        super().from_message(message)
        self.pinned_message = MessageContext(message.pinned_message)
