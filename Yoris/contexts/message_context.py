from aiogram.types import Message, ReactionTypeEmoji

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

    def reply(self, text, **kwargs):
        return self.bot.send_message(self.chat.id, text, reply_to_message_id=self.id, **kwargs)

    def reply_photo(self, photo, text=None, **kwargs):
        return self.bot.send_photo(self.chat.id, photo=photo, reply_to_message_id=self.id, caption=text, **kwargs)

    def answer(self, text, **kwargs):
        return self.bot.send_message(self.chat.id, text, **kwargs)

    def answer_dice(self, emoji=None, **kwargs):
        return self.bot.send_dice(self.chat.id, emoji=emoji, **kwargs)

    def send_reaction(self, emoji=None, **kwargs):
        return self.bot.set_message_reaction(self.chat.id, self.reply_to_message.message_id, reaction=[ReactionTypeEmoji(emoji=emoji)], **kwargs)
