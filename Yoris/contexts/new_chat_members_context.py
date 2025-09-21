from aiogram.types import Message

from contexts.base_context import Context, User


class NewChatMembersContext(Context):
    def __init__(self, message: Message):
        super().from_message(message)
        self.new_chat_members = [User(new_chat_member) for new_chat_member in message.new_chat_members]
