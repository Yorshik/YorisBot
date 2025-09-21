from aiogram.types import MessageEntity, User

import contexts
from factories.commands.base import BaseCommand


class TagCommand(BaseCommand):
    factory_type = "command"
    prefix = "тег"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        return self.prefix_used(ctx)

    async def execute(self, ctx: contexts.MessageContext):
        mention_entity = MessageEntity(
            type="text_mention",
            offset=0,  # где в тексте начинается имя
            length=len(str(ctx.from_user.id)),  # длина имени
            user=User(id=ctx.from_user.id, is_bot=False, first_name=ctx.from_user.first_name)
        )
        text = f"{ctx.from_user.id}, теееег"
        await ctx.answer(text, entities=[mention_entity])


class NotTagCommand(BaseCommand):
    factory_type = "command"
    prefix = "нетег"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        return self.prefix_used(ctx)

    async def execute(self, ctx: contexts.MessageContext):
        text = f'<a href="tg://openmessage?id={ctx.from_user.id}">{ctx.from_user.id}</a>, вот твоя ссылка (без уведомления).'
        await ctx.answer(text, parse_mode="HTML")
