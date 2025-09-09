import re

import aiogram


async def extract_user(msg: aiogram.types.Message):
    if msg.entities:
        for ent in msg.entities:
            if ent.type == "text_mention":
                return ent.user.id
            if ent.type == "mention":
                username = msg.text[ent.offset: ent.offset + ent.length]
                print(username)
                return username[1:]
    match = re.search(r"@(\d+)", msg.text)
    if match:
        return int(match.group(1))
    if msg.reply_to_message:
        return msg.reply_to_message.from_user.id


async def extract_chat(msg: aiogram.types.Message):
    if msg.entities:
        for ent in msg.entities:
            print(ent)
            if ent.type == "mention":
                return ent.user.id
    match = re.search(r"@(\d+)", msg.text)
    if match:
        return int(match.group(1))
    if msg.reply_to_message:
        return msg.reply_to_message.chat.id
