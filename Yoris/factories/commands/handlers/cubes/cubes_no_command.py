from utils import database_manager, cubes, parse_message
import json
from django_redis.cache import RedisCache
from typing import cast
from django.core.cache import cache
import contexts
from factories.commands.base import BaseCommand
import decouple
import shlex
import argparse
from utils.i18n import translate as _

cache = cast(RedisCache, cache)
CACHE_TIMEOUT = decouple.config("CACHE_TIMEOUT", cast=int, default=3600)


class CubesNoCommand(BaseCommand):
    def __init__(self):
        self.author = None
        self.user = None
        self.chat = None

    async def execute(self, ctx: contexts.MessageContext):
        if self.user:
            key = f"cubes:{self.chat.id}:{self.user.id}"
            user_cache = json.loads(cache.get(key, "{}"))
            if str(self.author.id) not in user_cache or user_cache[str(self.author.id)]["status"] != "pending":
                await ctx.reply(_("{name} didn't invite you to play cubes.", ctx=ctx, name=self.user.name))
                return
            del user_cache[str(self.author.id)]
            cache.set(key, json.dumps(user_cache), timeout=CACHE_TIMEOUT)

            await ctx.reply(_("You declined invitation to play cubes from {name}.", ctx=ctx, name=self.user.name))

        else:
            invited_authors = cubes.get_invited_users(self.chat.id, self.author.id)
            if not invited_authors:
                await ctx.reply(_("No one invited you to play cubes.", ctx=ctx))
                return
            first_author_id = invited_authors[0]
            first_player = await database_manager.get_user(int(first_author_id))
            key = f"cubes:{self.chat.id}:{first_player.id}"
            user_cache = json.loads(cache.get(key, "{}"))
            if str(self.author.id) in user_cache:
                del user_cache[str(self.author.id)]
                cache.set(key, json.dumps(user_cache), timeout=CACHE_TIMEOUT)

            await ctx.reply(_("You declined invitation to play cubes from {name}.", ctx=ctx, name=first_player.name))


class TerminalCubesNoCommand(CubesNoCommand):
    factory_type = "command"
    prefix = "cubes-no"

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
            self.user = None
        else:
            self.user = await database_manager.get_user(extracted_user)
        self.author = await database_manager.get_user(ctx.from_user.id)
        self.chat = await database_manager.get_chat(ctx.chat.id)
        return True
