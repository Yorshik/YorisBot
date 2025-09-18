import aiogram


class User:
    def __init__(self, user: aiogram.types.User):
        self.id = user.id
        self.is_bot = user.is_bot
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.username = user.username

    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return f"{self.username}"

class Chat:
    def __init__(self, chat: aiogram.types.Chat):
        self.id = chat.id
        self.type = chat.type
        self.title = chat.title
        self.username = chat.username
        self.first_name = chat.first_name
        self.last_name = chat.last_name
        self.is_direct = chat.is_direct_messages


class Context:
    def __init__(self, message: aiogram.types.Message):
        self.type = message.content_type
        self.id = message.message_id
        self.from_user = User(message.from_user)
        self.chat = Chat(message.chat)
        self.reply_to_message = message.reply_to_message
        self.quote = message.quote.text if message.quote else None
        self.is_via_bot = bool(message.via_bot)
        self.via_bot = message.via_bot.id if self.is_via_bot else None
        self.edit_date = message.edit_date
        self.entities = message.entities
        self.bot = message.bot


class FileContext:
    def __init__(self, message: aiogram.types.Message):
        self.caption = message.caption
        if message.document:
            file = message.document
        elif message.audio:
            file = message.audio
        elif message.video:
            file = message.video
        elif message.animation:
            file = message.animation
        elif message.photo:
            file = message.photo[-1]
        elif message.sticker:
            file = message.sticker
        else:
            file = None
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
