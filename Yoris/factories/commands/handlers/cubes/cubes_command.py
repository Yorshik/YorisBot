from factories.commands.base import BaseCommand
import contexts
from typing import cast
from django_redis.cache import RedisCache
from django.core.cache import cache
import decouple
import json
from utils import database_manager, parse_message
from utils.i18n import translate as _
import argparse
import shlex

cache = cast(RedisCache, cache)
CACHE_TIMEOUT = decouple.config("CACHE_TIMEOUT", cast=int, default=3600)


class CubesCommand(BaseCommand):
    def __init__(self):
        self.author = None
        self.user = None
        self.chat = None

    async def execute(self, ctx: contexts.MessageContext):
        key = f"cubes:{self.chat.id}:{ctx.from_user.id}"
        value = json.loads(cache.get(key) or "{}")
        if value:
            value = {int(key): value for key, value in value.items()}
        if self.user.id in value:
            if value[self.user.id] == "pending":
                await ctx.reply(_("You already invited {name} to play cubes", ctx=ctx, name=self.user.name))
                return
            if value[self.user.id] == "playing":
                await ctx.reply(_("You are already playing with {name}", ctx=ctx, name=self.user.name))
                return
        value[self.user.id] = {
            "status": "pending"
        }
        cache.set(key, json.dumps(value), timeout=CACHE_TIMEOUT)
        await ctx.reply(_("{user_name}, {author_name} invited you to play cubes", ctx=ctx, author_name=self.author.name, user_name=self.user.name))


class TerminalCubesCommand(CubesCommand):
    factory_type = "command"
    prefix = "cubes"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        prefix = self.prefix_used(ctx)
        if not prefix:
            return False
        text = ctx.text
        args = text[len(prefix):].strip()
        parser = argparse.ArgumentParser(prog=prefix, add_help=False)
        parser.add_argument("-user")
        try:
            _ = parser.parse_args(shlex.split(args))
        except SystemExit:
            return False
        extracted_user = await parse_message.extract_user(ctx)
        if not extracted_user:
            return False
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.user = await database_manager.get_user(extracted_user)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True


class FriendlyCubesCommand(CubesCommand):
    factory_type = "command"
    prefix = "кубы"

    async def matches(self, ctx: contexts.MessageContext) -> bool:
        if not self.prefix_used(ctx):
            return False
        extracted_user = await parse_message.extract_user(ctx)
        if not extracted_user:
            return False
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.user = await database_manager.get_user(extracted_user)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True
