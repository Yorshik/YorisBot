from aiogram.types import Message

from contexts.base_context import Context, User



class ChatMemberLeftContext(Context):
    def __init__(self, message: Message):
        super().from_message(message)
        self.left_user = User(message.left_chat_member)

