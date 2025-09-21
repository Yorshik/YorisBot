import re
import contexts


async def extract_user(ctx: contexts.MessageContext):
    if ctx.entities:
        for ent in ctx.entities:
            if ent.type == "text_mention":
                return ent.user.id
            if ent.type == "mention":
                username = ctx.text[ent.offset: ent.offset + ent.length]
                return username[1:]
    match = re.search(r"@(\d+)", ctx.text)
    if match:
        return int(match.group(1))
    if ctx.reply_to_message:
        return ctx.reply_to_message.from_user.id


async def extract_chat(ctx: contexts.MessageContext):
    if ctx.entities:
        for ent in ctx.entities:
            if ent.type == "mention":
                return ent.user.id
    match = re.search(r"@(\d+)", ctx.text)
    if match:
        return int(match.group(1))
    if ctx.reply_to_message:
        return ctx.reply_to_message.chat.id
