from aiogram.types import Message

from contexts.base_context import Context


class MessageContext(Context):
    def __init__(self, text=None, **kwargs):
        self.text = text
        super().__init__(**kwargs)

    @classmethod
    def from_message(cls, message: Message):
        ctx = super().from_message(message)
        ctx.text = message.text
        return ctx

