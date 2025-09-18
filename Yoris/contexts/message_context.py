from aiogram.types import Message

from contexts.base_context import Context


class MessageContext(Context):
    def __init__(self, message: Message):
        super().__init__(message)
        self.text = message.text

    def reply(self, text, **kwargs):
        return self.bot.send_message(self.chat.id, text, reply_to_message_id=self.id, **kwargs)

    def reply_photo(self, photo, text=None, **kwargs):
        return self.bot.send_photo(self.chat.id, photo=photo, reply_to_message_id=self.id, caption=text, **kwargs)

    def answer(self, text, **kwargs):
        return self.bot.send_message(self.chat.id, text, **kwargs)

    def answer_dice(self, emoji=None, **kwargs):
        return self.bot.send_dice(self.chat.id, emoji=emoji, **kwargs)