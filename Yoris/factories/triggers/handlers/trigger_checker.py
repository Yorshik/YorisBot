import aiogram
from aiogram.types import Message
from utils import database_manager


async def trigger(msg: Message):
    chat = await database_manager.get_chat(msg.chat.id)
    text = msg.text
    triggers = await database_manager.get_text_triggers(chat)

    for trigger in triggers:
        if text.lower() == trigger.text.lower():
            await msg.answer(trigger.answer)
            return
