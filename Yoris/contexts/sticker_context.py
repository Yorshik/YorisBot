from aiogram.types import Message

from contexts.base_context import Context, FileContext


class StickerContext(Context, FileContext):
    sticker_set: str
    emoji: str
    def __init__(self, message: Message):
        super().__init__(message)
        self.sticker_set = message.sticker_set
        self.emoji = message.emoji
