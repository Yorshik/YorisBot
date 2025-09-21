from factories.commands.base import BaseCommand
import argparse
import shlex
from typing import cast
from utils import database_manager, parse_message, cubes
from django_redis.cache import RedisCache
from django.core.cache import cache
import decouple
import contexts
import json
from utils.i18n import translate as _

cache = cast(RedisCache, cache)
CACHE_TIMEOUT = decouple.config("CACHE_TIMEOUT", cast=int, default=3600)


class CubesYesCommand(BaseCommand):
    def __init__(self):
        self.author = None
        self.user = None
        self.chat = None

    async def execute(self, ctx: contexts.MessageContext):
        second_player = self.author
        if self.user:
            key = f"cubes:{self.chat.id}:{self.user.id}"
            user_cache = json.loads(cache.get(key) or "{}")
            if str(self.author.id) not in user_cache:
                await ctx.reply(_("{name} didn't invite you to play cubes", ctx=ctx, name=self.user.name))
                return
            if user_cache[str(self.author.id)]["status"] == "playing":
                await ctx.reply(_("You are already playing cubes with {name}", ctx=ctx, name=self.user.name))
                return
            user_cache[str(self.author.id)]["status"] = "playing"
            cache.set(key, json.dumps(user_cache), timeout=CACHE_TIMEOUT)
            first_player = self.user
        else:
            invited_authors = cubes.get_invited_users(self.chat.id, self.author.id)
            if not invited_authors:
                await ctx.reply(_("Now one invited you to play cubes", ctx=ctx))
                return
            first_author_id = invited_authors[0]
            first_player = await database_manager.get_user(int(first_author_id))
            key = f"cubes:{self.chat.id}:{first_player.id}"
            user_cache = json.loads(cache.get(key) or "{}")
            if str(second_player.id) in user_cache:
                user_cache[str(second_player.id)]["status"] = "playing"
                cache.set(key, json.dumps(user_cache), timeout=CACHE_TIMEOUT)
        await cubes.play_cubes(first_player, second_player, ctx, self.chat)


class TerminalCubesYesCommand(CubesYesCommand):
    factory_type = "command"
    prefix = "cubes-yes"

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
