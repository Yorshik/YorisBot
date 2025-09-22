import aiogram
from aiogram.types import ReactionTypeEmoji


class User:
    def __init__(self, id=None, is_bot=None, first_name=None, last_name=None, username=None):
        self.id = id
        self.is_bot = is_bot
        self.first_name = first_name
        self.last_name = last_name
        self.username = username

    @classmethod
    def from_message(cls, user: aiogram.types.User):
        obj = cls()
        obj.id = user.id
        obj.is_bot = user.is_bot
        obj.first_name = user.first_name
        obj.last_name = user.last_name
        obj.username = user.username
        return obj

    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return f"{self.username}"


class Chat:
    def __init__(self, id=None, type=None, title=None, username=None, first_name=None, last_name=None, is_direct=None):
        self.id = id
        self.type = type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.is_direct = is_direct
        
    @classmethod
    def from_message(cls, chat: aiogram.types.Chat):
        obj = cls()
        obj.id = chat.id
        obj.type = chat.type
        obj.title = chat.title
        obj.username = chat.username
        obj.first_name = chat.first_name
        obj.last_name = chat.last_name
        obj.is_direct = chat.is_direct_messages
        return obj


class Context:
    def __init__(self, type=None, id=None, from_user=None, chat=None, reply_to_message=None, quote=None, is_via_bot=None, via_bot=None, edit_date=None, entities=None, bot=None):
        self.type = type
        self.id = id
        self.from_user = from_user
        self.chat = chat
        self.reply_to_message = reply_to_message
        self.quote = quote
        self.is_via_bot = is_via_bot
        self.via_bot = via_bot
        self.edit_date = edit_date
        self.entities = entities
        self.bot: aiogram.Bot = bot

    @classmethod
    def from_message(cls, message: aiogram.types.Message):
        obj = cls()
        obj.type = message.content_type
        obj.id = message.message_id
        obj.from_user = User.from_message(message.from_user)
        obj.chat = Chat.from_message(message.chat)
        obj.reply_to_message = message.reply_to_message
        obj.quote = message.quote.text if message.quote else None
        obj.is_via_bot = bool(message.via_bot)
        obj.via_bot = message.via_bot.id if obj.is_via_bot else None
        obj.edit_date = message.edit_date
        obj.entities = message.entities
        obj.bot = message.bot
        return obj

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

class FileContext(Context):
    def __init__(self, file=None, caption=None, **kwargs):
        super().__init__(**kwargs)
        self.caption = caption
        if file:
            self.file_id = file.file_id
            self.file_unique_id = file.file_unique_id
            self.file_size = file.file_size
            self.mime_type = file.mime_type
            self.file_name = file.file_name
            if not isinstance(file, aiogram.types.Document):
                self.width = file.width
                self.height = file.height
            if not isinstance(file, aiogram.types.Document) and not isinstance(file, aiogram.types.PhotoSize) and not isinstance(file, aiogram.types.Sticker):
                self.duration = file.duration


    @classmethod
    def from_message(cls, message: aiogram.types.Message):
        obj = super().from_message(message)
        obj.caption = message.caption
        file = (
                message.document or
                message.audio or
                message.video or
                message.animation or
                (message.photo[-1] if message.photo else None) or
                message.sticker
        )
        if file:
            obj.file_id = file.file_id
            obj.file_unique_id = file.file_unique_id
            obj.file_size = getattr(file, "file_size", None)
            obj.mime_type = getattr(file, "mime_type", None)
            obj.file_name = getattr(file, "file_name", None)
            if hasattr(file, "width"):
                obj.width = file.width
            if hasattr(file, "height"):
                obj.height = file.height
            if hasattr(file, "duration"):
                obj.duration = file.duration
        return obj
