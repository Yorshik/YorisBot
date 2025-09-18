from aiogram.types import Message

from contexts.base_context import Context


class DiceContext(Context):
    def __init__(self, message: Message):
        super().__init__(message)
        self.emoji = message.dice.emoji
        self.value = message.dice.value
